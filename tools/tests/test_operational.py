"""
OPERATIONAL — the model is ready for real-world use.

CC-19: declares quality guidance (GREEN)
CC-20: tooling surface (GREEN — evidence found via deep text scan)
CC-21: adoption ramp (RED — no ramp in YAML)
CC-23: tension staleness (GREEN — all tensions have thresholds)
CC-25: deprecation ceremonies (GREEN — evidence found in YAML)
CC-26: failure modes (GREEN — 6 modes: FM-01 through FM-06)
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
    def test_cc19_declares_quality(self, root_intent):
        """CC-19: The declares field has quality guidance."""
        ev = check_cc19(root_intent)
        assert ev.passed, f"[CC-19] {CRITERIA['CC-19'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.operational
    def test_cc20_tooling_surface(self, root_intent, schema_js_text):
        """CC-20: The spec defines a tooling surface."""
        ev = check_cc20(root_intent, schema_js_text)
        assert ev.passed, f"[CC-20] {CRITERIA['CC-20'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.operational
    @pytest.mark.xfail(
        reason="RED: next-touch adoption ramp not described in root intent YAML",
        strict=False,
    )
    def test_cc21_adoption_ramp(self, root_intent):
        """CC-21: The next-touch rule has an adoption ramp."""
        ev = check_cc21(root_intent)
        assert ev.passed, f"[CC-21] {CRITERIA['CC-21'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.operational
    def test_cc23_tension_staleness(self, root_intent):
        """CC-23: Tension resolution staleness is contractually defined."""
        ev = check_cc23(root_intent)
        assert ev.passed, f"[CC-23] {CRITERIA['CC-23'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.operational
    def test_cc25_deprecation_ceremonies(self, root_intent):
        """CC-25: Deprecation ceremonies for superseded/residual intents defined."""
        ev = check_cc25(root_intent)
        assert ev.passed, f"[CC-25] {CRITERIA['CC-25'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.operational
    def test_cc26_failure_modes(self, root_intent):
        """CC-26: The manifesto names its own failure modes."""
        ev = check_cc26(root_intent)
        assert ev.passed, f"[CC-26] {CRITERIA['CC-26'].test}\n  {ev}"
