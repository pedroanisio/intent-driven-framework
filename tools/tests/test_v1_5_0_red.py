"""
RED PHASE — v1.5.0 root + v1.7.0 criteria bridge forcing functions.

Two transitions, one RED phase:

  1. Root intent 1.4.0 → 1.5.0:
     Reframe domain-invariance from assertion to hypothesis.
     The feedback identified that the bootstrap proof used software-scoped
     criteria to validate a domain-invariant claim. Honest response:
     treat domain-invariance as a hypothesis under active testing, not
     an established fact.

  2. Criteria intent 1.6.1 → 1.7.0:
     Bridge the software-scoped criteria system to serve the domain-
     invariant root intent. The DIFF between 1.6.1 and 1.7.0 IS the
     theoretical/constraints bridge — empirical evidence of what
     domain-invariance costs.

These tests fail against v1.4.0 (root) and v1.6.1 (criteria).
When all pass, both transitions are complete.
"""

import pytest
from .helpers import deep_text_scan, any_text_contains


# ═══════════════════════════════════════════════════════════════════
#  ROOT INTENT v1.5.0 — hypothesis reframing
# ═══════════════════════════════════════════════════════════════════

class TestHypothesisReframing:
    """The root intent must reframe domain-invariance from an assertion
    ("the domain is a parameter") to a hypothesis under active testing
    ("we hypothesize domain-invariance and are building cases")."""

    @pytest.mark.core
    @pytest.mark.hypothesis
    def test_version_is_1_5_0(self, root_intent):
        """Version must be bumped to 1.5.0."""
        version = str(root_intent.get("version", ""))
        assert version == "1.5.0", (
            f"RED: version is {version}, expected 1.5.0. "
            "The hypothesis reframing requires a MINOR bump."
        )

    @pytest.mark.core
    @pytest.mark.hypothesis
    def test_declares_uses_hypothesis_language(self, root_intent):
        """The declares field must frame domain-invariance as hypothesis,
        not as established fact."""
        declares = root_intent.get("declares", "")
        has_hypothesis = any_text_contains(declares, "hypothesis")
        has_under_test = any_text_contains(declares, "under test") or any_text_contains(declares, "under active test")
        assert has_hypothesis or has_under_test, (
            "RED: declares still asserts domain-invariance as fact. "
            "The bootstrap used software-scoped criteria to validate a "
            "domain-invariant claim. Honest framing: domain-invariance "
            "is a hypothesis under active testing, not a proven property."
        )

    @pytest.mark.core
    @pytest.mark.hypothesis
    def test_domain_invariance_hypothesis_exists(self, root_intent):
        """A domain_invariance_hypothesis section must exist."""
        hyp = root_intent.get("domain_invariance_hypothesis")
        assert hyp is not None and isinstance(hyp, dict), (
            "RED: no domain_invariance_hypothesis section. "
            "The root intent must explicitly structure the domain-invariance "
            "claim as a testable hypothesis with cases."
        )

    @pytest.mark.core
    @pytest.mark.hypothesis
    def test_hypothesis_has_statement(self, root_intent):
        """The hypothesis must have an explicit statement."""
        hyp = root_intent.get("domain_invariance_hypothesis", {})
        statement = hyp.get("statement")
        assert statement and isinstance(statement, str) and len(statement) > 20, (
            "RED: domain_invariance_hypothesis has no statement. "
            "The hypothesis must be stated explicitly and falsifiably."
        )

    @pytest.mark.core
    @pytest.mark.hypothesis
    def test_hypothesis_has_status(self, root_intent):
        """The hypothesis must have a status field."""
        hyp = root_intent.get("domain_invariance_hypothesis", {})
        status = hyp.get("status", "")
        assert status, (
            "RED: domain_invariance_hypothesis has no status. "
            "Expected: under_test, supported, refuted, or similar."
        )

    @pytest.mark.core
    @pytest.mark.hypothesis
    def test_hypothesis_has_cases(self, root_intent):
        """The hypothesis must have a cases list."""
        hyp = root_intent.get("domain_invariance_hypothesis", {})
        cases = hyp.get("cases")
        assert cases and isinstance(cases, list) and len(cases) >= 2, (
            "RED: domain_invariance_hypothesis must have at least 2 cases: "
            "(1) self-application (the root intent governing itself) and "
            "(2) the criteria bridge (v1.6.1 → v1.7.0 adaptation)."
        )

    @pytest.mark.core
    @pytest.mark.hypothesis
    def test_hypothesis_case_self_application(self, root_intent):
        """Case 1: self-application — the root intent's own existence
        as a non-software application of the framework."""
        hyp = root_intent.get("domain_invariance_hypothesis", {})
        cases = hyp.get("cases", [])
        all_text = deep_text_scan(cases)
        has_self = any_text_contains(all_text, "self-application") or any_text_contains(all_text, "self-referential")
        assert has_self, (
            "RED: no self-application case in hypothesis. "
            "The root intent's own existence (governing prose/YAML/criteria, "
            "not software) is the first evidence case."
        )

    @pytest.mark.core
    @pytest.mark.hypothesis
    def test_hypothesis_case_criteria_bridge(self, root_intent):
        """Case 2: the criteria bridge — adapting v1.6.1 from software-
        scoped to domain-aware, with the diff as evidence."""
        hyp = root_intent.get("domain_invariance_hypothesis", {})
        cases = hyp.get("cases", [])
        all_text = deep_text_scan(cases)
        has_bridge = (
            any_text_contains(all_text, "criteria") or
            any_text_contains(all_text, "bridge") or
            any_text_contains(all_text, "1.7.0")
        )
        assert has_bridge, (
            "RED: no criteria bridge case in hypothesis. "
            "The v1.6.1 → v1.7.0 diff IS the empirical evidence — it shows "
            "what changes when a software-scoped document adapts to serve "
            "a domain-invariant framework."
        )

    @pytest.mark.core
    @pytest.mark.hypothesis
    def test_fc04_acknowledges_hypothesis(self, root_intent):
        """FC-04 (domain-invariance) must acknowledge the hypothesis
        framing rather than asserting invariance as established."""
        fcs = root_intent.get("falsifiable_claims", [])
        fc04 = next(
            (fc for fc in fcs if fc.get("id") == "FC-04"), None
        )
        assert fc04 is not None, "RED: FC-04 not found"
        all_text = deep_text_scan(fc04)
        has_hyp = (
            any_text_contains(all_text, "hypothesis") or
            any_text_contains(all_text, "under test")
        )
        assert has_hyp, (
            "RED: FC-04 still treats domain-invariance as a simple claim. "
            "It must acknowledge the hypothesis framing — the claim is "
            "under active testing, not merely asserted."
        )


