README.md


A fully functional command-line Task Manager built in Python for the CSC299 Final Project.
The project uses a clean architecture with models, storage, and CLI components, plus an automated JSON-based persistent storage layer.

This project was developed using a combination of:

Specification-driven development (Spec-Kit)

AI-assisted coding (ChatGPT + GitHub Copilot)

Automated testing (pytest)

CLI-first design for usability and grading requirements

🔧 Features
✔ Add Tasks

Create tasks with:

title

notes

due date (YYYY-MM-DD)

tags

priority (low / medium / high)

✔ List Tasks

Filter or sort tasks by:

status: open / done

priority

tags

created date

updated date

due date

✔ View Details

Show full metadata for any task, including:

status

priority

timestamps

tags

notes

✔ Update Tasks

Mark tasks as done

Edit metadata

Auto-update timestamps

✔ Delete Tasks

Remove tasks permanently from storage.

✔ Search

Find matching tasks using keyword search across:

titles

notes

tags

📂 Project Structure
tasks5/
├── src/
│   └── taskmgr/
│       ├── __init__.py
│       ├── cli.py
│       ├── models.py
│       ├── storage.py
│       └── tasks.json (auto-created)
├── tests/
│   └── unit/
│       └── test_storage.py  (Spec-Kit provided)
├── SUMMARY.md
├── README.md   ← you are here
└── pyproject.toml

▶️ How to Install
1. Create a virtual environment
python -m venv .venv

2. Activate it

Windows:

.venv\Scripts\activate


Mac/Linux:

source .venv/bin/activate

3. Install the package in editable mode

(Required so pytest and CLI can import taskmgr)

pip install -e .

🚀 How to Use
Add a task
python -m taskmgr add "Finish assignment" --notes "Due on Monday" --priority high --tag school

List tasks
python -m taskmgr list --sort priority

Show a task
python -m taskmgr show 1

Mark done
python -m taskmgr done 1

Delete a task
python -m taskmgr delete 1

Search
python -m taskmgr search "assignment"

🧪 Running Tests

To run the built-in Spec-Kit tests:

pytest -q


All tests should pass:

4 passed, 0 failed
