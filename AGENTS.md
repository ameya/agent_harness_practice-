# Agent Harness Lab — Codex Repository Instructions

## Purpose
Build a Python agent and evolve its **custom agent harness**, one small verified release at a time. The learning goal is harness internals (execution control, tools, context, security, state, recovery, observability, human approval, and evaluation), not replacing them with a managed agent SDK.

## Environment
- Python 3.11+; Windows and VS Code are primary local targets.
- Deterministic offline execution and testing must always work without credentials or running Ollama.
- Optional local model inference through Ollama (`qwen3:1.7b`) may be included behind a model adapter.
- Python package layout under `src/`. Use Pytest and type hints.

## Repository policies
- Read `specs/R00_SPEC.md` and `specs/ROADMAP.md` before coding.
- Work on **R00 only** unless the user explicitly authorizes another release.
- Custom runtime, not LangGraph, Pydantic AI, OpenAI Agents SDK or other agent orchestration frameworks for R00.
- Build only what R00 requires. Interfaces may anticipate later releases, but no speculative implementation.
- All data must be synthetic fixture data. No real credentials, personal data, production access, or uncontrolled shell/network execution.
- Produce Markdown specification detailing every created Python module, class, public function, important field, contract, and configuration variable.
- Update README and specs when implementation changes.
- Add tests for normal behavior, malformed inputs, model failures, and relevant security boundaries.
- Run `python -m pytest -q` and document actual results. Never claim tests passed if they were not executed.
- Do not create `.bat`, `.sh`, Docker images, JARs, downloaded model weights, binary assets, or compiled output. Only source, JSON fixtures, config and Markdown belong in source control.
- Add `.gitignore` for virtual environments, caches, build files, secrets and binaries.
- Do not create commits, push changes, deploy, create credentials, or operate external systems without separate user permission.
- Stop after R00; report files changed, tests executed, limitations and explicit readiness criteria for R01.

## Quality goals
- Observable, reproducible demo rather than a convincing but untestable chat response.
- Assertions about the incident must be grounded in synthetic fixture data or marked as hypotheses.
- Preserve distinct fields for verified observations, hypotheses and missing evidence.
- No mutating actions in R00; errors should be user-readable and machine-identifiable.
