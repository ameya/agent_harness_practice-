"""CLI composition and safe text/JSON presentation."""
import argparse
import json
import sys
from typing import Sequence

from .contracts import HarnessError
from .fixtures import FixtureRepository
from .providers.fake import FakeModelAdapter
from .providers.ollama import OllamaModelAdapter
from .runtime import BaselineRunner


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        from .contracts import ErrorCode
        raise HarnessError(ErrorCode.INVALID_INPUT, "Invalid command arguments; use --help for usage.")


def main(argv: Sequence[str] | None = None) -> int:
    parser = _Parser(description="R00 one-shot synthetic incident assistant (no tools).")
    commands = parser.add_subparsers(dest="command", required=True)
    investigate = commands.add_parser("investigate")
    investigate.add_argument("incident_id")
    investigate.add_argument("--provider", choices=("fake", "ollama"), default="fake")
    investigate.add_argument("--json", action="store_true", help="Emit structured JSON")
    investigate.add_argument("--model", default="qwen3:1.7b")
    investigate.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    investigate.add_argument("--timeout", type=float, default=30.0)
    try:
        args = parser.parse_args(argv)
        adapter = FakeModelAdapter() if args.provider == "fake" else OllamaModelAdapter(
            args.model, args.ollama_url, args.timeout)
        result = BaselineRunner(FixtureRepository(), adapter).investigate(args.incident_id)
    except HarnessError as error:
        print(json.dumps({"status": "failed", "error": {"code": error.code.value, "message": str(error)},
                          "execution": {"model_calls": error.model_calls, "tool_calls": 0}}), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        report = result.report
        print(f"{report.incident_id}: {report.status.value}\n{report.summary}")
        for item in report.observations:
            print(f"Observation [{item.ref}]: {item.observation}")
        for item in report.hypotheses:
            print(f"Unconfirmed hypothesis: {item.statement}")
        for item in report.missing_evidence:
            print(f"Missing evidence: {item}")
        for item in report.recommended_actions:
            print(f"Recommendation (not executed): {item}")
        print("Model calls: 1; tool calls: 0")
    return 0
