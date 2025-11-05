"""tasks3 - Minimal PKMS/task manager package

A lightweight, single-module task management system with full CRUD operations,
tagging, priorities, and search capabilities.

Usage:
    python -m tasks3 add "Task title" --priority high --tag work
    python -m tasks3 list --status open --sort due
    python -m tasks3 show 1
    python -m tasks3 done 1
    python -m tasks3 delete 1
    python -m tasks3 search "keyword"
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import argparse
import json
import sys
from datetime import datetime

__version__ = "3.0.0"
__all__ = ["Task", "Priority", "Status", "Store", "StorageError", "main", "inc"]


# ====================== UTILITIES ======================
# C:\Users\18723\Project\tasks3\src\tasks3\__init__.py



def iso_now() -> str:
    """Return current timestamp in ISO format."""
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_date(s: Optional[str]) -> Optional[str]:
    """Parse date string in YYYY-MM-DD format."""
    if s is None:
        return None
    s = s.strip()
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        print(f"⚠️  Invalid date format: {s}. Use YYYY-MM-DD")
        return None


def print_table(headers: List[str], rows: Iterable[Iterable[str]]) -> None:
    """Print a formatted table to console."""
    rows = list(rows)
    if not rows:
        print("(no results)")
        return
    
    # Calculate column widths
    cols = [list(map(str, [h] + [r[i] for r in rows])) for i, h in enumerate(headers)]
    widths = [max(len(x) for x in col) for col in cols]
    fmt = "  ".join("{:<" + str(w) + "}" for w in widths)
    
    # Print table
    print(fmt.format(*headers))
    print(fmt.format(*["-" * w for w in widths]))
    for r in rows:
        print(fmt.format(*r))
    print(f"\nTotal: {len(rows)} task(s)")


# ====================== DOMAIN MODELS ======================

class Priority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    
    @staticmethod
    def from_str(s: str) -> "Priority":
        """Convert string to Priority enum."""
        s = s.lower().strip()
        if s in ("low", "l"):
            return Priority.LOW
        if s in ("medium", "med", "m"):
            return Priority.MEDIUM
        if s in ("high", "h"):
            return Priority.HIGH
        raise ValueError(f"Invalid priority: {s}")
    
    def sort_key(self) -> int:
        """Return numeric sort key (higher = more important)."""
        return {"low": 0, "medium": 1, "high": 2}[self.value]
    
    def emoji(self) -> str:
        """Return emoji representation."""
        return {"low": "🟢", "medium": "🟡", "high": "🔴"}[self.value]


class Status(str, Enum):
    """Task status."""
    OPEN = "open"
    DONE = "done"
    
    @staticmethod
    def from_str(s: str) -> "Status":
        """Convert string to Status enum."""
        s = s.lower().strip()
        if s == "open":
            return Status.OPEN
        if s == "done":
            return Status.DONE
        raise ValueError(f"Invalid status: {s}")
    
    def emoji(self) -> str:
        """Return emoji representation."""
        return "✅" if self == Status.DONE else "⏳"


@dataclass
class Task:
    """Task data model."""
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
        """Convert task to dictionary for JSON serialization."""
        d = asdict(self)
        d["priority"] = self.priority.value
        d["status"] = self.status.value
        return d
    
    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Task":
        """Create task from dictionary."""
        return Task(
            id=int(d["id"]),
            title=d["title"],
            notes=d.get("notes", ""),
            created_at=d["created_at"],
            updated_at=d["updated_at"],
            due=d.get("due"),
            tags=list(d.get("tags", [])),
            priority=Priority.from_str(d.get("priority", "medium")),
            status=Status.from_str(d.get("status", "open")),
        )


# ====================== STORAGE ======================

class StorageError(Exception):
    """Custom exception for storage errors."""
    pass


class Store:
    """Task storage manager.
    
    JSON format:
        {
            "schema": 3,
            "last_id": 2,
            "tasks": [{"id": 1, ...}, ...]
        }
    """
    
    def __init__(self, path: Optional[Path] = None):
        """Initialize store with given path or default location."""
        if path:
            self.path = Path(path)
        else:
            # Store in package directory
            self.path = Path(__file__).parent.parent / "tasks.json"
        self._ensure()
    
    def _ensure(self) -> None:
        """Ensure storage file exists with proper schema."""
        if not self.path.exists():
            self._write({"schema": 3, "last_id": 0, "tasks": []})
        else:
            data = self._read()
            if "schema" not in data:
                data["schema"] = 3
                self._write(data)
    
    def _read(self) -> Dict[str, Any]:
        """Read data from JSON file."""
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception as e:
            raise StorageError(f"Failed to read {self.path}: {e}")
    
    def _write(self, data: Dict[str, Any]) -> None:
        """Write data to JSON file atomically."""
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        try:
            tmp.write_text(
                json.dumps(data, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
            tmp.replace(self.path)
        except Exception as e:
            raise StorageError(f"Failed to write {self.path}: {e}")
    
    def all(self) -> List[Task]:
        """Load all tasks."""
        return [Task.from_dict(t) for t in self._read().get("tasks", [])]
    
    def next_id(self) -> int:
        """Get next available task ID."""
        data = self._read()
        nid = int(data.get("last_id", 0)) + 1
        data["last_id"] = nid
        self._write(data)
        return nid
    
    def add(self, t: Task) -> None:
        """Add new task."""
        data = self._read()
        data["tasks"].append(t.to_dict())
        self._write(data)
    
    def get(self, tid: int) -> Optional[Task]:
        """Get task by ID."""
        for t in self.all():
            if t.id == tid:
                return t
        return None
    
    def update(self, t: Task) -> None:
        """Update existing task."""
        data = self._read()
        arr = data["tasks"]
        for i, td in enumerate(arr):
            if int(td["id"]) == t.id:
                arr[i] = t.to_dict()
                self._write(data)
                return
        raise StorageError(f"Task {t.id} not found")
    
    def delete(self, tid: int) -> bool:
        """Delete task by ID. Returns True if deleted, False if not found."""
        data = self._read()
        arr = data["tasks"]
        new = [x for x in arr if int(x["id"]) != tid]
        if len(new) == len(arr):
            return False
        data["tasks"] = new
        self._write(data)
        return True


# ====================== CLI COMMANDS ======================

def _cmd_add(args, store: Store) -> None:
    """Add a new task."""
    t = Task(
        id=store.next_id(),
        title=args.title.strip(),
        notes=args.notes or "",
        created_at=iso_now(),
        updated_at=iso_now(),
        due=parse_date(args.due),
        tags=args.tag or [],
        priority=Priority.from_str(args.priority) if args.priority else Priority.MEDIUM,
        status=Status.OPEN,
    )
    store.add(t)
    print(f"✅ Added task #{t.id}: {t.title}")


def _cmd_list(args, store: Store) -> None:
    """List tasks with optional filters."""
    ts = store.all()
    
    # Apply filters
    if args.status:
        ts = [t for t in ts if t.status.value == args.status]
    if args.tag:
        ts = [t for t in ts if set(args.tag) & set(t.tags)]
    if args.priority:
        ts = [t for t in ts if t.priority == Priority.from_str(args.priority)]
    
    # Apply sorting
    if args.sort == "due":
        ts.sort(key=lambda t: (t.due is None, t.due or ""))
    elif args.sort == "priority":
        ts.sort(key=lambda t: t.priority.sort_key(), reverse=True)
    elif args.sort == "created":
        ts.sort(key=lambda t: t.created_at)
    elif args.sort == "updated":
        ts.sort(key=lambda t: t.updated_at)
    
    # Format output with emojis
    rows = [
        [
            t.id,
            t.status.emoji(),
            t.priority.emoji(),
            (t.due or "")[:10],
            ", ".join(t.tags[:2]) + ("..." if len(t.tags) > 2 else ""),
            t.title[:50] + ("..." if len(t.title) > 50 else "")
        ]
        for t in ts
    ]
    print_table(["ID", "St", "Pri", "Due", "Tags", "Title"], rows)


def _cmd_show(args, store: Store) -> None:
    """Show detailed task information."""
    t = store.get(args.id)
    if not t:
        print(f"❌ No task with ID {args.id}")
        return
    
    print("\n" + "=" * 60)
    print(f"TASK #{t.id}")
    print("=" * 60)
    print(f"Status:   {t.status.emoji()} {t.status.value.upper()}")
    print(f"Priority: {t.priority.emoji()} {t.priority.value}")
    print(f"Due:      {t.due or '(none)'}")
    print(f"Tags:     {', '.join(t.tags) if t.tags else '(none)'}")
    print(f"Created:  {t.created_at}")
    print(f"Updated:  {t.updated_at}")
    print(f"\nTitle:\n  {t.title}")
    if t.notes:
        print(f"\nNotes:\n  {t.notes}")
    print("=" * 60 + "\n")


def _cmd_done(args, store: Store) -> None:
    """Mark task as done."""
    t = store.get(args.id)
    if not t:
        print(f"❌ No task with ID {args.id}")
        return
    
    t.status = Status.DONE
    t.updated_at = iso_now()
    store.update(t)
    print(f"✅ Marked task #{t.id} as done")


def _cmd_delete(args, store: Store) -> None:
    """Delete a task."""
    if store.delete(args.id):
        print(f"🗑️  Deleted task #{args.id}")
    else:
        print(f"❌ No task with ID {args.id}")


def _cmd_search(args, store: Store) -> None:
    """Search tasks by keyword."""
    q = args.q.lower()
    hits = []
    
    for t in store.all():
        haystack = " ".join([t.title, t.notes, " ".join(t.tags)]).lower()
        if q in haystack:
            hits.append(t)
    
    if not hits:
        print(f"📭 No tasks found matching '{args.q}'")
        return
    
    print(f"\n🔍 Found {len(hits)} task(s) matching '{args.q}':\n")
    rows = [
        [t.id, t.status.emoji(), t.priority.emoji(), (t.due or "")[:10],
         ", ".join(t.tags[:2]), t.title[:45]]
        for t in hits
    ]
    print_table(["ID", "St", "Pri", "Due", "Tags", "Title"], rows)


# ====================== CLI PARSER ======================

def _build_parser() -> argparse.ArgumentParser:
    """Build argument parser for CLI."""
    p = argparse.ArgumentParser(
        prog="tasks3",
        description="Minimal PKMS/task manager - tasks3 package"
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    
    # Add command
    a = sub.add_parser("add", help="Add a task")
    a.add_argument("title", help="Task title")
    a.add_argument("--notes", help="Task notes")
    a.add_argument("--due", help="Due date (YYYY-MM-DD)")
    a.add_argument("--priority", choices=["low", "medium", "high"])
    a.add_argument("--tag", action="append", help="Add tag (repeatable)")
    a.set_defaults(fn=_cmd_add)
    
    # List command
    l = sub.add_parser("list", help="List tasks")
    l.add_argument("--status", choices=["open", "done"])
    l.add_argument("--tag", action="append", help="Filter by tag")
    l.add_argument("--priority", choices=["low", "medium", "high"])
    l.add_argument("--sort", choices=["due", "priority", "created", "updated"])
    l.set_defaults(fn=_cmd_list)
    
    # Show command
    s = sub.add_parser("show", help="Show task details")
    s.add_argument("id", type=int, help="Task ID")
    s.set_defaults(fn=_cmd_show)
    
    # Done command
    d = sub.add_parser("done", help="Mark task as done")
    d.add_argument("id", type=int, help="Task ID")
    d.set_defaults(fn=_cmd_done)
    
    # Delete command
    rm = sub.add_parser("delete", help="Delete a task")
    rm.add_argument("id", type=int, help="Task ID")
    rm.set_defaults(fn=_cmd_delete)
    
    # Search command
    f = sub.add_parser("search", help="Search tasks")
    f.add_argument("q", help="Search query")
    f.set_defaults(fn=_cmd_search)
    
    return p


# ====================== MAIN ENTRY POINT ======================

def inc(n: int) -> int:
    """Increment function (for testing compatibility)."""
    return n + 1


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for CLI."""
    try:
        parser = _build_parser()
        args = parser.parse_args(argv)
        store = Store()
        args.fn(args, store)
        return 0
    except StorageError as e:
        print(f"❌ Storage error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())