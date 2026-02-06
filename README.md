# Intent Driven Framework

A purpose governance model. Intent is a first-class entity — structured, versioned, and verifiable — across any domain where decisions serve goals that degrade, drift, or become invisible over time.

The domain is a parameter: software, policy, strategy, regulation, or the framework's own specification documents. The mechanics of declaring, versioning, tracking, and tension-checking purpose are invariant across these domains. What changes is the scope syntax, the artifact types, and the verification methods. The core does not.

**Status:** `proposed` · **Confidence:** `medium` · **Version:** `1.3.0` · **Schema:** `0.4.0`

Confidence is medium because no adopter outside the authorship context has attempted the framework. Internal rigor cannot substitute for external survivability.

---

## The Core Claim

Purpose can be made explicit, versioned, and verifiable regardless of what carries it. Code carries purpose. Policy carries purpose. Strategy carries purpose. Specifications carry purpose.

Intent is not derived from artifacts, decisions, or documentation. It has its own identity, lifecycle, and authority. Decisions serve intent. Artifacts implement decisions. The chain is always:

```
Intent → Decision → Artifact
```

## What the Framework Provides

**(a)** A data model sufficient to declare, version, and relate intents.

**(b)** A lifecycle model for intent evolution with semantic versioning (`proposed → active → evolving → superseded | residual | retracted`).

**(c)** A structural relationship between intent, decisions, and artifacts that is mechanically traversable, not merely documented.

**(d)** A tension model that makes conflicts between intents explicit, owned, and resolvable before they surface as failures.

**(e)** Adoption pathways that do not require comprehensive audit of existing systems — aspirational intent can be declared without understanding the current state.

**(f)** An operational cycle — Red / Green / Refactor — that governs how intent is declared, satisfied, and evolved.

## The Operational Cycle

The cycle is structurally isomorphic to Test-Driven Development. TDD says: no production code without a failing test. Intent Driven says: no decision without an unsatisfied intent.

| Phase | Name | Rule | TDD Parallel |
|-------|------|------|-------------|
| **Red** | Declare | No decision is justified without a red intent that demands it. Work without a red intent is drift. | Write a failing test. |
| **Green** | Satisfy | Build only what the red intent demands. Every decision references an intent. Every artifact traces to a decision. | Write the minimum code to pass the test. |
| **Refactor** | Evolve | No evolution without a green state to protect. Version bumps require a transition log entry. | Refactor while keeping tests green. |

The isomorphism is a design commitment, not yet a proven property. See FC-07 in the root intent for falsification conditions.

---

## Repository Structure

```
.
├── prose/
│   ├── intent-manifesto.md          # The philosophy — why this exists
│   └── intent-spec-core.md          # The universal data model
├── criteria/
│   ├── intent-manifesto-v1.6.1.yml  # 28 completeness criteria
│   └── intent-driven-framework-definition.yml  # Root intent declaration
├── lean/
│   ├── IntentDrivenFramework.lean   # Lean 4 proofs (10 CC kernel-checked)
│   ├── lakefile.lean
│   └── lean-toolchain
├── tools/
│   ├── validate.js                  # Zod schema validation
│   ├── schema.js                    # Entity schemas
│   ├── store.js                     # Intent store
│   ├── nlp_validator.py             # NLP semantic entailment (13 CC)
│   ├── pyproject.toml
│   ├── package.json
│   └── tests/
│       ├── conftest.py
│       ├── criteria.py              # Criteria definitions
│       ├── evidence.py              # Evidence scoring
│       ├── test_model.py            # Data model tests
│       ├── test_structure.py        # Structural tests
│       ├── test_self_conformance.py # Self-conformance checks
│       ├── test_philosophy.py       # Philosophy section tests
│       ├── test_adoption.py         # Adoption pathway tests
│       ├── test_operational.py      # Operational cycle tests
│       ├── test_conflict.py         # Tension/conflict tests
│       ├── test_extensibility.py    # Extension surface tests
│       ├── test_self_sufficiency.py # Sufficiency tests
│       └── test_deferred.py         # Deferred/future criteria
└── .flaw-state.json
```

## Validation Pipeline

Each stage gates the next. Fail fast, fail cheap. Later layers assume earlier guarantees hold.

```
Stage 1 ──→ Stage 2 ──→ Stage 3 ──→ Stage 4 ──→ Stage 5
Schema      Lean         Self-        NLP          Human
(ms)        (sec)        conformance  (sec-min)    (async)
                         (sec)
```

### Stage 1 — Schema Validation

```bash
node tools/validate.js
```

Zod checks that every YAML file is structurally valid: correct field names, types, enums, required fields present. The equivalent of "does it compile." Gates everything else.

### Stage 2 — Lean Proofs

```bash
cd lean && lake build
```

10 completeness criteria verified by the Lean 4 kernel (CC-04, CC-05, CC-06, CC-07, CC-08, CC-08b, CC-18, CC-23, CC-25, CC-27) plus structural properties for the operational cycle, provides-FC cross-references, and governance compliance. These are properties of the model, not the prose. If a proof breaks, the model's structural commitments have changed.

### Stage 3 — Self-Conformance Tests

```bash
cd tools && pytest tests/ -x
```

Checks that the framework's own artifacts conform to the rules the framework declares. Catches inconsistencies like metadata contradicting evidence (the bug that forced the 1.1.0 transition). Deterministic, no API calls. The `-x` flag stops on first failure.

### Stage 4 — NLP Semantic Entailment

```bash
export ANTHROPIC_API_KEY=sk-...
python tools/nlp_validator.py prose/intent-manifesto.md prose/intent-spec-core.md
```

