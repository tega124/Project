import json
import os
from datetime import datetime
from typing import List, Dict

DATA_FILE = "tasks.json"

# ======================== DATA PERSISTENCE ========================

def load_tasks() -> List[Dict]:
    """Load tasks from JSON file with error handling."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("⚠️  Warning: Corrupted data file. Starting fresh.")
            return []
    return []

def save_tasks(tasks: List[Dict]) -> None:
    """Save tasks to JSON file."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Error saving tasks: {e}")

# ======================== TASK OPERATIONS ========================

def add_task() -> None:
    """Add a new task with title, description, and priority."""
    print("\n" + "="*50)
    print("📝 ADD NEW TASK")
    print("="*50)
    
    title = input("Task Title: ").strip()
    if not title:
        print("❌ Title cannot be empty!")
        return
    
    description = input("Description: ").strip()
    
    print("\nPriority Level:")
    print("1. 🔴 High")
    print("2. 🟡 Medium")
    print("3. 🟢 Low")
    priority_choice = input("Select priority (1-3, default: 2): ").strip() or "2"
    
    priority_map = {"1": "High", "2": "Medium", "3": "Low"}
    priority = priority_map.get(priority_choice, "Medium")
    
    due_date = input("Due Date (YYYY-MM-DD, optional): ").strip()
    if due_date:
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            print("⚠️  Invalid date format. Skipping due date.")
            due_date = None
    
    tasks = load_tasks()
    task = {
        "id": len(tasks) + 1,
        "title": title,
        "description": description,
        "priority": priority,
        "completed": False,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "due_date": due_date,
        "completed_at": None
    }
    
    tasks.append(task)
    save_tasks(tasks)
    print(f"\n✅ Task '{title}' added successfully!")

def list_tasks(filter_by: str = "all") -> None:
    """List all tasks with filtering options."""
    tasks = load_tasks()
    
    if not tasks:
        print("\n📭 No tasks found. Add some tasks to get started!")
        return
    
    # Filter tasks
    if filter_by == "completed":
        filtered = [t for t in tasks if t["completed"]]
        header = "✅ COMPLETED TASKS"
    elif filter_by == "pending":
        filtered = [t for t in tasks if not t["completed"]]
        header = "⏳ PENDING TASKS"
    elif filter_by == "high":
        filtered = [t for t in tasks if t.get("priority") == "High"]
        header = "🔴 HIGH PRIORITY TASKS"
    else:
        filtered = tasks
        header = "📋 ALL TASKS"
    
    if not filtered:
        print(f"\n📭 No {filter_by} tasks found.")
        return
    
    print("\n" + "="*70)
    print(header)
    print("="*70)
    
    for i, task in enumerate(filtered, start=1):
        status = "✅" if task["completed"] else "❌"
        priority_icon = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(task.get("priority", "Medium"), "🟡")
        
        print(f"\n{i}. [{status}] {priority_icon} {task['title']}")
        print(f"   ID: {task['id']}")
        
        if task.get("description"):
            print(f"   Description: {task['description']}")
        
        if task.get("due_date"):
            due = datetime.strptime(task["due_date"], "%Y-%m-%d")
            days_left = (due - datetime.now()).days
            if days_left < 0:
                print(f"   Due: {task['due_date']} ⚠️  OVERDUE by {abs(days_left)} days!")
            elif days_left == 0:
                print(f"   Due: {task['due_date']} 🚨 DUE TODAY!")
            else:
                print(f"   Due: {task['due_date']} ({days_left} days left)")
        
        print(f"   Created: {task.get('created_at', 'N/A')}")
        
        if task["completed"] and task.get("completed_at"):
            print(f"   Completed: {task['completed_at']}")
    
    print("\n" + "="*70)
    print(f"Total: {len(filtered)} task(s)")

