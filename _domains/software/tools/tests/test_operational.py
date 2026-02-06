"""
OPERATIONAL — the model is ready for real-world use.

CC-19: declares quality guidance
CC-20: Tooling surface defined
CC-21: Next-touch adoption ramp
CC-23: Tension staleness contract
CC-25: Deprecation ceremonies
CC-26: Failure mode catalogue
"""

import pytest
from .criteria import CRITERIA
from .evidence import (
    check_cc19, check_cc20, check_cc21,
    check_cc23, check_cc25, check_cc26,
)


class TestOperational:

    @pytest.mark.core
    @pytest.mark.operational
    def test_cc19_declares_quality(self, manifesto, spec):
        """CC-19: The declares field has quality guidance."""
        ev = check_cc19(manifesto, spec)
        assert ev.passed, f"[CC-19] {CRITERIA['CC-19'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.operational
    def test_cc20_tooling_surface(self, manifesto, spec):
        """CC-20: The spec defines a tooling surface."""
        ev = check_cc20(manifesto, spec)
        assert ev.passed, f"[CC-20] {CRITERIA['CC-20'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.operational
    def test_cc21_adoption_ramp(self, manifesto, spec):
        """CC-21: The next-touch rule has an adoption ramp."""
        ev = check_cc21(manifesto, spec)
        assert ev.passed, f"[CC-21] {CRITERIA['CC-21'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.operational
    def test_cc23_staleness_contract(self, manifesto, spec):
        """CC-23: Tension resolution staleness is contractually defined."""
        ev = check_cc23(manifesto, spec)
        assert ev.passed, f"[CC-23] {CRITERIA['CC-23'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.operational
    def test_cc25_deprecation_ceremonies(self, manifesto, spec):
        """CC-25: Deprecation ceremonies for superseded/residual intents."""
        ev = check_cc25(manifesto, spec)
        assert ev.passed, f"[CC-25] {CRITERIA['CC-25'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.operational
    def test_cc26_failure_modes(self, manifesto, spec):
        """CC-26: The manifesto names its own failure modes."""
        ev = check_cc26(manifesto, spec)
        assert ev.passed, f"[CC-26] {CRITERIA['CC-26'].test}\n  {ev}"
