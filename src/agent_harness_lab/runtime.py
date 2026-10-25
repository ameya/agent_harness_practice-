"""A bounded one-shot baseline, with no tools, retries, or execution loop."""
from .contracts import (ErrorCode, ExecutionSummary, HarnessError, InvestigationReport,
                        InvestigationResult)
from .fixtures import FixtureRepository
from .model_adapter import ModelAdapter, ModelRequest


class BaselineRunner:
    def __init__(self, repository: FixtureRepository, adapter: ModelAdapter):
        self.repository = repository
        self.adapter = adapter

    def investigate(self, incident_id: str) -> InvestigationResult:
        incident = self.repository.get(incident_id)
        try:
            output = self.adapter.generate(ModelRequest(incident))
        except HarnessError as error:
            raise HarnessError(error.code, str(error), model_calls=1) from None
        except Exception:
            raise HarnessError(ErrorCode.MODEL_UNAVAILABLE, "Model invocation failed; no actions were executed.", 1) from None
        try:
            report = InvestigationReport.from_dict(output, incident)
        except (ValueError, TypeError, KeyError, RecursionError):
            raise HarnessError(ErrorCode.INVALID_MODEL_OUTPUT, "Model response violates the grounded R00 report contract.", 1) from None
        return InvestigationResult(report, ExecutionSummary(model_calls=1))
