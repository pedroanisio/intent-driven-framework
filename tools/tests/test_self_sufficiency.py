"""
SELF-SUFFICIENCY — no external dependencies for understanding.

CC-16: No external-only concept references (GREEN/PARTIAL)
CC-17: Daily practice stated concretely (GREEN — operational_cycle.phases)
"""

import pytest
from .criteria import CRITERIA
from .evidence import check_cc16, check_cc17


class TestSelfSufficiency:

    @pytest.mark.core
    @pytest.mark.self_sufficiency
    def test_cc16_no_external_concepts(self, root_intent):
        """CC-16: No principle references concepts defined only outside the document."""
        ev = check_cc16(root_intent)
        assert ev.passed, f"[CC-16] {CRITERIA['CC-16'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.self_sufficiency
    def test_cc17_daily_practice(self, root_intent):
        """CC-17: The daily practice is stated concretely."""
        ev = check_cc17(root_intent)
        assert ev.passed, f"[CC-17] {CRITERIA['CC-17'].test}\n  {ev}"
