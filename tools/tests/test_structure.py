"""
STRUCTURE — the repository layout is fully specified.

CC-09: Repository structure documented (RED — no _repo/ tree in YAML)
CC-10: Self-sufficient documentation (RED — can't create _repo/ from YAML alone)
"""

import pytest
from .criteria import CRITERIA
from .evidence import check_cc09, check_cc10


class TestStructure:

    @pytest.mark.core
    @pytest.mark.structure
    @pytest.mark.xfail(
        reason="RED: _repo/ directory tree not documented in root intent YAML",
        strict=False,
    )
    def test_cc09_repo_structure(self, root_intent):
        """CC-09: Repository structure is fully specified."""
        ev = check_cc09(root_intent)
        assert ev.passed, f"[CC-09] {CRITERIA['CC-09'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.structure
    @pytest.mark.xfail(
        reason="RED: cannot create _repo/ from root intent YAML alone",
        strict=False,
    )
    def test_cc10_self_sufficient_structure(self, root_intent):
        """CC-10: A reader can create the _repo/ folder from docs alone."""
        ev = check_cc10(root_intent)
        assert ev.passed, f"[CC-10] {CRITERIA['CC-10'].test}\n  {ev}"
