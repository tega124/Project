#!/usr/bin/env python3
"""Validate the presence of required sections in the project constitution.

Exits with code 0 on success, 2 on missing file, 1 on validation failure.
"""
import sys
from pathlib import Path

REQ_SECTIONS = ["## Core Principles", "## Constraints", "## Governance"]


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    constitution = repo / ".specify" / "memory" / "constitution.md"
    if not constitution.exists():
        print(f"ERROR: Constitution file not found: {constitution}", file=sys.stderr)
        return 2
    text = constitution.read_text(encoding="utf-8")
    missing = [s for s in REQ_SECTIONS if s not in text]
    if missing:
        print("ERROR: Constitution is missing required sections:", file=sys.stderr)
        for s in missing:
            print(f"  - {s}", file=sys.stderr)
        return 1
    print("OK: Constitution contains required sections")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
