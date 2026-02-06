"""
SELF-CONFORMANCE — the model governs itself.

CC-18: Intent block conforms to its own model (depends on CC-08)
CC-27: Transition log is complete and consistent
"""

import pytest
from .criteria import CRITERIA
from .evidence import check_cc08, check_cc18, check_cc27


class TestSelfConformance:

    @pytest.mark.core
    @pytest.mark.self_conformance
    def test_cc18_self_conformance(self, manifesto, spec):
        """CC-18: The intent block conforms to the model it specifies."""
        # CC-18 depends on CC-08 — check dependency first
        cc08_ev = check_cc08(manifesto, spec)
        ev = check_cc18(manifesto, spec, cc08_passed=cc08_ev.passed)

        if ev.skipped:
            pytest.skip(ev.skip_reason)

        assert ev.passed, f"[CC-18] {CRITERIA['CC-18'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.self_conformance
    def test_cc27_transition_log(self, criteria_yml):
        """CC-27: Transition log is complete and consistent."""
        ev = check_cc27(criteria_yml)
        assert ev.passed, f"[CC-27] {CRITERIA['CC-27'].test}\n  {ev}"
