"""
IDF Init Plugin: SDLC v1.7.0 SKILL Generator
==============================================
Generates a Claude-compatible SKILL package for the Intent Driven Framework
SDLC specification v1.7.0 — the implementation layer.

This skill is scoped to the SDLC spec: repository structure, entity schemas,
CI validation contracts, extension surface, lifecycle hooks, staleness protocol,
deprecation ceremonies, and scope lookup. It does NOT cover the manifesto
(philosophy, failure modes, falsifiable claims) — that is a separate concern.

Hook points:
  - post_directories: creates skill/ directory tree
  - post_files: writes SKILL.md + references + scripts
  - post_init: prints usage instructions
"""

from pathlib import Path
import os

# ─── SKILL.md ────────────────────────────────────────────────────────────────

SKILL_MD = """\
---
name: idf-sdlc
description: >
  Intent Driven Framework SDLC v1.7.0 implementation skill. Use when the user
  wants to: (1) scaffold or maintain an IDF _repo/ directory structure,
  (2) write or validate intent/transition/decision/tension/origin YAML against
  the v1.7.0 schemas, (3) configure the plugin registry or write extension
  plugins (fields, validators, relations, lifecycle hooks), (4) implement or
  debug CI validation (structural tier + relational tier), (5) perform scope
  lookups to find which intents govern a file path, (6) manage lifecycle state
  transitions and propagate lifecycle events, (7) check tension resolution
  staleness after version bumps (MAJOR=block, MINOR=review, PATCH=noop),
  (8) execute deprecation ceremonies when intents enter superseded/residual,
  (9) configure cross-repo intent dependencies via depends_on_intents, or
  (10) manage schema_version migration across repos. Triggers on: "_repo/",
  "manifest.yaml", "intent YAML", "scope lookup", "lifecycle hook",
  "tension staleness", "deprecation ceremony", "plugin registry",
  "ext: namespace", "cross-repo dependencies", "CI validation contract".
---

# IDF SDLC v1.7.0

Implementation specification for Intent Driven Framework repositories.

## Repository Structure

Every IDF-governed repository contains a `_repo/` directory at the root:

```
_repo/
├── manifest.yaml              # repo identity + cross-repo deps + plugin list
├── intents/
│   ├── active/                # status: active | evolving
│   ├── superseded/            # status: superseded
│   └── proposed/              # status: proposed
├── transitions/               # version change records per intent
├── tensions/                  # declared conflicts between intents
├── decisions/
│   ├── active/                # status: accepted
│   └── superseded/            # status: superseded | deprecated
├── origins/
│   ├── product/               # origin.type grouping directories
│   ├── engineering/
│   ├── incident/ (and devops, ux, data, sre, security, compliance)
└── plugins/
    ├── registry.yaml          # active plugins + required/advisory flag
    └── <plugin-name>/
        ├── plugin.yaml        # manifest: name, version, extends, registers
        ├── schema.yaml        # extension field definitions
        └── validators.yaml    # plugin validation rules
```

The `_repo/` prefix signals meta — the system's knowledge about itself.

## Minimal Valid Intent

Four fields make a valid intent:

```yaml
intent:
  id: intent-checkout-reversibility
  version: 1.0.0
  declares: "Users can reverse any checkout action within 24 hours"
  scope: [src/checkout/**]
```

Start here. Add fields as they earn their place.

## CI Validation Contract

Two tiers, both run on every commit touching `_repo/`:

**Tier 1 — Structural**: YAML parses, conforms to schema, no unresolved `intent_ref` pointers.

**Tier 2 — Relational**: `serves`/`tensions`/`supersedes` refs resolve to existing intents.
`depends_on_intents` refs resolve to reachable repos. No `proposed` intent duplicates an
`active` intent's ID. Plugins contribute additional rules.

See `references/schemas.md` for full field definitions and enum values.

## Lifecycle State Machine

```
proposed → active | retracted
active   → evolving | superseded | residual
evolving → active | superseded | residual
superseded → residual
residual   (terminal)
retracted  (terminal)
```

**Event propagation contract** (4 guarantees):
(a) every plugin with matching `on_<event>` handler is invoked
(b) handlers invoked in registry order
(c) handler failure does not prevent subsequent handlers
(d) aggregate result (pass/fail/advisory) reported to caller

Events carry: intent_id, previous_state, new_state, transition_version, author.

## Tension Resolution Staleness

When a version bump lands on an intent referenced by a tension resolution:

| Bump  | Action       | Blocks transition? |
|-------|--------------|--------------------|
| MAJOR | Invalidate   | Yes — re-evaluate before merge |
| MINOR | Review flag  | No — advisory in CI output |
| PATCH | No action    | No |

Enforcement: `on_tension_resolution_stale` lifecycle hook fires with tension_id,
bumped_intent, bump_level, current applies_to versions.

## Deprecation Ceremonies

When status → `superseded` or `residual`:

1. **Identify** — scan `depends_on_intents`, `serves`, `tensions` refs to the deprecated intent
2. **Notify** — migration path per dependent: re-point to successor, drop, or acknowledge residual
3. **Grace period** — calendar deadline or deferral, recorded on the transition
4. **Surface** — after grace period, unresolved refs become tensions

## Extension Surface

Plugins extend the model in four ways. See `references/extension-surface.md` for
plugin.yaml schema, validator rule syntax, relation type registration, and hook events.

**Rules** (CC-12):
- Extensions live under `ext.<plugin_id>.*` — never shadow core fields
- Core tooling ignores unrecognized `ext:` keys gracefully
- Plugin validators run alongside core validation in CI

## Scope Lookup

Given a file path, return all intents whose `scope` glob matches it, ordered by
specificity (most specific first). When no intent matches, report the coverage gap.
This is the fundamental operation connecting code changes to declared purpose.

## Cross-Repo Dependencies

`depends_on_intents` in manifest.yaml declares purpose contracts (not API contracts):

```yaml
depends_on_intents:
  - repo: payments-service
    intent: intent-idempotent-processing
    minimum_version: 2.0.0
```

On upstream MAJOR bump → downstream repos receive signal (issue/notification/PR).
Downstream team evaluates, updates `minimum_version`, or transitions own intents.

## Reference Files

- `references/schemas.md` — full YAML schemas for all 6 entities + enum tables
- `references/extension-surface.md` — plugin manifest, validators, relations, hooks
- `references/tooling-contracts.md` — CI tiers, scope lookup, staleness, deprecation
"""

