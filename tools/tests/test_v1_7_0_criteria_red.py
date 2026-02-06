"""
RED PHASE — v1.7.0 SDLC criteria intent self-conformance forcing functions.

The SDLC criteria intent (intent-idf-sdlc-v1.7.0.yml) defines 28
completeness criteria and claims a five-layer verification stack.
CC-18 says: "This intent block conforms to the model it specifies."

This is the SDLC track — parallel to but separate from the IDF track.
The IDF root intent (intent-driven-framework-definition.yml) has its
own test files. These two intents relate via `serves`.

Tests check TWO things:
  1. STRUCTURAL: Does the SDLC criteria YAML have valid fields? (GREEN)
  2. SCOPE/LAYERS: Do the governed artifacts and verification layers
     actually exist and cover v1.7.0? (RED — some missing)

The RED tests create forcing functions for the GREEN phase, which will
build: prose/intent-spec-core.md and extend Lean 4 proofs to v1.7.0.
"""

import pytest
from pathlib import Path
from .helpers import (
    has_key, get_nested, deep_text_scan, any_text_contains,
    text_contains, collect_ids, count_items,
)
from .conftest import REPO_ROOT


# ═══════════════════════════════════════════════════════════════════
#  STRUCTURAL COMPLETENESS — required fields for an aspirational intent
# ═══════════════════════════════════════════════════════════════════

class TestCriteriaStructuralCompleteness:
    """CC-04/CC-08: The criteria intent is aspirational. It must have
    all fields required by the aspirational intent schema it defines."""

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_has_id(self, criteria_intent):
        """Required field: id."""
        assert criteria_intent.get("id"), "RED: criteria intent missing id"

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_has_version(self, criteria_intent):
        """Required field: version."""
        assert criteria_intent.get("version"), "RED: criteria intent missing version"

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_has_schema_version(self, criteria_intent):
        """Required field: schema_version (CC-24 self-conformance)."""
        assert criteria_intent.get("schema_version"), (
            "RED: criteria intent missing schema_version"
        )

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_has_declares(self, criteria_intent):
        """Required field: declares."""
        declares = criteria_intent.get("declares", "")
        assert declares and len(declares.strip()) > 20, (
            "RED: criteria intent has no substantial declares field"
        )

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_has_intent_type(self, criteria_intent):
        """Required field: intent_type must be aspirational or achieved."""
        it = criteria_intent.get("intent_type", "")
        assert it in ("aspirational", "achieved"), (
            f"RED: intent_type is '{it}', expected aspirational or achieved"
        )

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_has_current_reality(self, criteria_intent):
        """CC-08: Aspirational intents require current_reality block."""
        cr = criteria_intent.get("current_reality")
        assert cr and isinstance(cr, dict), (
            "RED: aspirational criteria intent missing current_reality block"
        )

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_current_reality_has_state(self, criteria_intent):
        """current_reality.state must be present and non-empty."""
        state = get_nested(criteria_intent, "current_reality", "state")
        assert state and isinstance(state, str) and len(state.strip()) > 10, (
            "RED: current_reality.state is missing or trivial"
        )

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_current_reality_has_status(self, criteria_intent):
        """current_reality.status must be present and non-empty."""
        status = get_nested(criteria_intent, "current_reality", "status")
        assert status and isinstance(status, str) and len(status.strip()) > 10, (
            "RED: current_reality.status is missing or trivial"
        )

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_has_scope_primary(self, criteria_intent):
        """Required field: scope.primary."""
        primary = get_nested(criteria_intent, "scope", "primary")
        assert primary and isinstance(primary, list) and len(primary) > 0, (
            "RED: criteria intent missing scope.primary"
        )

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_has_status_field(self, criteria_intent):
        """Required field: status (lifecycle per CC-07)."""
        status = criteria_intent.get("status", "")
        valid = {"proposed", "active", "evolving", "superseded", "residual", "retracted"}
        assert status in valid, (
            f"RED: status is '{status}', must be one of {valid}"
        )

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_has_priority(self, criteria_intent):
        """Required field: priority."""
        priority = criteria_intent.get("priority", "")
        valid = {"critical", "high", "medium", "low"}
        assert priority in valid, (
            f"RED: priority is '{priority}', must be one of {valid}"
        )

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_has_confidence(self, criteria_intent):
        """Required field: confidence."""
        conf = criteria_intent.get("confidence", "")
        valid = {"high", "medium", "low"}
        assert conf in valid, (
            f"RED: confidence is '{conf}', must be one of {valid}"
        )

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_has_origin(self, criteria_intent):
        """Required field: origin with type and relationship."""
        origin = criteria_intent.get("origin")
        assert origin and isinstance(origin, dict), (
            "RED: criteria intent missing origin"
        )
        assert origin.get("type"), "RED: origin missing type"
        assert origin.get("relationship"), "RED: origin missing relationship"


