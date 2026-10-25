# Agent Harness Lab — Progressive Roadmap

Implement and verify one release at a time; do not begin later releases automatically.

| Release | Focus | Primary learning outcome |
|---|---|---|
| R00 | Baseline assistant, fake model and optional Ollama adapter, typed report | Reproducible baseline and provider isolation |
| R01 | Agent loop with max-steps, stopping conditions, bounded model/tool steps | Execution control |
| R02 | Tool registry, schemas, deterministic local read-only tools | Tool contracts, routing and validation |
| R03 | Context assembly, provenance and budgeting | Context harness engineering |
| R04 | Harness security: allowlists, permission checks, tenant context isolation, injection test cases | Enforcement outside model |
| R05 | State persistence, checkpoints, retries and recovery | Durable, safe execution |
| R06 | Structured traces, audit events, latency and token metrics | Observability |
| R07 | Human approval for simulated mutating actions | Governed action authorization |
| R08 | Golden incidents, regression suite, reliability/security evals | Evaluation harness |
| R09 | Compare design with LangGraph, Pydantic AI and OpenAI Agents SDK | Architectural tradeoffs |

Each release requires its own scope, acceptance criteria, source code, tests, updates to architecture/specification and README, and observed test results. Never introduce actual dangerous or production-mutating tools into the practice project without explicit permission and appropriate controls.
