"""
Criteria Registry — the 28 completeness criteria as Python dataclasses.

Since the criteria YAML (intent-idf-sdlc-v1.7.0.yml) was restored to
disk, this registry is bootstrapped in Python. It mirrors the 28 CC
definitions exactly as they appeared in the criteria YAML.

When the criteria are embedded into the root intent YAML, this module
can switch to loading from YAML via load_registry().
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class Tier(Enum):
    CORE = "core"
    DEFERRED = "deferred"


class Category(Enum):
    PHILOSOPHY = "philosophy"
    MODEL = "model"
    CONFLICT = "conflict"
    STRUCTURE = "structure"
    EXTENSIBILITY = "extensibility"
    ADOPTION = "adoption"
    SELF_SUFFICIENCY = "self-sufficiency"
    SELF_CONFORMANCE = "self-conformance"
    OPERATIONAL = "operational"


@dataclass(frozen=True)
class Criterion:
    id: str
    category: Category
    tier: Tier
    test: str
    verifiable_by: str
    rationale: str = ""
    depends_on: tuple[str, ...] = ()
    promote_when: str = ""


# ── REGISTRY ─────────────────────────────────────────────────────

CRITERIA: dict[str, Criterion] = {}


def _r(c: Criterion) -> Criterion:
    """Register a criterion."""
    if c.id in CRITERIA:
        raise ValueError(f"Duplicate criterion ID: {c.id}")
    CRITERIA[c.id] = c
    return c


def by_category(cat: Category) -> list[Criterion]:
    return [c for c in CRITERIA.values() if c.category == cat]


def by_tier(tier: Tier) -> list[Criterion]:
    return [c for c in CRITERIA.values() if c.tier == tier]


# ═══════════════════════════════════════════════════════════════════
#  PHILOSOPHY — CC-01, CC-02, CC-03
# ═══════════════════════════════════════════════════════════════════

_r(Criterion(
    id="CC-01", category=Category.PHILOSOPHY, tier=Tier.CORE,
    test="Manifesto states the problem it solves",
    verifiable_by="Section exists that describes current state without the model",
))

_r(Criterion(
    id="CC-02", category=Category.PHILOSOPHY, tier=Tier.CORE,
    test="Manifesto states the inversion explicitly",
    verifiable_by="Section exists that names the old orientation and the new one",
))

_r(Criterion(
    id="CC-03", category=Category.PHILOSOPHY, tier=Tier.CORE,
    test="Every principle is named, numbered, and explained with rationale",
    verifiable_by="Count(principles) > 0 AND each has title + body + why-it-matters",
))

# ═══════════════════════════════════════════════════════════════════
#  MODEL — CC-04 through CC-08
# ═══════════════════════════════════════════════════════════════════

_r(Criterion(
    id="CC-04", category=Category.MODEL, tier=Tier.CORE,
    test="Every first-class entity has a complete schema",
    verifiable_by="Set(entities) = {intent, transition, decision, tension, manifest} AND each has a YAML schema with all fields typed",
))

_r(Criterion(
    id="CC-05", category=Category.MODEL, tier=Tier.CORE,
    test="Every enum field has all valid values listed",
    verifiable_by="No enum field has placeholder or unbounded values",
))

_r(Criterion(
    id="CC-06", category=Category.MODEL, tier=Tier.CORE,
    test="Every relationship between entities is bidirectionally defined",
    verifiable_by="If entity A references entity B, B's schema shows how it is referenced by A.",
))

_r(Criterion(
    id="CC-07", category=Category.MODEL, tier=Tier.CORE,
    test="Intent lifecycle is complete — every state has entry and exit conditions",
    verifiable_by="Set(states) = {proposed, active, evolving, superseded, residual, retracted} AND each state has defined transition triggers",
))

_r(Criterion(
    id="CC-08", category=Category.MODEL, tier=Tier.CORE,
    test="Both intent types (achieved/aspirational) have distinct schemas",
    verifiable_by="Aspirational intent schema includes current_reality block. Achieved intent schema does not require it.",
))

# ═══════════════════════════════════════════════════════════════════
#  CONFLICT — CC-08a through CC-08c
# ═══════════════════════════════════════════════════════════════════

_r(Criterion(
    id="CC-08a", category=Category.CONFLICT, tier=Tier.CORE,
    test="Contradiction between active intents is detected and resolved",
    verifiable_by="Document defines what happens when a proposed intent contradicts an existing active intent.",
))

_r(Criterion(
    id="CC-08b", category=Category.CONFLICT, tier=Tier.CORE,
    test="Transitions that would violate active intents are caught",
    verifiable_by="Document defines what happens when a proposed transition on intent A would break an active resolution.",
))

_r(Criterion(
    id="CC-08c", category=Category.CONFLICT, tier=Tier.CORE,
    test="Scope overlap between intents is detectable",
    verifiable_by="Document defines what happens when two intents bind overlapping scopes.",
))

# ═══════════════════════════════════════════════════════════════════
#  STRUCTURE — CC-09, CC-10
# ═══════════════════════════════════════════════════════════════════

_r(Criterion(
    id="CC-09", category=Category.STRUCTURE, tier=Tier.CORE,
    test="Repository structure is fully specified",
    verifiable_by="Directory tree exists with every folder named and purpose stated",
))

_r(Criterion(
    id="CC-10", category=Category.STRUCTURE, tier=Tier.CORE,
    test="A reader can create the _repo/ folder from the manifesto alone",
    verifiable_by="No directory or file in the structure requires knowledge not present in the document",
))

# ═══════════════════════════════════════════════════════════════════
#  EXTENSIBILITY — CC-11, CC-12
# ═══════════════════════════════════════════════════════════════════

_r(Criterion(
    id="CC-11", category=Category.EXTENSIBILITY, tier=Tier.CORE,
    test="Plugin architecture is defined with at least one concrete example",
    verifiable_by="Plugin manifest schema exists AND registry schema exists AND >= 1 worked example",
))

_r(Criterion(
    id="CC-12", category=Category.EXTENSIBILITY, tier=Tier.CORE,
    test="Extension surface on core entities is defined with semantics",
    verifiable_by="ext: namespace syntax is shown with example. Extensions MUST NOT override core fields.",
))

# ═══════════════════════════════════════════════════════════════════
#  ADOPTION — CC-13 through CC-15
# ═══════════════════════════════════════════════════════════════════

_r(Criterion(
    id="CC-13", category=Category.ADOPTION, tier=Tier.CORE,
    test="Adoption sequence is ordered and actionable",
    verifiable_by="Numbered steps exist. Each step has a concrete action.",
))

_r(Criterion(
    id="CC-14", category=Category.ADOPTION, tier=Tier.CORE,
    test="Legacy strategy does not require comprehensive audit",
    verifiable_by="Document explicitly states that aspirational intent can be declared without understanding existing code",
))

_r(Criterion(
    id="CC-15", category=Category.ADOPTION, tier=Tier.CORE,
    test="At least three practical entry points are described",
    verifiable_by="Distinct named strategies exist (e.g., pain-first, next-touch, amnesty) with enough detail to execute",
))

# ═══════════════════════════════════════════════════════════════════
#  SELF-SUFFICIENCY — CC-16, CC-17
# ═══════════════════════════════════════════════════════════════════

_r(Criterion(
    id="CC-16", category=Category.SELF_SUFFICIENCY, tier=Tier.CORE,
    test="No principle references concepts defined only outside the document",
    verifiable_by="Every term used in a principle is either common knowledge or defined in the manifesto",
))

_r(Criterion(
    id="CC-17", category=Category.SELF_SUFFICIENCY, tier=Tier.CORE,
    test="The daily practice is stated concretely",
    verifiable_by="A section exists with specific behavioral instructions: when to declare, when to link, when to record, when to check",
))

# ═══════════════════════════════════════════════════════════════════
#  SELF-CONFORMANCE — CC-18, CC-27
# ═══════════════════════════════════════════════════════════════════

_r(Criterion(
    id="CC-18", category=Category.SELF_CONFORMANCE, tier=Tier.CORE,
    test="This intent block conforms to the model it specifies",
    verifiable_by="The intent block passes validation against the aspirational intent schema. current_reality present, scope covers artifacts, all required fields populated, schema_version present.",
    depends_on=("CC-08",),
))

_r(Criterion(
    id="CC-27", category=Category.SELF_CONFORMANCE, tier=Tier.CORE,
    test="The transition log is complete and consistent",
    verifiable_by="Every version bump has a corresponding transition_log entry. Continuous chain, summaries present, change_types canonical.",
))

# ═══════════════════════════════════════════════════════════════════
#  OPERATIONAL — CC-19, CC-20, CC-21, CC-23, CC-25, CC-26
# ═══════════════════════════════════════════════════════════════════

_r(Criterion(
    id="CC-19", category=Category.OPERATIONAL, tier=Tier.CORE,
    test="The declares field has quality guidance",
    verifiable_by="At minimum: falsifiability test stated, positive and negative examples given, recommended grammar suggested.",
))

_r(Criterion(
    id="CC-20", category=Category.OPERATIONAL, tier=Tier.CORE,
    test="The spec defines a tooling surface",
    verifiable_by="Dedicated section defines: CI validation contract, scope lookup by file path, lifecycle event propagation.",
))

_r(Criterion(
    id="CC-21", category=Category.OPERATIONAL, tier=Tier.CORE,
    test="The next-touch rule has an adoption ramp",
    verifiable_by="Adoption sequence includes: advisory phase, transition to enforcement described, cold-start rationale.",
))

_r(Criterion(
    id="CC-23", category=Category.OPERATIONAL, tier=Tier.CORE,
    test="Tension resolution staleness is contractually defined",
    verifiable_by="Spec defines: MAJOR bump invalidates resolution, MINOR bump triggers review flag, PATCH explicitly excluded, enforcement hook named.",
))

_r(Criterion(
    id="CC-25", category=Category.OPERATIONAL, tier=Tier.CORE,
    test="Deprecation ceremonies for superseded/residual intents are defined",
    verifiable_by="Spec defines: dependents identified and notified, migration path stated, grace period defined, unresolved references surfaced as tensions.",
))

_r(Criterion(
    id="CC-26", category=Category.OPERATIONAL, tier=Tier.CORE,
    test="The manifesto names its own failure modes",
    verifiable_by="Dedicated section with at least three distinct failure modes: performative intent, over-specification, intent drift. Each has name, symptoms, mitigation.",
))

# ═══════════════════════════════════════════════════════════════════
#  DEFERRED — CC-22, CC-24
# ═══════════════════════════════════════════════════════════════════

_r(Criterion(
    id="CC-22", category=Category.OPERATIONAL, tier=Tier.DEFERRED,
    test="Cross-repo intent dependencies have a discovery protocol",
    verifiable_by="Spec defines: discovery mechanism specified, notification payload on MAJOR bump defined, failure mode for unacknowledged notifications.",
    promote_when="The model is adopted across more than one repository and at least one cross-repo depends_on_intents reference exists in production.",
))

_r(Criterion(
    id="CC-24", category=Category.OPERATIONAL, tier=Tier.DEFERRED,
    test="The core schema has evolution semantics",
    verifiable_by="Spec defines: PATCH/MINOR/MAJOR for schema changes, migration requirements per level stated.",
    promote_when="The first schema change proposal is made against the core intent model.",
))
