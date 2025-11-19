import pathlib


def test_constitution_has_core_and_constraints():
    repo = pathlib.Path(__file__).resolve().parents[2]
    const = repo / ".specify" / "memory" / "constitution.md"
    assert const.exists(), f"Constitution file missing at {const}"
    text = const.read_text(encoding="utf-8")
    assert "## Core Principles" in text, "Missing '## Core Principles'"
    assert "## Constraints" in text, "Missing '## Constraints'"
