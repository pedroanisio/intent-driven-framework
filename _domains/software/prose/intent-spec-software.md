# The Intent Specification — Software Engineering Domain Layer

## Instantiating the Core for Codebases

This document defines how the domain-agnostic Intent Framework core is instantiated for software engineering. It specifies scope as file paths, the self-model as a repository directory, verification as CI integration, and provides worked examples from software systems. Read the *Intent Specification — Core* first. This document assumes familiarity with the general data model.

---

## I. Scope Semantics

In software, scope is **file glob patterns**. An intent's `scope` array contains glob expressions that bind the intent to specific parts of the codebase:

```yaml
scope: [src/checkout/**]                    # all files under checkout
scope: [src/billing/calculations/**]        # a specific module
scope: [src/payments/**, lib/payments/**]    # multiple paths
scope: ["*.proto"]                          # all protocol buffers
```

**Scope lookup** walks the intent index and returns every intent whose glob pattern matches a queried file path. Results are ordered by specificity: `src/billing/calculations/**` is more specific than `src/billing/**`, and the more specific intent is returned first.

**Residual areas** in transitions use the same glob syntax. The core schema's `affected_areas` becomes `code_paths` in software practice:

```yaml
residual:
  code_paths: [src/billing/legacy-calc/**]   # code still serving old version
  risk: "Incorrect tax calculation on international orders"
  migration_intent: "All calculations use intent-billing-v3 ordering"
```

---

## II. The Repository Structure

The self-model lives in a `_repo/` directory at the repository root:

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

This structure is versioned with the code, visible to every engineer, lintable in CI. The underscore prefix signals meta — this is the system's knowledge about itself, not application code.

### Manifest

The core manifest instantiates for repositories as:

```yaml
repo:
  name: string
  declares: string             # top-level intent of this repository
  domain: string
  boundary_type: enum          # service | library | platform | gateway
  version: semver
  schema_version: semver

  serves:
    - org_intent: string       # organizational intents this repo supports

  depends_on_intents:
    - repo: string
      intent: string
      minimum_version: semver

  plugins: string              # path to plugins/registry.yaml
```

---

## III. CI Verification

In software, schema verification runs in CI on every commit that modifies `_repo/`. The verification contract from the core spec is implemented as:

**Tier 1 — Structural (blocks merge):**
- Every YAML file in `_repo/intents/` parses and conforms to the core schema.
- Extension fields conform to their registered schemas.
- All `intent_ref` pointers resolve to existing YAML files.

**Tier 2 — Relational (blocks merge):**
- `serves`, `tensions`, and `supersedes` resolve to existing intents.
- `depends_on_intents` references resolve to reachable repos and intent IDs.
- No `proposed` intent duplicates an `active` intent's `id`.
- Extension validators from `plugins/registry.yaml` pass.

**PR review gates.** The next-touch rule is enforced through a PR gate: when a PR modifies files in a scope governed by an active intent, the PR template surfaces the governing intent(s) and prompts the author to confirm the change is consistent. When a PR modifies files in an undeclared scope, the gate operates in advisory or enforcement mode depending on the team's adoption phase.

### Lifecycle Event Propagation

When an intent transitions, CI triggers lifecycle hooks. For cross-repo dependencies:

1. CI scans `depends_on_intents` across repos on MAJOR bumps.
2. Downstream repos receive a notification (issue, PR, or webhook).
3. Downstream teams evaluate their own intents against the changed dependency.

### Scope Lookup CLI

A command-line tool answers "which intents govern this file?":

```bash
intent-lookup src/billing/calculations/tax.py
# Returns:
#   intent-billing-calc-ordering v1.0.0 [critical, active]
#   intent-billing-auditable v2.1.0 [high, aspirational]
```

---

## IV. Worked Examples

### Forensic Intent (from incident)

```yaml
intent:
  id: intent-billing-calc-ordering
  version: 1.0.0
  declares: "Billing calculations must apply discounts before taxes. 
             Reversing this order produces incorrect totals that 
             propagate to invoices and revenue reporting."
  scope: [src/billing/calculations/**]
  status: active
  priority: critical

  origin:
    type: incident
    ref: "INC-2024-1847"
    relationship: derived_from
  
  context: "Discovered after Q3 revenue discrepancy. This ordering 
            requirement was known to the original billing team but 
            never documented. Three engineers have independently 
            introduced bugs by assuming the opposite order."
```

### Legacy Intent (unknown)

```yaml
intent:
  id: intent-pricing-engine-legacy
  version: 0.1.0
  declares: "UNVERIFIED — this module appears to implement tiered 
             pricing with volume discounts, but the logic has not 
             been fully traced. Edge cases around mid-cycle plan 
             changes are not understood."
  scope: [src/pricing/engine/**]
  status: active
  priority: high

  origin:
    type: engineering
    ref: "intent-archaeology-2025-q1"
    relationship: discovered_in

  confidence: low
  needs_verification: true
  last_affirmed: null
```

### Cross-Discipline Tension

```yaml
tension:
  id: tension-checkout-speed-vs-fraud-verification
  between:
    - intent-checkout-under-60s          # UX
    - intent-fraud-verification-steps    # Security
  declared: 2025-03-15
  status: active
  description: "UX requires checkout completable in under 60 seconds.
               Security requires multi-step fraud verification on 
               high-risk transactions."
  cross_discipline: true
  disciplines: [ux, security]

  current_resolution:
    strategy: "Risk-based step-up authentication. Low-risk transactions 
              skip verification. High-risk transactions get SMS challenge 
              with 15-second async window."
    decided: 2025-03-20
    applies_to: [1.2.0, 2.0.0]
    decision_ref: decision-checkout-stepup-auth

  resolution_owner: vp-product
  escalation_path: "CTO if resolution_owner cannot break deadlock"
  last_reviewed: 2025-06-01
```

### The Adoption Sequence (Software-Specific)

1. **Pick one service that hurts.** The one where people keep getting burned.
2. **Declare aspirational intents.** "We intend billing to be auditable." "We intend deploys to be independently reversible." Honest `current_reality` assessments.
3. **Run an intent amnesty.** Two hours. `0.x.x` declarations.
4. **Create `_repo/`.** Add manifest, intents to `intents/active/`. Commit.
5. **Adopt the next-touch rule.** Every PR either references an existing intent or declares a new one.
6. **Feed incidents in.** Every postmortem → at least one intent or transition.
7. **Let the gap close.** Achieved coverage grows. `0.x.x` → `1.0.0`.
8. **Expand to the next service.** By demonstration, not mandate.
