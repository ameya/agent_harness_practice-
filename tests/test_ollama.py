import json
from io import BytesIO
from urllib.error import URLError
from urllib.request import Request

import pytest

from agent_harness_lab.contracts import ErrorCode, HarnessError
from agent_harness_lab.fixtures import FixtureRepository
from agent_harness_lab.model_adapter import ModelRequest
from agent_harness_lab.providers.fake import FakeModelAdapter
from agent_harness_lab.providers.ollama import OllamaModelAdapter, _NoRedirect
from agent_harness_lab.runtime import BaselineRunner


@pytest.mark.parametrize("url", ["https://example.com", "http://example.com", "http://localhost:11434",
                                  "http://127.0.0.1@evil.test", "http://127.0.0.1/a",
                                  "http://127.0.0.1?x=1", "http://127.0.0.1:99999"])
def test_remote_or_ambiguous_endpoints_rejected(url):
    with pytest.raises(HarnessError) as caught:
        OllamaModelAdapter(base_url=url)
    assert caught.value.code is ErrorCode.INVALID_INPUT


@pytest.mark.parametrize("timeout", [0, -1, 301, float("nan"), float("inf")])
def test_timeout_bounds(timeout):
    with pytest.raises(HarnessError):
        OllamaModelAdapter(timeout=timeout)


def test_redirects_disabled():
    assert _NoRedirect().redirect_request(None, None, 302, "", {}, "http://example.com") is None


def test_local_protocol_success(monkeypatch):
    incident = FixtureRepository().get("INC-1042")
    report = FakeModelAdapter().generate(ModelRequest(incident))
    class Opener:
        def open(self, request, timeout):
            assert isinstance(request, Request)
            assert request.full_url == "http://127.0.0.1:11434/api/chat"
            payload = json.loads(request.data)
            assert payload["stream"] is False
            assert payload["messages"][0]["role"] == "system"
            assert "tools" not in payload
            assert timeout == 30
            return BytesIO(json.dumps({"message": {"content": json.dumps(report)}}).encode())
    def opener(*handlers):
        assert handlers[0].proxies == {}
        assert isinstance(handlers[1], _NoRedirect)
        return Opener()
    monkeypatch.setattr("agent_harness_lab.providers.ollama.build_opener", opener)
    result = BaselineRunner(FixtureRepository(), OllamaModelAdapter()).investigate("INC-1042")
    assert result.report.hypotheses[0].confirmed is False


@pytest.mark.parametrize("raw", [b"invalid", b"{}", b"x" * 65537,
                                  b'{"message":{"content":"[]"}}'])
def test_invalid_ollama_response(monkeypatch, raw):
    class Opener:
        def open(self, request, timeout):
            return BytesIO(raw)
    monkeypatch.setattr("agent_harness_lab.providers.ollama.build_opener", lambda *args: Opener())
    with pytest.raises(HarnessError) as caught:
        BaselineRunner(FixtureRepository(), OllamaModelAdapter()).investigate("INC-1042")
    assert caught.value.code is ErrorCode.INVALID_MODEL_OUTPUT
    assert caught.value.model_calls == 1


def test_unavailable_ollama(monkeypatch):
    class Opener:
        def open(self, request, timeout):
            raise URLError("private diagnostic")
    monkeypatch.setattr("agent_harness_lab.providers.ollama.build_opener", lambda *args: Opener())
    with pytest.raises(HarnessError) as caught:
        BaselineRunner(FixtureRepository(), OllamaModelAdapter()).investigate("INC-1042")
    assert caught.value.code is ErrorCode.MODEL_UNAVAILABLE
    assert "private diagnostic" not in str(caught.value)
    assert "--provider fake" in str(caught.value)
