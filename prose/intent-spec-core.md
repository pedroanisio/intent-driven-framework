# The Intent Specification — Core

## Companion to The Intent Manifesto

This document contains the domain-agnostic data model, self-model pattern, and extension surface for the intent model. It is the technical specification — the schemas, the structural conventions, the plugin architecture. Domain layers (software engineering, AI agent guardrails, regulatory compliance, etc.) instantiate this core with domain-specific scope semantics, verification mechanisms, and physical self-model structures. The *Intent Manifesto* establishes the worldview. This document specifies the general model. If you have not read the manifesto, start there.

---

## I. The Data Model

Intent is structured data. Its shape must be precise enough to be machine-readable, expressive enough to capture real-world complexity, and minimal enough that people will actually write it.

The data model has two layers: a **core** that is general and stable, and an **extension surface** (`ext`) where domains, organizations, and tools add their own structured data. The core never looks inside `ext`. Tools that understand a specific extension can read it. Tools that don't, skip it. No extension can override core fields.

### The Minimal Valid Intent

An intent declaration is valid with four fields:

```yaml
intent:
  id: intent-checkout-reversibility
  version: 1.0.0
  declares: "Users can reverse any checkout action within 24 hours"
  scope: [checkout]
```

This is the floor. Scope references are domain-specific: file paths in a codebase, capabilities in an agent system, clause references in a standard. Everything else in the full schema is enrichment.

### The Full Intent Schema

```yaml
intent:
  id: string              # stable, unique, never changes
  version: semver          # MAJOR.MINOR.PATCH
  declares: string         # what this intent asserts — natural language, precise
  scope: string[]          # what parts of the system this intent binds (domain-specific)
  priority: enum           # critical | high | medium | low
  status: enum             # proposed | active | evolving | superseded | residual | retracted

  # type — the fundamental distinction
  intent_type: enum        # achieved | aspirational
                           # achieved: what the system currently intends (descriptive)
                           # aspirational: what we want the system to intend (directional)

  # for aspirational intents — the gap between now and the goal
  current_reality:
    assessed: datetime     # when this assessment was last made
    description: string    # honest description of current state
    gaps: []               # specific areas where current state falls short

  # for any intent — how much of its commitments are implemented
  achieved_coverage: enum  # none | minimal | partial | substantial | full (optional)

  # relational
  tensions: intent_ref[]   # intents this is in active tension with
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

  # extension surface — namespaced, optional, domain-specific
  ext:
    <namespace>:           # e.g., compliance, observability, org-acme
      <fields>             # defined by the extension's schema
```

**Achieved coverage.** The `achieved_coverage` field is an optional enum (`none | minimal | partial | substantial | full`) that tracks how much of an intent's commitments have been implemented. It applies to both intent types. For an aspirational intent, it measures progress toward the goal — an aspiration at `partial` has closed some of its gaps but others remain. For an achieved intent, it measures maintenance depth — an achieved intent at `substantial` is well-implemented with edge cases outstanding. When an aspirational intent transitions to achieved, its `achieved_coverage` should already be at `full`; if it is not, the transition is premature. An aspiration that sits at `partial` for years without movement is a signal: either the aspiration is not real, or the organization is not funding the work to close the gap.

### Transition

```yaml
transition:
  intent_id: string
  from_version: semver
  to_version: semver
  date: datetime
  author: string

  change_type: enum        # clarification | extension | breaking | deprecation
  reason: string
  forcing_function: enum   # incident | requirement | scaling | organizational
                           # | regulatory | technical_evolution

  residual:
    affected_areas: string[]  # parts of the system still shaped by the old version
    risk: string              # what happens if residual areas aren't updated
    migration_intent: string  # what "done" looks like for cleanup

  # extension surface — plugins can enrich transitions
  ext:
    <namespace>:
      <fields>
```

**The retracted state.** Most lifecycle transitions describe evolution — an intent that was real and changed. Retraction is different: it declares that the intent was never right. A team declared an intent based on a misunderstanding of the domain, a misinterpreted regulation, or an assumption that proved false. Retracted is distinct from superseded: superseded means "this was real and has been replaced"; retracted means "this was never correct."

The distinction matters operationally. When an intent is superseded, its residual artifacts may still serve the old commitment and should be migrated gradually. When an intent is retracted, artifacts shaped by it should be evaluated for *removal*, not preservation — they were built in service of a commitment that was wrong. A transition to `retracted` must include a `residual` block that identifies the affected areas and assesses the risk of leaving them in place. Lifecycle hooks should treat `on_intent_retracted` as a distinct event from `on_intent_superseded`, because the downstream action (evaluate for removal vs. migrate to successor) is fundamentally different.