# ═══════════════════════════════════════════════════════════════════
#  CC-05 — enum closedness on the criteria intent itself
# ═══════════════════════════════════════════════════════════════════

class TestCriteriaEnumClosedness:
    """CC-05: Every enum field must use values from the canonical set.
    The criteria intent defines canonical enums — it must use them."""

    VALID_CHANGE_TYPES = {
        "clarification", "correction", "extension",
        "reclassification", "breaking", "deprecation",
    }

    VALID_ORIGIN_TYPES = {
        "engineering", "product", "incident", "discovery",
        "regulatory", "organizational", "devops", "ux",
        "data", "sre", "security",
    }

    VALID_ORIGIN_RELATIONSHIPS = {
        "derived_from", "motivated_by", "constrained_by",
        "triggered_by", "discovered_in",
    }

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_transition_log_change_types_valid(self, criteria_intent):
        """Every change_type in transition_log must be from canonical enum."""
        log = criteria_intent.get("transition_log", [])
        invalid = []
        for entry in log:
            ct = entry.get("change_type", "")
            if ct not in self.VALID_CHANGE_TYPES:
                invalid.append(f"{entry.get('from','?')}→{entry.get('to','?')}: {ct}")
        assert not invalid, (
            f"RED: transition_log has invalid change_type values: {invalid}"
        )

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_origin_type_valid(self, criteria_intent):
        """origin.type must be from canonical origin_type enum."""
        ot = get_nested(criteria_intent, "origin", "type", default="")
        assert ot in self.VALID_ORIGIN_TYPES, (
            f"RED: origin.type is '{ot}', not in canonical origin_type enum"
        )

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_origin_relationship_valid(self, criteria_intent):
        """origin.relationship must be from canonical enum."""
        rel = get_nested(criteria_intent, "origin", "relationship", default="")
        assert rel in self.VALID_ORIGIN_RELATIONSHIPS, (
            f"RED: origin.relationship is '{rel}', not in canonical enum"
        )


# ═══════════════════════════════════════════════════════════════════
#  CC-27 — transition log integrity
# ═══════════════════════════════════════════════════════════════════

class TestCriteriaTransitionLogIntegrity:
    """CC-27: The transition log must be complete and consistent.
    Every version bump from 1.0.0 to 1.7.0 must have a log entry."""

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_transition_log_exists(self, criteria_intent):
        """transition_log must exist and be non-empty."""
        log = criteria_intent.get("transition_log")
        assert log and isinstance(log, list) and len(log) > 0, (
            "RED: criteria intent has no transition_log"
        )

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_transition_log_no_gaps(self, criteria_intent):
        """CC-27(a): No gaps in the (from, to) chain from 1.0.0 to current."""
        version = str(criteria_intent.get("version", ""))
        log = criteria_intent.get("transition_log", [])
        pairs = []
        for entry in log:
            f = str(entry.get("from", entry.get("from_version", "")))
            t = str(entry.get("to", entry.get("to_version", "")))
            pairs.append((f, t))
        if not pairs:
            pytest.fail("RED: empty transition_log")
        assert pairs[0][0] == "1.0.0", (
            f"RED: transition_log starts at {pairs[0][0]}, expected 1.0.0"
        )
        for i in range(1, len(pairs)):
            assert pairs[i][0] == pairs[i-1][1], (
                f"RED: gap in transition_log: {pairs[i-1][1]} → {pairs[i][0]}"
            )
        assert pairs[-1][1] == version, (
            f"RED: transition_log ends at {pairs[-1][1]}, current version is {version}"
        )

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_transition_log_entries_have_summaries(self, criteria_intent):
        """CC-27(b): Every entry has a non-trivial summary."""
        log = criteria_intent.get("transition_log", [])
        missing = []
        for entry in log:
            summary = entry.get("summary", "")
            if not summary or len(str(summary).strip()) < 20:
                f = entry.get("from", entry.get("from_version", "?"))
                t = entry.get("to", entry.get("to_version", "?"))
                missing.append(f"{f}→{t}")
        assert not missing, (
            f"RED: transition_log entries with missing/trivial summaries: {missing}"
        )


