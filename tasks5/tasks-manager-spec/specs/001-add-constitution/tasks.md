---
description: "Task list for Add Constitution feature"
---

# Tasks: Add Constitution (001-add-constitution)

**Input**: Design documents from `/specs/001-add-constitution/` and `.specify/memory/constitution.md`

## Phase 1: Setup (Shared Infrastructure)

- [ ] T001 Create feature directory and add plan/spec/research files at `specs/001-add-constitution/plan.md`, `specs/001-add-constitution/spec.md`, `specs/001-add-constitution/research.md`
- [ ] T002 [P] Commit constitution file at `.specify/memory/constitution.md`
- [ ] T003 [P] Ensure `specs/001-add-constitution/data-model.md` exists and documents the `Task` schema
- [ ] T004 [P] Ensure `specs/001-add-constitution/contracts/cli.md` exists and documents CLI JSON outputs

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Minimal template and repository hygiene changes required before story work.

- [ ] T005 [P] Update `.specify/templates/plan-template.md` to include an explicit `Constitution Check` gate referencing: Simplicity; JSON storage; `argparse` CLI; `pytest` testing.
- [ ] T006 [P] Update `.specify/templates/spec-template.md` to include a short reminder that each story must include an independent test and to reference the constitution when applicable.
- [ ] T007 [P] Update `.specify/templates/tasks-template.md` to document the `[USX]` labels and the obligation to map tasks to user stories for independent testing.
- [ ] T008 [P] Add `data/` to `.gitignore` and create `data/example_tasks.json` at `data/example_tasks.json` to avoid committing real student data

---

## Phase 3: User Story 1 - View Constitution (Priority: P1) 🎯 MVP

**Goal**: Ensure instructors/students can discover the constitution and automated checks can surface its presence.

**Independent Test**: `tests/integration/test_constitution_present.py` verifies `.specify/memory/constitution.md` exists and contains `## Core Principles` and `## Constraints` headers.

- [ ] T009 [US1] Create integration test `tests/integration/test_constitution_present.py` that asserts the constitution file exists and contains required headers
- [ ] T010 [P] [US1] Add a short reference to the constitution in `README.md` (usage and governance excerpt) at repository root
- [ ] T011 [US1] Implement a lightweight validator script `tools/validate_constitution.py` that checks presence of required sections and returns exit code 0 on success; place at `tools/validate_constitution.py`

---

## Phase 4: User Story 2 - Plan Gate Alignment (Priority: P1)

**Goal**: Ensure plans produced from the templates include `Constitution Check` and that tests verify gating language.

**Independent Test**: `tests/unit/test_plan_template_gate.py` asserts `.specify/templates/plan-template.md` contains the string `Constitution Check` and mentions the required constraints.

- [ ] T012 [US2] Create unit test `tests/unit/test_plan_template_gate.py` to check `plan-template.md` includes constitution gate text and the listed constraints
- [ ] T013 [US2] Confirm and, if necessary, update `specs/001-add-constitution/contracts/cli.md` to align CLI contract examples with constitution's machine-mode JSON requirement (file: `specs/001-add-constitution/contracts/cli.md`)
- [ ] T014 [US2] Create or update quickstart file `specs/001-add-constitution/quickstart.md` to show how to run validator, tests, and CLI in JSON mode

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final documentation, CI integration notes, and housekeeping.

- [ ] T015 [P] Consolidate docs: ensure `docs/quickstart.md`, `README.md`, and `specs/001-add-constitution/*` are consistent and link to `.specify/memory/constitution.md`
- [ ] T016 [P] Add CI note (or job) in repo README or CI config that runs `python tools/validate_constitution.py` and `pytest` as part of PR checks (file path: `.github/workflows/` or `README.md` entry if workflow change needs manual review)

---

## Dependencies & Execution Order

- **Setup (Phase 1)** must be completed first.
- **Foundational (Phase 2)** must be completed before User Story phases start.
- **User Story 1 (Phase 3)** and **User Story 2 (Phase 4)** can be executed in parallel after Phase 2 completes.
- **Polish (Phase 5)** depends on all stories being complete.

## User Story Task Counts

- User Story 1 (`US1`): 3 tasks
- User Story 2 (`US2`): 3 tasks
- Setup & Foundational: 8 tasks
- Polish: 2 tasks
- **Total tasks**: 16

## Parallel Execution Examples

- Run all setup file creation tasks together:
  - `T002`, `T003`, `T004` (file edits & commits) — they operate on different files
- Run template edits in parallel:
  - `T005`, `T006`, `T007` can be done in parallel by different reviewers
- After foundational phase, run story work in parallel:
  - Developer A: `US1` tasks (`T009`-`T011`)
  - Developer B: `US2` tasks (`T012`-`T014`)

## Implementation Strategy

- MVP: Complete Phase 1 + Phase 2 + User Story 1 (`US1`) to provide visible value (constitution present and discoverable).
- Incremental: Add `US2`, tests, and CI hooks afterwards.

---

## Notes

- All tasks follow the strict checklist format required by speckit: `- [ ] T### [P?] [US?] Description with file path`.
- If you want, I can implement `T011` (`tools/validate_constitution.py`) and the two tests (`T009`, `T012`) now and run `pytest` locally (requires bash or native pytest invocation in PowerShell).

