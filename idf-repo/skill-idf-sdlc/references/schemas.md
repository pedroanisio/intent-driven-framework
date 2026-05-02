# IDF SDLC v1.7.0 — Entity Schemas

## Intent (full schema)

```yaml
intent:
  id: string                    # stable, unique, never changes
  version: semver               # MAJOR.MINOR.PATCH
  declares: string              # natural language, precise, falsifiable
  scope:
    primary: string[]           # at least one required — file globs or path patterns
    implicit: string[]          # optional derived scope
  priority: enum                # critical | high | medium | low
  status: enum                  # proposed | active | evolving | superseded | residual | retracted
  intent_type: enum             # achieved | aspirational
  achieved_coverage: enum       # none | minimal | partial | substantial | full
  current_reality:              # required if intent_type == aspirational
    state: string               # non-empty description of current state
    assessed: datetime
    last_assessed: datetime
    status: string
    remaining_work:             # string or structured list
      - id: string
        description: string
        blocks: string
        priority: enum
    gap_assessment: string
    gap: string
  tensions: Tension[]
  serves: intent_ref[]
  supersedes: intent_ref[]
  origin:
    type: enum                  # see OriginType below
    ref: string                 # external system reference
    relationship: enum          # see OriginRelationship below
  co_origins: origin[]
  owner: string
  last_affirmed: datetime
  confidence: enum              # high | medium | low
  needs_verification: bool
  created: datetime
  falsifiable_claims: FalsifiableClaim[]
  failure_modes: FailureMode[]
  retirement_conditions: string
  design_stance: string         # schema v0.4.0
  operational_cycle:            # schema v0.3.0
    name: string
    tdd_isomorphism: enum       # claimed | structural | analogical_only
    phases: Phase[]
    constraints: Constraint[]
  provides:                     # schema v0.4.0
    - id: string
      description: string
      tested_by: string[]       # FC or CC IDs
  transition_log: Transition[]
  ext:
    <namespace>: {}             # plugin-defined fields
```

## Transition

```yaml
transition:
  intent_id: string
  from_version: semver
  to_version: semver
  date: datetime
  author: string
  change_type: enum             # see ChangeType below
  reason: string
  forcing_function: string      # optional
  what_changed: string[]        # optional
  residue: string               # optional — leftover state or debt
  ext:
    <namespace>: {}
```

## Decision (ADR)

```yaml
decision:
  id: string
  title: string
  date: datetime
  status: enum                  # proposed | accepted | superseded | deprecated
  owner: string
  serves_intent: intent_ref     # the key traceability link
  intent_version: semver        # which version this decision serves
  scope: string[]               # code paths affected
  refs: string[]                # commit SHAs, PR URLs
  triggers_transition: transition_ref  # optional
  context: string
  decision: string
  consequences: string
```

## Tension

```yaml
tension:
  id: string
  between: [intent_ref, intent_ref]
  declared: datetime
  status: enum                  # active | resolved | dormant | escalated
  description: string
  cross_discipline: boolean
  disciplines: string[]
  current_resolution:
    strategy: string
    decided: datetime
    applies_to: [semver, semver]  # versions of the two intents at resolution time
    decision_ref: decision_ref
  resolution_history:
    - strategy: string
      decided: datetime
      applies_to: [semver, semver]
      superseded: datetime
      reason: string
      decision_ref: decision_ref
  resolution_owner: string
  escalation_path: string
  last_reviewed: datetime
```

## Origin Record

```yaml
origin_record:
  id: string
  type: enum                    # see OriginType
  external_ref: string          # e.g., JIRA-1234
  external_system: string       # jira | linear | pagerduty | figma | grafana | internal
  date: datetime
  summary: string
  generated_intents: intent_ref[]
  constrained_intents: intent_ref[]
```

Inline `origin.ref` on an intent matches `external_ref` here. Two views of the
same relationship — traverse either direction.

## Manifest

```yaml
repo:
  name: string
  declares: string              # top-level intent of this repo
  domain: string
  boundary_type: enum           # service | library | platform | gateway
  version: semver
  schema_version: semver        # determines migration path
  serves:
    - org_intent: string
  depends_on_intents:
    - repo: string
      intent: string
      minimum_version: semver   # purpose contract, not API contract
  plugins: string               # path to plugins/registry.yaml
```

## Canonical Enums (all closed — CC-05)

Adding a value requires a schema_version bump (CC-24).

**IntentStatus**: proposed | active | evolving | superseded | residual | retracted
**IntentType**: aspirational | achieved
**ChangeType** (fine-grained): clarification | correction | extension | reclassification | breaking | deprecation
**ChangeType** (semver-aligned): MAJOR | MINOR | PATCH
**Priority**: critical | high | medium | low
**Confidence**: high | medium | low
**AchievedCoverage**: none | minimal | partial | substantial | full
**OriginType**: engineering | product | incident | discovery | regulatory | organizational | devops | ux | data | sre | security
**OriginRelationship**: derived_from | motivated_by | constrained_by | triggered_by | discovered_in
**TensionStatus**: active | resolved | dormant | escalated
**FalsifiableClaimStatus**: supported | partially_verified | supported_in_theory | unverified | falsified
**TddIsomorphismStatus**: claimed | structural | analogical_only
**Tier**: core | deferred