# ─── REFERENCE: SCHEMAS ─────────────────────────────────────────────────────

REF_SCHEMAS = """\
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
"""

# ─── REFERENCE: EXTENSION SURFACE ───────────────────────────────────────────

REF_EXTENSION = """\
# IDF SDLC v1.7.0 — Extension Surface

## Plugin Registry

`_repo/plugins/registry.yaml` — declares active plugins and enforcement level:

```yaml
plugins:
  - name: compliance
    version: 1.2.0
    required: true       # CI fails if this plugin's validations fail

  - name: observability
    version: 1.0.0
    required: false      # advisory only
```

## Plugin Manifest

Each plugin declares what it extends and what it registers:

```yaml
plugin:
  name: compliance
  version: 1.2.0
  description: "Adds regulatory compliance tracking to intents"

  extends:
    intent:                    # adds fields under ext.compliance
      frameworks: string[]
      audit_required: boolean
      last_audit: datetime
    transition:                # plugins can extend any core entity
      compliance_review: boolean
      reviewer: string

  registers:
    validators: validators.yaml
    hooks: hooks.yaml
    relations: relations.yaml
```

## Extension Fields in Practice

An intent with multiple active plugins:

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

Core schema knows nothing about these namespaces. Each is owned, validated,
and ignored-by-default per CC-12.

## Validation Plugins

Plugin-contributed rules run alongside core CI validation:

```yaml
validators:
  - rule: >
      intents with ext.compliance.frameworks containing 'PCI-DSS'
      must have priority: critical
  - rule: >
      intents with scope crossing domain boundaries must declare
      at least one tension
  - rule: >
      active intents with ext.compliance.audit_required: true
      must have ext.compliance.last_audit within 365 days
```

## Relation Type Plugins

Core relations: serves, tensions, supersedes. Plugins can register new edge types:

```yaml
relations:
  - type: constrains_training
    from: intent
    to: intent
    description: >
      This intent places constraints on how models trained in this scope can be used
  - type: data_lineage
    from: intent
    to: intent
    description: >
      Data shaped by this intent feeds into the scope of another intent
```

Tools that understand the edge type traverse it. Others see a simpler graph.

## Lifecycle Hooks

Core emits events. Plugins subscribe in hooks.yaml:

```yaml
hooks:
  on_intent_proposed:
    - action: check_regulatory_impact
  on_intent_major_bump:
    - action: scan_downstream_repos
  on_intent_superseded:
    - action: flag_residual_dashboards
  on_intent_stale:                    # last_affirmed exceeds threshold
    - action: schedule_compliance_review
  on_tension_resolution_stale:        # staleness contract trigger
    - action: notify_resolution_owner
```

The lifecycle is an event bus. Core emits. Plugins react. Core never inspects responses.
"""

