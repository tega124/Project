from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from .models import Task


class StorageError(Exception):
    pass


class Store:
    """
    JSON-backed storage.

    Format:
      {
        "schema": 1,
        "last_id": N,
        "tasks": [{...}, ...]
      }
    """
    def __init__(self, path: Optional[Path] = None):
        if path:
            self.path = Path(path)
        else:
            # store next to the package (project root will usually be two levels up)
            # if installed as editable mode the package file location is fine.
            self.path = Path(__file__).parent.parent / "tasks.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure()

    def _ensure(self) -> None:
        if not self.path.exists():
            self._write({"schema": 1, "last_id": 0, "tasks": []})
        else:
            data = self._read()
            if "schema" not in data:
                data["schema"] = 1
                self._write(data)

    def _read(self) -> Dict[str, Any]:
        try:
            text = self.path.read_text(encoding="utf-8")
            return json.loads(text)
        except Exception as e:
            raise StorageError(f"Failed to read {self.path}: {e}")

    def _write(self, data: Dict[str, Any]) -> None:
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        try:
            tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            tmp.replace(self.path)
        except Exception as e:
            raise StorageError(f"Failed to write {self.path}: {e}")

    def all(self) -> List[Task]:
        data = self._read()
        return [Task.from_dict(t) for t in data.get("tasks", [])]

    def next_id(self) -> int:
        data = self._read()
        nid = int(data.get("last_id", 0)) + 1
        data["last_id"] = nid
        self._write(data)
        return nid

    def add(self, t: Task) -> None:
        data = self._read()
        arr = data.get("tasks", [])
        arr.append(t.to_dict())
        data["tasks"] = arr
        self._write(data)

    def get(self, tid: int) -> Optional[Task]:
        for t in self.all():
            if t.id == tid:
                return t
        return None

    def update(self, t: Task) -> None:
        data = self._read()
        arr = data.get("tasks", [])
        for i, td in enumerate(arr):
            if int(td.get("id")) == t.id:
                arr[i] = t.to_dict()
                data["tasks"] = arr
                self._write(data)
                return
        raise StorageError(f"Task {t.id} not found")

    def delete(self, tid: int) -> bool:
        data = self._read()
        arr = data.get("tasks", [])
        new = [x for x in arr if int(x.get("id")) != tid]
        if len(new) == len(arr):
            return False
        data["tasks"] = new
        self._write(data)
        return True