# ═══════════════════════════════════════════════════════════════════
#  CC-19 — declares quality
# ═══════════════════════════════════════════════════════════════════

class TestCriteriaDeclaresQuality:
    """CC-19: The declares field must be specific and falsifiable.
    If no change could violate it, it is not an intent."""

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_declares_is_falsifiable(self, criteria_intent):
        """The declares must contain a commitment that could be violated."""
        declares = criteria_intent.get("declares", "")
        has_commitment = any_text_contains(
            declares, "must", "defines", "ensures", "requires",
        )
        assert has_commitment, (
            "RED: criteria intent declares lacks commitment language. "
            "CC-19 requires falsifiable declarations — if no code change "
            "could violate it, it is not an intent."
        )

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_declares_identifies_scope(self, criteria_intent):
        """The declares must identify what it governs."""
        declares = criteria_intent.get("declares", "")
        has_scope = any_text_contains(declares, "criteria", "completeness", "checkpoint")
        assert has_scope, (
            "RED: criteria intent declares doesn't identify its governing scope. "
            "It should state what it IS (a completeness criteria system)."
        )


# ═══════════════════════════════════════════════════════════════════
#  SCOPE VALIDITY — governed artifacts must exist on disk
# ═══════════════════════════════════════════════════════════════════

class TestCriteriaScopeValidity:
    """CC-18(b): scope covers all artifacts referenced by CC-* criteria.
    The scope.primary and scope.implicit paths must resolve to real
    files/directories in the repository."""

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_scope_primary_prose_manifesto_exists(self, criteria_intent):
        """scope.primary: prose/intent-manifesto.md must exist."""
        path = REPO_ROOT / "prose" / "intent-manifesto.md"
        assert path.exists(), (
            f"RED: scope.primary references prose/intent-manifesto.md "
            f"but {path} does not exist"
        )

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_scope_primary_prose_spec_exists(self, criteria_intent):
        """scope.primary: prose/intent-spec-core.md must exist.
        The criteria system governs the universal data model spec."""
        path = REPO_ROOT / "prose" / "intent-spec-core.md"
        assert path.exists(), (
            f"RED: scope.primary references prose/intent-spec-core.md "
            f"but {path} does not exist. The criteria system claims to "
            f"govern a universal data model specification that has not "
            f"been written yet."
        )

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_scope_primary_root_intent_exists(self, criteria_intent):
        """scope.primary: criteria/intent-driven-framework-definition.yml must exist."""
        path = REPO_ROOT / "criteria" / "intent-driven-framework-definition.yml"
        assert path.exists(), (
            f"RED: scope.primary references the root intent YAML "
            f"but {path} does not exist"
        )

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_scope_implicit_schema_validator_exists(self):
        """scope.implicit: schemas/ refers to the Zod schema validator.
        CC-04 through CC-08 are validated by tools/schema.js."""
        path = REPO_ROOT / "tools" / "schema.js"
        assert path.exists(), (
            f"RED: scope.implicit references schemas/ (CC-04 through CC-08) "
            f"but the schema validator {path} does not exist."
        )

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_scope_implicit_tools_exists(self, criteria_intent):
        """scope.implicit: tools/ directory must exist (CC-20 tooling surface)."""
        path = REPO_ROOT / "tools"
        assert path.exists() and path.is_dir(), (
            f"RED: scope.implicit references tools/ but {path} does not exist"
        )

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_scope_implicit_lean_exists(self, criteria_intent):
        """scope.implicit: lean/ directory must exist (formal verification layer)."""
        path = REPO_ROOT / "lean"
        assert path.exists() and path.is_dir(), (
            f"RED: scope.implicit references lean/ but {path} does not exist"
        )


