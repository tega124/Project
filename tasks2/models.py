from __future__ import annotations
from dataclasses import dataclass, asdict
from enum import Enum
from typing import List, Optional, Dict, Any


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    @staticmethod
    def from_str(s: str) -> "Priority":
        s = s.lower().strip()
        if s in ("low", "l"):
            return Priority.LOW
        if s in ("medium", "med", "m"):
            return Priority.MEDIUM
        if s in ("high", "h"):
            return Priority.HIGH
        raise ValueError(f"Unknown priority: {s}")

    def sort_key(self) -> int:
        return {"low": 0, "medium": 1, "high": 2}[self.value]


class TaskStatus(str, Enum):
    OPEN = "open"
    DONE = "done"

    @staticmethod
    def from_str(s: str) -> "TaskStatus":
        s = s.lower().strip()
        if s == "open":
            return TaskStatus.OPEN
        if s == "done":
            return TaskStatus.DONE
        raise ValueError(f"Unknown status: {s}")


@dataclass
class Task:
    id: int
    title: str
    notes: str
    created_at: str  # ISO 8601
    updated_at: str  # ISO 8601
    due: Optional[str]  # YYYY-MM-DD
    tags: List[str]
    priority: Priority
    status: TaskStatus

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["priority"] = self.priority.value
        d["status"] = self.status.value
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Task":
        return Task(
            id=int(d["id"]),
            title=d["title"],
            notes=d.get("notes", ""),
            created_at=d["created_at"],
            updated_at=d["updated_at"],
            due=d.get("due"),
            tags=list(d.get("tags", [])),
            priority=Priority.from_str(d.get("priority", "medium")),
            status=TaskStatus.from_str(d.get("status", "open")),
        )
