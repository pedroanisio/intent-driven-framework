# The Intent Specification

## Companion to The Intent Manifesto

This document contains the data model, repository structure, and extension surface for the intent model. It is the technical specification — the schemas, the file layout, the plugin architecture. The *Intent Manifesto* establishes the worldview. This document specifies the implementation. If you have not read the manifesto, start there. This document assumes familiarity with the core principles.

---

## I. The Data Model

Intent is structured data. Its shape must be precise enough to be machine-readable, expressive enough to capture real-world complexity, and minimal enough that people will actually write it.

The data model has two layers: a **core** that is universal and stable, and an **extension surface** (`ext`) where domains, organizations, and tools add their own structured data. The core never looks inside `ext`. Tools that understand a specific extension can read it. Tools that don't, skip it. No extension can override core fields.

### The Minimal Valid Intent

An intent declaration is valid with four fields:

```yaml
intent:
  id: intent-checkout-reversibility
  version: 1.0.0
  declares: "Users can reverse any checkout action within 24 hours"
  scope: [src/checkout/**]
```

This is the floor. It is useful on its own — a searchable, versioned commitment attached to a part of the codebase. Everything else in the full schema is enrichment. Teams should start here and add fields as they become relevant, not because the schema demands them.

### The Full Intent Schema

```yaml
intent:
  id: string              # stable, unique, never changes
  version: semver          # MAJOR.MINOR.PATCH
  declares: string         # what this intent asserts — natural language, precise
  scope:                   # what parts of the system this intent binds
    primary: string[]      # explicit scope entries (at least one required)
    implicit: string[]     # optional — derived or inherited scope
  priority: enum           # critical | high | medium | low
  status: enum             # proposed | active | evolving | superseded | residual | retracted

  # type — the fundamental distinction
  intent_type: enum        # achieved | aspirational
                           # achieved: what the system currently intends (descriptive)
                           # aspirational: what we want the system to intend (directional)

  # coverage — top-level, not nested under current_reality
  achieved_coverage: enum  # none | minimal | partial | substantial | full

  # for aspirational intents — the gap between now and the goal
  current_reality:
    state: string          # required, non-empty description of current state
    assessed: datetime     # or last_assessed — at least one date required
    last_assessed: datetime
    status: string         # optional status summary
    remaining_work:        # string or structured list of work items
      - id: string
        description: string
        blocks: string     # optional — what this blocks
        priority: enum     # optional
    gap_assessment: string # optional overall gap description
    gap: string            # optional short gap summary

  # relational
  tensions: Tension[]      # structured tension objects (see Tension schema below)
  serves: intent_ref[]     # parent intents this supports
  supersedes: intent_ref[] # intents this replaced

  # provenance
  origin:
    type: enum             # engineering | product | incident | discovery
                           # | regulatory | organizational
                           # | devops | ux | data | sre | security
    ref: string            # external reference
    relationship: enum     # derived_from | motivated_by | constrained_by
                           # | triggered_by | discovered_in
  co_origins: origin[]     # additional provenance when multiple forces converge

  # ownership
  owner: string            # who is accountable for this intent
  last_affirmed: datetime  # when someone last confirmed this is still active

  # confidence — critical for legacy and inferred intents
  confidence: enum         # high | medium | low — how well-understood is this intent
  needs_verification: bool # true if this intent has not been verified by domain expert

  # metadata
  created: datetime

  # schema v0.2.0+ additions
  falsifiable_claims: []   # claims that can be tested and potentially falsified
  failure_modes: []        # named ways the intent can be misapplied
  retirement_conditions: string  # when this intent should be retired
  design_stance: string    # architectural philosophy (schema v0.4.0)

  # schema v0.3.0+ additions
  operational_cycle:        # Red/Green/Refactor cycle definition
    name: string
    tdd_isomorphism: enum  # claimed | structural | analogical_only
    phases: []             # ordered: red, green, refactor
    constraints: []        # OC-01 through OC-04

  # schema v0.4.0+ additions
  provides:                # what the intent delivers, with FC cross-references
    - id: string
      description: string
      tested_by: string[]  # FC or CC IDs that verify this deliverable

  # extension surface — namespaced, optional, domain-specific
  ext:
    <namespace>:           # e.g., compliance, observability, org-acme
      <fields>             # defined by the extension's schema
```

### Transition

```yaml
transition:
  intent_id: string
  from_version: semver
  to_version: semver
  date: datetime
  author: string

  change_type: enum        # clarification | correction | extension
                           # | reclassification | breaking | deprecation
  reason: string
  forcing_function: string # optional — freeform description of forcing function
  what_changed: string[]   # optional — list of specific changes made
  residue: string          # optional — description of leftover state or debt

  # extension surface — plugins can enrich transitions
  ext:
    <namespace>:
      <fields>
```

