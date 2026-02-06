"""
RED PHASE — prose spec drift detection.

The prose spec (intent-spec-idf-sdlc-v1.7.0.md) is a derived document.
Its schemas and enum values must match the canonical sources: the SDLC
criteria YAML, the Zod schema (schema.js), and the Lean formalization.

When the canonical sources evolve and the prose spec doesn't follow,
these tests fail — forcing the spec to be updated.
"""

import re
import pytest


# ═══════════════════════════════════════════════════════════════════
#  ENUM DRIFT — prose spec must use canonical enum values
# ═══════════════════════════════════════════════════════════════════

class TestSpecEnumDrift:
    """The prose spec contains inline YAML schemas with enum values.
    Those values must match the canonical enums from the SDLC criteria
    YAML and the Zod schema."""

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_priority_no_stale_standard(self, prose_spec_text):
        """Priority enum must not use 'standard' — canonical is 'medium'.

        The v1.5.0 transition canonicalized priority to:
          critical | high | medium | low
        The prose spec still uses 'standard' and 'aspirational'."""
        # Find priority enum lines in YAML code blocks
        has_standard = bool(re.search(
            r"#.*critical\s*\|\s*high\s*\|\s*standard",
            prose_spec_text,
        ))
        assert not has_standard, (
            "RED: prose spec uses stale priority value 'standard'. "
            "Canonical priority enum is: critical | high | medium | low"
        )

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_priority_no_stale_aspirational_value(self, prose_spec_text):
        """Priority enum must not use 'aspirational' as a priority value.

        'aspirational' is an intent_type, not a priority level."""
        has_aspirational_priority = bool(re.search(
            r"priority:.*aspirational",
            prose_spec_text,
        ))
        assert not has_aspirational_priority, (
            "RED: prose spec uses 'aspirational' as a priority value. "
            "'aspirational' is an intent_type, not a priority. "
            "Canonical priority: critical | high | medium | low"
        )

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_change_type_has_correction(self, prose_spec_text):
        """ChangeType enum must include 'correction'.

        Added in v1.4.0 — the first correction-type transition.
        The canonical enum has 6 values, not 4."""
        # The spec's transition schema defines change_type
        has_correction = "correction" in prose_spec_text.lower()
        assert has_correction, (
            "RED: prose spec's change_type enum is missing 'correction'. "
            "Canonical change_type: clarification | correction | extension "
            "| reclassification | breaking | deprecation"
        )

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_change_type_has_reclassification(self, prose_spec_text):
        """ChangeType enum must include 'reclassification'.

        Added in v1.4.1 canonicalization."""
        has_reclassification = "reclassification" in prose_spec_text.lower()
        assert has_reclassification, (
            "RED: prose spec's change_type enum is missing 'reclassification'. "
            "Canonical change_type: clarification | correction | extension "
            "| reclassification | breaking | deprecation"
        )

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_origin_type_no_stale_product_requirement(self, prose_spec_text):
        """OriginType must not use 'product_requirement' — canonical is 'product'.

        Fixed in v1.6.1: product_requirement → product."""
        has_product_requirement = "product_requirement" in prose_spec_text
        assert not has_product_requirement, (
            "RED: prose spec uses stale origin_type 'product_requirement'. "
            "Canonical value is 'product' (fixed in v1.6.1)"
        )

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_origin_type_has_discovery(self, prose_spec_text):
        """OriginType must include 'discovery'.

        Added in v1.6.1 — 11-value closed set."""
        # Check that 'discovery' appears near other origin_type values
        has_discovery = bool(re.search(
            r"(engineering|product|incident).*discovery|discovery.*(engineering|product|incident)",
            prose_spec_text,
        ))
        assert has_discovery, (
            "RED: prose spec's origin_type enum is missing 'discovery'. "
            "Canonical origin_type is 11 values (closed since v1.6.1)"
        )

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_origin_relationship_has_triggered_by(self, prose_spec_text):
        """OriginRelationship must include 'triggered_by'.

        Canonical: derived_from | motivated_by | constrained_by
                 | triggered_by | discovered_in"""
        has_triggered_by = "triggered_by" in prose_spec_text
        assert has_triggered_by, (
            "RED: prose spec's origin.relationship enum is missing 'triggered_by'. "
            "Canonical: derived_from | motivated_by | constrained_by "
            "| triggered_by | discovered_in"
        )

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_origin_relationship_has_discovered_in(self, prose_spec_text):
        """OriginRelationship must include 'discovered_in'."""
        has_discovered_in = "discovered_in" in prose_spec_text
        assert has_discovered_in, (
            "RED: prose spec's origin.relationship enum is missing 'discovered_in'. "
            "Canonical: derived_from | motivated_by | constrained_by "
            "| triggered_by | discovered_in"
        )


