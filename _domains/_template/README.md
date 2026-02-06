# Intent Framework — Domain Instantiation Template

## How to Create a New Domain Instantiation

This folder contains a template for instantiating the Intent Framework in a new domain. Follow this checklist to create a domain-specific version of the framework.

## Quick Start

```bash
# 1. Copy this template
cp -r _domains/_template _domains/YOUR_DOMAIN

# 2. Create the required files (see below)
cd _domains/YOUR_DOMAIN

# 3. Replace DOMAIN with your domain name throughout:
sed -i 's/DOMAIN/YOUR_DOMAIN/g' prose/*.md criteria/*.yml examples/*.md

# 4. Customize each file (see sections below)

# 5. Test with universal tools
python3 ../../tools/score_v150.py \
  prose/intent-spec-YOUR_DOMAIN.md \
  ../../prose/intent-spec-core.md \
  criteria/intent-YOUR_DOMAIN-v0.1.0.yml

# 6. Document lessons learned
```

## Checklist: What You Need

### Phase 1: Foundation (Week 1)

- [ ] Create `prose/intent-spec-DOMAIN.md` — how your domain specializes the universal spec
- [ ] Create `criteria/intent-DOMAIN-v0.1.0.yml` — your domain's bootstrap proof
- [ ] Document scope semantics — how "scope" works in your domain
- [ ] Identify verification layers — which of the five layers apply?

### Phase 2: Examples (Week 2)

- [ ] Create 2-3 example intents in `examples/example-intent.yml`
- [ ] Document a real-world case study
- [ ] Show how tensions work in your domain

### Phase 3: Validation (Week 3)

- [ ] Run universal tools: validate, score, NLP check
- [ ] Address validation errors
- [ ] Document what transferred vs. what broke

### Phase 4: Documentation (Week 4)

- [ ] Write domain-specific README explaining applicability
- [ ] Document future work / unproven claims
- [ ] Link back to universal framework

---

## Files to Create

### 1. `prose/intent-spec-DOMAIN.md`

**Purpose**: Explain how your domain specializes the universal spec.

**Template sections**:
```markdown
# Intent Framework — DOMAIN Specification

## Overview
[Brief description of the domain and why intent matters in it]

## Differences from Universal Core

### Scope Semantics
In the universal spec, scope is abstract: "parts of the system this intent governs."
In DOMAIN, scope is: [describe your domain's scope concept]

Examples:
- Software: `src/**/*.ts` (file paths)
- Regulatory: `GDPR Article 7` (clause references)
- Product: `checkout-flow` (user journey)
- Governance: `sales-department` (organizational unit)

### Verification Layers
The universal framework includes five verification layers:
1. Zod Schema
2. Regex Scorer
3. Pytest Suite
4. NLP Validator
5. Lean Proofs

In DOMAIN, applicable layers are: [list which apply and why]

Example:
- Regulatory: layers 1, 2, 3 (NLP not applicable; Lean proofs rare)
- AI Agent: layers 1, 2, 4 (real-time evaluation; tests not applicable)

### Tensions in DOMAIN
The universal spec defines tensions as cross-domain conflicts.
In DOMAIN, common tensions include: [list domain-specific tensions]

Example:
- Software: performance vs. correctness
- Regulatory: compliance cost vs. business agility
- Product: growth vs. risk, speed vs. quality
- Governance: innovation vs. stability

## Schema Extensions

Does your domain need fields beyond the universal core?

```yaml
ext:
  DOMAIN:
    # Add domain-specific fields here
    # Example for product: metric_name, target_value, data_source
    # Example for regulatory: external_authority, amendment_date
```

## Daily Practice

How do teams in DOMAIN use the framework?

Describe the typical workflow:
1. Declare intent (what creates/updates an intent?)
2. Link intent (what ties intent to decisions?)
3. Record transitions (what triggers a version bump?)
4. Check compliance (how is intent verified?)
```

### 2. `criteria/intent-DOMAIN-v0.1.0.yml`

**Purpose**: Declare your domain's bootstrap proof.

**Template**:
```yaml
intent:
  id: intent-framework-DOMAIN
  version: 0.1.0
  schema_version: 0.1.0

  declares: >
    [Brief statement of what this instantiation proves]

    Example for software:
    "The Intent Framework can govern software engineering decisions."

    Example for regulatory:
    "The Intent Framework can make compliance requirements explicit and versioned."

  intent_type: aspirational

  # Describe what the current state is
  current_reality:
    state: >
      [Describe where the domain instantiation currently stands]

      Example: "Pilot applied to WCAG 2.1 accessibility standard.
      Extracted 15 key requirements as intent blocks. Running verification
      against sample web application."

    remaining_work: >
      [What still needs to happen]

      Example: "Automated accessibility testing (WAVE, Axe) integration.
      Real-time guardrail enforcement in design review workflow."

    last_assessed: "2026-02-06"

  # Scope: what this instantiation covers
  scope:
    primary:
      - prose/intent-spec-DOMAIN.md
    implicit:
      - examples/
      - This criteria block

  priority: high
  status: proposed
  owner: [Your name/team]
  confidence: low  # because this is a pilot

  origin:
    type: engineering
    ref: "domain-instantiation-pilot"
    relationship: derived_from

  # What this domain transfer proves vs. what remains unproven
  ext:
    domain_transfer:
      proven_by_pilot:
        - "Core mechanic works in DOMAIN context"
        - "Scope semantics transfer without major modification"
        # Add what you learned

      unproven:
        - "Scalability beyond pilot"
        - "Political viability in larger organizations"
        # Add what's still unknown
```

