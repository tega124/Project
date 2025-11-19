# Quickstart: CSC299 Task Manager (reference)

Prerequisites

- Python 3.11+
- `pytest` (for running tests)

Install (virtualenv recommended)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt  # if provided
```

Run the CLI (examples)

```powershell
# Add a task (human output)
python -m taskmgr add "Write assignment"

# Add a task (JSON machine output)
python -m taskmgr add "Write assignment" --json

# List tasks
python -m taskmgr list --json
```

Run tests

```powershell
pytest -q
```

Notes

- Data is stored in `data/tasks.json`. Ensure `data/` exists and is git-ignored.
- Use `--yes` to bypass confirmations in non-interactive scripts.