### Decision (ADR)

Decisions are the bridge between intent and code. They must be traceable in both directions — to the intent they serve and to the code they affect.

```yaml
decision:
  id: string
  title: string
  date: datetime
  status: enum             # proposed | accepted | superseded | deprecated
  owner: string            # who made or is accountable for this decision

  # the key relationship
  serves_intent: intent_ref
  intent_version: semver   # the version of intent this decision serves

  # traceability to code
  scope: string[]          # code paths this decision affects
  refs: string[]           # commit SHAs, PR URLs, or other implementation references

  # optional: this decision caused an intent transition
  triggers_transition: transition_ref

  context: string
  decision: string
  consequences: string
```

### Tension

Tensions are as central to the model as intents — they are where the hardest architectural decisions live. Their resolutions evolve over time and that evolution must be tracked, just as intent transitions are tracked.

```yaml
tension:
  id: string
  between: [intent_ref, intent_ref]
  declared: datetime
  status: enum                       # active | resolved | dormant | escalated
  description: string
  cross_discipline: boolean          # true when intents originate from different disciplines
  disciplines: string[]              # which disciplines are involved

  # the current resolution
  current_resolution:
    strategy: string                 # how the system currently balances this tension
    decided: datetime                # when this resolution was adopted
    applies_to: [semver, semver]     # which versions of the two intents this resolution covers
    decision_ref: decision_ref       # the ADR that established this resolution

  # resolution history — how the balance has shifted over time
  resolution_history:
    - strategy: string
      decided: datetime
      applies_to: [semver, semver]
      superseded: datetime
      reason: string                 # why the resolution changed
      decision_ref: decision_ref

  # governance — who decides when the disciplines disagree
  resolution_owner: string           # person or role authorized to break deadlocks
  escalation_path: string            # where unresolved tensions go
  last_reviewed: datetime            # when the resolution was last actively confirmed
```

**Resolution staleness and the pre-transition check.** The `applies_to` field on a tension resolution binds it to specific versions of the two intents. When either intent undergoes a transition, existing resolutions that reference it must be checked before the transition is accepted. A resolution whose `applies_to` versions no longer match the current intent versions is stale — the tradeoff it describes may no longer hold.

The pre-transition contract is: before a version bump on intent A is accepted, all tensions where A appears in `between` are scanned. For each tension, if the current resolution's `applies_to` references the *pre-bump* version of A, the resolution is flagged as potentially stale. The transition is blocked until the resolution is either re-evaluated and confirmed still valid (in which case `applies_to` is updated to the new version), or the resolution must be updated with a new strategy that accounts for the changed intent. If the transition is a PATCH bump (clarification only), the check is advisory rather than blocking — clarifications do not change commitments and are unlikely to invalidate existing resolutions.

This contract ensures that intent evolution does not silently break architectural tradeoffs that depend on the prior version.

### Origin Record

The `origin` field inline on an intent is a lightweight provenance link — it says where the intent came from. The standalone origin record in the `origins/` directory is the reverse index: given an external event (an incident, a product requirement, a regulatory mandate), what intents did it produce or constrain?

These are two views of the same relationship. The inline `origin.ref` on an intent should match the `external_ref` of a standalone origin record. Tools can traverse the relationship in either direction: from intent to source, or from source to all intents it generated.

```yaml
origin_record:
  id: string
  type: enum               # engineering | product | incident | discovery
                           # | regulatory | organizational
                           # | devops | ux | data | sre | security
  external_ref: string         # identifier in the external system (e.g., JIRA-1234)
  external_system: string      # jira | linear | pagerduty | figma | grafana | internal
  date: datetime               # when this origin event occurred
  summary: string

  # reverse index — what this origin produced
  generated_intents: intent_ref[]
  constrained_intents: intent_ref[]
```

### Manifest

```yaml
repo:
  name: string
  declares: string             # top-level intent of this repository
  domain: string
  boundary_type: enum          # service | library | platform | gateway
  version: semver              # repo-level intent version
  schema_version: semver       # version of the intent model schema this repo uses

  serves:
    - org_intent: string       # organizational intents this repo supports

  depends_on_intents:
    - repo: string
      intent: string
      minimum_version: semver  # intent compatibility contract

  # active extensions
  plugins: string              # path to plugins/registry.yaml
```

**Cross-repo intent dependencies.** The `depends_on_intents` field declares that this repo's behavior relies on another repo maintaining a specific intent at or above a minimum version. This is not an API contract — it is a *purpose* contract. When the upstream repo bumps the depended-on intent past a MAJOR version, downstream repos are notified that the purpose they depend on has fundamentally changed and their own intents may need re-evaluation.

