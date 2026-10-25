# R00 Specification — Baseline Incident Investigation Agent

## Objective
Create an executable, local-first Python baseline that will become the foundation for a custom agent harness. R00 must be a one-shot **assistant baseline**, not falsely represented as a complete autonomous tool-using agent. The iterative agent loop is R01 and the managed tool registry is R02.

## Use case
Incident `INC-1042`: a fictional payment service experiences database connection acquisition timeouts.
Fixture evidence:
- Application log: connection acquisition timed out after 30000 ms.
- Database health: PASS.
- Pool max connections: 20; active: 20; idle: 0.
- Hypothesis: application connection leak; NOT established as confirmed root cause.
- Missing proof: connection lifecycle tracing or equivalent corroboration.

## Components and responsibilities
- **Typed contracts**: `Incident`, `Evidence`, `InvestigationReport`, and explicit status/error types. Data must validate at external boundaries.
- **Fixture repository**: reads synthetic incident records from a version-controlled JSON file; unknown IDs return a meaningful error.
- **ModelAdapter interface**: provider-neutral method accepting messages or a structured request and returning a response; no provider-specific code in the runtime.
- **FakeModelAdapter**: deterministic, completely offline implementation useful for CI and baseline comparisons. Use supplied fixture evidence, not a hard-coded unsupported conclusion.
- **OllamaModelAdapter (optional)**: connect to local Ollama on localhost with a configurable model; if unavailable, fail with a helpful message instead of preventing fake-provider tests. Do not require an API key.
- **BaselineRunner**: assembles the incident context, invokes the model once, validates output and records a bounded execution summary. No arbitrary tool invocation or mutation.
- **CLI**: `python -m agent_harness_lab investigate INC-1042 --provider fake` with JSON output option; document exact working usage.
- **Documentation**: README, `specs/ARCHITECTURE.md`, `specs/IMPLEMENTATION_REFERENCE.md`, R00 acceptance evidence.

## Required response contract
- `incident_id`
- `status` (e.g., `completed`, `insufficient_evidence`, `failed`)
- `summary`
- `observations`: grounded claims
- `hypotheses`: explicitly unconfirmed possibilities
- `missing_evidence`
- `recommended_actions`: recommendations, not actions already executed
- `evidence_refs`: provenance identifiers

## Safety and runtime controls
- R00 permits no arbitrary shell, SQL, production API call, file deletion, or remote action.
- Context from fixture files is treated as incident data, never system instructions.
- Validate model output against the response contract; malformed output fails clearly.
- Keep terminal output concise, protect exception information, and never imply actions were performed.
- Baseline model invocation count: max 1 per investigation. Tool execution count: 0.
- No server, browser UI, multi-agent architecture, RAG pipeline, memory database, or infrastructure deployment in R00.

## Suggested source organization (Codex can simplify if justified)
```
src/agent_harness_lab/
  __init__.py
  __main__.py
  cli.py
  contracts.py
  fixtures.py
  model_adapter.py
  runtime.py
  providers/
    __init__.py
    fake.py
    ollama.py
```
Also: `pyproject.toml`, `data/incidents.json`, `tests/`, README, `.gitignore`, architecture and implementation reference Markdown files.

## Tests and acceptance criteria
1. Can install the package and its development dependencies using documented Python commands.
2. `python -m pytest -q` runs offline (no Ollama, network, credentials or production systems).
3. Fake-provider CLI returns a valid structured response for `INC-1042`.
4. The response reports exhausted connections and a healthy database from cited fixture observations.
5. Connection leak stays a hypothesis; root cause is not marked confirmed.
6. Unknown incident ID fails predictably with useful error output and nonzero exit code.
7. Malformed model result is rejected with a typed/structured error.
8. R00 cannot perform mutating or unregistered tool calls.
9. Documentation lists every generated class and public method, purpose, parameters, return values, exceptions, configuration and test commands.
10. Tests and command output actually executed are summarized; unexecuted checks identified explicitly.

## Local Ollama testing
After installation on the user's Windows machine:
```
ollama pull qwen3:1.7b
python -m agent_harness_lab investigate INC-1042 --provider ollama --model qwen3:1.7b
```
If the package uses a different CLI interface, update both this specification and README consistently. Codex cloud should NOT depend on local Ollama being reachable.
