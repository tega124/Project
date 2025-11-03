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
├── cli.py             # Enhanced CLI with new commands
├── models.py          # Data models with recurring support
├── storage.py         # JSON storage manager
├── utils.py           # Utility functions
├── tasks.json         # Data file (auto-generated)
└── README.md          # This file

# tasks2 – Improved PKMS/Task CLI

A small, dependency-free CLI for personal task management.

## Quick start

```bash
# run from repo root
python -m tasks2.cli add "Finish DS homework" --due 2025-11-03 --priority high --tag school --tag csc299
python -m tasks2.cli list --sort due
python -m tasks2.cli show 1
python -m tasks2.cli edit 1 --priority medium --tag-add algorithms --notes "Ch. 5–7"
python -m tasks2.cli done 1
python -m tasks2.cli delete 1
python -m tasks2.cli search "homework"