The protocol is straightforward: when an intent undergoes a MAJOR bump, CI or lifecycle hooks scan for downstream repos that declare a dependency on that intent. Those repos receive a signal (issue, notification, or PR) that their dependency's intent has broken compatibility. The downstream team then evaluates whether their own intents still hold, updates their `minimum_version`, or declares a transition on their own intents.

**Schema versioning.** The `schema_version` field declares which version of the core intent model schema this repository uses. When the core schema evolves (new required fields, changed semantics), the schema version bumps. Migration tooling can read `schema_version` to determine what transformations are needed. Without this field, there is no migration path when the model itself changes.

---

## II. The Repository Structure

```
_repo/
├── manifest.yaml
├── intents/
│   ├── active/
│   ├── superseded/
│   └── proposed/
├── transitions/
├── tensions/
├── decisions/
│   ├── active/
│   └── superseded/
├── origins/
│   ├── product/
│   ├── engineering/
│   ├── devops/
│   ├── ux/
│   ├── data/
│   ├── sre/
│   ├── security/
│   ├── compliance/
│   └── incidents/
└── plugins/
    ├── registry.yaml
    └── <plugin-name>/
        ├── plugin.yaml
        ├── schema.yaml
        └── validators.yaml
```

This structure lives in every repository, versioned with the code, visible to every engineer, lintable in CI. It is convention-based and discoverable. The underscore prefix signals meta — this is the system's knowledge about itself, not application code.

---

## III. The Extension Surface

The `plugins/` directory is where the intent model becomes an ecosystem. Each plugin extends the model in one or more of four ways: **fields**, **validators**, **relations**, and **lifecycle hooks**.

### Plugin Registry

`registry.yaml` is the control plane — it declares which plugins are active in this repo and whether they are enforced or advisory:

```yaml
plugins:
  - name: compliance
    version: 1.2.0
    required: true          # CI fails if this plugin's validations fail

  - name: observability
    version: 1.0.0
    required: false          # advisory only

  - name: org-acme
    version: 3.1.0
    required: true
```

### Plugin Manifest

Each plugin declares what it is and what it contributes:

```yaml
plugin:
  name: compliance
  version: 1.2.0
  description: "Adds regulatory compliance tracking to intents"

  extends:
    intent:                  # adds fields under ext.compliance
      frameworks: string[]
      audit_required: boolean
      last_audit: datetime

    transition:              # plugins can extend any core entity
      compliance_review: boolean
      reviewer: string

  registers:
    validators: validators.yaml
    hooks: hooks.yaml
    relations: relations.yaml
```

### Extension Fields

Extensions add structured data to intents under the `ext` namespace. Here is an intent with multiple extensions active:

```yaml
intent:
  id: intent-payment-idempotency
  version: 2.0.0
  declares: "Payment processing must be idempotent across retries"
  scope: [src/payments/processing/**]
  status: active

  ext:
    compliance:
      frameworks: [PCI-DSS, SOX]
      audit_required: true
      last_audit: 2025-01-15

    observability:
      sli: "duplicate_payment_rate < 0.001%"
      dashboard: "https://grafana.internal/payments/idempotency"
      alert_threshold: "0.0005%"

    org-acme:
      business_unit: payments-core
      cost_center: CC-4200
      executive_sponsor: jane.doe
```

The core schema knows nothing about compliance, observability, or organizational metadata. Each namespace is owned by its plugin, validated by its plugin, and invisible to plugins that don't need it.

### Validation Plugins

Extensions contribute validation rules that run alongside core schema validation in CI:

```yaml
validators:
  - rule: "intents with ext.compliance.frameworks containing 'PCI-DSS'
           must have priority: critical"

  - rule: "intents with scope crossing domain boundaries must declare
           at least one tension"

  - rule: "active intents with ext.compliance.audit_required: true
           must have ext.compliance.last_audit within 365 days"
```

### Relation Type Plugins

The core defines a few relationships: `serves`, `tensions`, `supersedes`. Extensions can register new relation types, expanding the intent graph:

```yaml
relations:
  - type: constrains_training
    from: intent
    to: intent
    description: "This intent places constraints on how models
                  trained in this scope can be used"

  - type: data_lineage
    from: intent
    to: intent
    description: "Data shaped by this intent feeds into the
                  scope of another intent"
```

Tools that understand a specific edge type can traverse it. Tools that don't see a simpler graph. The graph is always at least as rich as the core, but can be arbitrarily richer.

### Lifecycle Hooks

The core lifecycle emits events. Extensions subscribe:

```yaml
hooks:
  on_intent_proposed:
    - action: check_regulatory_impact

  on_intent_major_bump:
    - action: scan_downstream_repos

  on_intent_superseded:
    - action: flag_residual_dashboards

  on_intent_stale:                     # last_affirmed exceeds threshold
    - action: schedule_compliance_review
```