### Decision

Decisions are the bridge between intent and artifacts. They must be traceable in both directions — to the intent they serve and to the artifacts they affect.

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

  # traceability to artifacts
  scope: string[]          # areas this decision affects (domain-specific)
  refs: string[]           # implementation references (domain-specific)

  # optional: this decision caused an intent transition
  triggers_transition: transition_ref

  context: string
  decision: string
  consequences: string
```

### Tension

Tensions are as central to the model as intents — they are where the hardest decisions live. Their resolutions evolve over time and that evolution must be tracked.

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
    applies_to: [semver, semver]     # which versions of the two intents this covers
    decision_ref: decision_ref       # the decision that established this resolution

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

**Resolution staleness and the pre-transition check.** The `applies_to` field on a tension resolution binds it to specific versions of the two intents. When either intent undergoes a transition, existing resolutions that reference it must be checked. A MAJOR bump triggers invalidation — the resolution is marked stale and must be re-evaluated. A MINOR bump triggers a review flag — advisory, not blocking. A PATCH bump does not trigger staleness.

This contract ensures that intent evolution does not silently break tradeoffs that depend on the prior version.

### Origin Record

The `origin` field inline on an intent is a lightweight provenance link — it says where the intent came from. The standalone origin record is the reverse index: given an external event, what intents did it produce or constrain?

```yaml
origin_record:
  id: string
  type: enum               # engineering | product | incident | discovery
                           # | regulatory | organizational
                           # | devops | ux | data | sre | security
  external_ref: string         # identifier in the external system
  external_system: string      # domain-specific (jira, linear, pagerduty, internal, etc.)
  date: datetime               # when this origin event occurred
  summary: string

  # reverse index — what this origin produced
  generated_intents: intent_ref[]
  constrained_intents: intent_ref[]
```

### Manifest

The manifest is the system's identity declaration — who it is, what it intends at the highest level, and what it depends on.

```yaml
manifest:
  name: string
  declares: string             # top-level intent of this system
  domain: string               # what kind of system this is
  boundary_type: string        # domain-specific (service, library, agent, standard, etc.)
  version: semver              # system-level intent version
  schema_version: semver       # version of the intent model schema this system uses

  serves:
    - org_intent: string       # organizational intents this system supports

  depends_on_intents:
    - system: string           # external system identifier
      intent: string
      minimum_version: semver  # intent compatibility contract

  # active extensions
  plugins: string              # path to plugin registry
```

**Cross-system intent dependencies.** The `depends_on_intents` field declares that this system's behavior relies on another system maintaining a specific intent at or above a minimum version. This is not an interface contract — it is a *purpose* contract. When the upstream system bumps the depended-on intent past a MAJOR version, downstream systems are notified that the purpose they depend on has fundamentally changed.

**Schema versioning.** The `schema_version` field declares which version of the core intent model schema this system uses. When the core schema evolves, the schema version bumps. Migration tooling can read `schema_version` to determine what transformations are needed.

---

## II. The Self-Model Pattern

Every governed system maintains a structured self-model — a collection of intent declarations, transitions, tensions, decisions, origins, and a manifest. The self-model answers the seven questions from the manifesto: who am I, what do I intend, how have I changed, what am I balancing, what did I choose, where did my intents come from, and what else do I know about myself.

The **physical structure** of the self-model is defined by each domain layer. In a software repository, it is a directory tree (`_repo/`). In an AI agent system, it may be a configuration store alongside tool definitions. In an organizational governance framework, it may be a shared document library. The core specifies the logical structure; domains specify the physical layout.

### Logical Structure

The self-model contains:

- **Manifest** — system identity and top-level intent.
- **Intents** — organized by lifecycle state (active, proposed, superseded).
- **Transitions** — the history of intent evolution.
- **Tensions** — declared tradeoffs between competing intents, with resolution strategies.
- **Decisions** — records of choices made in service of intent.
- **Origins** — provenance links connecting intents to external events.
- **Plugins** — extension registrations and configurations.

Each element is a structured YAML document that conforms to the schemas defined in Section I. The self-model is version-controlled — every change to intent declarations is tracked alongside the artifacts they govern.

---

## III. The Extension Surface

Extensions are where the intent model becomes an ecosystem. Each extension enriches the model in one or more of four ways: **fields**, **validators**, **relations**, and **lifecycle hooks**.

### Extension Registry

The registry declares which extensions are active and whether they are enforced or advisory:

```yaml
plugins:
  - name: compliance
    version: 1.2.0
    required: true          # verification fails if this extension's validations fail

  - name: observability
    version: 1.0.0
    required: false          # advisory only
