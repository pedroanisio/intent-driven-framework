# Intent Framework — Software Engineering Domain

## Overview

This is the **canonical instantiation** of the Intent Framework for software engineering. It demonstrates how the universal intent model is specialized for a specific domain: managing intent in codebases, systems, and architectural decisions.

## Status

- **Version**: 1.6.1
- **Type**: Achieved (bootstrap proof of concept)
- **Coverage**: 28/28 core criteria passing (software domain)
- **Confidence**: Medium (domain transfer untested)

## What This Proves

The software bootstrap (v1.0.0 → v1.6.1) demonstrates that the Intent Framework:

✓ **Can govern its own evolution** — the manifesto, spec, and criteria evolved using the model's own mechanics
✓ **Works on non-code targets** — scope is document sections and structured data, not just code
✓ **Enables mechanical verification** — five-layer stack validates prose against formal criteria
✓ **Captures honest intent lifecycle** — 9 versioned transitions, each with forcing functions and rationale
✓ **Handles tension resolution** — completeness vs. scope creep, specificity vs. domain-agnosticism

## What This Does NOT Prove

✗ The framework works in domains without tooling (human-only verification)
✗ The framework works when verification is political (organizational governance)
✗ The framework is useful when domain change outpaces version cycles
✗ The `achieved_coverage` enum is meaningful outside software
✗ The achieved/aspirational distinction transfers to non-inherited systems

See [../intent-domain-agnostic-applicability.yml](../intent-domain-agnostic-applicability.yml) for the full domain-transfer thesis.

## Structure

```
software/
├── prose/
│   ├── intent-spec-software.md    # How software specializes the universal spec
│   └── examples/
│       ├── checkout-intent.yml
│       ├── auth-intent.yml
│       └── README.md
├── criteria/
│   └── intent-software-v1.6.1.yml # Software bootstrap proof YAML
├── tools/
│   ├── tests/                     # Pytest suite (software-specific tests)
│   ├── conftest.py                # Fixtures pointing to software files
│   └── pyproject.toml
├── lean/
│   ├── IntentFramework.lean       # Formal proofs (software assumptions)
│   ├── lakefile.lean
│   ├── lean-toolchain
│   └── README.md
├── _repo/                         # Example: how to structure intent repo in software
└── README.md                       # This file
```

## Domain-Specific Semantics

### Scope

In software, scope is expressed as:
- **Glob patterns** — `src/**/*.ts`, `lib/**/*.py`
- **Line ranges** — `file.ts:42-51`
- **Module/package references** — `@package/component`, `module::function`
- **CI/deployment boundaries** — `staging`, `production`

### Verification Layers

All five layers are applicable to software:

1. **Zod Schema** (`../../tools/validate.js`) — YAML shape, structural invariants
2. **Regex Scorer** (`../../tools/score_v150.py`) — keyword heuristics
3. **Pytest Suite** (`tools/tests/`) — criteria-first TDD workflow, CI-native
4. **NLP Validator** (`../../tools/nlp_validator.py`) — semantic entailment checks
5. **Lean Proofs** (`lean/IntentFramework.lean`) — formal verification of state machine

### Tensions

Common tensions in software intent:

- **Performance vs. Correctness** — intent for caching vs. intent for audit trail
- **Feature velocity vs. Stability** — intent for rapid iteration vs. intent for backward compatibility
- **Security vs. Usability** — intent for zero-trust architecture vs. intent for frictionless UX
- **Completeness vs. Scope Creep** — covered in the universal spec; demonstrated in v1.6.1

### Daily Practice

How software teams use intent framework:

**Declare**
```bash
# New intent block in code comment or YAML
intent:
  id: checkout-idempotency
  declares: "Checkout actions are idempotent; repeated calls with same cart/user return same result"
  scope: [src/checkout/**, tests/integration/checkout]
  version: 1.0.0
```

**Link**
```bash
git log --grep="checkout-idempotency"  # Track decisions tied to intent
```

**Record**
```bash
# Transition when intent changes
transition_log:
  - from: 1.0.0
    to: 1.1.0
    change_type: extension
    reason: "Added timeout handling for stuck payment processors"
```

**Check**
```bash
pytest tests/ -m checkout-idempotency     # TDD verification
npm run validate                           # Schema check
python3 -m anthropic ...                   # NLP semantic check
```

## Running the Software Domain Tests

```bash
# Install universal tools (once)
cd ../../tools && npm install

# Run software domain tests
cd ../../../_domains/software
python3 -m pytest tools/tests/ -v         # Full suite

# Run specific category
python3 -m pytest tools/tests/ -v -m model

# Score regex
python3 ../../tools/score_v150.py \
  prose/intent-spec-software.md \
  ../../prose/intent-spec-core.md \
  criteria/intent-software-v1.6.1.yml

# Validate schema
npm run validate criteria/intent-software-v1.6.1.yml
```

## Relation to Universal Framework

The universal framework (`../../prose/intent-spec-core.md`) defines:
- The data model (intent, transition, decision, tension, repo)
- The lifecycle (proposed → active → evolving → superseded → residual → retracted)
- The 28 completeness criteria (CC-01 through CC-27)
- The verification architecture (five-layer stack)

This domain specializes by defining:
- **Software-specific scope semantics** (globs, line ranges, module paths)
- **Software-specific verification** (CI hooks, code analysis tools)
- **Software-specific tensions** (performance vs. correctness, etc.)
- **Software example intents** (authentication, caching, idempotency, etc.)

## Next: Domain Transfer

To prove the framework is truly domain-agnostic, the following domains should be instantiated:

- **Regulatory Compliance** (`../regulatory/`) — intent from external authorities
- **Product Strategy** (`../product/`) — OKRs and north stars
- **AI Agent Guardrails** (`../ai-agent/`) — real-time intent evaluation
- **Organizational Governance** (`../governance/`) — cross-functional tensions

See [../intent-domain-agnostic-applicability.yml](../intent-domain-agnostic-applicability.yml) for the transfer thesis and what remains to be proven.

## References

- **Universal Manifesto**: `../../prose/intent-manifesto.md`
- **Universal Spec**: `../../prose/intent-spec-core.md`
- **Software Spec**: `prose/intent-spec-software.md`
- **Lean Proofs**: `lean/IntentFramework.lean`
- **Domain-Agnostic Thesis**: `../../intent-domain-agnostic-applicability.yml`
- **Verification Architecture**: `../../VERIFICATION.md`
