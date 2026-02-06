"""
RED PHASE — v1.4.0 transition forcing functions.

These tests define what the root intent MUST satisfy to absorb the
findings from the external critical review. Each test is a forcing
function: it fails against v1.3.0, creating the mandate to expand
the YAML. When all pass, the transition is complete.

Forcing functions derived from:
  - "The Intent Driven Framework: A Critical Review of Ambition,
     Novelty, and Structural Limits" (external review)
  - Three-document analysis (review + YAML + Lean)

The framework's own operational cycle (OC-01) says: no work without
a declared unsatisfied intent. These tests ARE the red intents.
"""

import re
import pytest
from .helpers import get_nested, deep_text_scan, any_text_contains


# ═══════════════════════════════════════════════════════════════════
#  INTELLECTUAL LINEAGE — the framework must cite its ancestors
# ═══════════════════════════════════════════════════════════════════

class TestIntellectualLineage:
    """The critical review identified 30+ years of prior art that the
    framework does not cite. Failing to engage this lineage makes the
    framework appear either ignorant or dishonest."""

    @pytest.mark.core
    def test_lineage_section_exists(self, root_intent):
        """The root intent must have an intellectual_lineage field."""
        lineage = root_intent.get("intellectual_lineage")
        assert lineage is not None and isinstance(lineage, list), (
            "RED: root intent has no intellectual_lineage section. "
            "The critical review identified GORE/KAOS, Polarity Management, "
            "Paradox Theory, design rationale capture, PDCA, and ADRs as "
            "unacknowledged ancestors."
        )

    @pytest.mark.core
    def test_lineage_cites_gore_kaos(self, root_intent):
        """GORE/KAOS is the most significant prior art — must be cited."""
        lineage = root_intent.get("intellectual_lineage", [])
        all_text = deep_text_scan(lineage)
        assert any_text_contains(all_text, "KAOS") or any_text_contains(all_text, "GORE"), (
            "RED: intellectual_lineage does not cite GORE/KAOS. "
            "Van Lamsweerde (~1990) and Yu's i* (~1995) anticipated "
            "the IDF's claims 1, 2, 5, and partly 6."
        )

    @pytest.mark.core
    def test_lineage_cites_polarity_or_paradox(self, root_intent):
        """Tension management prior art — Polarity Management or Paradox Theory."""
        lineage = root_intent.get("intellectual_lineage", [])
        all_text = deep_text_scan(lineage)
        has_polarity = any_text_contains(all_text, "Polarity Management") or any_text_contains(all_text, "Johnson")
        has_paradox = any_text_contains(all_text, "Paradox") or any_text_contains(all_text, "Smith") and any_text_contains(all_text, "Lewis")
        assert has_polarity or has_paradox, (
            "RED: intellectual_lineage does not cite Polarity Management "
            "(Johnson 1975) or Paradox Theory (Smith & Lewis). "
            "50+ years of tension management research is unacknowledged."
        )

    @pytest.mark.core
    def test_lineage_cites_design_rationale(self, root_intent):
        """Design rationale capture (IBIS, QOC, DRL) addresses the same problem."""
        lineage = root_intent.get("intellectual_lineage", [])
        all_text = deep_text_scan(lineage)
        assert any_text_contains(all_text, "IBIS") or any_text_contains(all_text, "design rationale"), (
            "RED: intellectual_lineage does not cite design rationale "
            "capture (Rittel's IBIS 1970s, QOC, DRL). These systems "
            "tried to solve the same problem and their failure modes "
            "(capture tax) are directly relevant."
        )

    @pytest.mark.core
    def test_lineage_cites_alternative_cycles(self, root_intent):
        """PDCA, OODA, or double-loop learning as alternative structural foundations."""
        lineage = root_intent.get("intellectual_lineage", [])
        all_text = deep_text_scan(lineage)
        has_pdca = any_text_contains(all_text, "PDCA")
        has_double_loop = any_text_contains(all_text, "double-loop") or any_text_contains(all_text, "Argyris")
        has_ooda = any_text_contains(all_text, "OODA")
        assert has_pdca or has_double_loop or has_ooda, (
            "RED: intellectual_lineage does not engage with PDCA, OODA, "
            "or double-loop learning as alternative governance cycles. "
            "These are arguably more structurally appropriate than TDD "
            "for organizational contexts."
        )

    @pytest.mark.core
    def test_lineage_cites_adrs(self, root_intent):
        """ADRs are the simpler alternative the framework must differentiate from."""
        lineage = root_intent.get("intellectual_lineage", [])
        all_text = deep_text_scan(lineage)
        assert any_text_contains(all_text, "ADR") or any_text_contains(all_text, "Architectural Decision Record"), (
            "RED: intellectual_lineage does not cite ADRs (Nygard 2011). "
            "ADRs succeeded through radical simplicity. The IDF must "
            "explain what it adds that justifies the additional ceremony."
        )

    @pytest.mark.core
    def test_lineage_entries_have_what_idf_adds(self, root_intent):
        """Each lineage entry must explain what the IDF adds beyond prior art."""
        lineage = root_intent.get("intellectual_lineage", [])
        if not lineage:
            pytest.skip("No intellectual_lineage to check")
        missing = []
        for entry in lineage:
            tradition = entry.get("tradition", "?")
            if not entry.get("what_idf_adds"):
                missing.append(tradition)
        assert not missing, (
            f"RED: lineage entries missing what_idf_adds: {missing}. "
            "Each cited tradition must explain what the IDF contributes "
            "beyond what already exists."
        )


