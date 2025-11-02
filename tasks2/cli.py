#!/usr/bin/env python3
"""
tasks2 CLI – Enhanced PKMS/task manager with new features
Version 2.1.0 - Enhanced Edition

New features:
- Statistics dashboard
- Tag management
- Export/Import (JSON, CSV, Markdown)
- Task templates
- Bulk operations
- Recurring tasks
- Interactive mode
"""
from __future__ import annotations
import argparse
import sys
from datetime import datetime, timedelta
from typing import List, Optional

from .storage import TaskStore, StorageError
from .models import Task, Priority, TaskStatus, RecurrencePattern
from .util import (
    parse_date, print_table, iso_now, format_date, 
    days_until, priority_color, status_icon
)
from .export import export_to_csv, export_to_markdown, export_to_json
from .templates import TaskTemplate, TemplateManager


def _add_cmd(args, store: TaskStore):
    """Add a new task"""
    due = parse_date(args.due) if args.due else None
    
    # Handle template
    if args.template:
        template_mgr = TemplateManager()
        template = template_mgr.get_template(args.template)
        if template:
            task = template.create_task(
                store.next_id(),
                title=args.title.strip(),
                due=due
            )
        else:
            print(f"⚠️  Template '{args.template}' not found. Creating regular task.")
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
    else:
        # Handle recurrence
        recurrence = None
        if args.recurrence:
            recurrence = RecurrencePattern.from_str(args.recurrence)
        
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
            recurrence=recurrence,
        )
    
    store.add(task)
    print(f"✅ Added task #{task.id}: {task.title}")
    
    if task.recurrence:
        print(f"🔄 Recurrence: {task.recurrence.value}")


def _list_cmd(args, store: TaskStore):
    """List tasks with filters"""
    tasks = store.load_all()
    
    # Apply filters
    if args.status:
        tasks = [t for t in tasks if t.status.value == args.status]
    
    if args.tag:
        wanted = set(args.tag)
        tasks = [t for t in tasks if wanted.intersection(set(t.tags))]
    
    if args.priority:
        pri = Priority.from_str(args.priority)
        tasks = [t for t in tasks if t.priority == pri]
    
    if args.overdue:
        tasks = [t for t in tasks if t.due and days_until(t.due) and days_until(t.due) < 0]
    
    if args.today:
        tasks = [t for t in tasks if t.due and days_until(t.due) == 0]
    
    if args.week:
        tasks = [t for t in tasks if t.due and 0 <= days_until(t.due) <= 7]
    
    # Apply sorting
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
        elif key == "title":
            tasks.sort(key=lambda t: t.title.lower())
    
    # Format output
    if args.format == "simple":
        for t in tasks:
            print(f"{t.id}. {status_icon(t.status.value)} {t.title}")
    elif args.format == "detailed":
        for t in tasks:
            print(f"\n{'='*70}")
            print(f"ID: {t.id} | {status_icon(t.status.value)} {t.status.value.upper()}")
            print(f"Title: {t.title}")
            print(f"Priority: {priority_color(t.priority.value)} {t.priority.value}")
            if t.due:
                days = days_until(t.due)
                if days is not None:
                    if days < 0:
                        print(f"Due: {t.due} (⚠️  {abs(days)} days overdue)")
                    elif days == 0:
                        print(f"Due: {t.due} (🚨 DUE TODAY)")
                    else:
                        print(f"Due: {t.due} ({days} days left)")
            if t.tags:
                print(f"Tags: {', '.join(t.tags)}")
            if t.recurrence:
                print(f"Recurrence: 🔄 {t.recurrence.value}")
    else:  # table format
        rows = []
        for t in tasks:
            due_str = (t.due or "")[:10]
            if t.due:
                days = days_until(t.due)
                if days is not None:
                    if days < 0:
                        due_str += f" (⚠️ {abs(days)}d)"
                    elif days == 0:
                        due_str += " (🚨)"
            
            rows.append([
                t.id,
                status_icon(t.status.value),
                priority_color(t.priority.value),
                due_str,
                ", ".join(t.tags[:2]) + ("..." if len(t.tags) > 2 else ""),
                t.title[:50] + ("..." if len(t.title) > 50 else "")
            ])
        print_table(["ID", "St", "Pri", "Due", "Tags", "Title"], rows)


