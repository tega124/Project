#!/usr/bin/env python3
"""
tasks2 - Enhanced Single-File Task Manager
Pure Python stdlib. Data in tasks.json next to this script.

Usage:
  python tasks2.py add "Task name" --due 2025-11-10 --priority high --tag school
  python tasks2.py list --sort due
  python tasks2.py show 3
  python tasks2.py edit 3 --priority medium --tag-add urgent
  python tasks2.py done 3
  python tasks2.py delete 3
  python tasks2.py search "homework"
  python tasks2.py stats
  python tasks2.py tags
  python tasks2.py export --format csv --output tasks.csv
  python tasks2.py import-v1 ../tasks1/tasks.json
"""
from __future__ import annotations
import argparse, json, os, sys, csv
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
from typing import List, Optional, Iterable, Dict, Any

# ========================== UTILITIES ==========================

def iso_now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def parse_date(s: Optional[str]) -> Optional[str]:
    if s is None: return None
    s = s.strip()
    if not s: return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        print(f"⚠️  Invalid date format: {s}. Use YYYY-MM-DD")
        return None

def days_until(date_str: Optional[str]) -> Optional[int]:
    if not date_str: return None
    try:
        due = datetime.strptime(date_str, "%Y-%m-%d")
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return (due - today).days
    except:
        return None

def print_table(headers: List[str], rows: Iterable[Iterable[str]]):
    rows = list(rows)
    if not rows:
        print("No tasks found.")
        return
    cols = [list(map(str, [h] + [r[i] for r in rows])) for i, h in enumerate(headers)]
    widths = [max(len(x) for x in col) for col in cols]
    fmt = "  ".join("{:<" + str(w) + "}" for w in widths)
    print(fmt.format(*headers))
    print(fmt.format(*["-" * w for w in widths]))
    for r in rows:
        print(fmt.format(*r))
    print(f"\nTotal: {len(rows)} task(s)")

# ========================== MODELS ==========================

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    
    @staticmethod
    def from_str(s: str) -> "Priority":
        s = s.lower().strip()
        if s in ("low", "l"): return Priority.LOW
        if s in ("medium", "med", "m"): return Priority.MEDIUM
        if s in ("high", "h"): return Priority.HIGH
        return Priority.MEDIUM
    
    def sort_key(self) -> int:
        return {"low": 0, "medium": 1, "high": 2}[self.value]
    
    def emoji(self) -> str:
        return {"low": "🟢", "medium": "🟡", "high": "🔴"}[self.value]

class Status(str, Enum):
    OPEN = "open"
    DONE = "done"
    
    @staticmethod
    def from_str(s: str) -> "Status":
        s = s.lower().strip()
        return Status.DONE if s == "done" else Status.OPEN
    
    def emoji(self) -> str:
        return "✅" if self == Status.DONE else "⏳"

@dataclass
class Task:
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
        d = asdict(self)
        d["priority"] = self.priority.value
        d["status"] = self.status.value
        return d
    
    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Task":
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

# ========================== STORAGE ==========================

class StorageError(Exception):
    pass

