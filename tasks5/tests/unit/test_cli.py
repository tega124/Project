import json
import subprocess
import sys
from pathlib import Path


def run_cmd(args, env=None):
    cmd = [sys.executable, "-m", "taskmgr"] + args
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return proc


def test_cli_add_and_list(tmp_path):
    data_file = tmp_path / "tasks.json"
    env = dict(**{**(None or {})})
    env.update({"TASKMGR_DATA": str(data_file)})
    # add a task
    r = run_cmd(["add", "CLI Test", "--json"], env=env)
    assert r.returncode == 0
    created = json.loads(r.stdout.strip())
    assert created["title"] == "CLI Test" or created["title"] == "CLI Test"
    # list
    r2 = run_cmd(["list", "--json"], env=env)
    assert r2.returncode == 0
    arr = json.loads(r2.stdout)
    assert isinstance(arr, list)