def _show_cmd(args, store: TaskStore):
    """Show detailed task information"""
    t = store.get(args.id)
    if not t:
        print(f"❌ No task with id {args.id}")
        return
    
    print("\n" + "="*70)
    print(f"TASK #{t.id}")
    print("="*70)
    print(f"Status:    {status_icon(t.status.value)} {t.status.value.upper()}")
    print(f"Priority:  {priority_color(t.priority.value)} {t.priority.value}")
    print(f"Created:   {t.created_at}")
    print(f"Updated:   {t.updated_at}")
    
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
        print(f"Due:       {due_info}")
    
    if t.tags:
        print(f"Tags:      {', '.join(t.tags)}")
    
    if t.recurrence:
        print(f"Recurrence: 🔄 {t.recurrence.value}")
    
    print(f"\nTitle:")
    print(f"  {t.title}")
    
    if t.notes:
        print(f"\nNotes:")
        for line in t.notes.split('\n'):
            print(f"  {line}")
    
    print("="*70 + "\n")


def _edit_cmd(args, store: TaskStore):
    """Edit an existing task"""
    t = store.get(args.id)
    if not t:
        print(f"❌ No task with id {args.id}")
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
    
    if args.recurrence is not None:
        if args.recurrence:
            t.recurrence = RecurrencePattern.from_str(args.recurrence)
        else:
            t.recurrence = None
        changed = True
    
    if changed:
        t.updated_at = iso_now()
        store.update(t)
        print(f"✅ Updated task #{t.id}")
    else:
        print("⚠️  No changes provided.")


def _done_cmd(args, store: TaskStore):
    """Mark task as done"""
    t = store.get(args.id)
    if not t:
        print(f"❌ No task with id {args.id}")
        return
    
    t.status = TaskStatus.DONE
    t.updated_at = iso_now()
    t.completed_at = iso_now()
    store.update(t)
    print(f"✅ Marked task #{t.id} as done")
    
    # Handle recurrence
    if t.recurrence:
        new_task = t.create_next_occurrence(store.next_id())
        if new_task:
            store.add(new_task)
            print(f"🔄 Created next occurrence: #{new_task.id} (due {new_task.due})")


def _delete_cmd(args, store: TaskStore):
    """Delete a task"""
    ok = store.delete(args.id)
    if ok:
        print(f"🗑️  Deleted task #{args.id}")
    else:
        print(f"❌ No task with id {args.id}")


def _search_cmd(args, store: TaskStore):
    """Search tasks"""
    q = args.query.lower().strip()
    tasks = store.load_all()
    hits = []
    
    for t in tasks:
        hay = " ".join([t.title, t.notes, " ".join(t.tags)]).lower()
        if q in hay:
            hits.append(t)
    
    if not hits:
        print(f"📭 No tasks found matching '{args.query}'")
        return
    
    hits.sort(key=lambda t: (t.due is None, t.due or "", -t.priority.sort_key()))
    
    print(f"\n🔍 Found {len(hits)} task(s) matching '{args.query}':\n")
    rows = []
    for t in hits:
        rows.append([
            t.id,
            status_icon(t.status.value),
            priority_color(t.priority.value),
            (t.due or "")[:10],
            ", ".join(t.tags[:2]),
            t.title[:45] + ("..." if len(t.title) > 45 else "")
        ])
    print_table(["ID", "St", "Pri", "Due", "Tags", "Title"], rows)


def _stats_cmd(args, store: TaskStore):
    """Show statistics dashboard"""
    tasks = store.load_all()
    
    if not tasks:
        print("📭 No tasks found.")
        return
    
    total = len(tasks)
    open_tasks = [t for t in tasks if t.status == TaskStatus.OPEN]
    done_tasks = [t for t in tasks if t.status == TaskStatus.DONE]
    
    high_pri = [t for t in open_tasks if t.priority == Priority.HIGH]
    med_pri = [t for t in open_tasks if t.priority == Priority.MEDIUM]
    low_pri = [t for t in open_tasks if t.priority == Priority.LOW]
    
    overdue = [t for t in open_tasks if t.due and days_until(t.due) and days_until(t.due) < 0]
    today = [t for t in open_tasks if t.due and days_until(t.due) == 0]
    this_week = [t for t in open_tasks if t.due and 0 < days_until(t.due) <= 7]
    
    # Count tags
    tag_counts = {}
    for t in tasks:
        for tag in t.tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    recurring = [t for t in open_tasks if t.recurrence]
    
    print("\n" + "="*70)
    print("📊 TASK STATISTICS DASHBOARD")
    print("="*70)
    print(f"\n📋 Overview:")
    print(f"   Total Tasks:     {total}")
    print(f"   ⏳ Open:         {len(open_tasks)} ({len(open_tasks)/total*100:.1f}%)")
    print(f"   ✅ Completed:    {len(done_tasks)} ({len(done_tasks)/total*100:.1f}%)")
    
    print(f"\n🎯 Priority Breakdown (Open):")
    print(f"   🔴 High:         {len(high_pri)}")
    print(f"   🟡 Medium:       {len(med_pri)}")
    print(f"   🟢 Low:          {len(low_pri)}")
    
    print(f"\n📅 Due Dates:")
    print(f"   ⚠️  Overdue:     {len(overdue)}")
    print(f"   🚨 Due Today:    {len(today)}")
    print(f"   📆 This Week:    {len(this_week)}")
    
    if top_tags:
        print(f"\n🏷️  Top Tags:")
        for tag, count in top_tags:
            print(f"   {tag}: {count}")
    
    if recurring:
        print(f"\n🔄 Recurring Tasks: {len(recurring)}")
    
    print("="*70 + "\n")


