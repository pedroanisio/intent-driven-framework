"""
STRUCTURE — the repository layout is fully specified.

CC-09: Repo structure specified
CC-10: Reader can create _repo/ from docs
"""

import pytest
from .criteria import CRITERIA
from .evidence import check_cc09, check_cc10


class TestStructure:

    @pytest.mark.core
    @pytest.mark.structure
    def test_cc09_repo_structure(self, manifesto, spec):
        """CC-09: Repository structure is fully specified."""
        ev = check_cc09(manifesto, spec)
        assert ev.passed, f"[CC-09] {CRITERIA['CC-09'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.structure
    def test_cc10_self_contained(self, manifesto, spec):
        """CC-10: A reader can create _repo/ from the manifesto alone."""
        ev = check_cc10(manifesto, spec)
        assert ev.passed, f"[CC-10] {CRITERIA['CC-10'].test}\n  {ev}"