# ═══════════════════════════════════════════════════════════════════
#  GOODHART'S LAW — measurability creates gaming risk
# ═══════════════════════════════════════════════════════════════════

class TestGoodhartTension:
    """The critical review identified that formalizing intent into
    measurable, falsifiable conditions creates exactly the conditions
    Goodhart's Law predicts will be gamed."""

    @pytest.mark.core
    @pytest.mark.operational
    def test_goodhart_tension_exists(self, root_intent):
        """A tension addressing Goodhart's Law / metric corruption must exist."""
        tensions = root_intent.get("tensions", [])
        all_text = deep_text_scan(tensions)
        has_goodhart = any_text_contains(all_text, "Goodhart") or any_text_contains(all_text, "gaming")
        has_metric = any_text_contains(all_text, "metric corruption") or any_text_contains(all_text, "measure becomes a target")
        assert has_goodhart or has_metric, (
            "RED: no tension addresses Goodhart's Law. Once intent is "
            "formalized into measurable conditions, those conditions "
            "become targets susceptible to gaming. Campbell's Law states "
            "this even more forcefully. The framework needs a theory of "
            "metric corruption, not just metric definition."
        )

    @pytest.mark.core
    @pytest.mark.operational
    def test_goodhart_failure_mode_exists(self, root_intent):
        """A failure mode for metric gaming / Goodhart corruption must exist."""
        fms = root_intent.get("failure_modes", [])
        all_text = deep_text_scan(fms)
        has_gaming = any_text_contains(all_text, "gaming") or any_text_contains(all_text, "Goodhart")
        has_corruption = any_text_contains(all_text, "metric corruption") or any_text_contains(all_text, "corrupted measure")
        assert has_gaming or has_corruption, (
            "RED: no failure mode addresses metric gaming. FM-01 through "
            "FM-06 cover performative intent and green-washing but not "
            "the deeper problem: teams optimizing for the measurable "
            "conditions rather than the actual intent."
        )


# ═══════════════════════════════════════════════════════════════════
#  ALTERNATIVE CYCLES — TDD is not the only structural foundation
# ═══════════════════════════════════════════════════════════════════