def _export_cmd(args, store: TaskStore):
    """Export tasks to various formats"""
    tasks = store.load_all()
    
    if args.format == "csv":
        export_to_csv(tasks, args.output)
        print(f"✅ Exported {len(tasks)} tasks to {args.output}")
    elif args.format == "markdown":
        export_to_markdown(tasks, args.output)
        print(f"✅ Exported {len(tasks)} tasks to {args.output}")
    elif args.format == "json":
        export_to_json(tasks, args.output)
        print(f"✅ Exported {len(tasks)} tasks to {args.output}")


def _tags_cmd(args, store: TaskStore):
    """Manage tags"""
    tasks = store.load_all()
    tag_usage = {}
    
    for task in tasks:
        for tag in task.tags:
            if tag not in tag_usage:
                tag_usage[tag] = {"total": 0, "open": 0, "done": 0}
            tag_usage[tag]["total"] += 1
            if task.status == TaskStatus.OPEN:
                tag_usage[tag]["open"] += 1
            else:
                tag_usage[tag]["done"] += 1
    
    if not tag_usage:
        print("📭 No tags found.")
        return
    
    print("\n" + "="*70)
    print("🏷️  TAG MANAGEMENT")
    print("="*70 + "\n")
    
    rows = []
    for tag in sorted(tag_usage.keys()):
        stats = tag_usage[tag]
        rows.append([
            tag,
            stats["total"],
            stats["open"],
            stats["done"]
        ])
    
    print_table(["Tag", "Total", "Open", "Done"], rows)


def _bulk_cmd(args, store: TaskStore):
    """Bulk operations"""
    tasks = store.load_all()
    
    # Filter tasks based on criteria
    filtered = tasks
    
    if args.tag:
        wanted = set(args.tag)
        filtered = [t for t in filtered if wanted.intersection(set(t.tags))]
    
    if args.status:
        filtered = [t for t in filtered if t.status.value == args.status]
    
    if not filtered:
        print("📭 No tasks match the criteria.")
        return
    
    print(f"📋 Found {len(filtered)} task(s) matching criteria.")
    
    if args.action == "delete":
        confirm = input(f"⚠️  Delete {len(filtered)} task(s)? (yes/no): ").lower()
        if confirm == "yes":
            for task in filtered:
                store.delete(task.id)
            print(f"🗑️  Deleted {len(filtered)} task(s)")
        else:
            print("❌ Operation cancelled.")
    
    elif args.action == "tag-add":
        if not args.tag_value:
            print("❌ --tag-value required for tag-add action")
            return
        for task in filtered:
            task.tags = sorted(set(task.tags + [args.tag_value]))
            task.updated_at = iso_now()
            store.update(task)
        print(f"✅ Added tag '{args.tag_value}' to {len(filtered)} task(s)")
    
    elif args.action == "tag-remove":
        if not args.tag_value:
            print("❌ --tag-value required for tag-remove action")
            return
        for task in filtered:
            task.tags = [t for t in task.tags if t != args.tag_value]
            task.updated_at = iso_now()
            store.update(task)
        print(f"✅ Removed tag '{args.tag_value}' from {len(filtered)} task(s)")
    
    elif args.action == "priority":
        if not args.priority_value:
            print("❌ --priority-value required for priority action")
            return
        for task in filtered:
            task.priority = Priority.from_str(args.priority_value)
            task.updated_at = iso_now()
            store.update(task)
        print(f"✅ Set priority to '{args.priority_value}' for {len(filtered)} task(s)")


