# Intent Framework Definition

## The Single Source of Truth

**File**: `intent-framework-definition.yml`

This file IS the Intent Framework specification. Everything else (manifesto, specs, criteria, tools, tests, domains) is derived from this declaration.

## What Makes This Special

This YAML file uses the Intent Framework to define itself:

- **CC-01**: States the problem (intent invisibility)
- **CC-02**: States the inversion (intent-first model)
- **CC-03**: Lists core principles with rationale
- **CC-04**: Defines entity schemas (intent, transition, tension, decision, repo)
- **CC-05**: Lists all closed enums
- **CC-07**: Describes the lifecycle state machine
- **CC-20**: Contains tooling surface (five-layer verification)
- **CC-27**: Has a complete transition log
- **And 18 more completeness criteria...**

This is **CC-18 (self-conformance) taken to its logical extreme**: the framework defines itself using its own mechanics.

## How to Read This File

The file has 11 main sections:

1. **Declaration** — what the framework is
2. **Principles** (CC-03) — core values with rationale
3. **Entity Schemas** (CC-04) — intent, transition, tension, decision, repo
4. **Enums** (CC-05) — all closed enumerations
5. **Lifecycle** (CC-07) — state machine for intents
6. **Completeness Criteria** (CC-01 through CC-27) — what "complete" means
7. **Verification Architecture** (CC-20) — five-layer stack (Zod, regex, pytest, NLP, Lean)
8. **Domain Instantiation** (CC-12) — how to create new domains
9. **Current Reality & Gaps** (CC-08a) — what's done, what remains
10. **Tensions** (CC-23) — conflicts and resolution strategies
11. **Evolution Log** (CC-27) — transition history (v1.0.0 → v2.0.0)

## The Meta-Beauty

Someone reading ONLY this file can:

✓ Understand what the Intent Framework is
✓ See its core principles and why they matter
✓ Learn the data model (entities and their relationships)
✓ Read the 28 completeness criteria (what makes a framework "complete")
✓ Understand the five-layer verification strategy
✓ See how to instantiate it in a new domain
✓ Know the current status and what remains
✓ Understand the tensions and resolution strategies
✓ See the evolution history (9 transitions, now restructured)

**And** they can see it's a perfect example of a well-formed intent block.

## Relation to Other Documents

| Document | How it's derived from this file |
|----------|---|
| `prose/intent-manifesto.md` | Human-readable rendering of "Declaration" + "Principles" |
| `prose/intent-spec-core.md` | Technical rendering of "Entity Schemas" + "Enums" + "Lifecycle" |
| `criteria/` | Extraction of "Completeness Criteria" section |
| `VERIFICATION.md` | Detailed explanation of "Verification Architecture" |
| `_domains/` | Implementation of "Domain Instantiation" section |
| `tools/` | Implementation of the five verification layers described here |
| `tests/` | Validation of the 28 criteria listed here |

**Every other document in the framework is a manifestation of this file.**

## This is the Specification

Stop reading separate specs. Read this file. Understand it. Everything else follows from it.

## How to Use It

### For Understanding the Framework
1. Read the declaration
2. Read the principles
3. Skim the entity schemas
4. Read the completeness criteria (CC-01 through CC-27)
5. Understand the verification architecture
6. Look at domain instantiation examples

### For Implementing the Framework
1. Extract the completeness criteria
2. Build verification tools to validate those criteria
3. Create boilerplate for new domains (see _template/)
4. Test that new domains satisfy the criteria

### For Extending the Framework
1. Add new fields to entity schemas (in ext: namespace)
2. Add new criteria (update completeness_criteria section)
3. Add new domains (follow the instantiation pattern)
4. Update the transition_log to record the change

## The Next Step

Once this file is in place and correct:

1. **All other documents become optional** — they're just renderings of this file
2. **Verification becomes mechanical** — check if the file passes CC-01 through CC-27
3. **Evolution is clear** — update this file, update the transition_log, regenerate everything else
4. **Domain-agnosticism is proven** — the framework uses itself to describe itself

## Validation

This file should pass all 28 completeness criteria. To validate:

```bash
# Layer 1: Zod schema validation
npm run validate intent-framework-definition.yml

# Layer 2: Regex scoring
python3 tools/score_v150.py \
  intent-framework-definition.yml \
  prose/intent-manifesto.md \
  prose/intent-spec-core.md

# Layer 3: Pytest
python3 -m pytest _domains/software/tools/tests/ -v

# Layer 4: NLP semantic check (optional, requires API key)
export ANTHROPIC_API_KEY=sk-...
python3 tools/nlp_validator.py intent-framework-definition.yml

# Layer 5: Lean proofs (optional, requires Lean 4)
cd _domains/software/lean && lake build
```

## One File to Rule Them All

This is the Intent Framework. Everything else is commentary.
