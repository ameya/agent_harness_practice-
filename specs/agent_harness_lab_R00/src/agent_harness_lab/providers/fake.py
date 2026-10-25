"""Deterministic offline adapter driven only by the supplied incident."""
from dataclasses import asdict

from ..model_adapter import ModelRequest


class FakeModelAdapter:
    def generate(self, request: ModelRequest) -> object:
        incident = request.incident
        return {
            "incident_id": incident.incident_id,
            "status": "insufficient_evidence",
            "summary": "Evidence reviewed; root cause remains unconfirmed.",
            "observations": [asdict(item) for item in incident.evidence],
            "hypotheses": [{"statement": text, "confirmed": False} for text in incident.candidate_hypotheses],
            "missing_evidence": list(incident.missing_evidence),
            "recommended_actions": list(incident.recommended_actions),
            "evidence_refs": [item.ref for item in incident.evidence],
        }
