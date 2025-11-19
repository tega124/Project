import json
import os
import tempfile
from typing import List, Optional
from pathlib import Path

from .models import Task


def default_data_path() -> Path:
    env = os.environ.get("TASKMGR_DATA")
    if env:
        return Path(env)
    return Path("data") / "tasks.json"


def load_tasks(path: Optional[Path] = None) -> List[Task]:
    path = Path(path) if path else default_data_path()
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return []
    return [Task.from_dict(d) for d in data]


def save_tasks(tasks: List[Task], path: Optional[Path] = None) -> None:
    path = Path(path) if path else default_data_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [t.to_dict() for t in tasks]
    # atomic write: write to temp file in same dir and replace
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, str(path))
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except Exception:
                pass


def next_id(tasks: List[Task]) -> int:
    if not tasks:
        return 1
    return max(t.id for t in tasks) + 1


def add_task(title: str, notes: Optional[str] = None, due_date: Optional[str] = None, path: Optional[Path] = None) -> Task:
    tasks = load_tasks(path)
    tid = next_id(tasks)
    task = Task(id=tid, title=title, notes=notes, due_date=due_date)
    tasks.append(task)
    save_tasks(tasks, path)
    return task


def list_tasks(path: Optional[Path] = None):
    return load_tasks(path)


def find_task(task_id: int, path: Optional[Path] = None) -> Optional[Task]:
    tasks = load_tasks(path)
    for t in tasks:
        if t.id == task_id:
            return t
    return None


def update_task(task_id: int, completed: Optional[bool] = None, path: Optional[Path] = None) -> Optional[Task]:
    tasks = load_tasks(path)
    for t in tasks:
        if t.id == task_id:
            if completed is not None:
                t.completed = completed
            save_tasks(tasks, path)
            return t
    return None


def delete_task(task_id: int, path: Optional[Path] = None) -> bool:
    tasks = load_tasks(path)
    new = [t for t in tasks if t.id != task_id]
    if len(new) == len(tasks):
        return False
    save_tasks(new, path)
    return True