# ─── REFERENCE: TOOLING CONTRACTS ───────────────────────────────────────────

REF_TOOLING = """\
# IDF SDLC v1.7.0 — Tooling Contracts

These are the interfaces any conforming tool must satisfy. Not implementations — contracts.

## CI Validation

Triggered on every commit modifying `_repo/`. Two tiers:

### Tier 1 — Structural
- Every intent file parses as valid YAML
- Conforms to core intent schema (and extension schema for ext: fields)
- No unresolved intent_ref pointers

### Tier 2 — Relational
- serves, tensions, supersedes references resolve to existing intents
- depends_on_intents references resolve to reachable repos and intent IDs
- No proposed intent duplicates the id of an active intent
- Plugin validation rules run alongside core checks

## Scope Lookup

Input: file path
Output: all intents whose scope glob matches, ordered by specificity

```
src/billing/calculations/tax.py
  → intent-billing-accuracy (scope: src/billing/calculations/**)
  → intent-billing-compliance (scope: src/billing/**)
```

More specific scope returned first. When no intent matches → report gap
(advisory signal for next-touch declarations).

## Lifecycle Event Propagation

When intent transitions between states, core emits a lifecycle event.

**Invocation contract**:
(a) Every plugin in registry.yaml with matching on_<event> handler is invoked
(b) Handlers invoked in registry order
(c) Handler failure does NOT prevent subsequent handlers from executing
(d) Aggregate result (pass/fail/advisory) reported to caller

**Event payload**:
- intent_id
- previous_state
- new_state
- transition_version (semver)
- author

## Tension Resolution Staleness (CC-23)

applies_to on a resolution binds it to specific intent versions. When either evolves:

### Pre-transition check
Before a version bump on intent A is accepted:
1. Scan all tensions where A appears in `between`
2. For each tension, check if current_resolution.applies_to references pre-bump version
3. If yes:
   - MAJOR bump → resolution is stale, transition BLOCKED until resolution updated
   - MINOR bump → review flag (advisory, does not block)
   - PATCH bump → no action

### Enforcement
Hook: on_tension_resolution_stale
Payload: tension_id, bumped_intent, bump_level, current applies_to versions

## Deprecation Ceremonies (CC-25)

When intent enters superseded or residual:

### Step 1: Identify dependents
Scan depends_on_intents, serves, tensions refs to the deprecated intent.
Within single repo: static scan of _repo/intents/.
Cross-repo: depends on CC-22 protocol.

### Step 2: Notify with migration path
Each dependent must: re-point to successor (from supersedes field on new intent),
drop the dependency, or explicitly acknowledge residual state.

### Step 3: Grace period
Calendar deadline or deferral to dependent team's next planning cycle.
Recorded on the transition that moved intent to superseded/residual.

### Step 4: Surface unresolved
After grace period, unresolved downstream refs → surfaced as tensions.
Active intent depending on deprecated intent = structural inconsistency.

## Schema Versioning

manifest.yaml.schema_version declares which core schema version the repo uses.
When core schema evolves (new required fields, changed semantics), schema_version bumps.
Migration tooling reads this field to determine transformations needed.
"""