def search_tasks() -> None:
    """Search tasks by keyword in title or description."""
    keyword = input("\n🔍 Enter search keyword: ").strip().lower()
    
    if not keyword:
        print("❌ Search keyword cannot be empty!")
        return
    
    tasks = load_tasks()
    found = [
        t for t in tasks 
        if keyword in t["title"].lower() or keyword in t.get("description", "").lower()
    ]
    
    if not found:
        print(f"\n📭 No tasks found matching '{keyword}'")
        return
    
    print(f"\n🔍 Found {len(found)} task(s) matching '{keyword}':")
    print("="*70)
    
    for task in found:
        status = "✅" if task["completed"] else "❌"
        priority_icon = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(task.get("priority", "Medium"), "🟡")
        print(f"\n[{status}] {priority_icon} {task['title']} (ID: {task['id']})")
        if task.get("description"):
            print(f"   {task['description']}")

def mark_complete() -> None:
    """Mark a task as complete."""
    tasks = load_tasks()
    
    if not tasks:
        print("\n📭 No tasks to mark complete!")
        return
    
    # Show only pending tasks
    pending = [t for t in tasks if not t["completed"]]
    
    if not pending:
        print("\n🎉 All tasks are already complete!")
        return
    
    print("\n⏳ PENDING TASKS:")
    print("="*70)
    for i, task in enumerate(pending, start=1):
        priority_icon = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(task.get("priority", "Medium"), "🟡")
        print(f"{i}. {priority_icon} {task['title']} (ID: {task['id']})")
    
    try:
        choice = input("\nEnter task ID to mark complete: ").strip()
        task_id = int(choice)
        
        # Find task by ID
        task_found = False
        for task in tasks:
            if task["id"] == task_id and not task["completed"]:
                task["completed"] = True
                task["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_tasks(tasks)
                print(f"\n✅ Task '{task['title']}' marked as complete!")
                task_found = True
                break
        
        if not task_found:
            print(f"❌ Task with ID {task_id} not found or already completed!")
    
    except ValueError:
        print("❌ Invalid input! Please enter a valid task ID.")

def delete_task() -> None:
    """Delete a task by ID."""
    tasks = load_tasks()
    
    if not tasks:
        print("\n📭 No tasks to delete!")
        return
    
    list_tasks()
    
    try:
        choice = input("\nEnter task ID to delete: ").strip()
        task_id = int(choice)
        
        # Find and remove task
        original_length = len(tasks)
        tasks = [t for t in tasks if t["id"] != task_id]
        
        if len(tasks) < original_length:
            save_tasks(tasks)
            print(f"\n🗑️  Task deleted successfully!")
        else:
            print(f"❌ Task with ID {task_id} not found!")
    
    except ValueError:
        print("❌ Invalid input! Please enter a valid task ID.")

def edit_task() -> None:
    """Edit an existing task."""
    tasks = load_tasks()
    
    if not tasks:
        print("\n📭 No tasks to edit!")
        return
    
    list_tasks()
    
    try:
        choice = input("\nEnter task ID to edit: ").strip()
        task_id = int(choice)
        
        # Find task
        task = None
        for t in tasks:
            if t["id"] == task_id:
                task = t
                break
        
        if not task:
            print(f"❌ Task with ID {task_id} not found!")
            return
        
        print(f"\n✏️  Editing: {task['title']}")
        print("Leave blank to keep current value.\n")
        
        new_title = input(f"Title [{task['title']}]: ").strip()
        if new_title:
            task["title"] = new_title
        
        new_desc = input(f"Description [{task.get('description', '')}]: ").strip()
        if new_desc:
            task["description"] = new_desc
        
        print("\nPriority: 1=High, 2=Medium, 3=Low")
        new_priority = input(f"Priority [{task.get('priority', 'Medium')}]: ").strip()
        priority_map = {"1": "High", "2": "Medium", "3": "Low"}
        if new_priority in priority_map:
            task["priority"] = priority_map[new_priority]
        
        new_due = input(f"Due Date [{task.get('due_date', '')}] (YYYY-MM-DD): ").strip()
        if new_due:
            try:
                datetime.strptime(new_due, "%Y-%m-%d")
                task["due_date"] = new_due
            except ValueError:
                print("⚠️  Invalid date format. Keeping original due date.")
        
        save_tasks(tasks)
        print("\n✅ Task updated successfully!")
    
    except ValueError:
        print("❌ Invalid input! Please enter a valid task ID.")

def clear_completed() -> None:
    """Delete all completed tasks."""
    tasks = load_tasks()
    completed = [t for t in tasks if t["completed"]]
    
    if not completed:
        print("\n📭 No completed tasks to clear!")
        return
    
    print(f"\n⚠️  Found {len(completed)} completed task(s).")
    confirm = input("Delete all completed tasks? (yes/no): ").strip().lower()
    
    if confirm in ["yes", "y"]:
        tasks = [t for t in tasks if not t["completed"]]
        save_tasks(tasks)
        print(f"\n🗑️  Cleared {len(completed)} completed task(s)!")
    else:
        print("❌ Operation cancelled.")

def show_statistics() -> None:
    """Display task statistics."""
    tasks = load_tasks()
    
    if not tasks:
        print("\n📭 No tasks to analyze!")
        return
    
    total = len(tasks)
    completed = len([t for t in tasks if t["completed"]])
    pending = total - completed
    
    high_priority = len([t for t in tasks if t.get("priority") == "High" and not t["completed"]])
    medium_priority = len([t for t in tasks if t.get("priority") == "Medium" and not t["completed"]])
    low_priority = len([t for t in tasks if t.get("priority") == "Low" and not t["completed"]])
    
    overdue = 0
    for task in tasks:
        if not task["completed"] and task.get("due_date"):
            due = datetime.strptime(task["due_date"], "%Y-%m-%d")
            if (due - datetime.now()).days < 0:
                overdue += 1
    
    print("\n" + "="*50)
    print("📊 TASK STATISTICS")
    print("="*50)
    print(f"Total Tasks: {total}")
    print(f"✅ Completed: {completed} ({(completed/total*100):.1f}%)")
    print(f"⏳ Pending: {pending} ({(pending/total*100):.1f}%)")
    print(f"\nPending by Priority:")
    print(f"  🔴 High: {high_priority}")
    print(f"  🟡 Medium: {medium_priority}")
    print(f"  🟢 Low: {low_priority}")
    if overdue > 0:
        print(f"\n⚠️  Overdue Tasks: {overdue}")
    print("="*50)

# ======================== MAIN MENU ========================

def display_menu() -> None:
    """Display the main menu."""
    print("\n" + "="*50)
    print("📝 TASK MANAGER")
    print("="*50)
    print("1.  ➕ Add New Task")
    print("2.  📋 View All Tasks")
    print("3.  ⏳ View Pending Tasks")
    print("4.  ✅ View Completed Tasks")
    print("5.  🔴 View High Priority Tasks")
    print("6.  🔍 Search Tasks")
    print("7.  ✔️  Mark Task Complete")
    print("8.  ✏️  Edit Task")
    print("9.  🗑️  Delete Task")
    print("10. 🧹 Clear Completed Tasks")
    print("11. 📊 Show Statistics")
    print("12. 🚪 Exit")
    print("="*50)

def main():
    """Main program loop."""
    print("\n🎉 Welcome to Task Manager!")
    
    while True:
        display_menu()
        choice = input("\nChoose option (1-12): ").strip()
        
        if choice == "1":
            add_task()
        elif choice == "2":
            list_tasks("all")
        elif choice == "3":
            list_tasks("pending")
        elif choice == "4":
            list_tasks("completed")
        elif choice == "5":
            list_tasks("high")
        elif choice == "6":
            search_tasks()
        elif choice == "7":
            mark_complete()
        elif choice == "8":
            edit_task()
        elif choice == "9":
            delete_task()
        elif choice == "10":
            clear_completed()
        elif choice == "11":
            show_statistics()
        elif choice == "12":
            print("\n👋 Thank you for using Task Manager! Goodbye!")
            break
        else:
            print("\n❌ Invalid choice! Please select 1-12.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