This turns the intent lifecycle into an event bus. The core emits. Plugins react. The core doesn't know or care what plugins do — it guarantees only that lifecycle events are well-defined and reliable.

---

## IV. Tooling Surface

Schemas without operations are inert YAML files. This section defines the contracts that tooling must satisfy — not implementations, but the interfaces that any conforming tool provides. Adopters can build their own implementations; what matters is that the contracts are honored.

### CI Validation

Every commit that modifies files in `_repo/` triggers schema validation. The CI contract has two tiers. The first tier is structural: every intent file parses as valid YAML, conforms to the core intent schema (or the extension schema for `ext:` fields), and has no unresolved `intent_ref` pointers. The second tier is relational: `serves`, `tensions`, and `supersedes` references resolve to existing intents, `depends_on_intents` references resolve to reachable repos and intent IDs, and no `proposed` intent duplicates the `id` of an `active` intent. Plugins contribute additional validation rules that run alongside the core checks.

### Scope Lookup

Given a file path, tooling must answer: "Which intents govern this path?" This is the scope query — the fundamental operation that connects code changes to declared purpose. The lookup walks the intent index (all YAML files in `intents/active/`) and returns every intent whose `scope` glob pattern matches the queried path. Results are ordered by specificity: a scope of `src/billing/calculations/**` is more specific than `src/billing/**`, and the more specific intent is returned first. When no intent matches a path, the tooling reports the gap — this is the advisory signal that drives next-touch declarations.

### Lifecycle Event Propagation

When an intent transitions between lifecycle states — `proposed`, `active`, `evolving`, `superseded`, `residual` — the core emits a lifecycle event. The hook invocation contract guarantees: (a) every plugin registered in `registry.yaml` with a matching `on_<event>` handler is invoked, (b) handlers are invoked in registry order, (c) a handler failure does not prevent subsequent handlers from executing, and (d) the aggregate result (pass/fail/advisory) is reported to the caller. Lifecycle events carry the intent ID, the previous and new state, the transition version, and the author. Plugins receive this payload and act according to their own logic — the core never inspects plugin responses.

### Tension Resolution Staleness

A tension resolution is bound to specific intent versions via `applies_to: [semver, semver]`. When the referenced intents evolve, the resolution may no longer describe the real tradeoff. The staleness contract defines when a resolution requires attention.

A **MAJOR** bump on either referenced intent triggers invalidation — the resolution is marked stale and must be re-evaluated before the transition lands. MAJOR bumps change commitments fundamentally, and a resolution crafted for the prior commitment cannot be assumed valid. The resolution owner is notified, and the transition on the bumped intent is blocked until the resolution is either reaffirmed with updated `applies_to` versions or replaced with a new strategy.

A **MINOR** bump on either referenced intent triggers a review flag — the resolution is not invalidated but is surfaced for human assessment. MINOR bumps extend commitments in backward-compatible ways, which may or may not affect the resolution. The review flag is advisory: it appears in CI output and in the tension's metadata, but does not block the transition.

A **PATCH** bump on either referenced intent does not trigger staleness or review. PATCH bumps are clarifications with no semantic change — the resolution remains valid by definition.

The enforcement mechanism is the `on_tension_resolution_stale` lifecycle hook. When a transition triggers invalidation or review, this hook fires with the tension ID, the bumped intent, the bump level, and the current resolution's `applies_to` versions. Plugins or CI scripts subscribed to this hook implement the blocking or advisory behavior appropriate to their workflow.

### Deprecation Ceremonies

When an intent enters the `superseded` or `residual` lifecycle state, downstream references do not automatically update. Without a ceremony, superseded intents become zombie references — technically valid, semantically dead, and invisible to the teams that depend on them.

The deprecation contract has four steps. First, all intents with `depends_on_intents`, `serves`, or `tensions` references to the deprecated intent are identified. Within a single repository this is a static scan of `_repo/intents/`; cross-repo discovery depends on the protocol defined separately for cross-repo dependencies. Second, each dependent is notified with a migration path: re-point the reference to the successor intent (named in the `supersedes` field of the new intent), drop the dependency if it is no longer needed, or explicitly acknowledge the residual state if the dependent chooses to continue referencing a non-maintained intent. Third, a grace period for dependent migration is defined — either a calendar deadline set by the intent owner or an explicit deferral to the dependent team's next planning cycle. The grace period is recorded on the transition that moved the intent to `superseded` or `residual`. Fourth, after the grace period expires, any unresolved downstream references are surfaced as tensions — the system now has an active intent depending on a deprecated one, which is a structural inconsistency that demands resolution.
