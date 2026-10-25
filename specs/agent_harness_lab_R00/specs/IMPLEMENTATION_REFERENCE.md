# R00 implementation reference

All runtime modules use Python 3.11+ and the standard library. Dataclasses are immutable (`frozen=True`); tuple fields preserve immutable record structure. Validation occurs at external JSON boundaries through factory methods, not through direct dataclass constructors. Direct Python construction and custom adapters are trusted application code.

## Module inventory

| Module/file | Responsibility |
|---|---|
| `agent_harness_lab/__init__.py` | Package scope and R00 description; no exported initialization effects. |
| `__main__.py` | Calls `cli.main()` and exits with its return code. |
| `cli.py` | Parser, provider selection, stdout/stderr formatting and process result. |
| `contracts.py` | Typed records, validation and safe errors. |
| `fixtures.py` | Read-only packaged or explicitly supplied synthetic JSON loading. |
| `model_adapter.py` | Provider-neutral request and protocol. |
| `runtime.py` | One-call orchestration, provider failure handling and report validation. |
| `providers/__init__.py` | Provider package description; no startup effects. |
| `providers/fake.py` | Deterministic report formatting from supplied incident. |
| `providers/ollama.py` | Optional bounded local HTTP chat transport. |
| `data/incidents.json` | Packaged synthetic INC-1042 evidence and candidate annotations. |
| `tests/test_baseline.py` | Contract, runtime, fixture, offline/security and CLI checks. |
| `tests/test_ollama.py` | Endpoint, timeout, redirect, proxy, protocol and failure checks using mocks. |
| `pyproject.toml` | Setuptools build, src discovery, package JSON inclusion, development extra and test configuration. |
| `.gitignore` | Excludes local environments, caches, metadata, build outputs, secrets and binaries. |

## Contracts (`contracts.py`)

| Class | Fields / contract |
|---|---|
| `ErrorCode(str, Enum)` | `INVALID_INPUT`, `INVALID_FIXTURE`, `UNKNOWN_INCIDENT`, `MODEL_UNAVAILABLE`, `INVALID_MODEL_OUTPUT`; serialized lowercase values are stable machine-readable categories. |
| `HarnessError(Exception)` | `code: ErrorCode`; safe message via `str(error)`; `model_calls: int = 0`, attempted invocation count. Constructor `(code, message, model_calls=0)` initializes these. |
| `Status(str, Enum)` | `INSUFFICIENT_EVIDENCE` for valid R00 reports, `FAILED` for error envelopes. No successful confirmed-root-cause status. |
| `Evidence` | `ref: str` provenance identifier; `observation: str` synthetic recorded observation. |
| `Incident` | `incident_id`, `title`: text; `evidence: tuple[Evidence,...]`; `candidate_hypotheses`, `missing_evidence`, `recommended_actions`: text tuples. Candidates are annotations, not facts. |
| `Hypothesis` | `statement: str`; `confirmed: bool = False`. External reports must explicitly supply false, not numeric zero. |
| `InvestigationReport` | `incident_id`, `status`, `summary`; `observations: tuple[Evidence,...]`; `hypotheses: tuple[Hypothesis,...]`; text tuples `missing_evidence`, `recommended_actions`, `evidence_refs`. No execution/action fields accepted from a provider. |
| `ExecutionSummary` | `model_calls: int`; `tool_calls: int = 0`. R00 runner returns 1/0; failures carry attempted calls separately. |
| `InvestigationResult` | `report: InvestigationReport`, `execution: ExecutionSummary`. |

Public operations:

- `Evidence.from_dict(value: Any) -> Evidence`: requires exactly `ref` and `observation`, each nonblank text of at most 2000 characters; raises `ValueError` on invalid input.
- `Incident.from_dict(value: Any) -> Incident`: requires exactly its six fields, 1–32 evidence items with unique references, and 1–32 nonblank strings per annotation list. Raises `ValueError` on invalid input. Each string is bounded at 2000 characters.
- `InvestigationReport.from_dict(value: Any, incident: Incident) -> InvestigationReport`: requires exact report fields and fixture identity; observations and references match all incident evidence in order; each hypothesis matches a supplied candidate and has `confirmed is False`; missing evidence and actions match fixture lists. Status must be `insufficient_evidence`; summary must be `Evidence reviewed; root cause remains unconfirmed.` Raises `ValueError` on malformed or unsupported output. This intentionally disallows new model-generated diagnoses and paraphrases.
- `InvestigationReport.to_dict() -> dict[str, Any]`: dataclass serialization, retaining string-enum status and tuples; standard `json.dumps` serializes them as JSON strings/arrays.
- `InvestigationResult.to_dict() -> dict[str, Any]`: report fields at top level plus runtime-owned `execution` dictionary.

Internal helpers `_object(value, keys)`, `_text(value)` and `_texts(value)` validate exact object shape, bounded nonblank text and bounded nonempty lists; they raise `ValueError`. They never execute supplied content.

## Fixture repository (`fixtures.py`)

`FixtureRepository(path: Path | None = None)` retains `path`. None selects package resource `data/incidents.json` via `importlib.resources`; explicit paths support tests and trusted local callers. No CLI fixture-path option exists.