# ═══════════════════════════════════════════════════════════════════
#  SCHEMA DRIFT — prose spec schemas must match Zod/Lean
# ═══════════════════════════════════════════════════════════════════

class TestSpecSchemaDrift:
    """The prose spec defines entity schemas. Fields added in schema
    v0.2.0–v0.4.0 must appear in the spec."""

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_intent_schema_has_achieved_coverage(self, prose_spec_text):
        """Intent schema must include 'achieved_coverage' field.

        Added in schema v0.3.0. Top-level optional field, not nested
        under current_reality (fixed in v1.6.1)."""
        # Must appear as a top-level intent field, not just in current_reality
        has_field = "achieved_coverage" in prose_spec_text
        assert has_field, (
            "RED: prose spec intent schema missing 'achieved_coverage'. "
            "Added in schema v0.3.0 as top-level optional field."
        )

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_intent_schema_has_schema_version(self, prose_spec_text):
        """Intent schema must include 'schema_version' field.

        Added in schema v0.3.0 (CC-24 self-conformance)."""
        has_field = "schema_version" in prose_spec_text
        assert has_field, (
            "RED: prose spec intent schema missing 'schema_version'. "
            "Added in schema v0.3.0 for CC-24 self-conformance."
        )

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_intent_schema_has_provides(self, prose_spec_text):
        """Intent schema must include 'provides' field.

        Added in schema v0.4.0 with FC cross-references."""
        # Both 'provides' and 'tested_by' must appear (they may be
        # on different lines in the schema block)
        has_provides = "provides" in prose_spec_text
        has_tested_by = "tested_by" in prose_spec_text
        assert has_provides and has_tested_by, (
            "RED: prose spec intent schema missing 'provides' with 'tested_by'. "
            "Added in schema v0.4.0 with FC cross-references."
        )

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_intent_schema_has_falsifiable_claims(self, prose_spec_text):
        """Intent schema must include 'falsifiable_claims' field.

        Added in schema v0.2.0."""
        has_field = "falsifiable_claims" in prose_spec_text
        assert has_field, (
            "RED: prose spec intent schema missing 'falsifiable_claims'. "
            "Added in schema v0.2.0."
        )

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_intent_schema_has_operational_cycle(self, prose_spec_text):
        """Intent schema must include 'operational_cycle' field.

        Added in schema v0.3.0."""
        has_field = "operational_cycle" in prose_spec_text
        assert has_field, (
            "RED: prose spec intent schema missing 'operational_cycle'. "
            "Added in schema v0.3.0."
        )

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_intent_schema_has_design_stance(self, prose_spec_text):
        """Intent schema must include 'design_stance' field.

        Added in schema v0.4.0."""
        has_field = "design_stance" in prose_spec_text
        assert has_field, (
            "RED: prose spec intent schema missing 'design_stance'. "
            "Added in schema v0.4.0."
        )

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_intent_schema_has_serves(self, prose_spec_text):
        """Intent schema must include 'serves' as an intent-level field.

        Added in schema v0.2.0. Must appear in the intent schema block,
        not just in manifest."""
        # Check that 'serves' appears as a field in a YAML schema context
        # (with intent_ref or intent_ref[] type annotation)
        has_serves = bool(re.search(
            r"serves:\s*(intent_ref|string)",
            prose_spec_text,
        ))
        assert has_serves, (
            "RED: prose spec intent schema missing 'serves' field. "
            "Added in schema v0.2.0 for intent-to-intent relationships."
        )

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_intent_schema_has_retirement_conditions(self, prose_spec_text):
        """Intent schema must include 'retirement_conditions' field."""
        has_field = "retirement_conditions" in prose_spec_text
        assert has_field, (
            "RED: prose spec intent schema missing 'retirement_conditions'."
        )

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_status_enum_has_retracted(self, prose_spec_text):
        """IntentStatus enum must include 'retracted'.

        Added in v1.6.0. Terminal state proven in Lean."""
        # Find the status enum definition in the spec
        has_retracted = bool(re.search(
            r"proposed.*active.*evolving.*superseded.*residual.*retracted",
            prose_spec_text,
        ))
        assert has_retracted, (
            "RED: prose spec status enum is missing 'retracted'. "
            "Added in v1.6.0 as a terminal lifecycle state."
        )


