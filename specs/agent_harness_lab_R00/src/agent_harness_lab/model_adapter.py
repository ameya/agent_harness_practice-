"""Provider-independent structured request and single-call protocol."""
from dataclasses import asdict, dataclass
from typing import Any, Protocol

from .contracts import Incident


@dataclass(frozen=True)
class ModelRequest:
    incident: Incident

    def to_dict(self) -> dict[str, Any]:
        return {"incident": asdict(self.incident)}


class ModelAdapter(Protocol):
    def generate(self, request: ModelRequest) -> object:
        """Return an untrusted decoded report object; never execute actions."""
        ...
