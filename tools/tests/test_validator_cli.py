import os
import shutil
import subprocess
from pathlib import Path

import pytest


def test_validate_schema_failure_does_not_crash(tmp_path):
    node = shutil.which("node")
    if not node:
        pytest.skip("node not available")

    repo_root = Path(__file__).resolve().parents[2]
    yaml_path = tmp_path / "bad-intent.yml"
    yaml_path.write_text(
        "intent:\n"
        "  id: test\n"
        "  version: 0.0.1\n"
        "  intent_type: aspirational\n",
        encoding="utf-8",
    )

    env = os.environ.copy()
    env["FLAW_STATE"] = str(tmp_path / ".flaw-state.json")

    result = subprocess.run(
        [node, str(repo_root / "tools" / "validate.js"), str(yaml_path)],
        cwd=repo_root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert result.returncode != 0
    assert "SCHEMA" in result.stdout or "SCHEMA" in result.stderr
