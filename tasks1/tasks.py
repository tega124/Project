#!/usr/bin/env python3
"""
Simple command-line tasks manager (prototype)
Usage:
  python tasks.py add "Buy groceries"
  python tasks.py list
  python tasks.py search groceries
  python tasks.py remove 3
  python tasks.py complete 2
  python tasks.py export path/to/file.json
"""

import argparse
from pathlib import Path
from datetime import datetime
import uuid
import json
from typing import List, Dict, Any

from storage import read_json, atomic_write_json

DEFAULT_STORE = Path.home() / ".tasks1.json"

def make_task(text: str) -> Dict[str, Any]:
    return {
        "id": str(uuid.uuid4()),
        "text": text,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "completed": False,
        "completed_at": None
    }

def add_task(store_path: Path, text: str) -> None:
    data = read_json(store_path)
    data.setdefault("tasks", [])
    t = make_task(text)
    data["tasks"].append(t)
    atomic_write_json(store_path, data)
    print(f"Added task: {t['id']}")

def list_tasks(store_path: Path, show_all: bool = True) -> None:
    data = read_json(store_path)
    tasks: List[Dict] = data.get("tasks", [])
    if not tasks:
        print("No tasks.")
        return
    print(f"{'ID':36}  {'Done':4}  {'Created':20}  Text")
    print("-" * 96)
    for t in tasks:
        if not show_all and t.get("completed"):
            continue
        created = t.get("created_at", "")[:19].replace("T", " ")
        status = "x" if t.get("completed") else " "
        print(f"{t['id']:36}  [{status}]  {created:20}  {t['text']}")

def search_tasks(store_path: Path, query: str) -> None:
    data = read_json(store_path)
    tasks = data.get("tasks", [])
    found = [t for t in tasks if query.lower() in t.get("text", "").lower()]
    if not found:
        print("No matching tasks.")
        return
    for t in found:
        completed = "✓" if t.get("completed") else " "
        print(f"{t['id']}  [{completed}] {t['text']}")

def remove_task(store_path: Path, task_id: str) -> None:
    data = read_json(store_path)
    tasks = data.get("tasks", [])
    new_tasks = [t for t in tasks if t["id"] != task_id]
    if len(new_tasks) == len(tasks):
        print("Task not found.")
        return
    data["tasks"] = new_tasks
    atomic_write_json(store_path, data)
    print("Removed.")

def complete_task(store_path: Path, task_id: str) -> None:
    data = read_json(store_path)
    tasks = data.get("tasks", [])
    for t in tasks:
        if t["id"] == task_id:
            if t.get("completed"):
                print("Task already completed.")
            else:
                t["completed"] = True
                t["completed_at"] = datetime.utcnow().isoformat() + "Z"
                atomic_write_json(store_path, data)
                print("Marked complete.")
            return
    print("Task not found.")

def export_store(store_path: Path, out_path: Path) -> None:
    data = read_json(store_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Exported to {out_path}")

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="tasks.py", description="Simple JSON-backed task manager prototype.")
    p.add_argument("--store", "-s", default=str(DEFAULT_STORE), help="Path to JSON store (default: ~/.tasks1.json)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="List all tasks (use --active to show only incomplete)").add_argument("--active", action="store_true", help="Show only incomplete tasks")
    a = sub.add_parser("add", help="Add a new task")
    a.add_argument("text", help="Task text", nargs="+")
    sub.add_parser("search", help="Search tasks").add_argument("query", help="Search query")
    sub.add_parser("remove", help="Remove a task by id").add_argument("id", help="Task id")
    sub.add_parser("complete", help="Mark a task complete by id").add_argument("id", help="Task id")
    sub.add_parser("export", help="Export store JSON to a file").add_argument("out", help="Output path")

    return p.parse_args()

def main():
    args = parse_args()
    store_path = Path(args.store).expanduser().resolve()

    if args.cmd == "add":
        text = " ".join(args.text).strip()
        if not text:
            print("Empty task text.")
            return
        add_task(store_path, text)
    elif args.cmd == "list":
        list_tasks(store_path, show_all=not getattr(args, "active", False))
    elif args.cmd == "search":
        search_tasks(store_path, args.query)
    elif args.cmd == "remove":
        remove_task(store_path, args.id)
    elif args.cmd == "complete":
        complete_task(store_path, args.id)
    elif args.cmd == "export":
        export_store(store_path, Path(args.out).expanduser().resolve())
    else:
        print("Unknown command.")

if __name__ == "__main__":
    main()