class TestAlternativeCycles:
    """The critical review argued that PDCA, OODA, and double-loop
    learning are more structurally appropriate than TDD for governance.
    The framework must engage with these alternatives explicitly."""

    @pytest.mark.core
    @pytest.mark.operational
    def test_alternative_cycles_considered(self, root_intent):
        """The operational_cycle must acknowledge alternative governance cycles."""
        oc = root_intent.get("operational_cycle", {})
        all_text = deep_text_scan(oc)
        has_pdca = any_text_contains(all_text, "PDCA")
        has_double_loop = any_text_contains(all_text, "double-loop") or any_text_contains(all_text, "Argyris")
        assert has_pdca or has_double_loop, (
            "RED: operational_cycle does not consider PDCA or double-loop "
            "learning as alternative structural foundations. The divergence_"
            "from_tdd section documents HOW the TDD analogy breaks down "
            "but does not consider WHETHER a different cycle would be better."
        )

    @pytest.mark.core
    @pytest.mark.operational
    def test_cycle_commitment_is_to_discipline_not_label(self, root_intent):
        """The framework must explicitly state it can be reframed away from TDD."""
        oc = root_intent.get("operational_cycle", {})
        all_text = deep_text_scan(oc)
        # Must explicitly acknowledge reframability — not just use "constraint" language
        has_reframe = any_text_contains(all_text, "reframe") or any_text_contains(all_text, "not the TDD label")
        has_alternative = any_text_contains(all_text, "PDCA") or any_text_contains(all_text, "double-loop")
        assert has_reframe or has_alternative, (
            "RED: operational_cycle does not state that the cycle can be "
            "reframed away from TDD if the adoption bridge value proves "
            "smaller than the structural mismatch cost. The commitment "
            "must be to the discipline, not the label."
        )


# ═══════════════════════════════════════════════════════════════════
#  TRANSITION — the version bump must be documented
# ═══════════════════════════════════════════════════════════════════

class TestTransition1_4_0:
    """The transition from 1.3.0 to 1.4.0 must be documented with
    the external critical review as the forcing function."""

    @pytest.mark.core
    @pytest.mark.self_conformance
    def test_version_is_1_4_0(self, root_intent):
        """Version must be at least 1.4.0 (forcing function satisfied)."""
        version = str(root_intent.get("version", ""))
        parts = [int(x) for x in version.split(".")]
        assert parts >= [1, 4, 0], (
            f"RED: version is {version}, expected >= 1.4.0. "
            "The external critical review created forcing functions "
            "that require a MINOR bump."
        )

    @pytest.mark.core
    @pytest.mark.self_conformance
    def test_transition_log_has_1_3_to_1_4(self, root_intent):
        """Transition log must document the 1.3.0 -> 1.4.0 change."""
        log = root_intent.get("transition_log", [])
        has_entry = any(
            str(e.get("from_version", "")) == "1.3.0" and
            str(e.get("to_version", "")) == "1.4.0"
            for e in log
        )
        assert has_entry, (
            "RED: transition_log has no 1.3.0 -> 1.4.0 entry. "
            "The transition must document the external critical review "
            "as the forcing function and list what changed."
        )

    @pytest.mark.core
    @pytest.mark.self_conformance
    def test_transition_cites_external_review(self, root_intent):
        """The 1.4.0 transition must cite the external review as forcing function."""
        log = root_intent.get("transition_log", [])
        entry = next(
            (e for e in log
             if str(e.get("to_version", "")) == "1.4.0"),
            None,
        )
        if entry is None:
            pytest.skip("No 1.4.0 transition entry to check")
        all_text = deep_text_scan(entry)
        has_review = any_text_contains(all_text, "critical review") or any_text_contains(all_text, "external review")
        assert has_review, (
            "RED: 1.4.0 transition does not cite the external critical "
            "review as its forcing function. OC-01 says no work without "
            "a declared unsatisfied intent — the review IS the red state."
        )
