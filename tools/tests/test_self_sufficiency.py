"""
SELF-SUFFICIENCY — no external dependencies for understanding.

CC-16: No external-only concepts
CC-17: Daily practice stated concretely
"""

import pytest
from .criteria import CRITERIA
from .evidence import check_cc16, check_cc17


class TestSelfSufficiency:

    @pytest.mark.core
    @pytest.mark.self_sufficiency
    def test_cc16_no_external_concepts(self, manifesto, spec):
        """CC-16: No principle references concepts defined only outside the document."""
        ev = check_cc16(manifesto, spec)
        assert ev.passed, f"[CC-16] {CRITERIA['CC-16'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.self_sufficiency
    def test_cc17_daily_practice(self, manifesto, spec):
        """CC-17: The daily practice is stated concretely."""
        ev = check_cc17(manifesto, spec)
        assert ev.passed, f"[CC-17] {CRITERIA['CC-17'].test}\n  {ev}"