```

### Extension Manifest

Each extension declares what it is and what it contributes:

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

    transition:              # extensions can extend any core entity
      compliance_review: boolean
      reviewer: string

  registers:
    validators: validators.yaml
    hooks: hooks.yaml
    relations: relations.yaml
```

### Extension Fields

Extensions add structured data to intents under the `ext` namespace:

```yaml
intent:
  id: intent-payment-idempotency
  version: 2.0.0
  declares: "Payment processing must be idempotent across retries"
  scope: [payments/processing]
  status: active

  ext:
    compliance:
      frameworks: [PCI-DSS, SOX]
      audit_required: true
      last_audit: 2025-01-15

    observability:
      sli: "duplicate_payment_rate < 0.001%"
      dashboard: "https://grafana.internal/payments/idempotency"

    org-acme:
      business_unit: payments-core
      cost_center: CC-4200
```

The core schema knows nothing about compliance, observability, or organizational metadata. Each namespace is owned by its extension and invisible to extensions that don't need it.

### Validation Extensions

Extensions contribute validation rules that run alongside core schema verification:

```yaml
validators:
  - rule: "intents with ext.compliance.frameworks containing 'PCI-DSS'
           must have priority: critical"

  - rule: "active intents with ext.compliance.audit_required: true
           must have ext.compliance.last_audit within 365 days"
```

### Relation Type Extensions

The core defines a few relationships: `serves`, `tensions`, `supersedes`. Extensions can register new relation types:

```yaml
relations:
  - type: constrains_training
    from: intent
    to: intent
    description: "This intent constrains how models trained in this scope can be used"

  - type: data_lineage
    from: intent
    to: intent
    description: "Data shaped by this intent feeds into the scope of another intent"
```

### Lifecycle Hooks

The core lifecycle emits events. Extensions subscribe:

```yaml
hooks:
  on_intent_proposed:
    - action: check_regulatory_impact

  on_intent_major_bump:
    - action: notify_downstream_systems

  on_intent_superseded:
    - action: flag_residual_artifacts

  on_intent_stale:                     # last_affirmed exceeds threshold
    - action: schedule_review
```

This turns the intent lifecycle into an event bus. The core emits. Extensions react. The core doesn't know or care what extensions do — it guarantees only that lifecycle events are well-defined and reliable.

---

## IV. Verification Contracts

Schemas without operations are inert YAML files. This section defines the contracts that verification tooling must satisfy — not implementations, but the interfaces that any conforming tool provides. Domain layers specify how these contracts are implemented.

### Schema Verification

Every change to the self-model triggers schema verification. The contract has two tiers:

**Tier 1 — Structural.** Every intent declaration conforms to the core schema (or the extension schema for `ext:` fields). All required fields are present. All enum values are from the canonical set. All `intent_ref` pointers resolve to existing declarations.

**Tier 2 — Relational.** `serves`, `tensions`, and `supersedes` references resolve to existing intents. `depends_on_intents` references resolve to reachable systems and intent IDs. No `proposed` intent duplicates the `id` of an `active` intent. Extensions contribute additional validation rules.

How and when verification runs depends on the domain. In a software repository, it runs in CI on every commit. In an agent system, it may run at configuration load time. In organizational governance, it may run as a scheduled audit.

### Scope Lookup

Given a reference within the system, verification tooling must answer: "Which intents govern this reference?" This is the scope query — the fundamental operation that connects changes to declared purpose. How scope is resolved is domain-specific:

- **Software:** file path matched against glob patterns.
- **AI agents:** capability or tool name matched against declared scope.
- **Regulatory:** clause reference matched against governed sections.
- **Organizational:** department or function matched against scope.

When no intent matches a reference, the tooling reports the gap — this is the advisory signal that drives next-touch declarations.

### Lifecycle Event Propagation

When an intent transitions between lifecycle states, the core emits a lifecycle event. The contract guarantees: (a) every extension with a matching handler is invoked, (b) handlers are invoked in registry order, (c) a handler failure does not prevent subsequent handlers from executing, (d) the aggregate result is reported to the caller. Lifecycle events carry the intent ID, previous and new state, transition version, and author.

### Tension Resolution Staleness

A MAJOR bump on either intent in a tension triggers invalidation — the resolution must be re-evaluated. A MINOR bump triggers a review flag. A PATCH bump does not trigger staleness. The enforcement mechanism is the `on_tension_resolution_stale` lifecycle hook.

### Deprecation Ceremonies

When an intent enters `superseded` or `residual`, downstream references do not automatically update. The deprecation contract has four steps: (1) identify all dependent intents, (2) notify with migration path, (3) define grace period, (4) surface unresolved references as tensions after expiry.
