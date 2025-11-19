from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class Task:
    id: int
    title: str
    completed: bool = False
    created_at: str = None
    due_date: Optional[str] = None
    notes: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "completed": self.completed,
            "created_at": self.created_at,
            "due_date": self.due_date,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            id=int(data["id"]),
            title=str(data.get("title", "")),
            completed=bool(data.get("completed", False)),
            created_at=data.get("created_at"),
            due_date=data.get("due_date"),
            notes=data.get("notes"),
        )
