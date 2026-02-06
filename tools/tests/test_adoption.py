"""
ADOPTION — the model is practically adoptable.

CC-13: Ordered adoption sequence (RED — no numbered steps in YAML)
CC-14: No comprehensive audit required (RED/PARTIAL — provides-e mentions it)
CC-15: At least three entry points (GREEN — pain-first, next-touch, amnesty)
"""

import pytest
from .criteria import CRITERIA
from .evidence import check_cc13, check_cc14, check_cc15


class TestAdoption:

    @pytest.mark.core
    @pytest.mark.adoption
    @pytest.mark.xfail(
        reason="RED: no numbered adoption sequence in root intent YAML",
        strict=False,
    )
    def test_cc13_adoption_sequence(self, root_intent):
        """CC-13: Adoption sequence is ordered and actionable."""
        ev = check_cc13(root_intent)
        assert ev.passed, f"[CC-13] {CRITERIA['CC-13'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.adoption
    def test_cc14_no_audit_required(self, root_intent):
        """CC-14: Legacy strategy does not require comprehensive audit."""
        ev = check_cc14(root_intent)
        assert ev.passed, f"[CC-14] {CRITERIA['CC-14'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.adoption
    def test_cc15_entry_points(self, root_intent):
        """CC-15: At least three practical entry points described."""
        ev = check_cc15(root_intent)
        assert ev.passed, f"[CC-15] {CRITERIA['CC-15'].test}\n  {ev}"
