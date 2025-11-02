 Enhanced PKMS/Task Manager
 
An advanced command-line Personal Knowledge Management System (PKMS) and task manager with powerful features for organizing, tracking, and managing tasks efficiently.
🆕 What's New in v2.1.0
New Features

🔄 Recurring Tasks: Daily, weekly, monthly, and yearly task repetition
📊 Statistics Dashboard: Comprehensive task analytics
🏷️ Tag Management: View and manage tag usage across tasks
📤 Export Functions: Export to CSV, Markdown, and JSON
📋 Task Templates: Pre-configured templates for common tasks
⚡ Bulk Operations: Perform actions on multiple tasks at once
📅 Smart Filters: Filter by overdue, today, this week
🎨 Multiple Output Formats: Table, simple, and detailed views

✨ Core Features

🏷️ Tagging System: Organize with unlimited tags per task
🎯 Priority Levels: High, Medium, Low with visual indicators
📅 Due Dates: Track deadlines with overdue warnings
🔍 Advanced Search: Search across title, notes, and tags
📊 Flexible Sorting: Sort by due date, priority, or timestamps
🔄 Import v1 Tasks: Migrate from basic task manager
💾 Atomic Storage: Crash-safe file operations
📝 Rich Notes: Detailed multi-line task descriptions

📁 Project Structure
csc299-project/tasks2/
├── __init__.py        # Package initialization
├── __main__.py        # Entry point
├── cli.py             # Enhanced CLI with new commands
├── models.py          # Data models with recurring support
├── storage.py         # JSON storage manager
├── utils.py           # Utility functions
├── export.py          # Export to CSV/Markdown/JSON
├── templates.py       # Task template system
├── tasks.json         # Data file (auto-generated)
└── README.md          # This file
🚀 Quick Start
Installation
bash# Clone the repository
git clone <your-repo-url>
cd csc299-project/tasks2

# Verify Python 3.7+
python --version

# Test the installation
python -m tasks2.cli --help
Your First Tasks
bash# Add a simple task
python -m tasks2.cli add "Buy groceries"

# Add a task with all options
python -m tasks2.cli add "Finish project report" \
  --due 2025-11-15 \
  --priority high \
  --tag school \
  --tag project \
  --notes "Include charts and references"

# List all tasks
python -m tasks2.cli list

# Mark task as done
python -m tasks2.cli done 1
📖 Complete Command Reference
1. Add Tasks
bash# Basic task
python -m tasks2.cli add "Task title"

# With all options
python -m tasks2.cli add "Task title" \
  --due 2025-12-31 \
  --priority high \
  --tag work \
  --tag urgent \
  --notes "Detailed notes here" \
  --recurrence weekly \
  --template homework
Options:

--due YYYY-MM-DD: Set due date
--priority {low,medium,high}: Set priority (default: medium)
--tag TAG: Add tags (repeatable)
--notes TEXT: Add detailed notes
--recurrence {daily,weekly,monthly,yearly}: Make task recurring
--template NAME: Use predefined template

Templates Available:

homework: High priority school task
meeting: Work meeting preparation
exercise: Daily exercise routine
grocery: Weekly grocery shopping
review: Weekly task review
backup: Monthly backup reminder

2. List Tasks
bash# List all tasks (table format)
python -m tasks2.cli list

# Filter by status
python -m tasks2.cli list --status open
python -m tasks2.cli list --status done

# Filter by tags
python -m tasks2.cli list --tag school
python -m tasks2.cli list --tag urgent --tag work

# Filter by priority
python -m tasks2.cli list --priority high

# Smart date filters
python -m tasks2.cli list --overdue      # Show overdue tasks
python -m tasks2.cli list --today        # Due today
python -m tasks2.cli list --week         # Due this week

# Sort results
python -m tasks2.cli list --sort due
python -m tasks2.cli list --sort priority
python -m tasks2.cli list --sort created
python -m tasks2.cli list --sort updated
python -m tasks2.cli list --sort title

# Change output format
python -m tasks2.cli list --format simple     # Just ID and title
python -m tasks2.cli list --format detailed   # Full details
python -m tasks2.cli list --format table      # Default table view

