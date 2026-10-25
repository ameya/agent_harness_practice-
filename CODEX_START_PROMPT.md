# Paste this into Codex (Code mode)

Develop the source code for **R00 of Agent Harness Lab** in this GitHub repository.

The learning goal is **custom Agent Harness Engineering**. This is NOT a request to build the entire 12-discipline project or use a prebuilt managed orchestration framework. We will evolve the system release by release.

First read `AGENTS.md`, `specs/R00_SPEC.md` and `specs/ROADMAP.md`. If those files are absent because I started from an empty GitHub repository, CREATE THEM using the constraints below before implementing code:

- Python 3.11+ on Windows; source-oriented, local-first.
- R00 is a deterministic **one-shot assistant baseline**; R01 adds an execution loop; R02 adds a tool registry. Do not claim R00 is already an autonomous tool-using agent.
- Use synthetic incident `INC-1042` (payment application, database healthy, active/max connections 20/20, idle 0, connection acquisition timeouts). Connection leak is a **hypothesis**, not a confirmed root cause.
- Provider-neutral model interface, deterministic FakeModelAdapter for offline/CI tests and optional OllamaModelAdapter for local `qwen3:1.7b`.
- Typed report separating verified observations, hypotheses, missing evidence, recommendations and evidence references.
- R00 can make no mutating tool calls or production changes. One model invocation maximum. Never send data to external infrastructure except optional user-configured local Ollama.
- Provide a CLI, JSON fixture, Pytest suite, README, architecture and implementation reference docs, and `.gitignore`.
- Never create `.bat`, `.sh`, JARs, downloaded weights, binary outputs, or secrets in Git. Do not deploy, commit or push without explicit permission.

### Process
1. Perform a concise read-only inspection of the repository and explain your implementation plan and any necessary assumptions.
2. Build **R00 only**. Keep it minimal and well-factored; code should be understandable to developers learning how harnesses work.
3. Generate `specs/ARCHITECTURE.md` with a Mermaid component diagram and a readable run sequence.
4. Generate `specs/IMPLEMENTATION_REFERENCE.md` explaining every module, class, public method, essential field, configuration property and their purpose.
5. Write deterministic offline tests for success, unknown incident, invalid structured output, ground-truth separation (observation versus hypothesis) and no mutating actions.
6. Run `python -m pytest -q` plus CLI smoke test when supported; fix failures and report exactly which commands ran and their results. If prerequisites are missing, clearly say which tests could not execute.
7. End with a file tree, what was implemented, what was tested, commands to run in Windows PowerShell, limitations, and R01 handoff notes.

### R00 acceptance demonstration
The documented command `python -m agent_harness_lab investigate INC-1042 --provider fake` must run without Ollama or network access and return valid structured output grounded in synthetic evidence. Root cause must remain unconfirmed. Optional local Ollama execution is separate and must not be a prerequisite for the fake-provider tests.

Stop when R00 is complete. Do not begin R01.