class TestTransition1_5_0:
    """The 1.4.0 → 1.5.0 transition must be documented."""

    @pytest.mark.core
    @pytest.mark.self_conformance
    def test_transition_log_has_1_4_to_1_5(self, root_intent):
        """Transition log must document the 1.4.0 -> 1.5.0 change."""
        log = root_intent.get("transition_log", [])
        has_entry = any(
            str(e.get("from_version", "")) == "1.4.0" and
            str(e.get("to_version", "")) == "1.5.0"
            for e in log
        )
        assert has_entry, (
            "RED: transition_log has no 1.4.0 -> 1.5.0 entry. "
            "The hypothesis reframing must be documented as a transition."
        )

    @pytest.mark.core
    @pytest.mark.self_conformance
    def test_transition_cites_hypothesis_reframing(self, root_intent):
        """The 1.5.0 transition must cite the hypothesis reframing."""
        log = root_intent.get("transition_log", [])
        entry = next(
            (e for e in log
             if str(e.get("to_version", "")) == "1.5.0"),
            None,
        )
        if entry is None:
            pytest.skip("No 1.5.0 transition entry to check")
        all_text = deep_text_scan(entry)
        has_hyp = (
            any_text_contains(all_text, "hypothesis") or
            any_text_contains(all_text, "reframe")
        )
        assert has_hyp, (
            "RED: 1.5.0 transition does not cite hypothesis reframing. "
            "The forcing function is: domain-invariance was asserted using "
            "software-scoped criteria; honest response is to reframe as "
            "hypothesis under active testing."
        )


