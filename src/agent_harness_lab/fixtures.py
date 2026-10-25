"""Read-only packaged synthetic incident repository."""
import json
from importlib.resources import files
from pathlib import Path

from .contracts import ErrorCode, HarnessError, Incident


class FixtureRepository:
    def __init__(self, path: Path | None = None):
        self.path = path

    def get(self, incident_id: str) -> Incident:
        if not isinstance(incident_id, str) or not incident_id.strip() or len(incident_id) > 128:
            raise HarnessError(ErrorCode.INVALID_INPUT, "Provide a nonempty incident ID of at most 128 characters.")
        try:
            source = self.path if self.path is not None else files("agent_harness_lab").joinpath("data/incidents.json")
            with source.open("r", encoding="utf-8") as handle:
                raw = handle.read(65537)
            if len(raw) > 65536:
                raise ValueError("Oversized fixture")
            data = json.loads(raw)
            if not isinstance(data, dict) or set(data) != {"incidents"}:
                raise ValueError("Invalid fixture root")
            if not isinstance(data["incidents"], list) or not 1 <= len(data["incidents"]) <= 100:
                raise ValueError("Invalid incident list")
            incidents = [Incident.from_dict(item) for item in data["incidents"]]
            if len({item.incident_id for item in incidents}) != len(incidents):
                raise ValueError("Duplicate incidents")
        except (OSError, ValueError, TypeError, RecursionError):
            raise HarnessError(ErrorCode.INVALID_FIXTURE, "Cannot read valid synthetic incident fixtures.") from None
        for incident in incidents:
            if incident.incident_id == incident_id:
                return incident
        raise HarnessError(ErrorCode.UNKNOWN_INCIDENT, "Incident not found in synthetic fixtures.")