### 3. `examples/example-intent.yml`

**Purpose**: Show what a real intent looks like in your domain.

**Template**:
```yaml
intent:
  id: example-DOMAIN-intent-1
  version: 1.0.0

  declares: >
    [A specific, falsifiable claim in your domain]

    Examples:
    - Software: "Checkout is idempotent; repeated calls return same result"
    - Regulatory: "User consent is explicit, documented, and revocable"
    - Product: "Conversion rate reaches 4% by Q3 2024"
    - AI Agent: "Agent never executes DELETE operations on user data"

  intent_type: [achieved | aspirational]

  scope:
    - [Domain-specific scope reference(s)]

  # If aspirational, describe the gap
  current_reality:
    description: >
      [Current state — what is vs. what should be]
    gaps:
      - [specific areas that fall short]

  achieved_coverage: [none | minimal | partial | substantial | full]

  origin:
    type: [engineering | product | regulatory | ...]
    ref: [external reference]
    relationship: [derived_from | motivated_by | ...]

  tensions:
    - ref: [related intent that conflicts]
      description: >
        [How they conflict]
      resolution_strategy: >
        [How the tradeoff is being made]

  transition_log:
    - from: 0.0.1
      to: 1.0.0
      change_type: [clarification | extension | breaking | ...]
      reason: [Why this changed]
      forcing_function: [What prompted the change]
```

---

## Domain-Specific Guidance

### Defining Scope

The universal spec says scope is "parts of the system this intent governs."

In your domain, scope is domain-specific:

| Domain | Scope Concept | Examples |
|--------|---|---|
| Software | Code modules, files | `src/**/*.ts`, `services/auth/`, `util::hash` |
| Regulatory | Regulations, clauses | `GDPR Article 7`, `WCAG 2.1 Level AA`, `SOC 2 CC-7.2` |
| Product | User journeys, features | `checkout-flow`, `onboarding`, `account-settings` |
| AI Agent | Capabilities, boundaries | `customer-support-scope`, `payment-processing-boundary` |
| Governance | Departments, functions | `sales-team`, `engineering`, `executive-team` |

**Your scope format**:

---

### Choosing Verification Layers

Not every domain needs all five layers. Choose what makes sense:

| Layer | When to Use | Example |
|-------|---|---|
| 1. Zod Schema | Always | Validate YAML structure |
| 2. Regex Scorer | When prose is the target | Check for keywords |
| 3. Pytest Suite | When TDD workflow exists | Test-first validation |
| 4. NLP Validator | When semantic judgment matters | Falsifiability checks |
| 5. Lean Proofs | When formal proof is feasible | Mathematical properties |

**For software**: All 5 apply
**For regulatory**: 1, 2, 3 apply (maybe 4 for NLP semantic checks on requirements; Lean is overkill)
**For product**: 1, 2, 4 apply (metrics are hard to formalize; no Lean proofs)
**For AI agent**: 1, 2, 4 apply (real-time evaluation, no formal proof)
**For governance**: 1, 2 apply (human judgment dominates; NLP helps but doesn't solve politics)

---

## Testing Your Domain Instantiation

Once you've created the files, run the universal tools:

```bash
# 1. Schema validation (Layer 1)
npm run validate criteria/intent-DOMAIN-v0.1.0.yml

# 2. Regex scoring (Layer 2)
python3 ../../tools/score_v150.py \
  prose/intent-spec-DOMAIN.md \
  ../../prose/intent-spec-core.md \
  criteria/intent-DOMAIN-v0.1.0.yml

# 3. NLP semantic check (Layer 4)
export ANTHROPIC_API_KEY=sk-...
python3 ../../tools/nlp_validator.py \
  prose/intent-spec-DOMAIN.md \
  ../../prose/intent-spec-core.md
```

---

## What to Document

After completing your pilot, document:

1. **What transferred** — Which parts of the universal spec worked without modification?
2. **What broke** — Which assumptions didn't apply?
3. **Domain-specific patterns** — What unique structures did your domain need?
4. **Unproven claims** — What do you still need to test?
5. **Lessons learned** — What surprised you?

---

## Next Steps

When your domain instantiation is complete:

1. **Update root README** with a link to your domain
2. **Update VERIFICATION.md** with domain-specific verification status
3. **Submit feedback** on what the universal spec should change

The goal is not perfection — it's **evidence**. Show what works, document what doesn't, and help the framework evolve.
