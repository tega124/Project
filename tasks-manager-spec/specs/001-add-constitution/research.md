# Research: Add Constitution (Phase 0)

## Decisions and rationale

- Decision: Store constitution in `.specify/memory/constitution.md`.
  - Rationale: central location used by the speckit tooling; easily readable and editable.
  - Alternatives: top-level `docs/` — rejected for tooling integration reasons.

- Decision: Keep storage and runtime constraints minimal: JSON storage for app data; `argparse` for CLI; `pytest` for tests.
  - Rationale: aligns with teaching goals and reduces student friction.

## Patterns to recommend

- Atomic JSON write: write to `data/tasks.json.tmp`, fsync, then `os.replace`/`rename`.
- Task model suggestion:
  - `id` (int or uuid)
  - `title` (string)
  - `completed` (bool)
  - `created_at` (ISO 8601 string)
  - optional: `due_date`, `notes`

## Next research items (if desired)
- Short example of `argparse` subparser layout mapping to CLI commands.
- Minimal `pytest` examples showing CLI invocation (`subprocess` or `click.testing` style; here use `subprocess` since we restrict to `argparse`).

