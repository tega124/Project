from __future__ import annotations
import argparse
from typing import Iterable, List
from .storage import Store
from .models import Task, iso_now, parse_date, Priority, Status


def print_table(headers: List[str], rows: Iterable[Iterable[str]]) -> None:
    rows = list(rows)
    if not rows:
        print("(no results)")
        return
    cols = [list(map(str, [h] + [r[i] for r in rows])) for i, h in enumerate(headers)]
    widths = [max(len(x) for x in col) for col in cols]
    fmt = "  ".join("{:<" + str(w) + "}" for w in widths)
    print(fmt.format(*headers))
    print(fmt.format(*["-" * w for w in widths]))
    for r in rows:
        print(fmt.format(*r))
    print(f"\nTotal: {len(rows)} task(s)")


def _cmd_add(args, store: Store) -> None:
    nid = store.next_id()
    t = Task(
        id=nid,
        title=args.title.strip(),
        notes=args.notes or "",
        created_at=iso_now(),
        updated_at=iso_now(),
        due=parse_date(args.due),
        tags=args.tag or [],
        priority=Priority.from_str(args.priority),
        status=Status.OPEN,
    )
    store.add(t)
    print(f"✅ Added task #{t.id}: {t.title}")


def _cmd_list(args, store: Store) -> None:
    ts = store.all()
    if args.status:
        ts = [t for t in ts if t.status.value == args.status]
    if args.tag:
        ts = [t for t in ts if set(args.tag) & set(t.tags)]
    if args.priority:
        ts = [t for t in ts if t.priority == Priority.from_str(args.priority)]
    if args.sort == "due":
        ts.sort(key=lambda t: (t.due is None, t.due or ""))
    elif args.sort == "priority":
        ts.sort(key=lambda t: t.priority.sort_key(), reverse=True)
    elif args.sort == "created":
        ts.sort(key=lambda t: t.created_at)
    elif args.sort == "updated":
        ts.sort(key=lambda t: t.updated_at)

    rows = [
        [t.id, t.status.emoji(), t.priority.emoji(), (t.due or "")[:10], ", ".join(t.tags[:2]), (t.title[:45] + ("..." if len(t.title) > 45 else ""))]
        for t in ts
    ]
    print_table(["ID", "St", "Pri", "Due", "Tags", "Title"], rows)


def _cmd_show(args, store: Store) -> None:
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
    t = store.get(args.id)
    if not t:
        print(f"❌ No task with ID {args.id}")
        return
    t.status = Status.DONE
    t.updated_at = iso_now()
    store.update(t)
    print(f"✅ Marked task #{t.id} as done")


def _cmd_delete(args, store: Store) -> None:
    if store.delete(args.id):
        print(f"🗑️  Deleted task #{args.id}")
    else:
        print(f"❌ No task with ID {args.id}")


def _cmd_search(args, store: Store) -> None:
    q = args.q.lower()
    hits = []
    for t in store.all():
        hay = " ".join([t.title, t.notes, " ".join(t.tags)]).lower()
        if q in hay:
            hits.append(t)
    if not hits:
        print(f"📭 No tasks found matching '{args.q}'")
        return
    rows = [[t.id, t.status.emoji(), t.priority.emoji(), (t.due or "")[:10], ", ".join(t.tags[:2]), t.title[:45]] for t in hits]
    print_table(["ID", "St", "Pri", "Due", "Tags", "Title"], rows)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="taskmgr", description="Simple task manager CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="Add a task")
    a.add_argument("title", help="Task title")
    a.add_argument("--notes", help="Task notes")
    a.add_argument("--due", help="Due date YYYY-MM-DD")
    a.add_argument("--priority", choices=["low", "medium", "high"], default="medium")
    a.add_argument("--tag", action="append", help="Tag (repeatable)")
    a.set_defaults(fn=_cmd_add)

    l = sub.add_parser("list", help="List tasks")
    l.add_argument("--status", choices=["open", "done"])
    l.add_argument("--tag", action="append", help="Filter by tag")
    l.add_argument("--priority", choices=["low", "medium", "high"])
    l.add_argument("--sort", choices=["due", "priority", "created", "updated"])
    l.set_defaults(fn=_cmd_list)

    s = sub.add_parser("show", help="Show task details")
    s.add_argument("id", type=int, help="Task ID")
    s.set_defaults(fn=_cmd_show)

    d = sub.add_parser("done", help="Mark task done")
    d.add_argument("id", type=int, help="Task ID")
    d.set_defaults(fn=_cmd_done)

    rm = sub.add_parser("delete", help="Delete a task")
    rm.add_argument("id", type=int, help="Task ID")
    rm.set_defaults(fn=_cmd_delete)

    f = sub.add_parser("search", help="Search tasks")
    f.add_argument("q", help="Search query")
    f.set_defaults(fn=_cmd_search)

    return p
