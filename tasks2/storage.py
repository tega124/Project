from __future__ import annotations
import json
import os
from typing import List, Optional

from .models import Task

class StorageError(Exception):
    pass

class TaskStore:
    """
    JSON file format:
    {
      "schema": 2,
      "last_id": 7,
      "tasks": [ {task}, {task}, ... ]
    }
    """
    def __init__(self, path: Optional[str] = None):
        if path is None:
            # default to repo-local tasks2/tasks.json
            base = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(base, "tasks.json")
        self.path = path
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.path):
            data = {"schema": 2, "last_id": 0, "tasks": []}
            self._write(data)
        else:
            # migrate older schema if needed (simple pass-through for now)
            data = self._read()
            if "schema" not in data:
                data["schema"] = 2
                self._write(data)

    def _read(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise StorageError(f"Failed to read {self.path}: {e}")

    def _write(self, data):
        tmp = self.path + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(tmp, self.path)
        except Exception as e:
            raise StorageError(f"Failed to write {self.path}: {e}")

    def load_all(self) -> List[Task]:
        data = self._read()
        return [Task.from_dict(t) for t in data.get("tasks", [])]

    def next_id(self) -> int:
        data = self._read()
        nid = int(data.get("last_id", 0)) + 1
        data["last_id"] = nid
        self._write(data)
        return nid

    def add(self, task: Task):
        data = self._read()
        tasks = data.get("tasks", [])
        tasks.append(task.to_dict())
        data["tasks"] = tasks
        self._write(data)

    def get(self, tid: int) -> Optional[Task]:
        for t in self.load_all():
            if t.id == tid:
                return t
        return None

    def update(self, task: Task):
        data = self._read()
        tasks = data.get("tasks", [])
        found = False
        for i, td in enumerate(tasks):
            if int(td["id"]) == task.id:
                tasks[i] = task.to_dict()
                found = True
                break
        if not found:
            raise StorageError(f"Task {task.id} not found")
        data["tasks"] = tasks
        self._write(data)

    def delete(self, tid: int) -> bool:
        data = self._read()
        tasks = data.get("tasks", [])
        new_tasks = [t for t in tasks if int(t["id"]) != tid]
        if len(new_tasks) == len(tasks):
            return False
        data["tasks"] = new_tasks
        self._write(data)
        return True

    def import_from_v1(self, path: str) -> int:
        """
        Import from tasks1 JSON (expected shape is flexible: either a list of tasks
        with 'title'/'notes'/etc. or an object with 'tasks': [...]).
        """
        if not os.path.exists(path):
            raise StorageError(f"Path not found: {path}")
        try:
            with open(path, "r", encoding="utf-8") as f:
                old = json.load(f)
        except Exception as e:
            raise StorageError(f"Failed to read tasks1 file: {e}")

        if isinstance(old, dict) and "tasks" in old:
            items = old["tasks"]
        elif isinstance(old, list):
            items = old
        else:
            raise StorageError("Unrecognized tasks1 format")

        count = 0
        for item in items:
            title = item.get("title") or item.get("name") or item.get("task") or "Untitled"
            notes = item.get("notes", "")
            due = item.get("due") or None
            tags = item.get("tags") or []
            # Defaults on import
            from .models import Task, Priority, TaskStatus
            task = Task(
                id=self.next_id(),
                title=str(title),
                notes=str(notes),
                created_at=item.get("created_at") or item.get("created") or item.get("timestamp") or "",
                updated_at=item.get("updated_at") or item.get("updated") or item.get("timestamp") or "",
                due=due,
                tags=list(tags),
                priority=Priority.MEDIUM,
                status=TaskStatus.OPEN,
            )
            if not task.created_at:
                from .utils import iso_now
                task.created_at = iso_now()
            if not task.updated_at:
                from .utils import iso_now
                task.updated_at = iso_now()
            self.add(task)
            count += 1
        return count
