"""
ADOPTION — the model is practically adoptable.

CC-13: Adoption sequence ordered
CC-14: Legacy without audit
CC-15: At least three entry points
"""

import pytest
from .criteria import CRITERIA
from .evidence import check_cc13, check_cc14, check_cc15


class TestAdoption:

    @pytest.mark.core
    @pytest.mark.adoption
    def test_cc13_adoption_sequence(self, manifesto, spec):
        """CC-13: Adoption sequence is ordered and actionable."""
        ev = check_cc13(manifesto, spec)
        assert ev.passed, f"[CC-13] {CRITERIA['CC-13'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.adoption
    def test_cc14_legacy_no_audit(self, manifesto, spec):
        """CC-14: Legacy strategy does not require comprehensive audit."""
        ev = check_cc14(manifesto, spec)
        assert ev.passed, f"[CC-14] {CRITERIA['CC-14'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.adoption
    def test_cc15_entry_points(self, manifesto, spec):
        """CC-15: At least three practical entry points described."""
        ev = check_cc15(manifesto, spec)
        assert ev.passed, f"[CC-15] {CRITERIA['CC-15'].test}\n  {ev}"