def _import_v1_cmd(args, store: TaskStore):
    """Import from tasks1"""
    count = store.import_from_v1(args.path)
    print(f"✅ Imported {count} task(s) from {args.path}")


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser"""
    p = argparse.ArgumentParser(
        prog="tasks2",
        description="Enhanced PKMS/Task CLI Manager v2.1.0"
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # Add command
    a = sub.add_parser("add", help="Add a task")
    a.add_argument("title")
    a.add_argument("--notes")
    a.add_argument("--due", help="YYYY-MM-DD")
    a.add_argument("--priority", choices=["low", "medium", "high"])
    a.add_argument("--tag", action="append", help="repeatable")
    a.add_argument("--recurrence", choices=["daily", "weekly", "monthly", "yearly"])
    a.add_argument("--template", help="Use task template")
    a.set_defaults(func=_add_cmd)

    # List command
    l = sub.add_parser("list", help="List tasks")
    l.add_argument("--status", choices=["open", "done"])
    l.add_argument("--tag", action="append")
    l.add_argument("--priority", choices=["low", "medium", "high"])
    l.add_argument("--sort", choices=["due", "priority", "created", "updated", "title"])
    l.add_argument("--overdue", action="store_true", help="Show only overdue tasks")
    l.add_argument("--today", action="store_true", help="Show tasks due today")
    l.add_argument("--week", action="store_true", help="Show tasks due this week")
    l.add_argument("--format", choices=["table", "simple", "detailed"], default="table")
    l.set_defaults(func=_list_cmd)

    # Show command
    s = sub.add_parser("show", help="Show one task")
    s.add_argument("id", type=int)
    s.set_defaults(func=_show_cmd)

    # Edit command
    e = sub.add_parser("edit", help="Edit fields")
    e.add_argument("id", type=int)
    e.add_argument("--title")
    e.add_argument("--notes")
    e.add_argument("--priority", choices=["low", "medium", "high"])
    e.add_argument("--status", choices=["open", "done"])
    e.add_argument("--due", help="YYYY-MM-DD or empty to clear")
    e.add_argument("--tag-set", nargs="*", help="replace tags")
    e.add_argument("--tag-add", nargs="*", help="add tags")
    e.add_argument("--tag-rm", nargs="*", help="remove tags")
    e.add_argument("--recurrence", help="Set recurrence pattern")
    e.set_defaults(func=_edit_cmd)

    # Done command
    d = sub.add_parser("done", help="Mark as done")
    d.add_argument("id", type=int)
    d.set_defaults(func=_done_cmd)

    # Delete command
    rm = sub.add_parser("delete", help="Delete a task")
    rm.add_argument("id", type=int)
    rm.set_defaults(func=_delete_cmd)

    # Search command
    f = sub.add_parser("search", help="Search title/notes/tags")
    f.add_argument("query")
    f.set_defaults(func=_search_cmd)

    # Stats command
    st = sub.add_parser("stats", help="Show statistics dashboard")
    st.set_defaults(func=_stats_cmd)

    # Export command
    ex = sub.add_parser("export", help="Export tasks")
    ex.add_argument("--format", choices=["csv", "markdown", "json"], required=True)
    ex.add_argument("--output", required=True, help="Output file path")
    ex.set_defaults(func=_export_cmd)

    # Tags command
    tg = sub.add_parser("tags", help="View tag statistics")
    tg.set_defaults(func=_tags_cmd)

    # Bulk command
    bk = sub.add_parser("bulk", help="Bulk operations")
    bk.add_argument("--tag", action="append", help="Filter by tags")
    bk.add_argument("--status", choices=["open", "done"], help="Filter by status")
    bk.add_argument("--action", required=True, 
                   choices=["delete", "tag-add", "tag-remove", "priority"],
                   help="Action to perform")
    bk.add_argument("--tag-value", help="Tag value for tag operations")
    bk.add_argument("--priority-value", choices=["low", "medium", "high"],
                   help="Priority value for priority action")
    bk.set_defaults(func=_bulk_cmd)

    # Import command
    im = sub.add_parser("import-v1", help="Import from tasks1 JSON")
    im.add_argument("path")
    im.set_defaults(func=_import_v1_cmd)

    return p


def main():
    """Main entry point"""
    store = TaskStore()
    parser = build_parser()
    
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    args = parser.parse_args()
    
    try:
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