# ═══════════════════════════════════════════════════════════════════
#  CRITERIA INTENT v1.7.0 — bridge to domain-invariant root
# ═══════════════════════════════════════════════════════════════════

class TestCriteriaBridgeVersion:
    """The criteria intent (intent-manifesto-itself) must be bumped
    to v1.7.0 to bridge from its software-scoped origins to serve
    the domain-invariant root intent."""

    @pytest.mark.core
    @pytest.mark.bridge
    def test_criteria_version_is_1_7_0(self, criteria_intent):
        """Version must be bumped to 1.7.0."""
        version = str(criteria_intent.get("version", ""))
        assert version == "1.7.0", (
            f"RED: criteria intent version is {version}, expected 1.7.0. "
            "The bridge to domain-invariant root requires a MINOR bump."
        )

    @pytest.mark.core
    @pytest.mark.bridge
    def test_criteria_transition_1_6_1_to_1_7_0(self, criteria_intent):
        """Transition log must document the 1.6.1 -> 1.7.0 change."""
        log = criteria_intent.get("transition_log", [])
        has_entry = any(
            (str(e.get("from", "")) == "1.6.1" or
             str(e.get("from_version", "")) == "1.6.1") and
            (str(e.get("to", "")) == "1.7.0" or
             str(e.get("to_version", "")) == "1.7.0")
            for e in log
        )
        assert has_entry, (
            "RED: transition_log has no 1.6.1 -> 1.7.0 entry. "
            "The bridge adaptation must be documented as a transition."
        )


class TestCriteriaBridgeDeclares:
    """The criteria intent's declares must evolve beyond software-only
    scope to serve the domain-invariant root intent."""

    @pytest.mark.core
    @pytest.mark.bridge
    def test_criteria_declares_not_software_only(self, criteria_intent):
        """The declares field must not be scoped exclusively to software."""
        declares = criteria_intent.get("declares", "")
        # v1.6.1 says "intent-driven software development model"
        # v1.7.0 must broaden this
        is_software_only = (
            "software development" in declares.lower() and
            "domain" not in declares.lower() and
            "any domain" not in declares.lower()
        )
        assert not is_software_only, (
            "RED: criteria declares is still scoped exclusively to "
            "'intent-driven software development model'. The bridge "
            "must broaden scope to serve the domain-invariant root intent."
        )

    @pytest.mark.core
    @pytest.mark.bridge
    def test_criteria_declares_mentions_completeness(self, criteria_intent):
        """The declares must still identify itself as a completeness
        criteria system — its core purpose hasn't changed."""
        declares = criteria_intent.get("declares", "")
        has_completeness = any_text_contains(declares, "completeness") or any_text_contains(declares, "criteria")
        has_self_contained = any_text_contains(declares, "self-contained")
        assert has_completeness or has_self_contained, (
            "RED: criteria declares lost its identity as a completeness "
            "system. Broadening scope should not erase core purpose."
        )


class TestCriteriaBridgeRelationship:
    """The criteria intent must declare its relationship to the root
    intent — the FC-02 violation identified by the reviewer."""

    @pytest.mark.core
    @pytest.mark.bridge
    def test_criteria_serves_root_intent(self, criteria_intent):
        """The criteria intent must have a serves reference to the root."""
        serves = criteria_intent.get("serves", [])
        # Accept either a list with the root id or a string
        if isinstance(serves, str):
            serves = [serves]
        all_text = deep_text_scan(serves)
        has_root_ref = (
            any_text_contains(all_text, "intent-driven-framework-definition") or
            any_text_contains(all_text, "root intent") or
            any_text_contains(all_text, "root")
        )
        assert has_root_ref, (
            "RED: criteria intent has no serves reference to the root intent. "
            "The reviewer identified this as an FC-02 violation: two governance "
            "documents for the same framework with no declared relationship."
        )


