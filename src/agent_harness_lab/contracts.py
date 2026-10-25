"""Immutable validated boundary contracts and safe error categories."""
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


class ErrorCode(str, Enum):
    INVALID_INPUT = "invalid_input"
    INVALID_FIXTURE = "invalid_fixture"
    UNKNOWN_INCIDENT = "unknown_incident"
    MODEL_UNAVAILABLE = "model_unavailable"
    INVALID_MODEL_OUTPUT = "invalid_model_output"


class HarnessError(Exception):
    """Public error with a safe message, code, and attempted call count."""

    def __init__(self, code: ErrorCode, message: str, model_calls: int = 0):
        super().__init__(message)
        self.code = code
        self.model_calls = model_calls


class Status(str, Enum):
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    FAILED = "failed"


def _object(value: Any, keys: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError("Unexpected object fields")
    return value


def _text(value: Any) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 2000:
        raise ValueError("Expected bounded nonempty text")
    return value


def _texts(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list) or not 1 <= len(value) <= 32:
        raise ValueError("Expected bounded nonempty list")
    return tuple(_text(item) for item in value)


@dataclass(frozen=True)
class Evidence:
    ref: str
    observation: str

    @classmethod
    def from_dict(cls, value: Any) -> "Evidence":
        data = _object(value, {"ref", "observation"})
        return cls(_text(data["ref"]), _text(data["observation"]))


@dataclass(frozen=True)
class Incident:
    incident_id: str
    title: str
    evidence: tuple[Evidence, ...]
    candidate_hypotheses: tuple[str, ...]
    missing_evidence: tuple[str, ...]
    recommended_actions: tuple[str, ...]

    @classmethod
    def from_dict(cls, value: Any) -> "Incident":
        data = _object(value, {"incident_id", "title", "evidence", "candidate_hypotheses",
                               "missing_evidence", "recommended_actions"})
        evidence = data["evidence"]
        if not isinstance(evidence, list) or not 1 <= len(evidence) <= 32:
            raise ValueError("Expected evidence list")
        records = tuple(Evidence.from_dict(item) for item in evidence)
        if len({item.ref for item in records}) != len(records):
            raise ValueError("Duplicate evidence references")
        return cls(_text(data["incident_id"]), _text(data["title"]), records,
                   _texts(data["candidate_hypotheses"]), _texts(data["missing_evidence"]),
                   _texts(data["recommended_actions"]))


@dataclass(frozen=True)
class Hypothesis:
    statement: str
    confirmed: bool = False


@dataclass(frozen=True)
class InvestigationReport:
    incident_id: str
    status: Status
    summary: str
    observations: tuple[Evidence, ...]
    hypotheses: tuple[Hypothesis, ...]
    missing_evidence: tuple[str, ...]
    recommended_actions: tuple[str, ...]
    evidence_refs: tuple[str, ...]

    @classmethod
    def from_dict(cls, value: Any, incident: Incident) -> "InvestigationReport":
        """Accept only the conservative fixture-grounded R00 response contract."""
        data = _object(value, {"incident_id", "status", "summary", "observations", "hypotheses",
                               "missing_evidence", "recommended_actions", "evidence_refs"})
        if data["incident_id"] != incident.incident_id:
            raise ValueError("Incident mismatch")
        if data["status"] != Status.INSUFFICIENT_EVIDENCE.value:
            raise ValueError("Unconfirmed incident must remain insufficient_evidence")
        if data["summary"] != "Evidence reviewed; root cause remains unconfirmed.":
            raise ValueError("Unsupported summary")
        if not isinstance(data["observations"], list):
            raise ValueError("Invalid observations")
        observations = tuple(Evidence.from_dict(item) for item in data["observations"])
        if observations != incident.evidence:
            raise ValueError("Observations must match supplied evidence")
        raw_hypotheses = data["hypotheses"]
        if not isinstance(raw_hypotheses, list) or len(raw_hypotheses) != len(incident.candidate_hypotheses):
            raise ValueError("Invalid hypotheses")
        hypotheses = []
        for raw, expected in zip(raw_hypotheses, incident.candidate_hypotheses):
            item = _object(raw, {"statement", "confirmed"})
            if item["statement"] != expected or item["confirmed"] is not False:
                raise ValueError("Hypotheses must remain unconfirmed fixture candidates")
            hypotheses.append(Hypothesis(expected))
        for name in ("missing_evidence", "recommended_actions"):
            if _texts(data[name]) != getattr(incident, name):
                raise ValueError("Unsupported report content")
        refs = _texts(data["evidence_refs"])
        if refs != tuple(item.ref for item in incident.evidence):
            raise ValueError("Invalid provenance")
        return cls(incident.incident_id, Status.INSUFFICIENT_EVIDENCE, data["summary"],
                   observations, tuple(hypotheses), incident.missing_evidence,
                   incident.recommended_actions, refs)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExecutionSummary:
    model_calls: int
    tool_calls: int = 0


@dataclass(frozen=True)
class InvestigationResult:
    report: InvestigationReport
    execution: ExecutionSummary

    def to_dict(self) -> dict[str, Any]:
        return {**self.report.to_dict(), "execution": asdict(self.execution)}
