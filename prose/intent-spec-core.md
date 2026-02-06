# Intent Driven Framework — Core Data Model Specification

<!-- source: intent-idf-sdlc-v1.7.0.yml scope.primary[1] -->

**Schema version 0.4.0** | Criteria version 1.7.0

This document is the universal data model specification for the Intent Driven Framework. It defines the entities, enums, lifecycle states, relationships, and structural invariants that any conforming implementation must satisfy. It is derived from the root intent declaration (`criteria/intent-driven-framework-definition.yml`) and governed by the SDLC criteria intent (`criteria/intent-idf-sdlc-v1.7.0.yml`).

This spec is domain-invariant: the entities and their relationships apply regardless of the domain in which intents are declared. Domain-specific elements (scope syntax, artifact types, verification methods) are parameters, not hardcoded assumptions.

---

## First-Class Entities — CC-04

<!-- source: CC-04, schema.js v0.4.0, IntentDrivenFramework.lean §4 -->

The model defines five first-class entities. Each has a complete schema with all fields typed. No partial schemas are permitted.

| Entity | Purpose |
|---|---|
| **Intent** | A structured declaration of purpose — the primary governing entity |
| **Transition** | A versioned change record linking two versions of an intent |
| **Decision** | An action taken in service of an intent, traceable back to it |
| **Tension** | An explicit conflict between two intents, with resolution tracking |
| **Manifest** | A registry entry describing a domain or plugin instantiation |

### Intent Schema

The intent is the core entity. All fields are typed; required fields are marked.

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | Unique identifier |
| `version` | SemVer | yes | Current version (MAJOR.MINOR.PATCH) |
| `schema_version` | SemVer | no | Schema version this intent conforms to |
| `declares` | string | yes | The semantic payload — what this intent commits to |
| `scope` | list of strings or object | yes | Artifacts governed by this intent |
| `priority` | Priority enum | yes | Governance urgency |
| `status` | IntentStatus enum | yes | Lifecycle state |
| `intent_type` | IntentType enum | yes | Achieved or aspirational |
| `current_reality` | CurrentReality | conditional | Required if `intent_type` is `aspirational` (CC-08) |
| `achieved_coverage` | AchievedCoverage enum | no | Coverage level for achieved intents |
| `owner` | string | yes | Accountable party |
| `confidence` | Confidence enum | yes | Certainty level |
| `origin` | Origin | yes | Where this intent came from |
| `provides` | list of ProvidesItem | no | What the intent delivers, with FC cross-refs |
| `falsifiable_claims` | list of FalsifiableClaim | no | Claims that can be tested and potentially falsified |
| `failure_modes` | list of FailureMode | no | Named ways the intent can be misapplied |
| `operational_cycle` | OperationalCycle | no | Red/Green/Refactor cycle definition |
| `design_stance` | string | no | Architectural philosophy |
| `serves` | list of string | no | IDs of intents this intent serves |
| `retirement_conditions` | string | no | When this intent should be retired |
| `dependencies` | list | no | Declared dependencies |
| `transition_log` | list of Transition | no | Version history |

### Transition Schema

| Field | Type | Required |
|---|---|---|
| `from` / `from_version` | SemVer | yes |
| `to` / `to_version` | SemVer | yes |
| `change_type` | ChangeType enum | yes |
| `summary` | string | yes |

### Decision Schema

| Field | Type | Required |
|---|---|---|
| `id` | string | yes |
| `title` | string | yes |
| `status` | string | yes |
| `serves_intent` | string | yes |
| `intent_version` | SemVer | yes |
| `scope` | list of strings | yes |

### Tension Schema

| Field | Type | Required |
|---|---|---|
| `id` | string | yes |
| `between` | pair of strings | yes |
| `status` | TensionStatus enum | yes |
| `description` | string | yes |
| `cross_discipline` | boolean | yes |
| `disciplines` | list of strings | yes |
| `current_resolution` | TensionResolution | no |
| `resolution_owner` | string | yes |

### Manifest Schema

| Field | Type | Required |
|---|---|---|
| `name` | string | yes |
| `declares` | string | yes |
| `domain` | string | yes |
| `version` | SemVer | yes |
| `schema_version` | SemVer | yes |

---

## Canonical Enums — CC-05

<!-- source: CC-05, schema.js enums, IntentDrivenFramework.lean §2 -->

All enum types are closed. Adding values requires a `schema_version` bump (CC-24). The Lean 4 formalization proves closure by construction — each enum is an inductive type with no escape hatch.

### IntentStatus (CC-07 lifecycle states)

| Value | Semantics |
|---|---|
| `proposed` | Declared but not yet active |
| `active` | Current and enforced |
| `evolving` | Active but undergoing intentional change |
| `superseded` | Replaced by a successor intent |
| `residual` | No longer actively maintained; kept for reference |
| `retracted` | Withdrawn before reaching active; terminal state |

