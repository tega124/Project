#!/usr/bin/env python3
"""
tasks2 CLI – improved PKMS/task manager
Usage examples:
  python -m tasks2.cli add "Finish DS homework" --due 2025-11-03 --priority high --tag school --tag csc299
  python -m tasks2.cli list
  python -m tasks2.cli show 3
  python -m tasks2.cli edit 3 --title "Finish DS HW (Q1–Q5)" --priority medium
  python -m tasks2.cli done 3
  python -m tasks2.cli delete 3
  python -m tasks2.cli search --tag school --status open --sort due
  python -m tasks2.cli import-v1 ../tasks1/tasks.json
"""
from __future__ import annotations
import argparse
from datetime import datetime
from typing import List, Optional

from .storage import TaskStore, StorageError
from .models import Task, Priority, TaskStatus
from .utils import parse_date, print_table, iso_now


def _add_cmd(args, store: TaskStore):
    due = parse_date(args.due) if args.due else None
    task = Task(
        id=store.next_id(),
        title=args.title.strip(),
        notes=args.notes or "",
        created_at=iso_now(),
        updated_at=iso_now(),
        due=due,
        tags=args.tag or [],
        priority=Priority.from_str(args.priority) if args.priority else Priority.MEDIUM,
        status=TaskStatus.OPEN,
    )
    store.add(task)
    print(f"Added task #{task.id}: {task.title}")


def _list_cmd(args, store: TaskStore):
    tasks = store.load_all()
    if args.status:
        tasks = [t for t in tasks if t.status.value == args.status]
    if args.tag:
        wanted = set(args.tag)
        tasks = [t for t in tasks if wanted.intersection(set(t.tags))]
    if args.priority:
        pri = Priority.from_str(args.priority)
        tasks = [t for t in tasks if t.priority == pri]
    if args.sort:
        key = args.sort
        if key == "due":
            tasks.sort(key=lambda t: (t.due is None, t.due or ""))
        elif key == "priority":
            tasks.sort(key=lambda t: t.priority.sort_key(), reverse=True)
        elif key == "created":
            tasks.sort(key=lambda t: t.created_at)
        elif key == "updated":
            tasks.sort(key=lambda t: t.updated_at)
    rows = []
    for t in tasks:
        rows.append([
            t.id,
            t.status.value,
            t.priority.value,
            (t.due or "")[:10],
            ", ".join(t.tags),
            t.title
        ])
    print_table(["ID", "Status", "Pri", "Due", "Tags", "Title"], rows)


def _show_cmd(args, store: TaskStore):
    t = store.get(args.id)
    if not t:
        print(f"No task with id {args.id}")
        return
    print(f"ID:        {t.id}")
    print(f"Status:    {t.status.value}")
    print(f"Priority:  {t.priority.value}")
    print(f"Due:       {t.due or ''}")
    print(f"Tags:      {', '.join(t.tags)}")
    print(f"Created:   {t.created_at}")
    print(f"Updated:   {t.updated_at}")
    print("Title:")
    print(f"  {t.title}")
    if t.notes:
        print("Notes:")
        print(f"  {t.notes}")


def _edit_cmd(args, store: TaskStore):
    t = store.get(args.id)
    if not t:
        print(f"No task with id {args.id}")
        return
    changed = False
    if args.title is not None:
        t.title = args.title.strip()
        changed = True
    if args.notes is not None:
        t.notes = args.notes
        changed = True
    if args.priority is not None:
        t.priority = Priority.from_str(args.priority)
        changed = True
    if args.status is not None:
        t.status = TaskStatus.from_str(args.status)
        changed = True
    if args.due is not None:
        t.due = parse_date(args.due) if args.due else None
        changed = True
    if args.tag_set is not None:
        t.tags = args.tag_set
        changed = True
    if args.tag_add:
        t.tags = sorted(set(t.tags).union(set(args.tag_add)))
        changed = True
    if args.tag_rm:
        t.tags = [x for x in t.tags if x not in set(args.tag_rm)]
        changed = True
    if changed:
        t.updated_at = iso_now()
        store.update(t)
        print(f"Updated task #{t.id}")
    else:
        print("No changes provided.")


def _done_cmd(args, store: TaskStore):
    t = store.get(args.id)
    if not t:
        print(f"No task with id {args.id}")
        return
    t.status = TaskStatus.DONE
    t.updated_at = iso_now()
    store.update(t)
    print(f"Marked task #{t.id} as done")


def _delete_cmd(args, store: TaskStore):
    ok = store.delete(args.id)
    if ok:
        print(f"Deleted task #{args.id}")
    else:
        print(f"No task with id {args.id}")


def _search_cmd(args, store: TaskStore):
    q = args.query.lower().strip()
    tasks = store.load_all()
    hits = []
    for t in tasks:
        hay = " ".join([t.title, t.notes, " ".join(t.tags)]).lower()
        if q in hay:
            hits.append(t)
    hits.sort(key=lambda t: (t.due is None, t.due or "", -t.priority.sort_key()))
    rows = []
    for t in hits:
        rows.append([t.id, t.status.value, t.priority.value, (t.due or "")[:10], ", ".join(t.tags), t.title])
    print_table(["ID", "Status", "Pri", "Due", "Tags", "Title"], rows)


def _import_v1_cmd(args, store: TaskStore):
    count = store.import_from_v1(args.path)
    print(f"Imported {count} task(s) from {args.path}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="tasks2", description="Improved PKMS/task CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="Add a task")
    a.add_argument("title")
    a.add_argument("--notes")
    a.add_argument("--due", help="YYYY-MM-DD")
    a.add_argument("--priority", choices=["low", "medium", "high"])
    a.add_argument("--tag", action="append", help="repeatable")
    a.set_defaults(func=_add_cmd)

    l = sub.add_parser("list", help="List tasks")
    l.add_argument("--status", choices=["open", "done"])
    l.add_argument("--tag", action="append")
    l.add_argument("--priority", choices=["low", "medium", "high"])
    l.add_argument("--sort", choices=["due", "priority", "created", "updated"])
    l.set_defaults(func=_list_cmd)

    s = sub.add_parser("show", help="Show one task")
    s.add_argument("id", type=int)
    s.set_defaults(func=_show_cmd)

    e = sub.add_parser("edit", help="Edit fields")
    e.add_argument("id", type=int)
    e.add_argument("--title")
    e.add_argument("--notes")
    e.add_argument("--priority", choices=["low", "medium", "high"])
    e.add_argument("--status", choices=["open", "done"])
    e.add_argument("--due", help="YYYY-MM-DD or empty string to clear; use --due ''")
    e.add_argument("--tag-set", nargs="*", help="replace tags entirely")
    e.add_argument("--tag-add", nargs="*", help="add tags")
    e.add_argument("--tag-rm", nargs="*", help="remove tags")
    e.set_defaults(func=_edit_cmd)

    d = sub.add_parser("done", help="Mark as done")
    d.add_argument("id", type=int)
    d.set_defaults(func=_done_cmd)

    rm = sub.add_parser("delete", help="Delete a task")
    rm.add_argument("id", type=int)
    rm.set_defaults(func=_delete_cmd)

    f = sub.add_parser("search", help="Search title/notes/tags")
    f.add_argument("query")
    f.set_defaults(func=_search_cmd)

    im = sub.add_parser("import-v1", help="Import from tasks1 JSON")
    im.add_argument("path")
    im.set_defaults(func=_import_v1_cmd)

    return p


def main():
    store = TaskStore()  # tasks2/tasks.json by default
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args, store)
    except StorageError as e:
        print(f"Storage error: {e}")


if __name__ == "__main__":
    main()
