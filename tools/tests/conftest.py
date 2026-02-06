"""
Fixtures for intent framework self-conformance tests (Stage 3).

These tests verify YAML artifacts mechanically. The YAML IS the
specification. No prose documents are required.

Fixtures load parsed YAML dicts via PyYAML, cross-layer text from
schema.js and Lean, and provide CLI options for fork testing.
"""

import pytest
import yaml
from pathlib import Path


# ── Paths ────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).parent.parent.parent

DEFAULT_ROOT_INTENT = REPO_ROOT / "criteria" / "intent-driven-framework-definition.yml"
DEFAULT_SCHEMA_JS = REPO_ROOT / "tools" / "schema.js"
DEFAULT_LEAN_FILE = REPO_ROOT / "lean" / "IntentDrivenFramework.lean"
DEFAULT_SDLC_AI_INTENT = REPO_ROOT / "_domains" / "sdlc-ai" / "intent-sdlc-ai.yml"
DEFAULT_CRITERIA_INTENT = REPO_ROOT / "criteria" / "intent-idf-sdlc-v1.7.0.yml"


# ── CLI OPTIONS ──────────────────────────────────────────────────

DEFAULT_PROSE_MANIFESTO = REPO_ROOT / "prose" / "intent-manifesto.md"
DEFAULT_PROSE_SPEC = REPO_ROOT / "prose" / "intent-spec-idf-sdlc-v1.7.0.md"


def pytest_addoption(parser):
    parser.addoption(
        "--root-intent",
        default=str(DEFAULT_ROOT_INTENT),
        help="Path to the root intent definition YAML",
    )
    parser.addoption(
        "--schema-js",
        default=str(DEFAULT_SCHEMA_JS),
        help="Path to the Zod schema.js file",
    )
    parser.addoption(
        "--lean-file",
        default=str(DEFAULT_LEAN_FILE),
        help="Path to the Lean formalization file",
    )
    parser.addoption(
        "--prose-manifesto",
        default=str(DEFAULT_PROSE_MANIFESTO),
        help="Path to the prose manifesto markdown file",
    )
    parser.addoption(
        "--prose-spec",
        default=str(DEFAULT_PROSE_SPEC),
        help="Path to the prose specification markdown file",
    )
    parser.addoption(
        "--sdlc-ai-intent",
        default=str(DEFAULT_SDLC_AI_INTENT),
        help="Path to the SDLC+AI domain intent YAML",
    )
    parser.addoption(
        "--criteria-intent",
        default=str(DEFAULT_CRITERIA_INTENT),
        help="Path to the criteria intent YAML (intent-manifesto-itself)",
    )


# ── YAML FIXTURES ────────────────────────────────────────────────

@pytest.fixture(scope="session")
def root_intent_path(request) -> Path:
    return Path(request.config.getoption("--root-intent"))


@pytest.fixture(scope="session")
def root_intent(root_intent_path) -> dict:
    """The root intent definition as a parsed Python dict.

    Returns the top-level 'intent' key's value, so callers
    access fields directly: root_intent["declares"], etc.
    """
    if not root_intent_path.exists():
        pytest.skip(f"Root intent not found: {root_intent_path}")
    raw = yaml.safe_load(root_intent_path.read_text(encoding="utf-8"))
    assert "intent" in raw, "Root intent YAML must have a top-level 'intent' key"
    return raw["intent"]


@pytest.fixture(scope="session")
def root_intent_text(root_intent_path) -> str:
    """Raw text of the root intent file (for regex fallback checks)."""
    if not root_intent_path.exists():
        pytest.skip(f"Root intent not found: {root_intent_path}")
    return root_intent_path.read_text(encoding="utf-8")


# ── PROSE FIXTURES ──────────────────────────────────────────────

@pytest.fixture(scope="session")
def prose_manifesto_path(request) -> Path:
    return Path(request.config.getoption("--prose-manifesto"))


@pytest.fixture(scope="session")
def prose_manifesto_text(prose_manifesto_path) -> str:
    """Raw text of the prose manifesto for consistency checks."""
    if not prose_manifesto_path.exists():
        pytest.skip(f"Prose manifesto not found: {prose_manifesto_path}")
    return prose_manifesto_path.read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def prose_spec_path(request) -> Path:
    return Path(request.config.getoption("--prose-spec"))


@pytest.fixture(scope="session")
def prose_spec_text(prose_spec_path) -> str:
    """Raw text of the prose spec for drift checks."""
    if not prose_spec_path.exists():
        pytest.skip(f"Prose spec not found: {prose_spec_path}")
    return prose_spec_path.read_text(encoding="utf-8")


# ── DOMAIN FIXTURES ─────────────────────────────────────────────

@pytest.fixture(scope="session")
def sdlc_ai_intent_path(request) -> Path:
    return Path(request.config.getoption("--sdlc-ai-intent"))