# ═══════════════════════════════════════════════════════════════════
#  STRUCTURAL DRIFT — prose spec shapes must match Zod schema.js
# ═══════════════════════════════════════════════════════════════════

class TestSpecStructuralDrift:
    """The prose spec's YAML schema blocks must match the structural
    shapes defined in schema.js (Zod v0.4.0). Field names, nesting,
    and types must agree — not just enum values."""

    # ── scope ────────────────────────────────────────────────────

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_scope_not_flat_string_array(self, prose_spec_text):
        """Scope on the intent schema must not be shown as a flat string[].

        Zod: Scope = z.object({ primary: string[], implicit?: string[] })
        Prose currently shows: scope: string[]

        Only checks the Full Intent Schema block (between "### The Full
        Intent Schema" and "### Transition"), not other entities like
        Decision which have their own scope field."""
        # Extract the intent schema block
        m = re.search(
            r"### The Full Intent Schema.*?### Transition",
            prose_spec_text,
            re.DOTALL,
        )
        if not m:
            pytest.fail("Could not find 'Full Intent Schema' section")
        intent_block = m.group()
        has_flat_scope = bool(re.search(
            r"scope:\s*string\[\]",
            intent_block,
        ))
        assert not has_flat_scope, (
            "RED: prose spec intent schema defines scope as 'string[]' "
            "(flat array). Canonical Zod schema defines scope as "
            "{ primary: string[], implicit?: string[] }"
        )

    # ── current_reality ──────────────────────────────────────────

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_current_reality_no_stale_description_field(self, prose_spec_text):
        """current_reality must use 'state', not 'description'.

        Zod: state: z.string().min(1, "current_reality.state must be non-empty")
        Prose currently uses: description: string"""
        has_stale = bool(re.search(
            r"current_reality:.{0,200}?description:\s*string",
            prose_spec_text,
            re.DOTALL,
        ))
        assert not has_stale, (
            "RED: prose spec current_reality uses 'description: string'. "
            "Canonical Zod field name is 'state: string'"
        )

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_current_reality_no_stale_gaps_field(self, prose_spec_text):
        """current_reality must not use 'gaps' — not a Zod field.

        Canonical fields: state, last_assessed/assessed, status,
        remaining_work, gap_assessment, gap."""
        has_gaps = bool(re.search(
            r"current_reality:.{0,300}?gaps:\s*\[\]",
            prose_spec_text,
            re.DOTALL,
        ))
        assert not has_gaps, (
            "RED: prose spec current_reality uses 'gaps: []'. "
            "Canonical Zod fields are 'remaining_work', "
            "'gap_assessment', or 'gap'"
        )

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_current_reality_has_state_field(self, prose_spec_text):
        """current_reality must include 'state' as its primary field.

        Zod: state: z.string().min(1) — the only required field."""
        has_state = bool(re.search(
            r"current_reality:.{0,200}?\bstate:\s*string",
            prose_spec_text,
            re.DOTALL,
        ))
        assert has_state, (
            "RED: prose spec current_reality missing 'state' field. "
            "Canonical Zod requires state: string (non-empty)"
        )

    # ── achieved_coverage nesting ────────────────────────────────

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_achieved_coverage_not_nested_in_current_reality(self, prose_spec_text):
        """achieved_coverage must be top-level on IntentSchema, not
        nested under current_reality.

        Zod: IntentSchema.achieved_coverage (top-level optional)
        Prose currently nests it inside current_reality block."""
        nested = bool(re.search(
            r"current_reality:.{0,300}?achieved_coverage:",
            prose_spec_text,
            re.DOTALL,
        ))
        assert not nested, (
            "RED: prose spec nests 'achieved_coverage' under current_reality. "
            "Canonical Zod schema has achieved_coverage as a top-level "
            "IntentSchema field (fixed in v1.6.1)"
        )

    # ── tensions ─────────────────────────────────────────────────

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_tensions_not_bare_intent_ref_array(self, prose_spec_text):
        """tensions must be Tension[] (rich objects), not intent_ref[].

        Zod: Tension = z.object({ id, name, between, resolution_strategy,
        resolution_owner, last_reviewed, staleness_threshold_days })
        Prose currently shows: tensions: intent_ref[]"""
        has_bare_ref = bool(re.search(
            r"tensions:\s*intent_ref\[\]",
            prose_spec_text,
        ))
        assert not has_bare_ref, (
            "RED: prose spec defines tensions as 'intent_ref[]'. "
            "Canonical Zod defines tensions as Tension[] (rich objects "
            "with id, name, between, resolution_strategy, etc.)"
        )

    # ── transition.residual → residue ────────────────────────────

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_transition_no_residual_object(self, prose_spec_text):
        """Transition must use 'residue: string', not 'residual: {}'.

        Zod: residue: z.string().optional()
        Prose currently shows: residual: { code_paths, risk, migration_intent }"""
        has_residual_object = bool(re.search(
            r"residual:\s*\n\s+code_paths:",
            prose_spec_text,
        ))
        assert not has_residual_object, (
            "RED: prose spec transition has 'residual' as object "
            "(code_paths, risk, migration_intent). "
            "Canonical Zod uses 'residue: string' (flat optional)."
        )

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_transition_forcing_function_not_enum(self, prose_spec_text):
        """Transition forcing_function must be optional string, not enum.

        Zod: forcing_function: z.string().optional()
        Prose currently shows: forcing_function: enum"""
        has_enum = bool(re.search(
            r"forcing_function:\s*enum",
            prose_spec_text,
        ))
        assert not has_enum, (
            "RED: prose spec defines forcing_function as 'enum'. "
            "Canonical Zod defines it as optional string (freeform)."
        )

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_transition_has_what_changed(self, prose_spec_text):
        """Transition must include 'what_changed' field.

        Zod: what_changed: z.array(z.string().min(1)).optional()
        Added in canonical transition schema."""
        has_what_changed = "what_changed" in prose_spec_text
        assert has_what_changed, (
            "RED: prose spec transition schema missing 'what_changed'. "
            "Canonical Zod includes what_changed: string[] (optional)."
        )


