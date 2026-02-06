"""
EXTENSIBILITY — the plugin architecture is defined and demonstrated.

CC-11: Plugin architecture with example (RED — no plugin manifest schema)
CC-12: Extension surface demonstrated (GREEN — ext: block in root intent)
"""

import pytest
from .criteria import CRITERIA
from .evidence import check_cc11, check_cc12


class TestExtensibility:

    @pytest.mark.core
    @pytest.mark.extensibility
    @pytest.mark.xfail(
        reason="RED: plugin manifest schema and worked example not in current artifacts",
        strict=False,
    )
    def test_cc11_plugin_architecture(self, root_intent, schema_js_text):
        """CC-11: Plugin architecture defined with at least one concrete example."""
        ev = check_cc11(root_intent, schema_js_text)
        assert ev.passed, f"[CC-11] {CRITERIA['CC-11'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.extensibility
    def test_cc12_extension_surface(self, root_intent, schema_js_text):
        """CC-12: Extension surface on core entities defined with semantics."""
        ev = check_cc12(root_intent, schema_js_text)
        assert ev.passed, f"[CC-12] {CRITERIA['CC-12'].test}\n  {ev}"