class Store:
    def __init__(self, path: Optional[str] = None):
        if path is None:
            base = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(base, "tasks.json")
        self.path = path
        self._ensure()
    
    def _ensure(self):
        if not os.path.exists(self.path):
            self._write({"schema": 2, "last_id": 0, "tasks": []})
    
    def _read(self) -> Dict[str, Any]:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise StorageError(f"Read error: {e}")
    
    def _write(self, data: Dict[str, Any]):
        tmp = self.path + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(tmp, self.path)
        except Exception as e:
            raise StorageError(f"Write error: {e}")
    
    def all(self) -> List[Task]:
        return [Task.from_dict(t) for t in self._read().get("tasks", [])]
    
    def next_id(self) -> int:
        data = self._read()
        nid = int(data.get("last_id", 0)) + 1
        data["last_id"] = nid
        self._write(data)
        return nid
    
    def add(self, t: Task):
        data = self._read()
        data["tasks"].append(t.to_dict())
        self._write(data)
    
    def get(self, tid: int) -> Optional[Task]:
        for t in self.all():
            if t.id == tid:
                return t
        return None
    
    def update(self, t: Task):
        data = self._read()
        arr = data["tasks"]
        for i, td in enumerate(arr):
            if int(td["id"]) == t.id:
                arr[i] = t.to_dict()
                self._write(data)
                return
        raise StorageError(f"Task {t.id} not found")
    
    def delete(self, tid: int) -> bool:
        data = self._read()
        arr = data["tasks"]
        new = [x for x in arr if int(x["id"]) != tid]
        if len(new) == len(arr):
            return False
        data["tasks"] = new
        self._write(data)
        return True
    
    def import_v1(self, path: str) -> int:
        if not os.path.exists(path):
            raise StorageError(f"File not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            old = json.load(f)
        items = old if isinstance(old, list) else old.get("tasks", []) if isinstance(old, dict) else []
        count = 0
        for it in items:
            title = it.get("title") or "Untitled"
            t = Task(
                id=self.next_id(),
                title=str(title),
                notes=str(it.get("description", "")),
                created_at=it.get("created_at", iso_now()),
                updated_at=it.get("updated_at", iso_now()),
                due=it.get("due_date"),
                tags=[],
                priority=Priority.from_str(it.get("priority", "medium")),
                status=Status.DONE if it.get("completed") else Status.OPEN
            )
            self.add(t)
            count += 1
        return count

# ========================== COMMANDS ==========================

def cmd_add(a, store: Store):
    t = Task(
        id=store.next_id(),
        title=a.title.strip(),
        notes=a.notes or "",
        created_at=iso_now(),
        updated_at=iso_now(),
        due=parse_date(a.due),
        tags=a.tag or [],
        priority=Priority.from_str(a.priority) if a.priority else Priority.MEDIUM,
        status=Status.OPEN,
    )
    store.add(t)
    print(f"✅ Added task #{t.id}: {t.title}")

def cmd_list(a, store: Store):
    ts = store.all()
    
    # Apply filters
    if a.status:
        ts = [t for t in ts if t.status.value == a.status]
    if a.tag:
        ts = [t for t in ts if set(a.tag) & set(t.tags)]
    if a.priority:
        ts = [t for t in ts if t.priority == Priority.from_str(a.priority)]
    if a.overdue:
        ts = [t for t in ts if t.due and days_until(t.due) and days_until(t.due) < 0]
    if a.today:
        ts = [t for t in ts if t.due and days_until(t.due) == 0]
    if a.week:
        ts = [t for t in ts if t.due and 0 <= (days_until(t.due) or -999) <= 7]
    
    # Apply sorting
    if a.sort == "due":
        ts.sort(key=lambda t: (t.due is None, t.due or ""))
    elif a.sort == "priority":
        ts.sort(key=lambda t: t.priority.sort_key(), reverse=True)
    elif a.sort == "created":
        ts.sort(key=lambda t: t.created_at)
    elif a.sort == "updated":
        ts.sort(key=lambda t: t.updated_at)
    elif a.sort == "title":
        ts.sort(key=lambda t: t.title.lower())
    
    # Format output
    rows = []
    for t in ts:
        due_str = (t.due or "")[:10]
        if t.due:
            days = days_until(t.due)
            if days is not None:
                if days < 0:
                    due_str += f" (⚠️{abs(days)}d)"
                elif days == 0:
                    due_str += " (🚨)"
        
        rows.append([
            t.id,
            t.status.emoji(),
            t.priority.emoji(),
            due_str,
            ", ".join(t.tags[:2]) + ("..." if len(t.tags) > 2 else ""),
            t.title[:50] + ("..." if len(t.title) > 50 else "")
        ])
    
    print_table(["ID", "St", "Pri", "Due", "Tags", "Title"], rows)

def cmd_show(a, store: Store):
    t = store.get(a.id)
    if not t:
        return print(f"❌ No task with id {a.id}")
    
    print("\n" + "=" * 60)
    print(f"TASK #{t.id}")
    print("=" * 60)
    print(f"Status:   {t.status.emoji()} {t.status.value.upper()}")
    print(f"Priority: {t.priority.emoji()} {t.priority.value}")
    print(f"Created:  {t.created_at}")
    print(f"Updated:  {t.updated_at}")
    
    if t.due:
        days = days_until(t.due)
        due_info = t.due
        if days is not None:
            if days < 0:
                due_info += f" (⚠️  OVERDUE by {abs(days)} days)"
            elif days == 0:
                due_info += " (🚨 DUE TODAY)"
            else:
                due_info += f" ({days} days remaining)"
        print(f"Due:      {due_info}")
    
    if t.tags:
        print(f"Tags:     {', '.join(t.tags)}")
    
    print(f"\nTitle:\n  {t.title}")
    
    if t.notes:
        print(f"\nNotes:\n  {t.notes}")
    
    print("=" * 60 + "\n")

def cmd_edit(a, store: Store):
    t = store.get(a.id)
    if not t:
        return print(f"❌ No task with id {a.id}")
    
    changed = False
    if a.title is not None:
        t.title = a.title.strip()
        changed = True
    if a.notes is not None:
        t.notes = a.notes
        changed = True
    if a.priority is not None:
        t.priority = Priority.from_str(a.priority)
        changed = True
    if a.status is not None:
        t.status = Status.from_str(a.status)
        changed = True
    if a.due is not None:
        t.due = parse_date(a.due) if a.due else None
        changed = True
    if a.tag_set is not None:
        t.tags = a.tag_set
        changed = True
    if a.tag_add:
        t.tags = sorted(set(t.tags) | set(a.tag_add))
        changed = True
    if a.tag_rm:
        t.tags = [x for x in t.tags if x not in set(a.tag_rm)]
        changed = True
    
    if changed:
        t.updated_at = iso_now()
        store.update(t)
        print(f"✅ Updated task #{t.id}")
    else:
        print("⚠️  No changes provided.")

def cmd_done(a, store: Store):
    t = store.get(a.id)
    if not t:
        return print(f"❌ No task with id {a.id}")
    t.status = Status.DONE
    t.updated_at = iso_now()
    store.update(t)
    print(f"✅ Marked task #{t.id} as done")

def cmd_delete(a, store: Store):
    if store.delete(a.id):
        print(f"🗑️  Deleted task #{a.id}")
    else:
        print(f"❌ No task with id {a.id}")

def cmd_search(a, store: Store):
    q = a.query.lower().strip()
    hits = []
    for t in store.all():
        hay = " ".join([t.title, t.notes, " ".join(t.tags)]).lower()
        if q in hay:
            hits.append(t)
    
    if not hits:
        print(f"📭 No tasks found matching '{a.query}'")
        return
    
    hits.sort(key=lambda t: (t.due is None, t.due or "", -t.priority.sort_key()))
    
    print(f"\n🔍 Found {len(hits)} task(s) matching '{a.query}':\n")
    rows = [[t.id, t.status.emoji(), t.priority.emoji(), (t.due or "")[:10], 
             ", ".join(t.tags[:2]), t.title[:45]] for t in hits]
    print_table(["ID", "St", "Pri", "Due", "Tags", "Title"], rows)

def cmd_stats(a, store: Store):
    tasks = store.all()
    
    if not tasks:
        print("📭 No tasks found.")
        return
    
    total = len(tasks)
    open_tasks = [t for t in tasks if t.status == Status.OPEN]
    done_tasks = [t for t in tasks if t.status == Status.DONE]
    
    high = [t for t in open_tasks if t.priority == Priority.HIGH]
    med = [t for t in open_tasks if t.priority == Priority.MEDIUM]
    low = [t for t in open_tasks if t.priority == Priority.LOW]
    
    overdue = [t for t in open_tasks if t.due and days_until(t.due) and days_until(t.due) < 0]
    today = [t for t in open_tasks if t.due and days_until(t.due) == 0]
    this_week = [t for t in open_tasks if t.due and 0 < (days_until(t.due) or -999) <= 7]
    
    # Count tags
    tag_counts = {}
    for t in tasks:
        for tag in t.tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    print("\n" + "=" * 60)
    print("📊 TASK STATISTICS DASHBOARD")
    print("=" * 60)
    print(f"\n📋 Overview:")
    print(f"   Total Tasks:     {total}")
    print(f"   ⏳ Open:         {len(open_tasks)} ({len(open_tasks)/total*100:.1f}%)")
    print(f"   ✅ Completed:    {len(done_tasks)} ({len(done_tasks)/total*100:.1f}%)")
    
    print(f"\n🎯 Priority Breakdown (Open):")
    print(f"   🔴 High:         {len(high)}")
    print(f"   🟡 Medium:       {len(med)}")
    print(f"   🟢 Low:          {len(low)}")
    
    print(f"\n📅 Due Dates:")
    print(f"   ⚠️  Overdue:     {len(overdue)}")
    print(f"   🚨 Due Today:    {len(today)}")
    print(f"   📆 This Week:    {len(this_week)}")
    
    if top_tags:
        print(f"\n🏷️  Top Tags:")
        for tag, count in top_tags:
            print(f"   {tag}: {count}")
    
    print("=" * 60 + "\n")

def cmd_tags(a, store: Store):
    tasks = store.all()
    tag_usage = {}
    
    for task in tasks:
        for tag in task.tags:
            if tag not in tag_usage:
                tag_usage[tag] = {"total": 0, "open": 0, "done": 0}
            tag_usage[tag]["total"] += 1
            if task.status == Status.OPEN:
                tag_usage[tag]["open"] += 1
            else:
                tag_usage[tag]["done"] += 1
    
    if not tag_usage:
        print("📭 No tags found.")
        return
    
    print("\n" + "=" * 60)
    print("🏷️  TAG MANAGEMENT")
    print("=" * 60 + "\n")
    
    rows = [[tag, stats["total"], stats["open"], stats["done"]] 
            for tag, stats in sorted(tag_usage.items())]
    print_table(["Tag", "Total", "Open", "Done"], rows)

def cmd_export(a, store: Store):
    tasks = store.all()
    
    if a.format == "csv":
        with open(a.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Title', 'Status', 'Priority', 'Due', 'Tags', 'Notes', 'Created', 'Updated'])
            for t in tasks:
                writer.writerow([t.id, t.title, t.status.value, t.priority.value, 
                               t.due or '', ', '.join(t.tags), t.notes, t.created_at, t.updated_at])
        print(f"✅ Exported {len(tasks)} tasks to {a.output}")
    
    elif a.format == "json":
        with open(a.output, 'w', encoding='utf-8') as f:
            json.dump([t.to_dict() for t in tasks], f, indent=2, ensure_ascii=False)
        print(f"✅ Exported {len(tasks)} tasks to {a.output}")
    
    elif a.format == "markdown":
        with open(a.output, 'w', encoding='utf-8') as f:
            f.write("# Task List\n\n")
            f.write(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            
            open_tasks = [t for t in tasks if t.status == Status.OPEN]
            done_tasks = [t for t in tasks if t.status == Status.DONE]
            
            if open_tasks:
                f.write("## 📋 Open Tasks\n\n")
                for t in open_tasks:
                    f.write(f"### [ ] {t.priority.emoji()} {t.title}\n\n")
                    f.write(f"- **ID:** {t.id}\n")
                    f.write(f"- **Priority:** {t.priority.value}\n")
                    if t.due:
                        f.write(f"- **Due:** {t.due}\n")
                    if t.tags:
                        f.write(f"- **Tags:** {', '.join(f'`{tag}`' for tag in t.tags)}\n")
                    if t.notes:
                        f.write(f"\n{t.notes}\n")
                    f.write("\n---\n\n")
            
            if done_tasks:
                f.write("## ✅ Completed Tasks\n\n")
                for t in done_tasks:
                    f.write(f"### [x] {t.title}\n\n")
                    f.write(f"- **ID:** {t.id}\n")
                    if t.tags:
                        f.write(f"- **Tags:** {', '.join(f'`{tag}`' for tag in t.tags)}\n")
                    f.write("\n---\n\n")
        
        print(f"✅ Exported {len(tasks)} tasks to {a.output}")

def cmd_import_v1(a, store: Store):
    count = store.import_v1(a.path)
    print(f"✅ Imported {count} task(s) from {a.path}")

# ========================== CLI PARSER ==========================

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="tasks2", description="Enhanced Task Manager (Single File)")
    sub = p.add_subparsers(dest="cmd", required=True)
    
    # Add
    a = sub.add_parser("add", help="Add a task")
    a.add_argument("title")
    a.add_argument("--notes")
    a.add_argument("--due", help="YYYY-MM-DD")
    a.add_argument("--priority", choices=["low", "medium", "high"])
    a.add_argument("--tag", action="append")
    a.set_defaults(func=cmd_add)
    
    # List
    l = sub.add_parser("list", help="List tasks")
    l.add_argument("--status", choices=["open", "done"])
    l.add_argument("--tag", action="append")
    l.add_argument("--priority", choices=["low", "medium", "high"])
    l.add_argument("--sort", choices=["due", "priority", "created", "updated", "title"])
    l.add_argument("--overdue", action="store_true", help="Show overdue tasks")
    l.add_argument("--today", action="store_true", help="Show tasks due today")
    l.add_argument("--week", action="store_true", help="Show tasks due this week")
    l.set_defaults(func=cmd_list)
    
    # Show
    s = sub.add_parser("show", help="Show task details")
    s.add_argument("id", type=int)
    s.set_defaults(func=cmd_show)
    
    # Edit
    e = sub.add_parser("edit", help="Edit a task")
    e.add_argument("id", type=int)
    e.add_argument("--title")
    e.add_argument("--notes")
    e.add_argument("--priority", choices=["low", "medium", "high"])
    e.add_argument("--status", choices=["open", "done"])
    e.add_argument("--due", help="YYYY-MM-DD or empty to clear")
    e.add_argument("--tag-set", nargs="*")
    e.add_argument("--tag-add", nargs="*")
    e.add_argument("--tag-rm", nargs="*")
    e.set_defaults(func=cmd_edit)
    
    # Done
    d = sub.add_parser("done", help="Mark as done")
    d.add_argument("id", type=int)
    d.set_defaults(func=cmd_done)
    
    # Delete
    rm = sub.add_parser("delete", help="Delete a task")
    rm.add_argument("id", type=int)
    rm.set_defaults(func=cmd_delete)
    
    # Search
    f = sub.add_parser("search", help="Search tasks")
    f.add_argument("query")
    f.set_defaults(func=cmd_search)
    
    # Stats
    st = sub.add_parser("stats", help="Show statistics")
    st.set_defaults(func=cmd_stats)
    
    # Tags
    tg = sub.add_parser("tags", help="View tag statistics")
    tg.set_defaults(func=cmd_tags)
    
    # Export
    ex = sub.add_parser("export", help="Export tasks")
    ex.add_argument("--format", required=True, choices=["csv", "json", "markdown"])
    ex.add_argument("--output", required=True)
    ex.set_defaults(func=cmd_export)
    
    # Import
    im = sub.add_parser("import-v1", help="Import from tasks1")
    im.add_argument("path")
    im.set_defaults(func=cmd_import_v1)
    
    return p

def main():
    try:
        store = Store()
        args = build_parser().parse_args()
        args.func(args, store)
    except StorageError as e:
        print(f"❌ Storage error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
