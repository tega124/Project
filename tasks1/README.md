📝 TASK MANAGER
A feature-rich command-line task management application built with Python. Organize your tasks with priorities, due dates, and comprehensive tracking features.
✨ Features

✅ Task Management: Add, edit, delete, and mark tasks as complete
🎯 Priority Levels: Organize tasks by High, Medium, or Low priority
📅 Due Dates: Set deadlines and get overdue warnings
🔍 Search Functionality: Find tasks by keyword
📊 Statistics Dashboard: View completion rates and task analytics
🗂️ Filtering Options: View all, pending, completed, or high-priority tasks
💾 Persistent Storage: All data saved in JSON format
🎨 User-Friendly Interface: Clean CLI with emojis and clear formatting

📁 Project Structure
tasks1/
├── tasks.py          # Main application file
├── tasks.json        # Task data storage (auto-generated)
└── README.md         # This file
🚀 Getting Started
Prerequisites

Python 3.6 or higher
No external dependencies required (uses only Python standard library)

Installation

Clone or download the project:

bash   cd tasks1

Verify Python installation:

bash   python --version
   # or
   python3 --version

Make sure you have the required files:

tasks.py - Main application
tasks.json - Sample data (optional, will be created automatically)



Running the Application
On Windows:
bashpython tasks.py
On macOS/Linux:
bashpython3 tasks.py

📖 USER GUIDE
Main Menu Options
When you run the application, you'll see the following menu:
1.  ➕ Add New Task
2.  📋 View All Tasks
3.  ⏳ View Pending Tasks
4.  ✅ View Completed Tasks
5.  🔴 View High Priority Tasks
6.  🔍 Search Tasks
7.  ✔️  Mark Task Complete
8.  ✏️  Edit Task
9.  🗑️  Delete Task
10. 🧹 Clear Completed Tasks
11. 📊 Show Statistics
12. 🚪 Exit
How to Use Each Feature
1️⃣ Add New Task

Enter task title (required)
Add description (optional)
Select priority: High (1), Medium (2), or Low (3)
Set due date in YYYY-MM-DD format (optional)

Example:
Task Title: Complete project documentation
Description: Write README and user guide
Priority: 1 (High)
Due Date: 2025-02-15
2️⃣ VIEW TASKS

All Tasks: Shows a complete list with all details
Pending Tasks: Only incomplete tasks
Completed Tasks: Only finished tasks
High Priority: Tasks marked as high priority

Each task displays:

Status (✅ complete or ❌ pending)
Priority icon (🔴 High, 🟡 Medium, 🟢 Low)
Title and ID
Description
Due date with days remaining or overdue warning
Creation and completion timestamps

3️⃣ SEARCH TASKS

Enter any keyword
Searches in both title and description
Returns all matching tasks

Example:
🔍 Enter search keyword: project
Found 3 task(s) matching 'project'
4️⃣ MARK TASK COMPLETE

Shows a list of pending tasks
Enter the task ID to mark as done
Automatically records completion timestamp

5️⃣ EDIT TASK

Select task by ID
Update any field (leave blank to keep current value)
Supports editing title, description, priority, and due date

6️⃣ DELETE TASK

View all tasks
Enter the task ID to delete
Permanently removes the task from the list

7️⃣ CLEAR COMPLETED TASKS

Bulk delete all completed tasks
Requires confirmation before deletion
Useful for cleaning up old tasks

8️⃣ SHOW STATISTICS
Displays comprehensive analytics:

Total number of tasks
Completion percentage
Pending task breakdown by priority
Number of overdue tasks

Example Output:
📊 TASK STATISTICS
==================================================
Total Tasks: 10
✅ Completed: 3 (30.0%)
⏳ Pending: 7 (70.0%)

Pending by Priority:
  🔴 High: 3
  🟡 Medium: 3
  🟢 Low: 1

⚠️  Overdue Tasks: 1
==================================================
💡 Tips and Best Practices

Use Descriptive Titles: Make tasks easy to identify at a glance
Set Realistic Due Dates: Helps prioritize and avoid overdue tasks
Use Priority Wisely: Reserve High priority for truly urgent tasks
Regular Cleanup: Use "Clear Completed Tasks" to keep list manageable
Check Statistics: Weekly review helps track productivity
Search Feature: Quickly find related tasks without scrolling

📊 TASK DATA FORMAT
Tasks are stored in tasks.json with the following structure:
json{
    "id": 1,
    "title": "Complete Python project",
    "description": "Finish the weather app with all features",
    "priority": "High",
    "completed": false,
    "created_at": "2025-01-15 09:30:00",
    "due_date": "2025-02-01",
    "completed_at": null
}
🔧 TROUBLESHOOTING
Issue: "tasks.json not found"
Solution: The file will be created automatically when you add your first task. If you want sample data, use the provided tasks.json file.
Issue: "Corrupted data file"
Solution: The app will display a warning and start fresh. Your old file will remain intact - rename or delete it manually if needed.
Issue: "Invalid date format"
Solution: Always use YYYY-MM-DD format (e.g., 2025-12-31). The app will skip invalid dates.
Issue: Python command not recognized
Solution:

Make sure Python is installed: python --version
Try Python3 instead of Python
Add Python to your system PATH

🎨 CUSTOMIZATION
Modify Priority Icons
Edit the emoji icons in tasks.py:
pythonpriority_icon = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
Change Date Format
Modify the datetime format strings:
python"%Y-%m-%d %H:%M:%S"  # Current format
"%m/%d/%Y %I:%M %p"  # US format with AM/PM
Add New Features
The code is well-documented and modular. Common additions:

Tags or categories
Subtasks
Export to CSV
Email reminders
Color coding in terminal

📝 Example Workflow
bash# Start the application
python tasks.py

# Add a new high-priority task
# Choose option: 1
# Title: Submit tax return
# Priority: 1 (High)
# Due Date: 2025-04-15

# View pending tasks
# Choose option: 3

# Mark task as complete when done
# Choose option: 7
# Enter ID of completed task

# Check statistics weekly
# Choose option: 11

# Clean up completed tasks monthly
# Choose option: 10
🤝 CONTRIBUTING
Feel free to modify and enhance this task manager for your needs:

Add new features
Improve the UI
Add database support
Create a GUI version
Add cloud sync

📄 LISCENCE
This project is open source and available for personal and educational use.
👨‍💻 Support
If you encounter issues:

Check the Troubleshooting section
Verify your Python version (3.6+)
Ensure tasks.py is in your current directory
Check file permissions for tasks.json
