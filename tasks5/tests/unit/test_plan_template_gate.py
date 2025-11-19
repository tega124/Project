import pathlib


def test_plan_template_contains_constitution_gate():
    repo = pathlib.Path(__file__).resolve().parents[2]
    plan_template = repo / ".specify" / "templates" / "plan-template.md"
    assert plan_template.exists(), f"plan-template.md missing at {plan_template}"
    text = plan_template.read_text(encoding="utf-8")
    assert "Constitution Check" in text, "Missing 'Constitution Check' section"
    # check key gate mentions
    assert "JSON" in text or "storage" in text
    assert "argparse" in text or "CLI" in text
    assert "pytest" in text or "Testing" in text
    assert "Simplicity" in text
