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


def _parse_embedded_valid_enums(init_text: str) -> dict[str, list[str]] | None:
    """Parse VALID_ENUMS dict from the embedded ci_validator_script template."""
    m = re.search(r"VALID_ENUMS\s*=\s*\{(.*?)\n\s*\}", init_text, re.DOTALL)
    if not m:
        return None
    block = m.group(1)
    enums: dict[str, list[str]] = {}
    key_re = re.compile(r'"([a-zA-Z_]+)"\s*:\s*\[(.*?)\]', re.DOTALL)
    for km in key_re.finditer(block):
        key = km.group(1)
        raw = km.group(2)
        vals = [v.strip().strip("'\"") for v in raw.split(",") if v.strip().strip("'\"")]
        enums[key] = vals
    return enums if enums else None


def _parse_embedded_valid_ct(init_text: str) -> list[str] | None:
    """Parse the valid_ct list from the embedded ci_validator_script template."""
    m = re.search(r"valid_ct\s*=\s*\[(.*?)\]", init_text, re.DOTALL)
    if not m:
        return None
    raw = m.group(1)
    return [v.strip().strip("'\"") for v in raw.split(",") if v.strip().strip("'\"")]


def _parse_embedded_valid_transitions(init_text: str) -> dict[str, list[str]] | None:
    """Parse VALID_TRANSITIONS dict from the embedded lifecycle_hook_script template."""
    m = re.search(r"VALID_TRANSITIONS\s*=\s*\{(.*?)\n\s*\}", init_text, re.DOTALL)
    if not m:
        return None
    transitions: dict[str, list[str]] = {}
    key_re = re.compile(r'"([a-zA-Z_]+)"\s*:\s*\[(.*?)\]', re.DOTALL)
    for km in key_re.finditer(m.group(1)):
        key = km.group(1)
        raw = km.group(2)
        vals = [v.strip().strip("'\"") for v in raw.split(",") if v.strip().strip("'\"")]
        transitions[key] = vals
    return transitions if transitions else None


def _parse_zod_enum_from_js(js_text: str, enum_name: str) -> list[str] | None:
    m = re.search(rf"(?:const|let|var)\s+{re.escape(enum_name)}\s*=\s*z\.enum\(\[(.*?)\]\)", js_text, re.DOTALL)
    if not m:
        return None
    raw = m.group(1)
    return [v.strip().strip("'\"") for v in raw.split(",") if v.strip().strip("'\"")]


def _parse_intent_template_block(init_text: str) -> str | None:
    m = re.search(r"def\\s+intent_template\\(.*?\\):\\s*.*?return\\s+\"\\\\n\"\\.join\\(lines\\)", init_text, re.DOTALL)
    return m.group(0) if m else None


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


@pytest.mark.core
@pytest.mark.cross_layer
def test_drift_sdlc_init_intent_template_fields():
    """SDLC init intent_template must include required intent fields."""
    init_text = (REPO_ROOT / "prose" / "tools" / "idf-sdlc-v1.7.0-init.py").read_text(encoding="utf-8")
    block = _parse_intent_template_block(init_text)
    assert block, "DRIFT: SDLC init intent_template missing or unparsable"

    required = [
        "intent:",
        "id:",
        "version:",
        "schema_version:",
        "intent_type:",
        "declares:",
        "current_reality:",
        "scope:",
        "priority:",
        "status:",
        "confidence:",
        "owner:",
        "origin:",
        "serves:",
        "dependencies:",
        "transition_log:",
    ]
    missing = [s for s in required if s not in block]
    assert not missing, f\"DRIFT: SDLC init intent_template missing fields: {', '.join(missing)}\"


# ── Embedded template drift tests ────────────────────────────────────


@pytest.mark.core
@pytest.mark.cross_layer
def test_drift_sdlc_init_embedded_valid_enums_status(schema_js_text):
    """Embedded VALID_ENUMS.status in ci_validator_script must match Zod Status."""
    init_text = (REPO_ROOT / "prose" / "tools" / "idf-sdlc-v1.7.0-init.py").read_text(encoding="utf-8")
    valid_enums = _parse_embedded_valid_enums(init_text)
    assert valid_enums is not None, "DRIFT: VALID_ENUMS block not found in init script"

    embedded_status = sorted(valid_enums.get("status", []))
    zod_status = sorted(_parse_zod_enum_from_js(schema_js_text, "Status") or [])
    assert embedded_status == zod_status, (
        f"DRIFT: embedded VALID_ENUMS.status {embedded_status} != Zod Status {zod_status}"
    )


@pytest.mark.core
@pytest.mark.cross_layer
def test_drift_sdlc_init_embedded_valid_enums_keys():
    """Embedded VALID_ENUMS must cover all enum keys from top-level ENUMS."""
    init_text = (REPO_ROOT / "prose" / "tools" / "idf-sdlc-v1.7.0-init.py").read_text(encoding="utf-8")
    top_level = _parse_init_enums(init_text)
    embedded = _parse_embedded_valid_enums(init_text)
    assert top_level is not None, "Top-level ENUMS block missing"
    assert embedded is not None, "Embedded VALID_ENUMS block missing"

    missing = sorted(set(top_level.keys()) - set(embedded.keys()))
    assert not missing, (
        f"DRIFT: embedded VALID_ENUMS missing keys present in top-level ENUMS: {missing}"
    )


@pytest.mark.core
@pytest.mark.cross_layer
def test_drift_sdlc_init_embedded_valid_ct(schema_js_text):
    """Embedded valid_ct in ci_validator_script must match Zod ChangeType."""
    init_text = (REPO_ROOT / "prose" / "tools" / "idf-sdlc-v1.7.0-init.py").read_text(encoding="utf-8")
    embedded_ct = _parse_embedded_valid_ct(init_text)
    assert embedded_ct is not None, "DRIFT: valid_ct list not found in init script"

    zod_ct = sorted(_parse_zod_enum_from_js(schema_js_text, "ChangeType") or [])
    assert sorted(embedded_ct) == zod_ct, (
        f"DRIFT: embedded valid_ct {sorted(embedded_ct)} != Zod ChangeType {zod_ct}"
    )


@pytest.mark.core
@pytest.mark.cross_layer
def test_drift_sdlc_init_embedded_valid_transitions_states(schema_js_text):
    """Embedded VALID_TRANSITIONS must include all Zod Status values as states."""
    init_text = (REPO_ROOT / "prose" / "tools" / "idf-sdlc-v1.7.0-init.py").read_text(encoding="utf-8")
    transitions = _parse_embedded_valid_transitions(init_text)
    assert transitions is not None, "DRIFT: VALID_TRANSITIONS block not found in init script"

    zod_status = set(_parse_zod_enum_from_js(schema_js_text, "Status") or [])
    transition_states = set(transitions.keys())
    missing = sorted(zod_status - transition_states)
    assert not missing, (
        f"DRIFT: embedded VALID_TRANSITIONS missing states: {missing}"
    )
