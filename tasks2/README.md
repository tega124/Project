 Enhanced PKMS/Task Manager
 
# 📝 tasks2.py - Single File Task Manager

Everything in ONE file! No installation, no packages, just Python.

## 🚀 Quick Start

### 1. Download the File

Save `tasks2.py` to your computer.

### 2. Run It!

```bash
# Add your first task
python tasks2.py add "Buy milk"

# See your tasks
python tasks2.py list

# Get help
python tasks2.py --help
```

That's it! Your tasks are saved in `tasks.json` in the same folder.

## 📖 All Commands

### Add Tasks

```bash
# Simple
python tasks2.py add "Task name"

# With everything
python tasks2.py add "Finish homework" \
  --due 2025-11-10 \
  --priority high \
  --tag school \
  --tag urgent \
  --notes "Pages 45-60"
```

### View Tasks

```bash
# All tasks
python tasks2.py list

# Filter by status
python tasks2.py list --status open
python tasks2.py list --status done

# Filter by priority
python tasks2.py list --priority high

# Filter by tag
python tasks2.py list --tag school

# Smart filters
python tasks2.py list --overdue     # Overdue tasks
python tasks2.py list --today       # Due today
python tasks2.py list --week        # Due this week

# Sort results
python tasks2.py list --sort due
python tasks2.py list --sort priority
python tasks2.py list --sort title
```

### Show Task Details

```bash
python tasks2.py show 5
```

Shows everything about task #5.

### Edit Tasks

```bash
# Change title
python tasks2.py edit 5 --title "New title"

# Change priority
python tasks2.py edit 5 --priority high

# Change due date
python tasks2.py edit 5 --due 2025-12-01

# Add tags
python tasks2.py edit 5 --tag-add urgent review

# Remove tags
python tasks2.py edit 5 --tag-rm old-tag

# Replace all tags
python tasks2.py edit 5 --tag-set work important
```

### Mark as Done

```bash
python tasks2.py done 5
```

### Delete Task

```bash
python tasks2.py delete 5
```

### Search

```bash
python tasks2.py search "homework"
python tasks2.py search "urgent"
```

Searches title, notes, and tags!

### Statistics

```bash
python tasks2.py stats
```

Shows:
- Total tasks
- Completion rate
- Priority breakdown
- Overdue count
- Top tags

### Tag Management

```bash
python tasks2.py tags
```

See all your tags with usage stats.

### Export

```bash
# Export to CSV (for Excel)
python tasks2.py export --format csv --output tasks.csv

# Export to JSON (backup)
python tasks2.py export --format json --output backup.json

# Export to Markdown (for notes)
python tasks2.py export --format markdown --output tasks.md
```

### Import from tasks1

```bash
python tasks2.py import-v1 ../tasks1/tasks.json
```

## 💡 Examples

### School Tasks

```bash
# Add homework
python tasks2.py add "Math homework Ch 5" \
  --due 2025-11-08 \
  --priority high \
  --tag school \
  --tag math

# Add exam prep
python tasks2.py add "Study for exam" \
  --due 2025-11-12 \
  --priority high \
  --tag school \
  --tag exam

# View all school tasks
python tasks2.py list --tag school --sort due

# Check what's due this week
python tasks2.py list --tag school --week
```

### Work Tasks

```bash
# Add project task
python tasks2.py add "Code review PR #123" \
  --priority medium \
  --tag work \
  --tag code-review

# Add meeting
python tasks2.py add "Team standup" \
  --due 2025-11-02 \
  --tag work \
  --tag meeting

# View high priority work items
python tasks2.py list --tag work --priority high
```

### Daily Routine

```bash
# Morning: Check today's tasks
python tasks2.py list --today

# See what's overdue
python tasks2.py list --overdue

# Add new task
python tasks2.py add "Buy groceries" --tag personal

# Mark tasks done
python tasks2.py done 5

# Evening: Check stats
python tasks2.py stats
```

## 🎯 Features

- ✅ Add/edit/delete tasks
- 🏷️ Unlimited tags per task
- 🎯 Priority levels (high, medium, low)
- 📅 Due dates with warnings
- 🔍 Full-text search
- 📊 Statistics dashboard
- 📤 Export to CSV/JSON/Markdown
- 💾 Auto-saves to `tasks.json`
- 🎨 Emoji indicators
- ⚡ Fast and lightweight

## 📁 Files Created

When you run tasks2.py, it creates:

```
📂 Your folder/
├── tasks2.py         # The script
└── tasks.json        # Your tasks (auto-created)
```

That's it! Just 2 files.

## 🔧 Requirements

- Python 3.6 or higher
- No external packages needed!

## 💾 Backup Your Tasks

```bash
# Export to JSON for backup
python tasks2.py export --format json --output backup_$(date +%Y%m%d).json

# Or just copy tasks.json
cp tasks.json tasks_backup.json
```

## 🐛 Troubleshooting

### "python: command not found"

Try `python3` instead:
```bash
python3 tasks2.py list
```

### "No tasks found"

Add some tasks first:
```bash
python tasks2.py add "My first task"
python tasks2.py list
```

### Want to start over?

```bash
# Backup first!
cp tasks.json tasks_backup.json

# Delete and start fresh
rm tasks.json
python tasks2.py add "Fresh start"
```

## 📚 Quick Reference

```bash
# Basic commands
python tasks2.py add "Task"           # Add task
python tasks2.py list                 # View tasks
python tasks2.py show ID              # Task details
python tasks2.py edit ID --priority high  # Edit task
python tasks2.py done ID              # Mark done
python tasks2.py delete ID            # Delete task

# Filters
python tasks2.py list --status open   # Open tasks only
python tasks2.py list --priority high # High priority
python tasks2.py list --tag school    # With school tag
python tasks2.py list --overdue       # Overdue tasks
python tasks2.py list --today         # Due today
python tasks2.py list --week          # Due this week

# Sorting
python tasks2.py list --sort due      # By due date
python tasks2.py list --sort priority # By priority
python tasks2.py list --sort title    # Alphabetical

# Other
python tasks2.py search "keyword"     # Search
python tasks2.py stats                # Statistics
python tasks2.py tags                 # Tag stats
python tasks2.py export --format csv --output file.csv  # Export
```

## 🎓 Pro Tips

1. **Use consistent tags:** Create a system like `school`, `work`, `personal`
2. **Set priorities:** High = urgent, Medium = important, Low = when you can
3. **Check stats weekly:** See your progress with `python tasks2.py stats`
4. **Export regularly:** Back up with `export --format json`
5. **Use --overdue daily:** Stay on top of deadlines
6. **Search everything:** Search works on title, notes, AND tags

## 📄 License

Free to use for personal and educational purposes!

---

**Single file. No dependencies. Just works.** 🚀

```bash
python tasks2.py add "Start being productive!" --priority high
python tasks2.py list
```



