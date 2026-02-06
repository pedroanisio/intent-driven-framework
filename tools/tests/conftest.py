"""
Fixtures for intent framework prose validation.

Document paths are configurable via CLI options so the same tests
work for any intent framework fork, not just this repo's layout.
"""

import pytest
from pathlib import Path


# ── CLI OPTIONS ──────────────────────────────────────────────────────

def pytest_addoption(parser):
    parser.addoption(
        "--manifesto", default=str(Path(__file__).parent.parent.parent / "prose" / "intent-manifesto.md"),
        help="Path to the manifesto markdown file",
    )
    parser.addoption(
        "--spec", default=str(Path(__file__).parent.parent.parent / "prose" / "intent-spec.md"),
        help="Path to the spec markdown file",
    )
    parser.addoption(
        "--criteria-yml", default=str(Path(__file__).parent.parent.parent / "criteria" / "intent-manifesto-v1.6.1.yml"),
        help="Path to the criteria YAML file",
    )


# ── DOCUMENT FIXTURES ────────────────────────────────────────────────

@pytest.fixture(scope="session")
def manifesto(request) -> str:
    path = Path(request.config.getoption("--manifesto"))
    if not path.exists():
        pytest.skip(f"Manifesto not found: {path}")
    return path.read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def spec(request) -> str:
    path = Path(request.config.getoption("--spec"))
    if not path.exists():
        pytest.skip(f"Spec not found: {path}")
    return path.read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def criteria_yml(request) -> str:
    path = Path(request.config.getoption("--criteria-yml"))
    if not path.exists():
        pytest.skip(f"Criteria YAML not found: {path}")
    return path.read_text(encoding="utf-8")


# ── CUSTOM MARKERS ───────────────────────────────────────────────────

def pytest_configure(config):
    config.addinivalue_line("markers", "core: core criteria (must pass for v1)")
    config.addinivalue_line("markers", "deferred: deferred criteria (tracked, not blocking)")
    config.addinivalue_line("markers", "philosophy: CC-01 through CC-03")
    config.addinivalue_line("markers", "model: CC-04 through CC-08")
    config.addinivalue_line("markers", "conflict: CC-08a through CC-08c")
    config.addinivalue_line("markers", "structure: CC-09, CC-10")
    config.addinivalue_line("markers", "extensibility: CC-11, CC-12")
    config.addinivalue_line("markers", "adoption: CC-13 through CC-15")
    config.addinivalue_line("markers", "self_sufficiency: CC-16, CC-17")
    config.addinivalue_line("markers", "self_conformance: CC-18, CC-27")
    config.addinivalue_line("markers", "operational: CC-19 through CC-26")


# ── CUSTOM REPORTING ─────────────────────────────────────────────────

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Print a summary matching the original scorer's style."""
    reports = terminalreporter.stats

    passed = len(reports.get("passed", []))
    failed = len(reports.get("failed", []))
    skipped = len(reports.get("skipped", []))
    deferred_failed = 0
    for r in reports.get("failed", []):
        marks = r.keywords.get("pytestmark", [])
        if isinstance(marks, list):
            if any(getattr(m, "name", None) == "deferred" for m in marks):
                deferred_failed += 1
    core_failed = failed - deferred_failed

    terminalreporter.write_sep("=", "INTENT FRAMEWORK — PROSE VALIDATION SUMMARY")
    terminalreporter.write_line(f"  CORE:     {passed - (failed - core_failed)}/{passed + core_failed} passed")
    terminalreporter.write_line(f"  DEFERRED: {failed - core_failed - deferred_failed} tracked")
    if skipped:
        terminalreporter.write_line(f"  SKIPPED:  {skipped}")