# ═══════════════════════════════════════════════════════════════════
#  LEAN 4 LAYER — proofs must cover v1.7.0
# ═══════════════════════════════════════════════════════════════════

class TestCriteriaLean4Layer:
    """The Lean 4 formalization covers CC-05, CC-07, CC-23, CC-27 for
    the criteria intent. But the proofs are stuck at v1.6.1 — the
    v161_log ends at (.v 1 6 1). The v1.7.0 transition must be
    added to the Lean proofs."""

    @pytest.mark.core
    @pytest.mark.criteria_self
    @pytest.mark.cross_layer
    def test_lean_has_criteria_transition_log(self, lean_text):
        """Lean file must have a transition log for the criteria intent."""
        assert "v161_log" in lean_text or "criteria_log" in lean_text, (
            "RED: Lean file has no transition log for the criteria intent"
        )

    @pytest.mark.core
    @pytest.mark.criteria_self
    @pytest.mark.cross_layer
    def test_lean_criteria_log_covers_v1_7_0(self, lean_text):
        """Lean transition log must end at v1.7.0, not v1.6.1.
        The v1.6.1→v1.7.0 bridge transition must be proven."""
        # The current Lean file has v161_log ending at (.v 1 6 1)
        # It needs to be extended to (.v 1 7 0)
        has_v170 = "1 7 0" in lean_text or "v 1 7 0" in lean_text
        assert has_v170, (
            "RED: Lean proofs end at v1.6.1. The v1.7.0 bridge transition "
            "(1.6.1→1.7.0) must be added to the Lean transition log and "
            "proven contiguous. The current v161_log needs a 10th entry."
        )

    @pytest.mark.core
    @pytest.mark.criteria_self
    @pytest.mark.cross_layer
    def test_lean_criteria_version_sync(self, lean_text, criteria_intent):
        """Lean intent version must match YAML version."""
        yaml_version = str(criteria_intent.get("version", ""))
        # Lean encodes version as (.v major minor patch)
        parts = yaml_version.split(".")
        lean_version_str = f"version := .v {parts[0]} {parts[1]} {parts[2]}"
        assert lean_version_str in lean_text, (
            f"RED: Lean criteria intent version does not match YAML {yaml_version}. "
            f"Expected '{lean_version_str}' in Lean file."
        )


# ═══════════════════════════════════════════════════════════════════
#  SCHEMA LAYER — Zod must validate the criteria YAML
# ═══════════════════════════════════════════════════════════════════

class TestCriteriaSchemaLayer:
    """CC-20: The tooling surface must validate the criteria YAML.
    The schema.js defines Zod schemas — they must parse the criteria
    intent without errors."""

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_schema_js_exists(self):
        """schema.js must exist for Zod validation."""
        path = REPO_ROOT / "tools" / "schema.js"
        assert path.exists(), (
            "RED: tools/schema.js does not exist — no Zod schema layer"
        )

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_schema_handles_completeness_criteria(self, schema_js_text):
        """schema.js must define a schema for completeness_criteria."""
        assert "completeness_criteria" in schema_js_text, (
            "RED: schema.js has no completeness_criteria schema. "
            "The Zod layer must validate the criteria YAML structure."
        )

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_schema_validates_criteria_intent(self, schema_js_text):
        """schema.js structural checks must reference the criteria intent.
        validate.js should be able to validate the criteria YAML."""
        validate_path = REPO_ROOT / "tools" / "validate.js"
        assert validate_path.exists(), (
            "RED: tools/validate.js does not exist — no validation runner"
        )


