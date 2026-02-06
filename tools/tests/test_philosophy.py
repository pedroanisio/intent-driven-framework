"""
PHILOSOPHY — the manifesto earns the right to propose a model.

CC-01: States the problem (GREEN — declares field contains problem language)
CC-02: States the inversion (GREEN — design_stance names orientations)
CC-03: Principles named and numbered (RED — no principles section yet)
"""

import pytest
from .criteria import CRITERIA
from .evidence import check_cc01, check_cc02, check_cc03


class TestPhilosophy:
    """The manifesto must establish why this model exists."""

    @pytest.mark.core
    @pytest.mark.philosophy
    def test_cc01_problem_stated(self, root_intent):
        """CC-01: Manifesto states the problem it solves."""
        ev = check_cc01(root_intent)
        assert ev.passed, f"[CC-01] {CRITERIA['CC-01'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.philosophy
    def test_cc02_inversion_stated(self, root_intent):
        """CC-02: Manifesto states the inversion explicitly."""
        ev = check_cc02(root_intent)
        assert ev.passed, f"[CC-02] {CRITERIA['CC-02'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.philosophy
    @pytest.mark.xfail(
        reason="RED: root intent lacks principles section — forces CC-03 expansion",
        strict=False,
    )
    def test_cc03_principles_complete(self, root_intent):
        """CC-03: Every principle is named, numbered, and explained."""
        ev = check_cc03(root_intent)
        assert ev.passed, f"[CC-03] {CRITERIA['CC-03'].test}\n  {ev}"
