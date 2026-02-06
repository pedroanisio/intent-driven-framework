"""
MODEL — the data model is complete and internally consistent.

CC-04: Entity schemas complete
CC-05: Enum values listed (cross-layer)
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
    def test_cc04_entity_schemas(self, schema_js_text):
        """CC-04: Every first-class entity has a complete schema."""
        ev = check_cc04(schema_js_text)
        assert ev.passed, f"[CC-04] {CRITERIA['CC-04'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.model
    def test_cc05_enum_closure(self, root_intent_text, schema_js_text, lean_text):
        """CC-05: Every enum field has all valid values listed."""
        ev = check_cc05(root_intent_text, schema_js_text, lean_text)
        assert ev.passed, f"[CC-05] {CRITERIA['CC-05'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.model
    def test_cc06_bidirectional_relationships(self, schema_js_text):
        """CC-06: Relationships are bidirectionally defined."""
        ev = check_cc06(schema_js_text)
        assert ev.passed, f"[CC-06] {CRITERIA['CC-06'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.model
    def test_cc07_lifecycle_complete(self, root_intent_text, schema_js_text):
        """CC-07: Intent lifecycle is complete."""
        ev = check_cc07(root_intent_text, schema_js_text)
        assert ev.passed, f"[CC-07] {CRITERIA['CC-07'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.model
    def test_cc08_achieved_aspirational(self, root_intent, schema_js_text):
        """CC-08: Achieved and aspirational have distinct schemas."""
        ev = check_cc08(root_intent, schema_js_text)
        assert ev.passed, f"[CC-08] {CRITERIA['CC-08'].test}\n  {ev}"
