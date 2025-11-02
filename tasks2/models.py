"""
tasks2.models – Data models for tasks
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class Priority(Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    
    @classmethod
    def from_str(cls, s: str) -> Priority:
        """Convert string to Priority enum"""
        s = s.lower().strip()
        for p in cls:
            if p.value == s:
                return p
        return cls.MEDIUM
    
    def sort_key(self) -> int:
        """Return numeric key for sorting (higher = more important)"""
        return {"low": 1, "medium": 2, "high": 3}[self.value]


class TaskStatus(Enum):
    """Task status"""
    OPEN = "open"
    DONE = "done"
    
    @classmethod
    def from_str(cls, s: str) -> TaskStatus:
        """Convert string to TaskStatus enum"""
        s = s.lower().strip()
        for status in cls:
            if status.value == s:
                return status
        return cls.OPEN


@dataclass
class Task:
    """Task data model"""
    id: int
    title: str
    notes: str = ""
    created_at: str = ""
    updated_at: str = ""
    due: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    priority: Priority = Priority.MEDIUM
    status: TaskStatus = TaskStatus.OPEN
    
    def to_dict(self) -> dict:
        """Convert task to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "title": self.title,
            "notes": self.notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "due": self.due,
            "tags": self.tags,
            "priority": self.priority.value,
            "status": self.status.value,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> Task:
        """Create task from dictionary"""
        return cls(
            id=data["id"],
            title=data["title"],
            notes=data.get("notes", ""),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            due=data.get("due"),
            tags=data.get("tags", []),
            priority=Priority.from_str(data.get("priority", "medium")),
            status=TaskStatus.from_str(data.get("status", "open")),
        )