# ─── SCRIPT: VALIDATE INTENT ────────────────────────────────────────────────

SCRIPT_VALIDATE = '''\
#!/usr/bin/env python3
"""
IDF SDLC v1.7.0 — Quick intent validator.
Validates a single intent YAML file against the v1.7.0 schema.

Usage: python validate_intent.py <path-to-intent.yml>
"""

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("pip install pyyaml")
    sys.exit(1)

REQUIRED = ["id", "version", "declares", "scope"]
FULL_REQUIRED = [
    "id", "version", "schema_version", "intent_type", "declares",
    "scope", "priority", "status", "confidence", "owner", "origin",
]

ENUMS = {
    "intent_type": ["aspirational", "achieved"],
    "priority": ["critical", "high", "medium", "low"],
    "status": ["proposed", "active", "evolving", "superseded", "residual", "retracted"],
    "confidence": ["high", "medium", "low"],
    "achieved_coverage": ["none", "minimal", "partial", "substantial", "full"],
    "origin_type": [
        "engineering", "product", "incident", "discovery", "regulatory",
        "organizational", "devops", "ux", "data", "sre", "security",
    ],
    "origin_relationship": [
        "derived_from", "motivated_by", "constrained_by",
        "triggered_by", "discovered_in",
    ],
    "change_type": [
        "clarification", "correction", "extension",
        "reclassification", "breaking", "deprecation",
        "MAJOR", "MINOR", "PATCH",
    ],
}


def validate(path):
    errors = []
    warnings = []

    try:
        doc = yaml.safe_load(Path(path).read_text())
    except Exception as e:
        return [f"YAML parse error: {e}"], []

    if not doc or "intent" not in doc:
        return ["Missing root 'intent' key"], []

    i = doc["intent"]

    # required fields
    for f in REQUIRED:
        if f not in i:
            errors.append(f"Missing required field: {f}")

    # enum checks
    for field, valid in ENUMS.items():
        val = i.get(field)
        if val and val not in valid:
            errors.append(f"{field}: '{val}' not in {valid}")

    # nested enum: origin.type, origin.relationship
    origin = i.get("origin", {})
    if isinstance(origin, dict):
        ot = origin.get("type")
        if ot and ot not in ENUMS["origin_type"]:
            errors.append(f"origin.type: '{ot}' not in {ENUMS['origin_type']}")
        orel = origin.get("relationship")
        if orel and orel not in ENUMS["origin_relationship"]:
            errors.append(f"origin.relationship: '{orel}' not in {ENUMS['origin_relationship']}")

    # CC-08: aspirational requires current_reality
    if i.get("intent_type") == "aspirational" and i.get("status") != "proposed":
        if not i.get("current_reality"):
            errors.append("Aspirational intent (non-proposed) requires current_reality block")
        else:
            cr = i["current_reality"]
            if not cr.get("state"):
                errors.append("current_reality.state is required and must be non-empty")

    # transition_log change_type check
    for entry in i.get("transition_log", []):
        ct = entry.get("change_type", "")
        if ct and ct not in ENUMS["change_type"]:
            errors.append(f"transition_log.change_type: '{ct}' not in {ENUMS['change_type']}")
        if not entry.get("summary", "").strip():
            warnings.append("transition_log entry has empty summary")

    # scope structure
    scope = i.get("scope")
    if isinstance(scope, dict):
        if not scope.get("primary"):
            warnings.append("scope.primary is empty")
    elif isinstance(scope, list):
        if not scope:
            warnings.append("scope is empty list")

    # warns
    if "TODO" in str(i.get("declares", "")):
        warnings.append("declares still contains TODO placeholder")

    for f in FULL_REQUIRED:
        if f not in i and f not in REQUIRED:
            warnings.append(f"Recommended field missing: {f}")

    return errors, warnings


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_intent.py <path-to-intent.yml>")
        sys.exit(1)

    path = sys.argv[1]
    errors, warnings = validate(path)

    if errors:
        print(f"FAIL: {path}")
        for e in errors:
            print(f"  ERROR: {e}")
    else:
        print(f"PASS: {path}")

    for w in warnings:
        print(f"  WARN: {w}")

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
'''

