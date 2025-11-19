import json
from pathlib import Path

from taskmgr import storage


def test_atomic_write_and_load(tmp_path):
    data_file = tmp_path / "tasks.json"
    # initially empty
    assert storage.load_tasks(data_file) == []
    t = storage.add_task("Test", notes="n", path=data_file)
    assert t.id == 1
    # ensure file exists and content parseable
    raw = json.loads(data_file.read_text(encoding="utf-8"))
    assert isinstance(raw, list)
    assert raw[0]["title"] == "Test"
    # add another
    t2 = storage.add_task("Two", path=data_file)
    assert t2.id == 2
    tasks = storage.load_tasks(data_file)
    assert len(tasks) == 2
