# CLI Contracts: Commands and Machine Output

This document describes the CLI commands and the JSON shapes produced in machine mode.

## CLI Commands (suggested)

- `taskmgr add "TITLE" [--notes TEXT] [--due DATE] [--json]`
  - Human mode: prints confirmation message to `stdout`.
  - JSON mode (`--json`): prints the created Task object.

- `taskmgr list [--all|--completed|--pending] [--json]`
  - Human mode: prints table-like lines.
  - JSON mode: prints array of Task objects.

- `taskmgr show ID [--json]`
  - JSON mode: prints Task object or `{ "error": "not found" }` with non-zero exit code.

- `taskmgr complete ID [--yes] [--json]`
  - Marks task completed. JSON mode prints updated Task.

- `taskmgr delete ID [--yes] [--json]`
  - Deletes task. JSON mode prints `{ "deleted": ID }`.

## JSON Output Examples

- Create (stdout when `--json` passed):

```json
{ "id": 2, "title": "Read chapter 3", "completed": false, "created_at": "2025-11-18T13:00:00Z" }
```

- List (stdout when `--json` passed):

```json
[ { "id": 1, "title": "Task 1", "completed": false, "created_at": "..." } ]
```

- Error (machine mode):

```json
{ "error": "task not found", "code": 404 }
```

## Exit Codes

- `0`: success
- `1`: general error (invalid args, I/O error)
- `2`: not found / user error (e.g., missing task)