# ─── SCRIPT: STALENESS CHECK ────────────────────────────────────────────────

SCRIPT_STALENESS = '''\
#!/usr/bin/env python3
"""
IDF SDLC v1.7.0 — Tension resolution staleness checker.
Checks whether a version bump on an intent invalidates any tension resolutions.

Usage: python staleness_check.py <tensions-dir> <intent-id> <old-version> <new-version>
"""

import sys
import glob
from pathlib import Path

try:
    import yaml
except ImportError:
    print("pip install pyyaml")
    sys.exit(1)


def bump_level(old, new):
    o = [int(x) for x in old.split("-")[0].split(".")]
    n = [int(x) for x in new.split("-")[0].split(".")]
    if n[0] > o[0]:
        return "MAJOR"
    elif n[1] > o[1]:
        return "MINOR"
    return "PATCH"


def check(tensions_dir, intent_id, old_ver, new_ver):
    level = bump_level(old_ver, new_ver)
    results = []

    for path in glob.glob(f"{tensions_dir}/**/*.yml", recursive=True) + glob.glob(f"{tensions_dir}/**/*.yaml", recursive=True):
        try:
            doc = yaml.safe_load(Path(path).read_text())
        except Exception:
            continue
        t = doc.get("tension", {})
        between = t.get("between", [])
        refs = [b.get("intent_id", "") for b in between if isinstance(b, dict)]
        if intent_id not in refs:
            continue

        res = t.get("resolution", t.get("current_resolution", {}))
        applies_to = res.get("applies_to", [])
        tid = t.get("id", Path(path).stem)

        if level == "MAJOR":
            results.append(("BLOCK", tid, path, f"MAJOR bump invalidates resolution (applies_to: {applies_to})"))
        elif level == "MINOR":
            results.append(("REVIEW", tid, path, f"MINOR bump — review resolution (applies_to: {applies_to})"))
        else:
            results.append(("OK", tid, path, "PATCH bump — no action needed"))

    return level, results


def main():
    if len(sys.argv) < 5:
        print("Usage: python staleness_check.py <tensions-dir> <intent-id> <old-version> <new-version>")
        sys.exit(1)

    tensions_dir, intent_id, old_ver, new_ver = sys.argv[1:5]
    level, results = check(tensions_dir, intent_id, old_ver, new_ver)

    print(f"Bump: {old_ver} -> {new_ver} ({level})")
    print(f"Intent: {intent_id}")
    print()

    blocked = False
    for action, tid, path, msg in results:
        icon = {"BLOCK": "BLOCK", "REVIEW": "REVIEW", "OK": "OK"}.get(action, "?")
        print(f"  [{icon}] {tid}: {msg}")
        if action == "BLOCK":
            blocked = True

    if not results:
        print("  No tensions reference this intent.")

    sys.exit(1 if blocked else 0)


if __name__ == "__main__":
    main()
'''

# ─── SCRIPT: SCOPE LOOKUP ───────────────────────────────────────────────────

