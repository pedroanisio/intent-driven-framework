# Intent Framework — DOMAIN Specification

## Overview

This document specifies how the Intent Framework is adapted for the [DOMAIN NAME] domain. It explains the domain-specific interpretations of universal concepts like scope, verification, and tension resolution.

[Write a 2-3 paragraph introduction explaining why intent matters in your domain.]

---

## Part I: Domain-Specific Semantics

### Scope Definition

**In the universal spec**, scope is abstract: "parts of the system this intent governs."

**In DOMAIN**, scope refers to:

[Describe what "scope" means in your domain. Examples:]
- Software: file paths and modules (`src/**/*.ts`, `services/auth::login()`)
- Regulatory: regulation sections and clauses (`GDPR Article 7`, `WCAG 2.1 Level AA`)
- Product: user journeys and feature areas (`checkout-flow`, `onboarding`)
- AI Agent: agent capabilities and decision boundaries (`customer-support-scope`, `billing-authority`)
- Governance: departments and functions (`sales-team`, `finance-leadership`)

**Your domain's scope semantics:**

```
[Describe your domain's scope format, syntax, and resolution rules]

Examples:
1. [scope example 1]
2. [scope example 2]
3. [scope example 3]
```

---

### Verification Layers

The Intent Framework includes five verification layers. Not all apply to every domain.

**In DOMAIN**, the applicable layers are:

| Layer | Tool | Applicable? | Rationale |
|-------|------|---|---|
| 1. Zod Schema | `validate.js` | ✓/✗ | [Why or why not] |
| 2. Regex Scorer | `score_v150.py` | ✓/✗ | [Why or why not] |
| 3. Pytest Suite | `tests/` | ✓/✗ | [Why or why not] |
| 4. NLP Validator | `nlp_validator.py` | ✓/✗ | [Why or why not] |
| 5. Lean Proofs | `IntentFramework.lean` | ✓/✗ | [Why or why not] |

---

### Tensions in DOMAIN

**In the universal spec**, tensions are cross-cutting conflicts between multiple intents. Resolving them requires a tradeoff and a decision-maker.

**In DOMAIN**, common tensions include:

[List 3-5 typical tensions in your domain. Examples:]

- Software: Performance vs. Correctness, Feature velocity vs. Stability
- Regulatory: Compliance cost vs. Business agility, Privacy vs. Usability
- Product: Growth vs. Risk, Speed to market vs. Product quality
- AI Agent: Helpfulness vs. Safety, Autonomy vs. Control
- Governance: Innovation vs. Stability, Centralization vs. Autonomy

**Your domain's tensions:**

1. **[Tension name]** — [Description of the two conflicting goals]
   - Resolution strategy: [How to decide the tradeoff]
   - Resolution owner: [Who decides]

2. **[Tension name]** — [Description]
   - Resolution strategy: [How to decide]
   - Resolution owner: [Who decides]

3. **[Tension name]** — [Description]
   - Resolution strategy: [How to decide]
   - Resolution owner: [Who decides]

---

## Part II: Schema Extensions

The universal core schema may be insufficient for your domain. This section defines domain-specific extensions in the `ext:` namespace.

[Delete this section if your domain needs no extensions.]

```yaml
# In DOMAIN intents, the ext: block looks like:
ext:
  DOMAIN:
    # Your domain-specific fields go here
    field1: type
    field2: type
```

**Example domains:**

- **Product**: `metric_name`, `target_value`, `measurement_method`, `data_source`
- **Regulatory**: `external_authority`, `amendment_date`, `sunset_date`, `grace_period`
- **AI Agent**: `confidence_threshold`, `fallback_action`, `escalation_owner`
- **Governance**: `stakeholders`, `approval_process`, `veto_rights`

**Your domain's extensions:**

```yaml
ext:
  DOMAIN:
    # Define what you need
```

---

## Part III: Daily Practice

How do practitioners in DOMAIN use the Intent Framework?

### 1. Declare

[How do people create new intents in your domain?]

```
Example for software:
  # Create intent block in codebase comment or YAML file
  # Reference in README with @intent-id

Example for product:
  # Declare as north star or OKR
  # Track in product roadmap

Example for regulatory:
  # Extract from regulatory text
  # Map to audit requirement
```

**In DOMAIN:**

---

### 2. Link

[How do people tie intent to decisions in your domain?]

```
Example for software:
  # git log --grep="intent-id"
  # Code review comments reference intent
  # PR description explains which intent this serves

Example for product:
  # Feature request linked to north star
  # Design doc cites governing intent

Example for regulatory:
  # Audit finding mapped to compliance intent
  # Process documented with reference
```

**In DOMAIN:**

---

### 3. Record

[How do people track intent evolution in your domain?]

```
Example for software:
  # Update version in YAML
  # Add transition_log entry
  # Explain what changed and why

Example for product:
  # Update metric target when goal changes
  # Document forcing function

Example for regulatory:
  # Track amendments with grace periods
  # Note superseded requirements
```

**In DOMAIN:**

---

### 4. Check

[How do people verify intent compliance in your domain?]

```
Example for software:
  # pytest tests/
  # npm run validate
  # npm run score
  # code review gates

Example for product:
  # Monthly metrics review
  # Assess achieved_coverage
  # Track progress toward aspirational

Example for regulatory:
  # Compliance audit
  # Evidence collection
  # Gap assessment
```

**In DOMAIN:**

---

## Part IV: Limitations and Open Questions

### What This Domain Instantiation Proves

- [Claim 1 — with evidence]
- [Claim 2 — with evidence]
- [Claim 3 — with evidence]

### What Remains Unproven

- [Unknown 1 — why it's unproven]
- [Unknown 2 — why it's unproven]
- [Unknown 3 — why it's unproven]

### Questions for Future Research

1. [Research question 1]
2. [Research question 2]
3. [Research question 3]

---

## References

- **Universal Manifesto**: `../../prose/intent-manifesto.md`
- **Universal Spec**: `../../prose/intent-spec-core.md`
- **Verification Architecture**: `../../VERIFICATION.md`
- **Domain-Agnostic Thesis**: `../../intent-domain-agnostic-applicability.yml`
