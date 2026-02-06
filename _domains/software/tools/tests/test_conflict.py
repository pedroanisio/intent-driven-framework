"""
CONFLICT — the model handles contradictions and overlaps.

CC-08a: Contradiction → supersession
CC-08b: Transitions checked against resolutions
CC-08c: Scope overlap detectable
"""

import pytest
from .criteria import CRITERIA
from .evidence import check_cc08a, check_cc08b, check_cc08c


class TestConflict:
    """The model must handle the hard cases: contradictions, stale resolutions, overlapping scope."""

    @pytest.mark.core
    @pytest.mark.conflict
    def test_cc08a_contradiction_to_supersession(self, manifesto, spec):
        """CC-08a: Contradiction between active intents → supersession proposal."""
        ev = check_cc08a(manifesto, spec)
        assert ev.passed, f"[CC-08a] {CRITERIA['CC-08a'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.conflict
    def test_cc08b_transitions_checked(self, manifesto, spec):
        """CC-08b: Transitions that would violate active resolutions are caught."""
        ev = check_cc08b(manifesto, spec)
        assert ev.passed, f"[CC-08b] {CRITERIA['CC-08b'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.conflict
    def test_cc08c_scope_overlap(self, manifesto, spec):
        """CC-08c: Scope overlap between intents is detectable."""
        ev = check_cc08c(manifesto, spec)
        assert ev.passed, f"[CC-08c] {CRITERIA['CC-08c'].test}\n  {ev}"
