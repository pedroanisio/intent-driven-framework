"""
CONFLICT — the model handles contradictions and overlaps.

CC-08a: Contradiction resolution (GREEN — tensions have resolution strategies)
CC-08b: Pre-transition check (RED — contract not explicit in YAML)
CC-08c: Scope overlap detection (RED — no overlap mechanics in YAML)
"""

import pytest
from .criteria import CRITERIA
from .evidence import check_cc08a, check_cc08b, check_cc08c


class TestConflict:

    @pytest.mark.core
    @pytest.mark.conflict
    def test_cc08a_contradiction_resolved(self, root_intent):
        """CC-08a: Contradiction between active intents is detected and resolved."""
        ev = check_cc08a(root_intent)
        assert ev.passed, f"[CC-08a] {CRITERIA['CC-08a'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.conflict
    @pytest.mark.xfail(
        reason="RED: pre-transition check contract not explicit in root intent YAML",
        strict=False,
    )
    def test_cc08b_transition_checked(self, root_intent):
        """CC-08b: Transitions that would violate active intents are caught."""
        ev = check_cc08b(root_intent)
        assert ev.passed, f"[CC-08b] {CRITERIA['CC-08b'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.conflict
    @pytest.mark.xfail(
        reason="RED: scope overlap detection not described in root intent YAML",
        strict=False,
    )
    def test_cc08c_scope_overlap(self, root_intent):
        """CC-08c: Scope overlap between intents is detectable."""
        ev = check_cc08c(root_intent)
        assert ev.passed, f"[CC-08c] {CRITERIA['CC-08c'].test}\n  {ev}"
