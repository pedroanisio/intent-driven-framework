"""
DEFERRED — tracked, not blocking v1.

CC-22: Cross-repo discovery protocol
CC-24: Schema evolution semantics
"""

import pytest
from .criteria import CRITERIA
from .evidence import check_cc22, check_cc24


class TestDeferred:

    @pytest.mark.deferred
    @pytest.mark.operational
    @pytest.mark.xfail(reason="CC-22 deferred: cross-repo discovery not needed for v1")
    def test_cc22_cross_repo_discovery(self, root_intent):
        """CC-22: Cross-repo intent dependencies have a discovery protocol."""
        ev = check_cc22(root_intent)
        assert ev.passed, f"[CC-22] {CRITERIA['CC-22'].test}\n  {ev}"

    @pytest.mark.deferred
    @pytest.mark.operational
    @pytest.mark.xfail(reason="CC-24 deferred: schema governance not needed for v1")
    def test_cc24_schema_evolution(self, root_intent):
        """CC-24: The core schema has evolution semantics."""
        ev = check_cc24(root_intent)
        assert ev.passed, f"[CC-24] {CRITERIA['CC-24'].test}\n  {ev}"
