# Intent Framework v1.6.1

A self-contained declaration of the intent-driven software development
model, with formal verification of its own completeness.

## Status

**28/28 core criteria passing.** 2 deferred (CC-22 cross-repo, CC-24
schema governance) tracked with promote-when conditions.

## Structure

```
├── prose/
│   ├── intent-manifesto.md         # The manifesto (philosophy + practice)
│   └── intent-spec.md              # The specification (schema + contracts)
├── criteria/
│   └── intent-manifesto-v1.6.1.yml # Self-conforming criteria block
├── tools/
│   ├── validate.js                 # Zod v4 schema + structural validator
│   ├── schema.js                   # Zod type definitions
│   ├── store.js                    # Zustand flaw store (regression tracking)
│   ├── score_v150.py               # Regex scorer (28 CC, deterministic)
│   ├── nlp_validator.py            # NLP semantic scorer (16 CC, API-powered)
│   ├── tests/                      # Pytest suite — TDD prose validation (30 tests)
│   │   ├── criteria.py             # Criterion registry (declared before tests)
│   │   ├── evidence.py             # Evidence extraction (markers + gaps)
│   │   ├── conftest.py             # Fixtures, CLI options, custom reporting
│   │   └── test_*.py               # One file per category
│   ├── pyproject.toml              # Pytest configuration
│   └── package.json                # npm scripts for all tools
├── lean/
│   ├── IntentFramework.lean        # Lean 4 proofs (12 CC, kernel-checked)
│   ├── lakefile.lean               # Lean build config
│   ├── lean-toolchain              # v4.16.0
│   └── README.md                   # Provability map
├── VERIFICATION.md                 # Five-layer architecture + coverage map
├── intent-domain-agnostic-applicability.yml  # Domain-agnostic thesis
└── README.md                       # This file
```

## Five verification layers

| Layer | Tool | What it checks | Covers |
|-------|------|---------------|--------|
| 1 | `validate.js` (Zod) | YAML schema shape, structural invariants, transition log | Schema conformance |
| 2 | `score_v150.py` | Keyword presence, section existence, counts | 28 CC (fragile on prose) |
| 3 | `tests/` (pytest) | Criteria→evidence→verdict, TDD workflow, CI-native | 28 CC + 2 deferred |
| 4 | `nlp_validator.py` | Semantic content, entailment, sufficiency (LLM-as-judge) | 16 CC |
| 5 | `IntentFramework.lean` | Algebraic structure, state machine, invariants (kernel-checked) | 12 CC |

See [VERIFICATION.md](VERIFICATION.md) for the full coverage map.

## Quick Start

```bash
cd tools && npm install

# Layer 1: Zod validator — checks the criteria YAML
npm run validate

# Layer 2: Regex scorer — checks prose against all 28 criteria
npm run score

# Layer 3: Pytest suite — TDD prose validation
pip install pytest pyyaml
npm run test                             # full suite (28 passed, 2 xfailed)
python3 -m pytest tests/ -v -m conflict  # single category
python3 -m pytest tests/ -v -m core      # core only

# Layer 4: NLP semantic scorer (requires Anthropic API key)
export ANTHROPIC_API_KEY=sk-...
npm run score:nlp

# Layer 5: Lean 4 formal proofs
cd ../lean && lake build
```

## Version History

| Version | Change |
|---|---|
| 1.0.0 | Initial 17 criteria |
| 1.1.0 | current_reality, CC-08a, CC-18 |
| 1.2.0 | CC-08a/b/c split, CC-19–CC-24 |
| 1.3.0 | Tier system, CC-25, CC-26 |
| 1.4.0 | CC-27, scope correction |
| 1.4.1 | change_type enum canonicalization |
| 1.5.0 | All enum canonicalization |
| 1.5.1 | Prose gaps closed (28/28 core) |
| 1.6.0 | Lean/Zod/YAML sync, retracted status, achieved_coverage |
| 1.6.1 | Spec drift fixed: achieved_coverage placement, origin_type alignment |