# ═══════════════════════════════════════════════════════════════════
#  STORE LAYER — flaw tracking must exist
# ═══════════════════════════════════════════════════════════════════

class TestCriteriaStoreLayer:
    """The current_reality claims: 'A Zustand flaw store tracks
    regressions across validation runs.' This must be real."""

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_store_js_exists(self):
        """store.js must exist for flaw tracking."""
        path = REPO_ROOT / "tools" / "store.js"
        assert path.exists(), (
            "RED: tools/store.js does not exist — no flaw store. "
            "The current_reality claims a Zustand flaw store exists."
        )

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_store_references_flaw_tracking(self):
        """store.js must implement flaw tracking."""
        path = REPO_ROOT / "tools" / "store.js"
        if not path.exists():
            pytest.skip("store.js does not exist")
        text = path.read_text(encoding="utf-8")
        has_flaw = "flaw" in text.lower() or "Flaw" in text
        assert has_flaw, (
            "RED: store.js exists but does not reference flaw tracking. "
            "The current_reality claims flaw regression tracking."
        )


# ═══════════════════════════════════════════════════════════════════
#  COMPLETENESS CRITERIA COVERAGE — all 28 CC present
# ═══════════════════════════════════════════════════════════════════

class TestCriteriaCoverage:
    """The criteria YAML defines 28 CC. All must be present, structured,
    and categorized."""

    EXPECTED_CC = {
        "CC-01", "CC-02", "CC-03",                                  # philosophy
        "CC-04", "CC-05", "CC-06", "CC-07", "CC-08",               # model
        "CC-08a", "CC-08b", "CC-08c",                               # conflict
        "CC-09", "CC-10",                                           # structure
        "CC-11", "CC-12",                                           # extensibility
        "CC-13", "CC-14", "CC-15",                                  # adoption
        "CC-16", "CC-17",                                           # self-sufficiency
        "CC-18",                                                    # self-conformance
        "CC-19", "CC-20", "CC-21", "CC-23", "CC-25", "CC-26", "CC-27",  # operational
        "CC-22", "CC-24",                                           # deferred
    }

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_completeness_criteria_section_exists(self, criteria_intent):
        """completeness_criteria must exist as a structured section."""
        cc = criteria_intent.get("completeness_criteria")
        assert cc and isinstance(cc, dict), (
            "RED: criteria intent missing completeness_criteria section"
        )

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_all_28_cc_present(self, criteria_intent):
        """All 28 CC (CC-01 through CC-27 plus CC-08a/b/c, CC-22, CC-24) present."""
        cc = criteria_intent.get("completeness_criteria", {})
        all_ids = set()
        for category_items in cc.values():
            if isinstance(category_items, list):
                for item in category_items:
                    if isinstance(item, dict) and "id" in item:
                        all_ids.add(item["id"])
        missing = self.EXPECTED_CC - all_ids
        assert not missing, (
            f"RED: completeness_criteria missing CC IDs: {sorted(missing)}"
        )

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_no_unexpected_cc(self, criteria_intent):
        """No phantom CC IDs beyond the defined set (anti-hallucination)."""
        cc = criteria_intent.get("completeness_criteria", {})
        all_ids = set()
        for category_items in cc.values():
            if isinstance(category_items, list):
                for item in category_items:
                    if isinstance(item, dict) and "id" in item:
                        all_ids.add(item["id"])
        unexpected = all_ids - self.EXPECTED_CC
        assert not unexpected, (
            f"RED: unexpected CC IDs found: {sorted(unexpected)}. "
            "Adding criteria requires a transition_log entry."
        )

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_every_cc_has_test_field(self, criteria_intent):
        """Every CC must have a 'test' field describing what it checks."""
        cc = criteria_intent.get("completeness_criteria", {})
        missing = []
        for category, items in cc.items():
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict) and not item.get("test"):
                        missing.append(item.get("id", f"unknown in {category}"))
        assert not missing, (
            f"RED: CC entries missing 'test' field: {missing}"
        )

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_every_cc_has_verifiable_by(self, criteria_intent):
        """Every CC must have a 'verifiable_by' field."""
        cc = criteria_intent.get("completeness_criteria", {})
        missing = []
        for category, items in cc.items():
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict) and not item.get("verifiable_by"):
                        missing.append(item.get("id", f"unknown in {category}"))
        assert not missing, (
            f"RED: CC entries missing 'verifiable_by' field: {missing}"
        )

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_every_cc_has_tier(self, criteria_intent):
        """Every CC must have a 'tier' field (core or deferred)."""
        cc = criteria_intent.get("completeness_criteria", {})
        missing = []
        for category, items in cc.items():
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        tier = item.get("tier", "")
                        if tier not in ("core", "deferred"):
                            missing.append(
                                f"{item.get('id', '?')}: tier='{tier}'"
                            )
        assert not missing, (
            f"RED: CC entries with invalid/missing tier: {missing}"
        )

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_deferred_cc_have_promote_when(self, criteria_intent):
        """Deferred CC must have a promote_when field."""
        cc = criteria_intent.get("completeness_criteria", {})
        missing = []
        for category, items in cc.items():
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict) and item.get("tier") == "deferred":
                        if not item.get("promote_when"):
                            missing.append(item.get("id", "?"))
        assert not missing, (
            f"RED: deferred CC missing promote_when: {missing}"
        )