# Combine filters
python -m tasks2.cli list --status open --tag school --priority high --sort due
3. Show Task Details
bashpython -m tasks2.cli show 5
Output includes:

Full task information
Days until/overdue
All tags and notes
Creation and update timestamps
Recurrence pattern if applicable

4. Edit Tasks
bash# Change title
python -m tasks2.cli edit 5 --title "New title"

# Update priority
python -m tasks2.cli edit 5 --priority high

# Change status
python -m tasks2.cli edit 5 --status done

# Update due date
python -m tasks2.cli edit 5 --due 2025-12-25

# Clear due date
python -m tasks2.cli edit 5 --due ""

# Tag management
python -m tasks2.cli edit 5 --tag-set work urgent    # Replace all tags
python -m tasks2.cli edit 5 --tag-add review         # Add tag
python -m tasks2.cli edit 5 --tag-rm old-tag         # Remove tag

# Set recurrence
python -m tasks2.cli edit 5 --recurrence weekly

# Multiple edits at once
python -m tasks2.cli edit 5 \
  --title "Updated title" \
  --priority high \
  --tag-add urgent \
  --due 2025-11-20
5. Mark as Done
bashpython -m tasks2.cli done 5
For recurring tasks, this automatically creates the next occurrence!
6. Delete Tasks
bashpython -m tasks2.cli delete 5
⚠️ Warning: This is permanent and cannot be undone.
7. Search Tasks
bash# Search anywhere (title, notes, tags)
python -m tasks2.cli search "project"
python -m tasks2.cli search "urgent deadline"
Results are sorted by due date and priority.
8. Statistics Dashboard 📊
bashpython -m tasks2.cli stats
Shows:

Total tasks and completion rate
Priority breakdown for open tasks
Due date summary (overdue, today, this week)
Top 5 most-used tags
Recurring task count

Example output:
📊 TASK STATISTICS DASHBOARD
======================================================================

📋 Overview:
   Total Tasks:     25
   ⏳ Open:         15 (60.0%)
   ✅ Completed:    10 (40.0%)

🎯 Priority Breakdown (Open):
   🔴 High:         5
   🟡 Medium:       7
   🟢 Low:          3

📅 Due Dates:
   ⚠️  Overdue:     2
   🚨 Due Today:    1
   📆 This Week:    4

🏷️  Top Tags:
   school: 8
   work: 6
   personal: 5
   urgent: 3
   project: 2

🔄 Recurring Tasks: 3
9. Tag Management 🏷️
bashpython -m tasks2.cli tags
Shows all tags with usage statistics:

Total uses
Open task count
Completed task count

10. Export Tasks 📤
bash# Export to CSV
python -m tasks2.cli export --format csv --output tasks_export.csv

# Export to Markdown
python -m tasks2.cli export --format markdown --output tasks_report.md

# Export to JSON
python -m tasks2.cli export --format json --output tasks_backup.json
CSV Export: Spreadsheet-compatible format
Markdown Export: Beautiful formatted report with sections
JSON Export: Complete data backup
11. Bulk Operations ⚡
bash# Delete all completed tasks
python -m tasks2.cli bulk --status done --action delete

# Add tag to multiple tasks
python -m tasks2.cli bulk --tag school --action tag-add --tag-value exam

# Remove tag from multiple tasks
python -m tasks2.cli bulk --tag old-project --action tag-remove --tag-value old-project

# Change priority of multiple tasks
python -m tasks2.cli bulk --tag urgent --action priority --priority-value high

# Combine filters
python -m tasks2.cli bulk --status open --tag work --action tag-add --tag-value review
⚠️ Bulk delete requires confirmation!
12. Import from v1
bashpython -m tasks2.cli import-v1 ../tasks1/tasks.json
Converts and imports tasks from the basic task manager.
🎯 Common Workflows
Daily Morning Routine
bash# Check what's urgent today
python -m tasks2.cli list --today --format detailed

# Check overdue items
python -m tasks2.cli list --overdue

# Add today's tasks
python -m tasks2.cli add "Review emails" --priority high --tag work
python -m tasks2.cli add "Team standup" --due 2025-11-01 --tag meeting
Project Management
bash# Create project tasks
python -m tasks2.cli add "Design mockups" \
  --tag project-x --tag design --priority high --due 2025-11-10

