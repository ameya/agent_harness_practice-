# R00 acceptance evidence

Validated on 2026-10-25 in the Linux cloud environment with Python 3.12.14 and Pytest 8.4.2. No credentials, Ollama service or model weights were used. Commands below ran in the repository root with `/workspace/.venvs/agent-harness-lab/bin` on PATH and `PYTHONDONTWRITEBYTECODE=1`.

| Command/check | Actual result |
|---|---|
| `python -m pip install --no-cache-dir -e '.[dev]'` | Editable package and development dependencies installed successfully. |
| `python -m pip check` | No broken requirements found. |
| `python -m pytest -q` | **57 passed in 0.14s**, none skipped or expected-failing. |
| `python -m agent_harness_lab investigate INC-1042 --provider fake` | Exit 0; readable observations, unconfirmed hypothesis, missing evidence and recommendations. |
| `python -m agent_harness_lab investigate INC-1042 --provider fake --json` | Exit 0; valid JSON with insufficient-evidence status, `confirmed: false`, model_calls 1, tool_calls 0. |
| `python -m agent_harness_lab investigate UNKNOWN --provider fake --json` | Exit 2; structured `unknown_incident` error, model_calls 0, tool_calls 0. |
| `python -m agent_harness_lab investigate INC-1042 --provider bad` | Exit 2; structured `invalid_input` error. |
| Fake-provider JSON command from `/tmp` | Exit 0; packaged INC-1042 fixture located independently of working directory. |
| `git diff --check` | Passed. |

The fake-provider test rejects any attempted socket creation or subprocess execution while exercising the runner. Other tests cover exactly-one-call behavior, unknown inputs before invocation, invalid fixtures, malformed/unsupported output, root-cause promotion rejection, evidence provenance, unexpected tool request rejection, provider failure sanitization, CLI/module execution, instruction-like fixture text as inert data, and mocked local Ollama success/failure. Ollama tests check literal-loopback-only endpoints, timeout limits, no redirects, proxy bypass, payload shape, invalid JSON and response size limits. These checks validate the implemented paths, not a sandbox for malicious in-process Python adapters.

## Not executed

- Live Ollama inference: no service or downloaded model was available. Mocked protocol/error checks passed; no live inference success is claimed.
- Windows PowerShell execution and Python 3.11: commands are documented, but this environment is Linux/Python 3.12.14. No Windows or 3.11 execution is claimed.
- R01 and later checks: intentionally outside R00 scope.

## R01 handoff

R00 supplies an installed src-layout package, synthetic fixture repository, immutable contracts, one-call provider interface, offline deterministic baseline, conservative report validator, CLI, documentation and a passing regression suite. It is ready as an input baseline for a separately authorized R01 task. Before beginning that release, define and approve R01 scope/acceptance around bounded loop steps, termination and failure handling; retain offline behavior, grounded observations, unconfirmed hypotheses, sanitized errors and no mutation. No R01 work was performed, committed or pushed.