# ═══════════════════════════════════════════════════════════════════
#  EXTENSION COVERAGE — prose spec entities beyond Zod scope
# ═══════════════════════════════════════════════════════════════════

class TestSpecExtensionEntities:
    """The prose spec defines entities that are valid extensions —
    not yet modeled in schema.js but intentionally part of the
    specification. These tests protect them from accidental removal."""

    # ── Decision (ADR) ────────────────────────────────────────────

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_decision_entity_exists(self, prose_spec_text):
        """Prose spec must define the Decision (ADR) entity."""
        assert "decision:" in prose_spec_text, (
            "Prose spec missing Decision (ADR) entity schema"
        )

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_decision_has_serves_intent(self, prose_spec_text):
        """Decision must link to the intent it serves."""
        assert "serves_intent:" in prose_spec_text, (
            "Decision schema missing 'serves_intent' — the key "
            "relationship linking decisions to intents"
        )

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_decision_has_triggers_transition(self, prose_spec_text):
        """Decision must support triggering intent transitions."""
        assert "triggers_transition:" in prose_spec_text, (
            "Decision schema missing 'triggers_transition' — "
            "the bridge from decision to intent evolution"
        )

    # ── Tension (standalone) ──────────────────────────────────────

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_tension_standalone_entity_exists(self, prose_spec_text):
        """Prose spec must define the standalone Tension entity
        with resolution history (richer than Zod inline Tension)."""
        assert "current_resolution:" in prose_spec_text, (
            "Prose spec missing standalone Tension entity with "
            "current_resolution block"
        )

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_tension_has_resolution_history(self, prose_spec_text):
        """Standalone Tension must track resolution evolution."""
        assert "resolution_history:" in prose_spec_text, (
            "Tension schema missing 'resolution_history' — "
            "how the balance has shifted over time"
        )

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_tension_has_cross_discipline(self, prose_spec_text):
        """Standalone Tension must support cross-discipline flag."""
        assert "cross_discipline:" in prose_spec_text, (
            "Tension schema missing 'cross_discipline' — "
            "true when intents originate from different disciplines"
        )

    # ── Origin Record ─────────────────────────────────────────────

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_origin_record_entity_exists(self, prose_spec_text):
        """Prose spec must define the standalone Origin Record entity."""
        assert "origin_record:" in prose_spec_text, (
            "Prose spec missing Origin Record entity — "
            "the reverse index from external events to intents"
        )

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_origin_record_has_reverse_index(self, prose_spec_text):
        """Origin Record must provide reverse lookup fields."""
        has_generated = "generated_intents:" in prose_spec_text
        has_constrained = "constrained_intents:" in prose_spec_text
        assert has_generated and has_constrained, (
            "Origin Record missing reverse index fields: "
            "generated_intents and/or constrained_intents"
        )

    # ── Manifest ──────────────────────────────────────────────────

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_manifest_entity_exists(self, prose_spec_text):
        """Prose spec must define the repo Manifest entity."""
        assert "boundary_type:" in prose_spec_text, (
            "Prose spec missing Manifest entity with boundary_type"
        )

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_manifest_has_cross_repo_deps(self, prose_spec_text):
        """Manifest must support cross-repo intent dependencies."""
        assert "depends_on_intents:" in prose_spec_text, (
            "Manifest missing 'depends_on_intents' — "
            "the cross-repo purpose contract"
        )

    # ── Repository Structure (Section II) ─────────────────────────

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_repo_structure_section_exists(self, prose_spec_text):
        """Prose spec must document the _repo/ directory layout."""
        has_section = "## II. The Repository Structure" in prose_spec_text
        has_tree = "_repo/" in prose_spec_text
        assert has_section and has_tree, (
            "Prose spec missing Section II: Repository Structure"
        )

    # ── Extension Surface (Section III) ───────────────────────────

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_extension_surface_section_exists(self, prose_spec_text):
        """Prose spec must document the plugin extension surface."""
        assert "## III. The Extension Surface" in prose_spec_text, (
            "Prose spec missing Section III: Extension Surface"
        )

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_extension_four_mechanisms(self, prose_spec_text):
        """Extension surface must describe all four plugin mechanisms."""
        has_fields = "### Extension Fields" in prose_spec_text
        has_validators = "### Validation Plugins" in prose_spec_text
        has_relations = "### Relation Type Plugins" in prose_spec_text
        has_hooks = "### Lifecycle Hooks" in prose_spec_text
        missing = []
        if not has_fields:
            missing.append("Extension Fields")
        if not has_validators:
            missing.append("Validation Plugins")
        if not has_relations:
            missing.append("Relation Type Plugins")
        if not has_hooks:
            missing.append("Lifecycle Hooks")
        assert not missing, (
            f"Extension Surface missing plugin mechanisms: "
            f"{', '.join(missing)}"
        )

    # ── Tooling Surface (Section IV) ──────────────────────────────

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_tooling_surface_section_exists(self, prose_spec_text):
        """Prose spec must document the tooling contracts."""
        assert "## IV. Tooling Surface" in prose_spec_text, (
            "Prose spec missing Section IV: Tooling Surface"
        )

    @pytest.mark.spec_drift
    @pytest.mark.core
    def test_tooling_contracts_coverage(self, prose_spec_text):
        """Tooling surface must describe all five contracts."""
        has_ci = "### CI Validation" in prose_spec_text
        has_scope = "### Scope Lookup" in prose_spec_text
        has_lifecycle = "### Lifecycle Event Propagation" in prose_spec_text
        has_staleness = "### Tension Resolution Staleness" in prose_spec_text
        has_deprecation = "### Deprecation Ceremonies" in prose_spec_text
        missing = []
        if not has_ci:
            missing.append("CI Validation")
        if not has_scope:
            missing.append("Scope Lookup")
        if not has_lifecycle:
            missing.append("Lifecycle Event Propagation")
        if not has_staleness:
            missing.append("Tension Resolution Staleness")
        if not has_deprecation:
            missing.append("Deprecation Ceremonies")
        assert not missing, (
            f"Tooling Surface missing contracts: "
            f"{', '.join(missing)}"
        )
