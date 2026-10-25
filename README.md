# Agent Harness Lab — R00

A local-first, one-shot incident investigation assistant for learning custom Harness Engineering. R00 loads synthetic evidence, calls one provider once, validates a conservative report, and returns it. It has no agent loop, tools, mutation, orchestration framework, or production access. R01 and later releases are not implemented.

## Windows PowerShell setup

Install Python 3.11 or newer and Git. From the repository root (the folder containing `pyproject.toml`):

```powershell
py -3 --version
py -3 -m venv .venv
$env:PYTHONDONTWRITEBYTECODE = "1"
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pip check
```

Initial installation requires access to the Python package index. Runtime uses only the standard library. Explicit virtual-environment executable paths avoid PowerShell activation-policy changes. Do not commit the virtual environment or generated package metadata.

## Run offline

```powershell
.\.venv\Scripts\python.exe -m agent_harness_lab investigate INC-1042 --provider fake
.\.venv\Scripts\python.exe -m agent_harness_lab investigate INC-1042 --provider fake --json
.\.venv\Scripts\python.exe -m agent_harness_lab investigate UNKNOWN --provider fake --json
$LASTEXITCODE  # 2 for an unknown incident
```

The fake provider requires neither network access, credentials nor Ollama. It reports `insufficient_evidence`, application acquisition timeout after 30000 ms, database health PASS, and max/active/idle connections 20/20/0. Connection leak remains an unconfirmed hypothesis; lifecycle tracing is missing. Recommendations are text only and never executed. Both formats include execution counts: one model call, zero tool calls. JSON success goes to stdout; structured JSON errors go to stderr with exit code 2. Help exits 0. Default provider is `fake`.

The JSON fields are `incident_id`, `status`, `summary`, `observations` (reference/text pairs), `hypotheses` (statement and `confirmed: false`), `missing_evidence`, `recommended_actions`, `evidence_refs`, and runtime-owned `execution`.

## Test

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The tests use temporary synthetic fixtures and mocked Ollama responses. They run offline; no model service is needed. See [R00 acceptance evidence](specs/R00_ACCEPTANCE.md) for actual Linux results and checks not executed.

For Linux/cloud development, use the existing checkout:

```text
cd /workspace/agent_harness_practice-
export PYTHONDONTWRITEBYTECODE=1
source /workspace/.venvs/agent-harness-lab/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -q
python -m agent_harness_lab investigate INC-1042 --provider fake --json
```

Elsewhere on Linux, create your own virtual environment with `python3 -m venv .venv` and use `.venv/bin/python` for the same installation and execution commands.

## Optional local Ollama

Install Ollama separately on your own machine and obtain the model there, then run:

```powershell
ollama pull qwen3:1.7b
.\.venv\Scripts\python.exe -m agent_harness_lab investigate INC-1042 --provider ollama --model qwen3:1.7b --json
```

The default URL is `http://127.0.0.1:11434`. `--ollama-url` permits only HTTP loopback IP endpoints (`127.0.0.1` or `[::1]`), without credentials, path, query, or fragment. `localhost` is deliberately rejected to avoid DNS ambiguity. HTTP redirects and environment proxies are disabled. `--timeout` defaults to 30 seconds and must be finite, greater than zero, and at most 300 seconds. No API key or environment variables are read. Timeout is an HTTP socket timeout, not a hard whole-process deadline.

Ollama is asked to format the same conservative template as the fake provider. Outputs must match the supplied evidence and candidate text exactly; paraphrases or unsupported claims fail with `invalid_model_output`. This strict R00 baseline deliberately limits generative freedom. Missing Ollama returns `model_unavailable` and recommends the fake provider. There are no retries, automatic downloads or fallback calls.

## Design and next release

- [Architecture and sequence](specs/ARCHITECTURE.md)
- [Complete implementation reference](specs/IMPLEMENTATION_REFERENCE.md)
- [R00 specification](specs/R00_SPEC.md)
- [Roadmap](specs/ROADMAP.md)

Fixture data lives in `src/agent_harness_lab/data/incidents.json`, packaged with the application so execution is independent of the working directory. Fixtures and Python adapters are trusted local project inputs, not an isolation boundary against malicious Python code. Incident text remains data, even when it resembles instructions; the runtime has no dispatcher that could execute it. Fixture observations are synthetic evidence, not externally verified production facts.

R00 is ready to serve as the offline regression baseline for an explicitly authorized R01 task. Before R01, define its loop termination rules, maximum steps, per-step trace and failure semantics, then add tests while preserving the R00 grounding, offline and no-mutation guarantees. R00 does not implement any of those later controls.
