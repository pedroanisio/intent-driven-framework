"""
MODEL — the data model is complete and internally consistent.

CC-04: Entity schemas complete
CC-05: Enum values listed
CC-06: Relationships bidirectional
CC-07: Lifecycle complete
CC-08: Achieved/aspirational distinct
"""

import pytest
from .criteria import CRITERIA
from .evidence import (
    check_cc04, check_cc05, check_cc06, check_cc07, check_cc08,
)


class TestModel:
    """The data model must be precise, expressive, and minimal."""

    @pytest.mark.core
    @pytest.mark.model
    def test_cc04_entity_schemas(self, manifesto, spec):
        """CC-04: Every first-class entity has a complete schema."""
        ev = check_cc04(manifesto, spec)
        assert ev.passed, f"[CC-04] {CRITERIA['CC-04'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.model
    def test_cc05_enum_values(self, manifesto, spec):
        """CC-05: Every enum field has all valid values listed."""
        ev = check_cc05(manifesto, spec)
        assert ev.passed, f"[CC-05] {CRITERIA['CC-05'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.model
    def test_cc06_bidirectional_relationships(self, manifesto, spec):
        """CC-06: Relationships are bidirectionally defined."""
        ev = check_cc06(manifesto, spec)
        assert ev.passed, f"[CC-06] {CRITERIA['CC-06'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.model
    def test_cc07_lifecycle_complete(self, manifesto, spec):
        """CC-07: Intent lifecycle is complete."""
        ev = check_cc07(manifesto, spec)
        assert ev.passed, f"[CC-07] {CRITERIA['CC-07'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.model
    def test_cc08_achieved_aspirational(self, manifesto, spec):
        """CC-08: Achieved and aspirational have distinct schemas."""
        ev = check_cc08(manifesto, spec)
        assert ev.passed, f"[CC-08] {CRITERIA['CC-08'].test}\n  {ev}"
