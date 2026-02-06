"""
Criteria Registry — the aspirational intent for the prose documents.

This file is written BEFORE tests, BEFORE prose. It declares what the
documents must satisfy. Each criterion is a falsifiable commitment.

Methodology:
  1. Add a criterion here (declares the gap).
  2. Write the test in the appropriate test_*.py (mechanizes the check).
  3. Run pytest. See red.
  4. Write the prose that satisfies it.
  5. Run pytest. See green.

Never write prose to fill a gap without first declaring the gap here.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


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
    test: str                               # what this checks (human-readable)
    verifiable_by: str                      # how to verify it mechanically
    rationale: str = ""                     # why this criterion exists
    depends_on: tuple[str, ...] = ()        # criteria that must pass first
    promote_when: str = ""                  # for deferred: when to promote to core


# ── REGISTRY ─────────────────────────────────────────────────────────
#
# Convention: add criteria here in the order you discover them.
# The test files import this registry and parametrize against it.
# A criterion with no corresponding test is a declared gap —
# visible, tracked, waiting for its verification to be written.

CRITERIA: dict[str, Criterion] = {}


def register(c: Criterion) -> Criterion:
    """Register a criterion. Duplicate IDs are a hard error."""
    if c.id in CRITERIA:
        raise ValueError(f"Duplicate criterion ID: {c.id}")
    CRITERIA[c.id] = c
    return c


def by_category(cat: Category) -> list[Criterion]:
    return [c for c in CRITERIA.values() if c.category == cat]


def by_tier(tier: Tier) -> list[Criterion]:
    return [c for c in CRITERIA.values() if c.tier == tier]


# ═══════════════════════════════════════════════════════════════════════
#  PHILOSOPHY — the manifesto earns the right to propose a model
# ═══════════════════════════════════════════════════════════════════════

register(Criterion(
    id="CC-01",
    category=Category.PHILOSOPHY,
    tier=Tier.CORE,
    test="Manifesto states the problem it solves",
    verifiable_by="Section exists that describes current state without the model",
))

register(Criterion(
    id="CC-02",
    category=Category.PHILOSOPHY,
    tier=Tier.CORE,
    test="Manifesto states the inversion explicitly",
    verifiable_by="Section exists that names the old orientation and the new one",
))

register(Criterion(
    id="CC-03",
    category=Category.PHILOSOPHY,
    tier=Tier.CORE,
    test="Every principle is named, numbered, and explained with rationale",
    verifiable_by="Count(principles) > 0 AND each has title + body + why-it-matters",
))

# ═══════════════════════════════════════════════════════════════════════
#  MODEL — the data model is complete and internally consistent
# ═══════════════════════════════════════════════════════════════════════

register(Criterion(
    id="CC-04",
    category=Category.MODEL,
    tier=Tier.CORE,
    test="Every first-class entity has a complete schema",
    verifiable_by=(
        "Set(entities) = {intent, transition, decision, tension, manifest} "
        "AND each has a YAML schema with all fields typed"
    ),
))

register(Criterion(
    id="CC-05",
    category=Category.MODEL,
    tier=Tier.CORE,
    test="Every enum field has all valid values listed",
    verifiable_by="No enum field has placeholder or unbounded values",
))

register(Criterion(
    id="CC-06",
    category=Category.MODEL,
    tier=Tier.CORE,
    test="Every relationship between entities is bidirectionally defined",
    verifiable_by=(
        "If entity A references entity B, B's schema shows "
        "how it is referenced by A."
    ),
))

register(Criterion(
    id="CC-07",
    category=Category.MODEL,
    tier=Tier.CORE,
    test="Intent lifecycle is complete — every state has entry and exit conditions",
    verifiable_by=(
        "Set(states) = {proposed, active, evolving, superseded, residual, retracted} "
        "AND each state has defined transition triggers"
    ),
))

register(Criterion(
    id="CC-08",
    category=Category.MODEL,
    tier=Tier.CORE,
    test="Both intent types (achieved/aspirational) have distinct schemas",
    verifiable_by=(
        "Aspirational intent schema includes current_reality block. "
        "Achieved intent schema does not require it. "
        "Transition from aspirational → achieved is defined."
    ),
))

# ═══════════════════════════════════════════════════════════════════════
#  CONFLICT — the model handles contradictions and overlaps
# ═══════════════════════════════════════════════════════════════════════

register(Criterion(
    id="CC-08a",
    category=Category.CONFLICT,
    tier=Tier.CORE,
    test="Contradiction between active intents is detected and resolved",
    verifiable_by=(
        "Document defines what happens when a proposed intent directly "
        "contradicts an existing active intent. At minimum: "
        "(a) surfaced as supersession proposal, "
        "(b) resolution_owner decides, "
        "(c) outcome recorded as transition."
    ),
))

register(Criterion(
    id="CC-08b",
    category=Category.CONFLICT,
    tier=Tier.CORE,
    test="Transitions that would violate active intents are caught",
    verifiable_by=(
        "Document defines what happens when a proposed transition on "
        "intent A would break an active resolution that depends on A's "
        "current version. At minimum: "
        "(a) tensions checked, (b) stale resolutions flagged, "
        "(c) transition blocked or resolution updated."
    ),
))

register(Criterion(
    id="CC-08c",
    category=Category.CONFLICT,
    tier=Tier.CORE,
    test="Scope overlap between intents is detectable",
    verifiable_by=(
        "Document defines what happens when two intents bind "
        "overlapping scopes with potentially conflicting commitments."
    ),
))

# ═══════════════════════════════════════════════════════════════════════
#  STRUCTURE — the repository layout is fully specified
# ═══════════════════════════════════════════════════════════════════════

register(Criterion(
    id="CC-09",
    category=Category.STRUCTURE,
    tier=Tier.CORE,
    test="Repository structure is fully specified",
    verifiable_by="Directory tree exists with every folder named and purpose stated",
))

register(Criterion(
    id="CC-10",
    category=Category.STRUCTURE,
    tier=Tier.CORE,
    test="A reader can create the _repo/ folder from the manifesto alone",
    verifiable_by=(
        "No directory or file in the structure requires knowledge "
        "not present in the document"
    ),
))

# ═══════════════════════════════════════════════════════════════════════
#  EXTENSIBILITY — the plugin architecture is defined and demonstrated
# ═══════════════════════════════════════════════════════════════════════

register(Criterion(
    id="CC-11",
    category=Category.EXTENSIBILITY,
    tier=Tier.CORE,
    test="Plugin architecture is defined with at least one concrete example",
    verifiable_by=(
        "Plugin manifest schema exists AND registry schema exists "
        "AND >= 1 worked example shows a plugin extending the core model"
    ),
))

register(Criterion(
    id="CC-12",
    category=Category.EXTENSIBILITY,
    tier=Tier.CORE,
    test="Extension surface on core entities is defined with semantics",
    verifiable_by=(
        "ext: namespace syntax is shown with example. Semantics specify: "
        "(a) extensions MUST NOT override core fields, "
        "(b) extensions are namespaced per-plugin, "
        "(c) core tooling MUST ignore unrecognised ext: keys, "
        "(d) at least one example demonstrates a plugin adding an ext: field."
    ),
))

# ═══════════════════════════════════════════════════════════════════════
#  ADOPTION — the model is practically adoptable
# ═══════════════════════════════════════════════════════════════════════

register(Criterion(
    id="CC-13",
    category=Category.ADOPTION,
    tier=Tier.CORE,
    test="Adoption sequence is ordered and actionable",
    verifiable_by=(
        "Numbered steps exist. Each step has a concrete action. "
        "No step requires external knowledge."
    ),
))

register(Criterion(
    id="CC-14",
    category=Category.ADOPTION,
    tier=Tier.CORE,
    test="Legacy strategy does not require comprehensive audit",
    verifiable_by=(
        "Document explicitly states that aspirational intent can be "
        "declared without understanding existing code"
    ),
))

register(Criterion(
    id="CC-15",
    category=Category.ADOPTION,
    tier=Tier.CORE,
    test="At least three practical entry points are described",
    verifiable_by=(
        "Distinct named strategies exist (e.g., pain-first, "
        "next-touch, amnesty) with enough detail to execute"
    ),
))

# ═══════════════════════════════════════════════════════════════════════
#  SELF-SUFFICIENCY — no external dependencies for understanding
# ═══════════════════════════════════════════════════════════════════════

register(Criterion(
    id="CC-16",
    category=Category.SELF_SUFFICIENCY,
    tier=Tier.CORE,
    test="No principle references concepts defined only outside the document",
    verifiable_by=(
        "Every term used in a principle is either common knowledge "
        "or defined in the manifesto"
    ),
))

register(Criterion(
    id="CC-17",
    category=Category.SELF_SUFFICIENCY,
    tier=Tier.CORE,
    test="The daily practice is stated concretely",
    verifiable_by=(
        "A section exists with specific behavioral instructions: "
        "when to declare, when to link, when to record, when to check"
    ),
))

# ═══════════════════════════════════════════════════════════════════════
#  SELF-CONFORMANCE — the model governs itself
# ═══════════════════════════════════════════════════════════════════════

register(Criterion(
    id="CC-18",
    category=Category.SELF_CONFORMANCE,
    tier=Tier.CORE,
    test="This intent block conforms to the model it specifies",
    verifiable_by=(
        "The intent block passes validation against the aspirational "
        "intent schema. Specifically: (a) current_reality present, "
        "(b) scope covers all artifacts, (c) all required fields populated, "
        "(d) schema_version present."
    ),
    depends_on=("CC-08",),
))

register(Criterion(
    id="CC-27",
    category=Category.SELF_CONFORMANCE,
    tier=Tier.CORE,
    test="The transition log is complete and consistent",
    verifiable_by=(
        "Every version bump has a corresponding transition_log entry. "
        "(a) continuous chain from 1.0.0 to current, no gaps. "
        "(b) each entry has summary accounting for changes. "
        "(c) each change_type is from the canonical enum."
    ),
))

# ═══════════════════════════════════════════════════════════════════════
#  OPERATIONAL — the model is ready for real-world use
# ═══════════════════════════════════════════════════════════════════════

register(Criterion(
    id="CC-19",
    category=Category.OPERATIONAL,
    tier=Tier.CORE,
    test="The declares field has quality guidance",
    verifiable_by=(
        "At minimum: (a) falsifiability test stated, "
        "(b) positive and negative examples given, "
        "(c) recommended grammar suggested."
    ),
))

register(Criterion(
    id="CC-20",
    category=Category.OPERATIONAL,
    tier=Tier.CORE,
    test="The spec defines a tooling surface",
    verifiable_by=(
        "Dedicated section defines: (a) CI validation contract, "
        "(b) scope lookup by file path, "
        "(c) lifecycle event propagation."
    ),
))

register(Criterion(
    id="CC-21",
    category=Category.OPERATIONAL,
    tier=Tier.CORE,
    test="The next-touch rule has an adoption ramp",
    verifiable_by=(
        "Adoption sequence includes: (a) advisory phase, "
        "(b) transition to enforcement described, "
        "(c) cold-start rationale addresses legacy burden."
    ),
))

register(Criterion(
    id="CC-23",
    category=Category.OPERATIONAL,
    tier=Tier.CORE,
    test="Tension resolution staleness is contractually defined",
    verifiable_by=(
        "Spec defines: (a) MAJOR bump invalidates resolution, "
        "(b) MINOR bump triggers review flag, "
        "(c) PATCH explicitly excluded, "
        "(d) enforcement hook named."
    ),
))

register(Criterion(
    id="CC-25",
    category=Category.OPERATIONAL,
    tier=Tier.CORE,
    test="Deprecation ceremonies for superseded/residual intents are defined",
    verifiable_by=(
        "Spec defines: (a) dependents identified and notified, "
        "(b) migration path stated, (c) grace period defined, "
        "(d) unresolved references surfaced as tensions."
    ),
))

register(Criterion(
    id="CC-26",
    category=Category.OPERATIONAL,
    tier=Tier.CORE,
    test="The manifesto names its own failure modes",
    verifiable_by=(
        "Dedicated section with at least three distinct failure modes: "
        "(a) performative intent, (b) over-specification/bureaucratic, "
        "(c) intent drift. Each has name, symptoms, mitigation."
    ),
))

# ═══════════════════════════════════════════════════════════════════════
#  DEFERRED — tracked, not blocking v1
# ═══════════════════════════════════════════════════════════════════════

register(Criterion(
    id="CC-22",
    category=Category.OPERATIONAL,
    tier=Tier.DEFERRED,
    test="Cross-repo intent dependencies have a discovery protocol",
    verifiable_by=(
        "Spec defines: (a) discovery mechanism specified, "
        "(b) notification payload on MAJOR bump defined, "
        "(c) failure mode for unacknowledged notifications."
    ),
    promote_when=(
        "The model is adopted across more than one repository "
        "and at least one cross-repo depends_on_intents reference "
        "exists in production."
    ),
))

register(Criterion(
    id="CC-24",
    category=Category.OPERATIONAL,
    tier=Tier.DEFERRED,
    test="The core schema has evolution semantics",
    verifiable_by=(
        "Spec defines: (a) PATCH/MINOR/MAJOR for schema changes, "
        "(b) migration requirements per level stated."
    ),
    promote_when=(
        "The first schema change proposal is made against the "
        "core intent model."
    ),
))
