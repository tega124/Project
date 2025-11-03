"""
tasks2.models – Enhanced data models for tasks
Version 2.1.0 - Added recurring tasks, templates, and more
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from datetime import datetime, timedelta


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


class RecurrencePattern(Enum):
    """Recurring task patterns"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    
    @classmethod
    def from_str(cls, s: str) -> Optional[RecurrencePattern]:
        """Convert string to RecurrencePattern enum"""
        if not s:
            return None
        s = s.lower().strip()
        for pattern in cls:
            if pattern.value == s:
                return pattern
        return None
    
    def next_due_date(self, current_due: str) -> str:
        """Calculate next due date based on pattern"""
        try:
            current = datetime.strptime(current_due, "%Y-%m-%d")
        except ValueError:
            # Fallback to today if invalid
            current = datetime.now()
        
        if self == RecurrencePattern.DAILY:
            next_date = current + timedelta(days=1)
        elif self == RecurrencePattern.WEEKLY:
            next_date = current + timedelta(weeks=1)
        elif self == RecurrencePattern.MONTHLY:
            # Add one month (handle month overflow)
            month = current.month + 1
            year = current.year
            if month > 12:
                month = 1
                year += 1
            try:
                next_date = current.replace(year=year, month=month)
            except ValueError:
                # Handle day overflow (e.g., Jan 31 -> Feb 28)
                next_date = current.replace(year=year, month=month, day=28)
        else:  # YEARLY
            next_date = current.replace(year=current.year + 1)
        
        return next_date.strftime("%Y-%m-%d")


@dataclass
class Task:
    """Enhanced task data model with recurring support"""
    id: int
    title: str
    notes: str = ""
    created_at: str = ""
    updated_at: str = ""
    completed_at: Optional[str] = None
    due: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    priority: Priority = Priority.MEDIUM
    status: TaskStatus = TaskStatus.OPEN
    recurrence: Optional[RecurrencePattern] = None
    parent_id: Optional[int] = None  # For recurring task lineage
    
    def to_dict(self) -> dict:
        """Convert task to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "title": self.title,
            "notes": self.notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
            "due": self.due,
            "tags": self.tags,
            "priority": self.priority.value,
            "status": self.status.value,
            "recurrence": self.recurrence.value if self.recurrence else None,
            "parent_id": self.parent_id,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> Task:
        """Create task from dictionary"""
        recurrence_str = data.get("recurrence")
        recurrence = RecurrencePattern.from_str(recurrence_str) if recurrence_str else None
        
        return cls(
            id=data["id"],
            title=data["title"],
            notes=data.get("notes", ""),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            completed_at=data.get("completed_at"),
            due=data.get("due"),
            tags=data.get("tags", []),
            priority=Priority.from_str(data.get("priority", "medium")),
            status=TaskStatus.from_str(data.get("status", "open")),
            recurrence=recurrence,
            parent_id=data.get("parent_id"),
        )
    
    def create_next_occurrence(self, new_id: int) -> Optional[Task]:
        """
        Create next occurrence of a recurring task.
        Returns None if task is not recurring or has no due date.
        """
        if not self.recurrence or not self.due:
            return None
        
        next_due = self.recurrence.next_due_date(self.due)
        
        # Create new task with same properties but new due date
        return Task(
            id=new_id,
            title=self.title,
            notes=self.notes,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            due=next_due,
            tags=self.tags.copy(),
            priority=self.priority,
            status=TaskStatus.OPEN,
            recurrence=self.recurrence,
            parent_id=self.id,
        )
