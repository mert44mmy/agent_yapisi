from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class ProjectState:
    user_request: str
    requirements: Any = None
    design: Any = None
    implementation: Any = None
    review: Any = None
    final_output: Any = None
    history: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def update(self, agent_name: str, updates: dict[str, Any]) -> None:
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.history.append({"agent": agent_name, "updates": updates})