@pytest.fixture(scope="session")
def sdlc_ai_intent(sdlc_ai_intent_path) -> dict:
    """The SDLC+AI domain intent as a parsed Python dict.

    Returns the top-level 'intent' key's value.
    """
    if not sdlc_ai_intent_path.exists():
        pytest.skip(f"SDLC+AI domain intent not found: {sdlc_ai_intent_path}")
    raw = yaml.safe_load(sdlc_ai_intent_path.read_text(encoding="utf-8"))
    assert "intent" in raw, "Domain intent YAML must have a top-level 'intent' key"
    return raw["intent"]


@pytest.fixture(scope="session")
def sdlc_ai_intent_text(sdlc_ai_intent_path) -> str:
    """Raw text of the SDLC+AI domain intent file."""
    if not sdlc_ai_intent_path.exists():
        pytest.skip(f"SDLC+AI domain intent not found: {sdlc_ai_intent_path}")
    return sdlc_ai_intent_path.read_text(encoding="utf-8")


# ── CRITERIA INTENT FIXTURES ────────────────────────────────────

@pytest.fixture(scope="session")
def criteria_intent_path(request) -> Path:
    return Path(request.config.getoption("--criteria-intent"))


@pytest.fixture(scope="session")
def criteria_intent(criteria_intent_path) -> dict:
    """The criteria intent (intent-manifesto-itself) as a parsed dict.

    Returns the top-level 'intent' key's value.
    """
    if not criteria_intent_path.exists():
        pytest.skip(f"Criteria intent not found: {criteria_intent_path}")
    raw = yaml.safe_load(criteria_intent_path.read_text(encoding="utf-8"))
    assert "intent" in raw, "Criteria intent YAML must have a top-level 'intent' key"
    return raw["intent"]


@pytest.fixture(scope="session")
def criteria_intent_text(criteria_intent_path) -> str:
    """Raw text of the criteria intent file."""
    if not criteria_intent_path.exists():
        pytest.skip(f"Criteria intent not found: {criteria_intent_path}")
    return criteria_intent_path.read_text(encoding="utf-8")


# ── CROSS-LAYER FIXTURES ────────────────────────────────────────

@pytest.fixture(scope="session")
def schema_js_text(request) -> str:
    """Raw text of schema.js for cross-layer checks."""
    path = Path(request.config.getoption("--schema-js"))
    if not path.exists():
        pytest.skip(f"schema.js not found: {path}")
    return path.read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def lean_text(request) -> str:
    """Raw text of the Lean file for cross-layer checks."""
    path = Path(request.config.getoption("--lean-file"))
    if not path.exists():
        pytest.skip(f"Lean file not found: {path}")
    return path.read_text(encoding="utf-8")


# ── CUSTOM MARKERS ───────────────────────────────────────────────

def pytest_configure(config):
    for marker in [
        "core: core criteria (must pass for v1)",
        "deferred: deferred criteria (tracked, not blocking)",
        "philosophy: CC-01 through CC-03",
        "model: CC-04 through CC-08",
        "conflict: CC-08a through CC-08c",
        "structure: CC-09, CC-10",
        "extensibility: CC-11, CC-12",
        "adoption: CC-13 through CC-15",
        "self_sufficiency: CC-16, CC-17",
        "self_conformance: CC-18, CC-27",
        "operational: CC-19 through CC-26",
        "cross_layer: cross-layer consistency (YAML/Zod/Lean)",
        "prose: prose-YAML consistency checks",
        "domain: domain instantiation tests",
        "hypothesis: domain-invariance hypothesis tests",
        "bridge: criteria-to-root bridge tests",
        "criteria_self: criteria intent self-conformance tests",
        "spec_drift: prose spec drift from canonical YAML/Zod/Lean",
    ]:
        config.addinivalue_line("markers", marker)


# ── CUSTOM REPORTING ─────────────────────────────────────────────

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Print a summary matching the pipeline's reporting style."""
    reports = terminalreporter.stats

    passed = len(reports.get("passed", []))
    failed = len(reports.get("failed", []))
    skipped = len(reports.get("skipped", []))
    xfailed = len(reports.get("xfailed", []))

    deferred_failed = 0
    for r in reports.get("failed", []):
        marks = r.keywords.get("pytestmark", [])
        if isinstance(marks, list):
            if any(getattr(m, "name", None) == "deferred" for m in marks):
                deferred_failed += 1
    core_failed = failed - deferred_failed

    terminalreporter.write_sep("=", "INTENT FRAMEWORK — YAML SELF-CONFORMANCE SUMMARY")
    terminalreporter.write_line(f"  CORE:     {passed}/{passed + core_failed} passed")
    if xfailed:
        terminalreporter.write_line(f"  RED:      {xfailed} forcing functions (xfail)")
    if deferred_failed:
        terminalreporter.write_line(f"  DEFERRED: {deferred_failed} tracked (not blocking)")
    if skipped:
        terminalreporter.write_line(f"  SKIPPED:  {skipped}")
