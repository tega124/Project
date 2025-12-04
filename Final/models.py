from __future__ import annotations
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone


def iso_now() -> str:
    """Return the current time in ISO 8601 UTC (Zulu) format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_date(s: Optional[str]) -> Optional[str]:
    """Parse a YYYY-MM-DD date string; return same format or None."""
    if s is None:
        return None
    s = s.strip()
    if not s:
        return None
    try:
        dt = datetime.strptime(s, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        print(f"⚠️  Invalid date format: {s}. Use YYYY-MM-DD")
        return None


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    @staticmethod
    def from_str(s: Optional[str]) -> "Priority":
        if not s:
            return Priority.MEDIUM
        s = s.lower().strip()
        if s in ("low", "l"):
            return Priority.LOW
        if s in ("high", "h"):
            return Priority.HIGH
        return Priority.MEDIUM

    def sort_key(self) -> int:
        return {"low": 0, "medium": 1, "high": 2}[self.value]

    def emoji(self) -> str:
        return {"low": "🟢", "medium": "🟡", "high": "🔴"}[self.value]


class Status(str, Enum):
    OPEN = "open"
    DONE = "done"

    @staticmethod
    def from_str(s: Optional[str]) -> "Status":
        if not s:
            return Status.OPEN
        s = s.lower().strip()
        if s == "done":
            return Status.DONE
        return Status.OPEN

    def emoji(self) -> str:
        return "✅" if self == Status.DONE else "⏳"


@dataclass
class Task:
    id: int
    title: str
    notes: str
    created_at: str
    updated_at: str
    due: Optional[str]
    tags: List[str]
    priority: Priority
    status: Status

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["priority"] = self.priority.value
        d["status"] = self.status.value
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Task":
        return Task(
            id=int(d["id"]),
            title=d.get("title", ""),
            notes=d.get("notes", ""),
            created_at=d["created_at"],
            updated_at=d["updated_at"],
            due=d.get("due"),
            tags=list(d.get("tags", [])),
            priority=Priority.from_str(d.get("priority")),
            status=Status.from_str(d.get("status")),
        )
