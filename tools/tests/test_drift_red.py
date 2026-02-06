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


def _parse_init_enums(init_text: str) -> dict[str, list[str]] | None:
    m = re.search(r"ENUMS\s*=\s*\{(.*?)\n\}\s*", init_text, re.DOTALL)
    if not m:
        return None
    block = m.group(1)
    enums: dict[str, list[str]] = {}
    key_re = re.compile(r"^\s*\"([a-zA-Z_]+)\"\s*:\s*\[(.*?)\]\s*,?\s*$", re.MULTILINE | re.DOTALL)
    for km in key_re.finditer(block):
        key = km.group(1)
        raw = km.group(2)
        vals = [v.strip().strip("'\"") for v in raw.split(",") if v.strip()]
        enums[key] = vals
    return enums if enums else None


def _parse_zod_enum_from_js(js_text: str, enum_name: str) -> list[str] | None:
    m = re.search(rf"(?:const|let|var)\s+{re.escape(enum_name)}\s*=\s*z\.enum\(\[(.*?)\]\)", js_text, re.DOTALL)
    if not m:
        return None
    raw = m.group(1)
    return [v.strip().strip("'\"") for v in raw.split(",") if v.strip().strip("'\"")]


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


@pytest.mark.core
@pytest.mark.cross_layer
def test_drift_sdlc_init_enums_vs_zod(schema_js_text):
    """SDLC init ENUMS must match Zod enums for change_type and status."""
    init_text = (REPO_ROOT / "prose" / "tools" / "idf-sdlc-v1.7.0-init.py").read_text(encoding="utf-8")
    init_enums = _parse_init_enums(init_text)
    assert init_enums is not None, "DRIFT: SDLC init ENUMS block missing or unparsable"

    change_type_init = sorted(init_enums.get("change_type", []))
    status_init = sorted(init_enums.get("status", []))
    change_type_zod = sorted(_parse_zod_enum_from_js(schema_js_text, "ChangeType") or [])
    status_zod = sorted(_parse_zod_enum_from_js(schema_js_text, "Status") or [])

    assert change_type_init == change_type_zod, (
        f"DRIFT: SDLC init ENUMS.change_type {change_type_init} != Zod ChangeType {change_type_zod}"
    )
    assert status_init == status_zod, (
        f"DRIFT: SDLC init ENUMS.status {status_init} != Zod Status {status_zod}"
    )
