"""
DEFERRED — tracked, not blocking v1.

CC-22: Cross-repo discovery protocol
CC-24: Schema evolution semantics

These are expected to fail. They are declared as xfail so the test
suite passes green while still tracking the gap. When the promotion
condition is met, remove the xfail marker — the test goes red,
forcing the prose to be written.
"""

import pytest
from .criteria import CRITERIA
from .evidence import check_cc22, check_cc24


class TestDeferred:

    @pytest.mark.deferred
    @pytest.mark.operational
    @pytest.mark.xfail(reason="Deferred: awaiting multi-repo adoption", strict=False)
    def test_cc22_cross_repo_discovery(self, manifesto, spec):
        """CC-22: Cross-repo intent dependencies have a discovery protocol."""
        ev = check_cc22(manifesto, spec)
        assert ev.passed, f"[CC-22] {CRITERIA['CC-22'].test}\n  {ev}"

    @pytest.mark.deferred
    @pytest.mark.operational
    @pytest.mark.xfail(reason="Deferred: awaiting first schema change proposal", strict=False)
    def test_cc24_schema_evolution(self, manifesto, spec):
        """CC-24: The core schema has evolution semantics."""
        ev = check_cc24(manifesto, spec)
        assert ev.passed, f"[CC-24] {CRITERIA['CC-24'].test}\n  {ev}"
