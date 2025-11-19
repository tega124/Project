# Data Model: Task

## Entity: Task

- **id**: integer | unique identifier for the task (recommended: auto-increment int or UUID)
- **title**: string | short human-friendly title (required)
- **completed**: boolean | whether the task is done (default: false)
- **created_at**: string (ISO 8601) | timestamp when task was created
- **due_date**: string (ISO 8601) | optional due date
- **notes**: string | optional longer description

## Validation Rules

- `title` must be non-empty and trimmed.
- `due_date` if present must be valid ISO 8601 date or datetime.
- `id` must be unique within `data/tasks.json`.

## Storage Schema (example JSON array)

```
[
  {
    "id": 1,
    "title": "Write lab report",
    "completed": false,
    "created_at": "2025-11-18T12:00:00Z",
    "due_date": null,
    "notes": "Bring references"
  }
]
```

## Atomic Write Pattern

- Write to a temporary file in same directory, e.g. `data/tasks.json.tmp`.
- Flush and fsync the file handle (where supported).
- Rename/replace to `data/tasks.json` using `os.replace` to guarantee atomicity on most platforms.