# ═══════════════════════════════════════════════════════════════════
#  CC-18 RECURSIVE — the criteria intent must pass its own CC-18
# ═══════════════════════════════════════════════════════════════════

class TestCriteriaSelfConformanceRecursive:
    """CC-18 applied recursively: the criteria intent defines CC-18 and
    must satisfy CC-18 itself. This is the bootstrap test."""

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_cc18_self_conformance_recursive(self, criteria_intent):
        """The criteria intent passes its own CC-18 check:
        (a) current_reality is present and non-empty,
        (b) scope covers artifacts referenced by CC-*,
        (c) all required fields per schema are populated,
        (d) schema_version is present."""
        # (a) current_reality
        cr = criteria_intent.get("current_reality")
        assert cr and isinstance(cr, dict), "CC-18(a): missing current_reality"
        assert cr.get("state"), "CC-18(a): current_reality.state empty"
        assert cr.get("status"), "CC-18(a): current_reality.status empty"

        # (b) scope covers referenced artifacts
        scope = criteria_intent.get("scope", {})
        primary = scope.get("primary", [])
        assert primary and isinstance(primary, list), "CC-18(b): scope.primary missing"

        # (c) required fields populated
        required = ["id", "version", "declares", "intent_type", "status",
                     "priority", "confidence", "origin"]
        missing = [f for f in required if not criteria_intent.get(f)]
        assert not missing, f"CC-18(c): missing required fields: {missing}"

        # (d) schema_version present
        assert criteria_intent.get("schema_version"), "CC-18(d): schema_version missing"


# ═══════════════════════════════════════════════════════════════════
#  SERVES RELATIONSHIP — must declare what it serves
# ═══════════════════════════════════════════════════════════════════

class TestCriteriaServesRelationship:
    """The criteria intent serves the root intent. This was added in
    v1.7.0 — verify it's properly structured."""

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_serves_is_list(self, criteria_intent):
        """serves must be a list (not a bare string)."""
        serves = criteria_intent.get("serves")
        assert serves and isinstance(serves, list), (
            "RED: serves should be a list of intent IDs"
        )

    @pytest.mark.core
    @pytest.mark.criteria_self
    def test_serves_references_root(self, criteria_intent):
        """serves must reference the root intent."""
        serves = criteria_intent.get("serves", [])
        all_text = deep_text_scan(serves)
        assert any_text_contains(all_text, "intent-driven-framework-definition"), (
            "RED: serves does not reference intent-driven-framework-definition"
        )
