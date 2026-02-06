"""
EXTENSIBILITY — the plugin architecture is defined and demonstrated.

CC-11: Plugin architecture with example
CC-12: Extension surface with semantics
"""

import pytest
from .criteria import CRITERIA
from .evidence import check_cc11, check_cc12


class TestExtensibility:

    @pytest.mark.core
    @pytest.mark.extensibility
    def test_cc11_plugin_architecture(self, manifesto, spec):
        """CC-11: Plugin architecture defined with at least one example."""
        ev = check_cc11(manifesto, spec)
        assert ev.passed, f"[CC-11] {CRITERIA['CC-11'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.extensibility
    def test_cc12_extension_surface(self, manifesto, spec):
        """CC-12: Extension surface on core entities defined with semantics."""
        ev = check_cc12(manifesto, spec)
        assert ev.passed, f"[CC-12] {CRITERIA['CC-12'].test}\n  {ev}"
