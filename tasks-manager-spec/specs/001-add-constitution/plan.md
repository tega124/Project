# Implementation Plan: Add Constitution

**Branch**: `001-add-constitution` | **Date**: 2025-11-18 | **Spec**: `specs/001-add-constitution/spec.md`
**Input**: Feature specification from `/specs/001-add-constitution/spec.md` (initial input: update constitution file in `.specify/memory/constitution.md`)

## Summary

Add a ratified project constitution for the CSC299 Task Manager CLI app. This plan documents the technical context, constraints, and the implementation phases needed to (1) finalize the constitution in the repository, (2) wire it into the `plan`/`spec` templates' gating / checks, and (3) provide small deliverables to help students and maintainers adopt the rules (quickstart, data model, and example tests).

Primary outputs:
- `specs/001-add-constitution/plan.md` (this file)
- `specs/001-add-constitution/spec.md` (feature spec populated from template)
- `specs/001-add-constitution/research.md` (Phase 0 research notes)
- Updated `.specify/memory/constitution.md` (already written)
- Small template adjustments to ensure `Constitution Check` gating references the new constraints

## Technical Context

**Language/Version**: Python 3.11+ (target; document exact minor version in `README`)
**Primary Dependencies**: None required beyond standard library for the constitution itself; recommended minimal dev deps: `pytest` (testing), `black`/`ruff` (optional lint/format), `click` NOT used (we require `argparse`).
**Storage**: JSON files on disk (e.g., `data/tasks.json`) for the application data model; plan artifacts stored as markdown in `specs/`.
**Testing**: `pytest` for unit and integration tests; CI should run `pytest`.
**Target Platform**: Developer machines and CI (cross-platform: Windows, macOS, Linux). CLI must run under Python on these OSes.
**Project Type**: Single CLI project (source under `src/` or `.` and tests under `tests/`).
**Performance Goals**: Not applicable beyond responsive CLI (<500ms simple commands) and deterministic, fast tests.
**Constraints**: See Constitution — JSON storage only, `argparse` for CLI, `pytest` for testing, minimal external deps.
**Scale/Scope**: Small teaching project; single-user local usage; no networked persistence required.

## Constitution Check

GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.

Gates applied for this plan (derived from `.specify/memory/constitution.md`):
- Simplicity: Plan scope is minimal and incremental.
- Storage: No DBs; planned artifacts and templates reference JSON storage and atomic write practice.
- Interface: CLI expectations (argparse, JSON output) are documented for integration into contracts.
- Testing: `pytest` required for deliverables and CI.

Result: PASS — this plan is explicitly aligned with the constitution. Any future features must surface conflicts through the `Constitution Check` section.

## Project Structure

Selected structure: Single project layout suitable for small CLI apps and classroom examples.

```
specs/001-add-constitution/
├── plan.md                 # This file
├── spec.md                 # Feature spec (to be populated)
├── research.md             # Phase 0 research notes

src/                       # (project root - existing repo structure)
├── taskmgr/                # (suggested) package for the CLI and logic
│   ├── __main__.py         # CLI entry
│   ├── cli.py              # argparse command definitions
│   ├── storage.py          # JSON read/write helpers
│   └── models.py           # Task data classes

data/
└── tasks.json              # example data file (not committed with real student data)

tests/
├── unit/
└── integration/

docs/
└── quickstart.md
```

**Structure Decision**: Single project to preserve simplicity and make examples easily runnable for students.

## Complexity Tracking

No constitution violations detected. No additional projects or external services required. No complexity exceptions requested.

## Phase Plan & Deliverables

Phase 0: Research & Confirmation (complete / lightweight)
- Deliverable: `specs/001-add-constitution/research.md` (notes summarizing rationale for constraints and recommended patterns such as atomic JSON writes and test templates)
- Actions:
  - Confirm `argparse` usage pattern and example CLI contract
  - Document recommended JSON schema for `Task` (`id`, `title`, `completed`, `created_at`, `due_date?`, `notes?`)
  - Document atomic write pattern (write to temp file, fsync, rename)

Phase 1: Design & Contracts
- Deliverables:
  - `specs/001-add-constitution/data-model.md` (entity: Task, fields, validation)
  - `specs/001-add-constitution/contracts/cli-openapi.md` (simple CLI contract listing commands and JSON machine outputs)
  - `docs/quickstart.md` (how to install and run examples)
- Actions:
  - Create a minimal `Task` dataclass in `src/taskmgr/models.py` and sample JSON
  - Define CLI commands (create, list, update, complete, delete) and their JSON output shapes
  - Add example pytest tests demonstrating storage atomicity and CLI JSON mode

Phase 2: Implementation (small reference implementation for instructors)
- Deliverables:
  - Minimal reference CLI `src/taskmgr/cli.py` using `argparse` implementing the commands
  - Storage helper `src/taskmgr/storage.py` with atomic JSON read/write
  - Unit tests in `tests/unit/test_storage.py` and `tests/unit/test_cli.py`
- Actions:
  - Implement and run tests locally; ensure `pytest` passes
  - Document how to run the CLI and the tests in `README` / `docs/quickstart.md`

Phase 3: Template integration & gating
- Deliverables:
  - Small edits to `.specify/templates/plan-template.md` to include explicit `Constitution Check` gates referencing: Simplicity; JSON storage; argparse; pytest
  - A short note in `.specify/memory/constitution.md` (done) referencing template locations
- Actions:
  - Apply small wording edits to the three templates flagged in the Sync Impact Report
  - Add a pre-check note in the `plan-template.md` that CI or reviewers should verify constitution alignment during planning

## Implementation Strategy

MVP-first: produce minimal documentation + small design artifacts (data model + CLI contract) so instructors can grade and students can follow.

Order of work (short):
1. Create `specs/001-add-constitution/research.md` (Phase 0 small doc)
2. Produce `data-model.md` and `contracts/cli.md` (Phase 1)
3. Optionally produce reference implementation and tests (Phase 2)
4. Update templates with explicit constitution gates (Phase 3)

## Acceptance Criteria

- The constitution file exists at `.specify/memory/constitution.md` and contains the required sections (done).
- `specs/001-add-constitution/plan.md` exists (this file).
- `specs/001-add-constitution/spec.md` and `research.md` are present (placeholders created by this plan step).
- Templates (`.specify/templates/plan-template.md`, `spec-template.md`, `tasks-template.md`) either contain no ambiguous placeholders or have notes added indicating the constitution gates.
- Reference `pytest` tests demonstrate at least one unit test (storage atomic write) passing.

## Risks & Mitigations

- Risk: Templates may be used in other features and editing them could have broad impact. Mitigation: keep edits minimal and add comments indicating the required gate, not automated enforcement.
- Risk: Students may commit data files accidentally. Mitigation: add `data/` to `.gitignore` and include a `data/example_tasks.json` template.

## Next Steps (short)
- Create `specs/001-add-constitution/spec.md` and `research.md` (I will create these now as placeholders).
- If you want, I can also:
  - Open a feature branch `001-add-constitution` and commit these files, or
  - Make the small safe edits to the plan/spec/tasks templates to explicitly reference the constitution gates (I will not edit templates without your confirmation).

---