python -m tasks2.cli add "Implement API" \
  --tag project-x --tag backend --priority high --due 2025-11-15

python -m tasks2.cli add "Write tests" \
  --tag project-x --tag testing --priority medium --due 2025-11-20

# View all project tasks
python -m tasks2.cli list --tag project-x --sort due

# Check project statistics
python -m tasks2.cli search "project-x"
Weekly Review
bash# View completed tasks this week
python -m tasks2.cli list --status done

# Check upcoming tasks
python -m tasks2.cli list --week --sort due

# See overall statistics
python -m tasks2.cli stats

# Add weekly review task (recurring)
python -m tasks2.cli add "Weekly planning session" \
  --recurrence weekly \
  --tag planning \
  --priority medium \
  --due 2025-11-03
School/Academic Workflow
bash# Add homework with template
python -m tasks2.cli add "Math Assignment 5" \
  --template homework \
  --due 2025-11-08 \
  --tag math

# Track all school tasks
python -m tasks2.cli list --tag school --sort due

# High priority school items
python -m tasks2.cli list --tag school --priority high

# Export for review
python -m tasks2.cli export --format markdown --output school_tasks.md
💡 Pro Tips

Use Consistent Tags: Create a tagging system early

Categories: school, work, personal
Status: urgent, review, waiting
Projects: project-x, thesis, app-dev


Leverage Recurring Tasks: Set up regular tasks once

bash   python -m tasks2.cli add "Weekly planning" \
     --recurrence weekly --template review

Regular Statistics Check: Monitor productivity

bash   python -m tasks2.cli stats

Export for Backups: Regular exports prevent data loss

bash   python -m tasks2.cli export --format json --output backup_$(date +%Y%m%d).json

Bulk Operations for Cleanup: Keep your list clean

bash   python -m tasks2.cli bulk --status done --action delete

Smart Filters for Focus: Use date filters for daily planning

bash   python -m tasks2.cli list --today --priority high

Search for Quick Access: Find tasks instantly

bash   python -m tasks2.cli search "meeting"
🔧 Advanced Usage
Custom Templates
You can extend the template system by modifying templates.py:
pythontemplates["custom"] = TaskTemplate(
    name="custom",
    title_pattern="Your template",
    notes="Template notes",
    priority=Priority.HIGH,
    tags=["custom", "tag"],
    recurrence=RecurrencePattern.WEEKLY
)
Scripting with tasks2
Create bash/PowerShell scripts for common workflows:
bash#!/bin/bash
# daily_review.sh

echo "=== Your Daily Tasks ==="
python -m tasks2.cli list --today

echo -e "\n=== Overdue Items ==="
python -m tasks2.cli list --overdue

echo -e "\n=== High Priority Open ==="
python -m tasks2.cli list --status open --priority high
Integration with Other Tools
Export to Markdown and use with note-taking apps:
bashpython -m tasks2.cli export --format markdown --output notes/tasks.md
🐛 Troubleshooting
ModuleNotFoundError
bash# Make sure you're in the csc299-project directory
cd /path/to/csc299-project
python -m tasks2.cli --help
Invalid JSON Error
bash# Backup corrupted file
cp tasks2/tasks.json tasks2/tasks.json.backup

# Start fresh or restore from export
python -m tasks2.cli import-v1 backup.json
Permission Errors
bash# Fix file permissions
chmod 644 tasks2/tasks.json
chmod 755 tasks2/*.py
📊 Data Format
Tasks are stored in tasks2/tasks.json:
json[
  {
    "id": 1,
    "title": "Complete project report",
    "notes": "Include all sections and references",
    "created_at": "2025-11-01 09:00:00",
    "updated_at": "2025-11-01 09:00:00",
    "completed_at": null,
    "due": "2025-11-15",
    "tags": ["school", "project", "writing"],
    "priority": "high",
    "status": "open",
    "recurrence": null,
    "parent_id": null
  }
]
🔄 Migration from tasks1
bash# Import all tasks from v1
python -m tasks2.cli import-v1 ../tasks1/tasks.json

# Verify import
python -m tasks2.cli stats
python -m tasks2.cli list
