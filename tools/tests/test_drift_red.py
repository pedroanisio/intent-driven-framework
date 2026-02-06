import re
from pathlib import Path

import pytest

from .conftest import REPO_ROOT


def _fc_status_from_root_intent(root_intent: dict, fc_id: str) -> str | None:
    for fc in root_intent.get("falsifiable_claims", []):
        if isinstance(fc, dict) and fc.get("id") == fc_id:
            return fc.get("status")
    return None


def _fc_status_from_lean(lean_text: str, fc_id: str) -> str | None:
    m = re.search(
        rf'id\s*:=\s*"{re.escape(fc_id)}".*?status\s*:=\s*\.([a-zA-Z_]+)',
        lean_text,
        re.DOTALL,
    )
    return m.group(1) if m else None


def _fc_status_from_readme(readme_text: str, fc_id: str) -> str | None:
    m = re.search(
        rf"\|\s*{re.escape(fc_id)}\s*\|.*?\|\s*`(\w+)`\s*\|",
        readme_text,
    )
    return m.group(1) if m else None


def _root_transition_log_len(root_intent: dict) -> int:
    log = root_intent.get("transition_log", [])
    return len(log) if isinstance(log, list) else 0


def _lean_root_transition_log_len(lean_text: str) -> int:
    m = re.search(
        r"def\s+root_intent_log\s*:.*?\[\s*(.*?)\n\]",
        lean_text,
        re.DOTALL,
    )
    if not m:
        return 0
    block = m.group(1)
    return len(re.findall(r"intent_id\s*:=\s*\"intent-driven-framework-definition\"", block))


@pytest.mark.core
@pytest.mark.cross_layer
def test_drift_fc04_status_root_vs_lean(root_intent, lean_text):
    """FC-04 status must match between root intent and Lean."""
    root_status = _fc_status_from_root_intent(root_intent, "FC-04")
    lean_status = _fc_status_from_lean(lean_text, "FC-04")
    assert root_status == lean_status, (
        f"DRIFT: FC-04 status root={root_status} vs Lean={lean_status}"
    )


@pytest.mark.core
@pytest.mark.cross_layer
def test_drift_fc04_status_root_vs_readme(root_intent):
    """FC-04 status must match between root intent and README."""
    readme_text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    root_status = _fc_status_from_root_intent(root_intent, "FC-04")
    readme_status = _fc_status_from_readme(readme_text, "FC-04")
    assert root_status == readme_status, (
        f"DRIFT: FC-04 status root={root_status} vs README={readme_status}"
    )


@pytest.mark.core
@pytest.mark.cross_layer
def test_drift_root_transition_log_len(root_intent, lean_text):
    """Root transition log entry count must match Lean."""
    root_len = _root_transition_log_len(root_intent)
    lean_len = _lean_root_transition_log_len(lean_text)
    assert root_len == lean_len, (
        f"DRIFT: root transition_log has {root_len} entries, Lean has {lean_len}"
    )