`get(incident_id: str) -> Incident` checks a nonblank ID of at most 128 characters. It reads UTF-8 JSON bounded at 65536 characters, requires only the root `incidents` field, validates 1–100 records and rejects duplicate IDs. It returns the matching incident without filesystem mutation. Errors are `HarnessError`: invalid ID → `invalid_input`; missing/unreadable/malformed fixture → `invalid_fixture`; unmatched ID → `unknown_incident`. Original exception details and paths are suppressed.

## Request and protocol (`model_adapter.py`)

`ModelRequest(incident: Incident)` holds only immutable incident data. `to_dict() -> dict[str, Any]` returns an `incident` object for transport. No callable tools or execution capabilities are included.

`ModelAdapter(Protocol).generate(request: ModelRequest) -> object` specifies one invocation returning an untrusted decoded report. Providers may raise `HarnessError`; unexpected exceptions are sanitized by the runner. There is no retry, streaming, tool-call or continuation method.

## Runtime (`runtime.py`)

`BaselineRunner(repository: FixtureRepository, adapter: ModelAdapter)` retains `repository` and `adapter` dependencies.

`investigate(incident_id: str) -> InvestigationResult` loads/validates context, calls the adapter once, validates its result and returns `ExecutionSummary(model_calls=1, tool_calls=0)`. Repository failures occur before model invocation. Provider `HarnessError` is rethrown with call count 1; unexpected provider exceptions become sanitized `model_unavailable`. Invalid report data becomes `invalid_model_output` with call count 1. It never retries or executes an action.

## Providers

`FakeModelAdapter.generate(request: ModelRequest) -> object` returns a fresh report dictionary copying request evidence and annotations, conservative summary, insufficient-evidence status and false hypothesis confirmations. It performs no network, subprocess or file operations. Identical requests yield equal outputs. It does not hard-code the incident ID or evidence findings.

`OllamaModelAdapter(model: str = "qwen3:1.7b", base_url: str = "http://127.0.0.1:11434", timeout: float = 30.0)` validates and retains `model`, normalized `base_url` and `timeout`. A model is nonblank text of at most 128 characters. URL must be HTTP with host exactly `127.0.0.1` or `::1`, no authentication/query/fragment/non-root path, and a valid positive optional port. Timeout must be finite and in `(0, 300]`. Bad configuration raises `invalid_input`.

`generate(request: ModelRequest) -> object` POSTs UTF-8 JSON to `/api/chat` using a system instruction and user JSON data/template. The template is supplied by `FakeModelAdapter` for consistent conservative formatting; the runtime remains provider-independent. Request fields are `model`, `stream: false`, `format: json`, `options.temperature: 0`, and `messages`. It disables proxy routing and redirects, reads at most 65537 bytes, rejects over 65536, then decodes the Ollama envelope `message.content` as report JSON. Transport/HTTP failures become `model_unavailable`; malformed/oversized output becomes `invalid_model_output`. The runner performs final report validation. No model download occurs.

Internal `_NoRedirect(HTTPRedirectHandler).redirect_request(req, fp, code, msg, headers, newurl)` returns None so redirects fail instead of following another destination.

## CLI (`cli.py`)

`main(argv: Sequence[str] | None = None) -> int` uses explicit arguments or process arguments. Composes repository/provider/runner; prints a valid report to stdout and returns 0, or structured error JSON to stderr and returns 2. `--help` uses argparse's standard `SystemExit(0)`. Internal `_Parser.error(message)` maps argument errors to a safe `HarnessError(invalid_input)` without echoing arbitrary input. Entry module converts the return code to process exit status.

| Argument | Default / behavior |
|---|---|
| `investigate incident_id` | Required subcommand and ID. |
| `--provider {fake,ollama}` | `fake`; selects adapter. |
| `--json` | Off; selects JSON instead of readable text for success. Errors always use JSON. |
| `--model` | `qwen3:1.7b`; used only by Ollama. |
| `--ollama-url` | `http://127.0.0.1:11434`; used only by Ollama. |
| `--timeout` | Float, 30 seconds; used only by Ollama. |

Error envelope: `status: failed`, `error: {code, message}`, `execution: {model_calls, tool_calls: 0}`. No traceback or raw provider diagnostics are printed. `insufficient_evidence` is a valid result, not a process failure.

## Configuration and tests

No application environment variables or secrets are required/read. `PYTHONDONTWRITEBYTECODE=1` is an optional Python interpreter setting to avoid bytecode artifacts. No `.bat`/`.sh` startup helpers exist. Project version is 0.1.0; runtime dependency list is empty. Build backend requires setuptools >=68; development extra pins Pytest 8.4.2. Tests are discovered in `tests/` and Pytest's persistent cache is disabled. Package data includes `data/*.json` for working-directory-independent reads.

`tests/test_baseline.py` uses a test-only `StubAdapter(output=None, error=None)` with `generate(request)` and `calls` to assert invocation counts, plus `incident`/`report` fixtures. Tests cover grounded offline determinism, supplied-context use, unknown/malformed incident IDs, output-field mutations, malformed output shapes, safe failures, invalid fixtures/duplicate evidence, instruction-like text, text/JSON/error CLI output and the actual module entry point. `tests/test_ollama.py` mocks HTTP openers to exercise payloads and transport failures; no live service is contacted. Run `python -m pytest -q`; actual results and unexecuted platform checks are in `R00_ACCEPTANCE.md`.