13 prose-level criteria checked via Claude. Verifies that the prose actually says what the model requires it to say. Most expensive layer — run only when Stages 1–3 are green.

Options:
- `--dry-run` — show prompts without calling the API
- `--verbose` — print raw API responses
- `--min-conf N` — confidence threshold (default: 0.7)
- `--out FILE` — output path for results JSON

### Stage 5 — Human Review

5 criteria that NLP cannot reliably automate. Triggered by NLP validator output at release boundaries (per T-04), not on every commit.

### CI Script

```bash
#!/bin/bash
set -euo pipefail

echo "═══ Stage 1: Schema validation ═══"
node tools/validate.js

echo "═══ Stage 2: Lean proofs ═══"
(cd lean && lake build)

echo "═══ Stage 3: Self-conformance ═══"
(cd tools && pytest tests/ -x)

echo "═══ Stage 4: NLP semantic checks ═══"
python tools/nlp_validator.py prose/intent-manifesto.md prose/intent-spec-core.md

echo "═══ All automated stages green ═══"
```

### Coverage Architecture

```
┌──────────────────────────────────────────────────────┐
│  Lean 4          │  10 CC  │  Kernel-checked         │
├──────────────────┼─────────┼─────────────────────────┤
│  NLP validator   │  13 CC  │  Semantic entailment    │
├──────────────────┼─────────┼─────────────────────────┤
│  Human judgment  │   5 CC  │  Cannot automate        │
├──────────────────┼─────────┼─────────────────────────┤
│  Regex scorer    │  28 CC  │  Keyword heuristics     │
└──────────────────┴─────────┴─────────────────────────┘
```

---

## Key Concepts

### Intent as First-Class Entity

An intent has its own `id`, `version`, `lifecycle`, `scope`, `owner`, and `declares` field. It is not a comment, not an ADR, not documentation. It is a structured, addressable, governable entity that decisions serve and artifacts implement.

### Minimum Viable Intent

Five fields to start: `id`, `version`, `declares`, `scope`, `owner`. Everything else accretes as the intent matures. Adoptability wins when it conflicts with rigor (T-02).

### Semantic Versioning for Intent

| Change | Type | Governance Consequence |
|--------|------|----------------------|
| Prior artifacts may no longer satisfy | **MAJOR** | Triggers artifact review |
| New commitments added, prior still valid | **MINOR** | No artifact review required |
| Clarification, no commitment change | **PATCH** | Metadata only |

### Tensions

Structural conflicts between legitimate goals, declared explicitly so they cannot be re-litigated silently. Each tension names what it is between, has a typed resolution strategy, an owner, and a staleness threshold.

### Failure Modes

The framework names six ways it fails when adopted badly:

- **FM-01 Performative intent** — declarations exist but are never checked or referenced
- **FM-02 Over-specification** — every function has its own intent; signal drowns in noise
- **FM-03 Version inflation** — MAJOR bumps for PATCH changes; review fatigue
- **FM-04 Tension avoidance** — teams refuse to name political conflicts
- **FM-05 Cargo cult structure** — template-generated files, never modified
- **FM-06 Green-washing** — claiming satisfaction without updating evidence

---

## Adoption

Three entry strategies, none requiring comprehensive audit:

**Pain-first.** Start with one real intent driven by a real pain point. Not a comprehensive declaration — a single commitment that matters to someone on the team today.

**Next-touch.** The next time anyone touches a file in undeclared territory, they declare intent for it. Coverage grows organically with the work, not ahead of it.

**Amnesty.** Existing systems get aspirational intents that acknowledge the gap between what is and what should be. No pretense of current conformance. The `current_reality` field carries the honest assessment.

---

## Current Reality

The framework has been validated against exactly one non-trivial target: itself. Six versioned transitions, 28 completeness criteria, Lean proofs, Zod validation — all on a non-software target (specification documents, criteria YAML, principle declarations).

What remains unproven: whether the model survives adoption by someone who did not design it, on a system they did not build, in an organization with real political constraints on tension declaration.

Absence of adoption is not grounds for retraction. Structural refutation is. A correct model that nobody uses is a distribution failure, not a model failure.

---

## Setup

### Prerequisites

- Node.js ≥ 18
- Python ≥ 3.11
- Lean 4 (via `elan`)

### Install

```bash
# JavaScript dependencies (Zod schema validation)
cd tools && npm install

# Python dependencies (pytest, NLP validator)
cd tools && pip install -e .

# Lean toolchain
cd lean && elan toolchain install $(cat lean-toolchain)
```

### Verify

```bash
# Run the full pipeline
node tools/validate.js && \
  (cd lean && lake build) && \
  (cd tools && pytest tests/ -x)
```

---

## Falsifiable Claims

The framework makes eight falsifiable claims. If any is falsified, the intent must evolve or be retracted.

| ID | Claim | Status |
|----|-------|--------|
| FC-01 | Intent is a first-class entity with its own lifecycle | `supported` |
| FC-02 | Intent → Decision → Artifact chain is mechanically traversable | `supported` |
| FC-03 | Aspirational intent can be declared without understanding current state | `supported` |
| FC-04 | The framework is domain-invariant | `partially_verified` |
| FC-05 | The framework is self-contained for adoption | `unverified` |
| FC-06 | Semantic versioning communicates governance-relevant impact | `supported_in_theory` |
| FC-07 | Red/Green/Refactor is operationally isomorphic to TDD | `supported_in_theory` |
| FC-08 | Tensions between intents are made explicit and their resolution is tracked | `supported` |

---

## License

TBD

## Contributing

The most valuable contribution right now is attempting adoption. If you use this framework on a real system — software or otherwise — the result, whether success or failure, is the evidence the framework most needs. See RW-01 and RW-02 in the root intent declaration.