### IntentType

| Value | Semantics |
|---|---|
| `aspirational` | Intent not yet fully achieved; `current_reality` block required |
| `achieved` | Intent fully satisfied; `current_reality` optional |

### ChangeType

Two vocabularies coexist. Both are legitimate.

**Fine-grained** (criteria YAML):

| Value | Semantics | SemVer mapping |
|---|---|---|
| `clarification` | Rewording with no semantic change | PATCH |
| `correction` | Fixing inconsistencies or errors | PATCH |
| `extension` | Additive new content; backward-compatible | MINOR |
| `reclassification` | Tier or category move | MINOR |
| `breaking` | Backward-incompatible change | MAJOR |
| `deprecation` | Marking for removal | N/A (lifecycle) |

**SemVer-aligned** (root intent):

| Value | Semantics |
|---|---|
| `MAJOR` / `major_bump` | Breaking change |
| `MINOR` / `minor_bump` | Backward-compatible addition |
| `PATCH` / `patch_bump` | Clarification or correction |

### Priority

`critical` | `high` | `medium` | `low`

### Confidence

`high` | `medium` | `low`

### AchievedCoverage

`none` | `minimal` | `partial` | `substantial` | `full`

### OriginType (closed, 11 values)

`engineering` | `product` | `incident` | `discovery` | `regulatory` | `organizational` | `devops` | `ux` | `data` | `sre` | `security`

### OriginRelationship

`derived_from` | `motivated_by` | `constrained_by` | `triggered_by` | `discovered_in`

### TensionStatus

`active` | `resolved` | `dormant` | `escalated`

### FalsifiableClaimStatus

`supported` | `partially_verified` | `supported_in_theory` | `unverified` | `falsified`

Governance consequence: `falsified` triggers mandatory evolution or retraction.

### TddIsomorphismStatus

`claimed` | `structural` | `analogical_only`

Governance constraint: `structural` requires FC-07 status = `supported`.

### Tier

`core` | `deferred`

---

## Intent Lifecycle — CC-07

<!-- source: CC-07, IntentDrivenFramework.lean §3 -->

The lifecycle is a finite state machine with defined transitions. Terminal states have no outgoing edges. All states are reachable from `proposed`.

```
proposed ──→ active ──→ evolving ──→ superseded ──→ residual
   │            │           │
   │            │           ├──→ active (re-stabilize)
   │            │           └──→ retracted
   │            ├──→ superseded
   │            └──→ retracted
   └──→ retracted
```

**Terminal states**: `residual`, `retracted` (proven in Lean: no outgoing `ValidTransition`).

**Invariants** (machine-checked):
- Every non-terminal state has at least one exit transition.
- All 6 states are reachable from `proposed`.
- Terminal states have zero outgoing transitions.

---

## Achieved vs. Aspirational — CC-08

<!-- source: CC-08, IntentDrivenFramework.lean §5 -->

| Property | Aspirational | Achieved |
|---|---|---|
| `current_reality` | Required | Optional |
| `achieved_coverage` | Typically absent | Recommended |
| Lifecycle entry | `proposed` → `active` | Direct to `active` |

**Well-formedness predicate**: an intent is well-formed if, when its `intent_type` is `aspirational`, its `current_reality` field is present (proven in Lean as `Intent.wellFormed`).

---

## Bidirectional Relationships — CC-06

<!-- source: CC-06, IntentDrivenFramework.lean §10 -->

Every relationship between entities has a defined inverse. The inverse function is an involution (applying it twice returns the original). No relation is its own inverse.

| Relation | Inverse |
|---|---|
| `serves` | `served_by` |
| `tensions` | `tensioned_by` |
| `supersedes` | `superseded_by` |
| `generated_by` | `generates` |
| `tests` | `tested_by` |

---

## Tension Resolution Staleness — CC-23

<!-- source: CC-23, IntentDrivenFramework.lean §8 -->

When an intent referenced by a tension resolution is bumped, the staleness contract determines what happens:

| Bump level | Action | Rationale |
|---|---|---|
| MAJOR | **Invalidated** — resolution must be re-evaluated before transition lands | MAJOR changes can alter the `declares` meaning |
| MINOR | **Review flag** — resolution surfaced for human assessment, not auto-invalidated | MINOR adds commitments that may affect compatibility |
| PATCH | **No action** — resolution remains valid | PATCH is cosmetic |

The validator or lifecycle hook named `staleness_check` enforces this contract.

---

## Pre-Transition Resolution Check — CC-08b

<!-- source: CC-08b, IntentDrivenFramework.lean §9 -->

