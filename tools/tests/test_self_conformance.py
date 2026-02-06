"""
SELF-CONFORMANCE — the model governs itself.

CC-18: Intent block conforms to its own model (depends on CC-08)
CC-27: Transition log is complete and consistent

These are the bootstrap criteria. If the root intent doesn't eat its
own cooking, the model is performative.
"""

import pytest
from .criteria import CRITERIA
from .evidence import check_cc18, check_cc27, check_cc08


class TestSelfConformance:

    @pytest.mark.core
    @pytest.mark.self_conformance
    def test_cc18_self_conformance(self, root_intent, schema_js_text):
        """CC-18: The intent block conforms to the model it specifies."""
        # CC-18 depends on CC-08 — check dependency first
        cc08_ev = check_cc08(root_intent, schema_js_text)
        if not cc08_ev.passed:
            pytest.skip("CC-08 failed — cannot evaluate self-conformance")

        ev = check_cc18(root_intent)
        assert ev.passed, f"[CC-18] {CRITERIA['CC-18'].test}\n  {ev}"

    @pytest.mark.core
    @pytest.mark.self_conformance
    def test_cc27_transition_log(self, root_intent):
        """CC-27: Transition log is complete and consistent."""
        ev = check_cc27(root_intent)
        assert ev.passed, f"[CC-27] {CRITERIA['CC-27'].test}\n  {ev}"