class TestCriteriaBridgeScope:
    """The criteria intent's scope must reflect the current file
    structure, not the original layout."""

    @pytest.mark.core
    @pytest.mark.bridge
    def test_criteria_scope_updated(self, criteria_intent):
        """Scope must reference current file paths, not legacy ones."""
        scope = criteria_intent.get("scope", {})
        primary = scope.get("primary", [])
        all_text = deep_text_scan(primary)
        # v1.6.1 scope.primary references: intent-manifesto.md, intent-spec.md
        # v1.7.0 should reference the current file structure
        has_prose_path = any_text_contains(all_text, "prose/")
        has_old_path = (
            "intent-manifesto.md" in str(primary) and
            "prose/" not in str(primary)
        )
        assert has_prose_path or not has_old_path, (
            "RED: criteria scope still references legacy file paths "
            "(intent-manifesto.md, intent-spec.md without prose/ prefix). "
            "Scope must reflect the current repository structure."
        )


class TestCriteriaBridgeVocabulary:
    """The change_type vocabulary divergence identified by the reviewer
    must be addressed in the bridge."""

    @pytest.mark.core
    @pytest.mark.bridge
    def test_criteria_change_type_reconciled(self, criteria_intent):
        """The criteria must acknowledge or reconcile the change_type
        vocabulary with the root intent's MAJOR/MINOR/PATCH."""
        # Check transition log for semver-aligned vocabulary
        log = criteria_intent.get("transition_log", [])
        entry_1_7 = next(
            (e for e in log
             if str(e.get("to", "")) == "1.7.0" or
                str(e.get("to_version", "")) == "1.7.0"),
            None,
        )
        if entry_1_7 is None:
            pytest.fail(
                "RED: no 1.7.0 transition entry to check vocabulary reconciliation."
            )

        # The 1.7.0 transition itself should use reconciled vocabulary
        # or the intent text should acknowledge the mapping
        all_text = deep_text_scan(criteria_intent)
        has_semver_mention = (
            any_text_contains(all_text, "MAJOR") or
            any_text_contains(all_text, "MINOR") or
            any_text_contains(all_text, "semver")
        )
        assert has_semver_mention, (
            "RED: criteria intent does not acknowledge semver vocabulary. "
            "The reviewer identified incompatible governance vocabularies: "
            "this file uses clarification|correction|extension while the "
            "root intent uses MAJOR|MINOR|PATCH. The bridge must reconcile."
        )


class TestCriteriaBridgeTransitionContent:
    """The 1.7.0 transition entry must document the bridge purpose."""

    @pytest.mark.core
    @pytest.mark.bridge
    def test_criteria_transition_cites_bridge(self, criteria_intent):
        """The 1.7.0 transition must cite the domain-invariance bridge
        as its forcing function."""
        log = criteria_intent.get("transition_log", [])
        entry = next(
            (e for e in log
             if str(e.get("to", "")) == "1.7.0" or
                str(e.get("to_version", "")) == "1.7.0"),
            None,
        )
        if entry is None:
            pytest.skip("No 1.7.0 transition entry to check")
        all_text = deep_text_scan(entry)
        has_bridge = (
            any_text_contains(all_text, "bridge") or
            any_text_contains(all_text, "domain-invariant") or
            any_text_contains(all_text, "root intent")
        )
        assert has_bridge, (
            "RED: 1.7.0 transition does not cite the domain-invariance "
            "bridge as its purpose. The diff from v1.6.1 IS the evidence "
            "— it must explain what changed and why."
        )