SCRIPT_SCOPE = '''\
#!/usr/bin/env python3
"""
IDF SDLC v1.7.0 — Scope lookup.
Given a file path, returns all intents whose scope covers it.

Usage: python scope_lookup.py <intents-dir> <query-path>
"""

import sys
import glob
import fnmatch
from pathlib import Path

try:
    import yaml
except ImportError:
    print("pip install pyyaml")
    sys.exit(1)


def lookup(intents_dir, query_path):
    matches = []
    for filepath in glob.glob(f"{intents_dir}/**/*.yml", recursive=True) + glob.glob(f"{intents_dir}/**/*.yaml", recursive=True):
        try:
            doc = yaml.safe_load(Path(filepath).read_text())
        except Exception:
            continue
        if not doc or "intent" not in doc:
            continue
        i = doc["intent"]
        scope = i.get("scope", {})
        if isinstance(scope, dict):
            patterns = scope.get("primary", []) + scope.get("implicit", [])
        elif isinstance(scope, list):
            patterns = scope
        else:
            continue

        for pattern in patterns:
            if not pattern:
                continue
            if fnmatch.fnmatch(query_path, pattern) or query_path.startswith(pattern.rstrip("*/")):
                matches.append({
                    "intent_id": i.get("id", "?"),
                    "file": filepath,
                    "pattern": pattern,
                    "specificity": len(pattern),
                })
                break

    matches.sort(key=lambda m: m["specificity"], reverse=True)
    return matches


def main():
    if len(sys.argv) < 3:
        print("Usage: python scope_lookup.py <intents-dir> <query-path>")
        sys.exit(1)

    intents_dir, query_path = sys.argv[1], sys.argv[2]
    results = lookup(intents_dir, query_path)

    if results:
        print(f"Intents governing: {query_path}")
        for r in results:
            print(f"  {r['intent_id']} (scope: {r['pattern']}) — {r['file']}")
    else:
        print(f"GAP: No intent governs {query_path}")
        print("  Consider declaring one (next-touch rule).")

    sys.exit(0)


if __name__ == "__main__":
    main()
'''


# ─── PLUGIN HOOKS ───────────────────────────────────────────────────────────

SKILL_NAME = "skill-idf-sdlc"


def _on_post_directories(root, config):
    skill = Path(root) / SKILL_NAME
    for sub in ["references", "scripts"]:
        (skill / sub).mkdir(parents=True, exist_ok=True)
    return "skill directories created"


def _on_post_files(root, config):
    skill = Path(root) / SKILL_NAME
    (skill / "SKILL.md").write_text(SKILL_MD)
    (skill / "references" / "schemas.md").write_text(REF_SCHEMAS)
    (skill / "references" / "extension-surface.md").write_text(REF_EXTENSION)
    (skill / "references" / "tooling-contracts.md").write_text(REF_TOOLING)

    scripts = {
        "validate_intent.py": SCRIPT_VALIDATE,
        "staleness_check.py": SCRIPT_STALENESS,
        "scope_lookup.py": SCRIPT_SCOPE,
    }
    for name, content in scripts.items():
        p = skill / "scripts" / name
        p.write_text(content)
        os.chmod(p, 0o755)

    return f"skill written to {skill}"


def _on_post_init(root, config):
    print()
    print(f"  🧠 SKILL generated: {SKILL_NAME}/")
    print( "     SKILL.md        — SDLC v1.7.0 repo structure, lifecycle, CI contracts")
    print( "     references/     — full schemas, extension surface, tooling contracts")
    print( "     scripts/        — validate_intent, staleness_check, scope_lookup")
    return "instructions printed"


# ─── REGISTER ────────────────────────────────────────────────────────────────
# PLUGIN_REGISTRY and PluginRegistration are injected by the init loader.

PLUGIN_REGISTRY.register(PluginRegistration(
    id="skill-sdlc-generator",
    name="IDF SDLC v1.7.0 SKILL Generator",
    version="1.0.0",
    description="Generates a Claude SKILL package for IDF SDLC v1.7.0 implementation",
    hooks={
        "post_directories": _on_post_directories,
        "post_files": _on_post_files,
        "post_init": _on_post_init,
    },
    extra_directories=[
        SKILL_NAME,
        f"{SKILL_NAME}/references",
        f"{SKILL_NAME}/scripts",
    ],
    extra_files={},
))