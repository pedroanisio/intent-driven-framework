"""
PHILOSOPHY — the manifesto earns the right to propose a model.

CC-01: States the problem
CC-02: States the inversion
CC-03: Principles are named, numbered, explained
"""

import pytest
from .criteria import CRITERIA, Tier
from .evidence import check_cc01, check_cc02, check_cc03


class TestPhilosophy:
    """The manifesto must establish why this model exists."""

    @pytest.mark.core
    @pytest.mark.philosophy
    def test_cc01_problem_stated(self, manifesto, spec):
        """CC-01: Manifesto states the problem it solves."""
        c = CRITERIA["CC-01"]
        ev = check_cc01(manifesto, spec)
        assert ev.passed, f"[{c.id}] {c.test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.philosophy
    def test_cc02_inversion_stated(self, manifesto, spec):
        """CC-02: Manifesto states the inversion explicitly."""
        c = CRITERIA["CC-02"]
        ev = check_cc02(manifesto, spec)
        assert ev.passed, f"[{c.id}] {c.test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.philosophy
    def test_cc03_principles_complete(self, manifesto, spec):
        """CC-03: Every principle is named, numbered, and explained."""
        c = CRITERIA["CC-03"]
        ev = check_cc03(manifesto, spec)
        assert ev.passed, f"[{c.id}] {c.test}\n  {ev}"