Before a transition on intent A is accepted, all tensions referencing A are checked. If any active tension has a resolution with `applies_to` referencing A's current version, and the transition is a MAJOR bump, the resolution is stale and the transition is blocked until the resolution is updated or invalidated.

---

## Deprecation Ceremonies — CC-25

<!-- source: CC-25, IntentDrivenFramework.lean §12 -->

When an intent enters the `superseded` or `residual` lifecycle state:

1. All intents with `depends_on` references to the deprecated intent are identified.
2. A migration path is stated: dependents re-point to the successor, drop the dependency, or acknowledge the residual state.
3. A grace period for migration is defined (or explicitly left to the intent owner).
4. Unresolved downstream references after the grace period are surfaced as tensions.

Within a single repository, downstream references are discoverable by static analysis. Cross-repo discovery requires CC-22 (deferred).

---

## Operational Cycle — Red / Green / Refactor

<!-- source: intent.operational_cycle, IntentDrivenFramework.lean §14 -->

The framework's discipline is a three-phase cycle, operationally analogous to TDD.

| Phase | Name | Definition |
|---|---|---|
| **Red** | Declare | Declare an intent that is currently unsatisfied. No decision is justified without a red intent that demands it. |
| **Green** | Satisfy | Make decisions and produce artifacts that serve the declared intent until the gap closes. |
| **Refactor** | Evolve | Once an intent is satisfied, it can be evolved. No evolution without a green state to protect. |

**Constraints**:

| ID | Rule | Violation |
|---|---|---|
| OC-01 | Red before Green — no work without a declared unsatisfied intent | Drift |
| OC-02 | Green before Refactor — no evolution without demonstrated satisfaction | Premature abstraction |
| OC-03 | Every Green must be evidenced — achieved_coverage or current_reality must move | Green-washing |
| OC-04 | Refactor produces a transition, not a new intent — the identity persists | Intent sprawl |

**TDD isomorphism**: currently `claimed`, not `structural`. FC-07 status is `supported_in_theory`. The claim cannot be upgraded until external validation occurs.

---

## Tooling Surface — CC-20

<!-- source: CC-20 -->

The tooling contract defines what implementations must satisfy:

1. **CI validation**: Schema validation (Zod) and reference resolution run on every change. Invalid intents block merge.
2. **Scope lookup**: Given a file path, the tooling resolves which intent(s) govern it via scope matching.
3. **Lifecycle hooks**: Transitions trigger staleness checks (CC-23), deprecation notifications (CC-25), and pre-transition resolution checks (CC-08b).

---

## Provides–FC Cross-Reference Integrity

<!-- source: IntentDrivenFramework.lean §15 -->

Every `provides` item with a non-empty `tested_by` list must reference FC IDs that exist in the intent's `falsifiable_claims`. This is mechanically verified.

---

## Falsifiable Claim Governance

<!-- source: IntentDrivenFramework.lean §16 -->

An intent with any `falsified` claim is not governance-compliant. The intent must either evolve (version bump) or be retracted. The `isomorphismConsistent` predicate ensures that if `tdd_isomorphism` is `structural`, FC-07 must have status `supported`.

---

## Transition Log Integrity — CC-27

<!-- source: CC-27, IntentDrivenFramework.lean §6-§7, §13 -->

Every version bump must have a corresponding `transition_log` entry. The log must form a contiguous chain from the initial version to the current version with no gaps, and every entry must have a non-trivial summary.

**Machine-checked properties** (Lean 4):
- Chain starts at declared initial version
- Chain ends at declared current version
- Adjacent entries link (`to_version[n]` = `from_version[n+1]`)
- All entries have non-empty summaries

---

## Extension Surface — CC-12

<!-- source: CC-12 -->

Core entities support an `ext:` namespace for domain-specific extensions:

- Extensions MUST NOT override or shadow core fields.
- Extensions are namespaced per-plugin: `ext.<plugin_id>.*`
- Core tooling MUST ignore unrecognized `ext:` keys gracefully.

---

## Verification Architecture

<!-- source: intent-idf-sdlc-v1.7.0.yml current_reality.state -->

The framework is verified by a five-layer stack:

| Layer | Tool | Coverage |
|---|---|---|
| 1 | **Lean 4** | ~12 CC — algebraic structure, lifecycle, staleness, log integrity |
| 2 | **Pytest** | ~30 CC — criteria-to-evidence-to-verdict, TDD workflow, CI-native |
| 3 | **Zod v4** | YAML shape + structural invariants |
| 4 | **NLP semantic scorer** | ~16 CC — entailment checks on prose |
| 5 | **Python regex scorer** | 28 CC — keyword heuristics, legacy baseline |

A Zustand flaw store tracks regressions across validation runs.
