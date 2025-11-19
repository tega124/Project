import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from . import storage


def parse_args(argv=None):
    parser = argparse.ArgumentParser(prog="taskmgr", description="Simple Task Manager CLI")
    parser.add_argument("--data-file", help="Path to tasks JSON file (overrides TASKMGR_DATA env)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="Add a new task")
    p_add.add_argument("title")
    p_add.add_argument("--notes")
    p_add.add_argument("--due")
    p_add.add_argument("--json", action="store_true")

    p_list = sub.add_parser("list", help="List tasks")
    p_list.add_argument("--all", action="store_true")
    p_list.add_argument("--completed", action="store_true")
    p_list.add_argument("--pending", action="store_true")
    p_list.add_argument("--json", action="store_true")

    p_show = sub.add_parser("show", help="Show task")
    p_show.add_argument("id", type=int)
    p_show.add_argument("--json", action="store_true")

    p_complete = sub.add_parser("complete", help="Mark task completed")
    p_complete.add_argument("id", type=int)
    p_complete.add_argument("--yes", action="store_true")
    p_complete.add_argument("--json", action="store_true")

    p_delete = sub.add_parser("delete", help="Delete a task")
    p_delete.add_argument("id", type=int)
    p_delete.add_argument("--yes", action="store_true")
    p_delete.add_argument("--json", action="store_true")

    return parser.parse_args(argv)


def data_path(args) -> Optional[Path]:
    if args and getattr(args, "data_file", None):
        return Path(args.data_file)
    env = Path(storage.default_data_path())
    return env


def main(argv=None):
    args = parse_args(argv)
    dp = None
    if getattr(args, "data_file", None):
        dp = Path(args.data_file)

    if args.cmd == "add":
        task = storage.add_task(args.title, notes=args.notes, due_date=args.due, path=dp)
        if args.json:
            print(json.dumps(task.to_dict(), ensure_ascii=False))
        else:
            print(f"Added task {task.id}: {task.title}")
        return 0

    if args.cmd == "list":
        tasks = storage.list_tasks(path=dp)
        if args.completed:
            tasks = [t for t in tasks if t.completed]
        if args.pending:
            tasks = [t for t in tasks if not t.completed]
        if args.json:
            print(json.dumps([t.to_dict() for t in tasks], ensure_ascii=False))
        else:
            for t in tasks:
                status = "x" if t.completed else " "
                print(f"[{status}] {t.id}: {t.title}")
        return 0

    if args.cmd == "show":
        t = storage.find_task(args.id, path=dp)
        if not t:
            print(json.dumps({"error": "task not found", "code": 404}) if args.json else "Task not found", file=sys.stderr)
            return 2
        if args.json:
            print(json.dumps(t.to_dict(), ensure_ascii=False))
        else:
            print(f"{t.id}: {t.title} (completed={t.completed})")
        return 0

    if args.cmd == "complete":
        t = storage.update_task(args.id, completed=True, path=dp)
        if not t:
            print("Task not found", file=sys.stderr)
            return 2
        if args.json:
            print(json.dumps(t.to_dict(), ensure_ascii=False))
        else:
            print(f"Marked {t.id} completed")
        return 0

    if args.cmd == "delete":
        if not args.yes:
            print("Refusing to delete without --yes", file=sys.stderr)
            return 1
        ok = storage.delete_task(args.id, path=dp)
        if not ok:
            print("Task not found", file=sys.stderr)
            return 2
        if args.json:
            print(json.dumps({"deleted": args.id}))
        else:
            print(f"Deleted {args.id}")
        return 0

    return 1
