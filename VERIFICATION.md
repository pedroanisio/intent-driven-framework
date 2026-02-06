# Intent Framework v1.6.1 — Verification Architecture

## Five-Layer Stack

```
┌──────────────────────────────────────────────────────────────┐
│  Layer 5: Lean 4 (lean/IntentFramework.lean)                 │
│  Proves: algebraic structure, state machine, invariants      │
│  Strength: kernel-checked dependent types, highest guarantee │
│  Covers: 12 CC                                               │
├──────────────────────────────────────────────────────────────┤
│  Layer 4: NLP Semantic (tools/nlp_validator.py)              │
│  Checks: entailment, sufficiency, actionability              │
│  Strength: reads prose like a human, structured verdicts     │
│  Covers: 16 CC (all non-Lean criteria)                       │
├──────────────────────────────────────────────────────────────┤
│  Layer 3: Pytest Suite (tools/tests/)                        │
│  Checks: criteria→evidence→verdict, TDD prose workflow       │
│  Strength: standard runner, markers, CI-native, portable     │
│  Covers: 28 CC core + 2 deferred (xfail)                    │
├──────────────────────────────────────────────────────────────┤
│  Layer 2: Regex Scorer (tools/score_v150.py)                 │
│  Checks: keyword presence, section existence, counts         │
│  Strength: fast, deterministic, no API dependency            │
│  Covers: 28 CC (all, but fragile on prose-heavy criteria)    │
├──────────────────────────────────────────────────────────────┤
│  Layer 1: Zod Schema + Flaw Store (tools/validate.js)        │
│  Checks: YAML shape, structural rules, regression tracking   │
│  Strength: runtime type checking, temporal flaw lifecycle     │
│  Covers: schema conformance + 6 structural invariants        │
└──────────────────────────────────────────────────────────────┘
```

## Coverage Map

```
CC    What it checks                     Lean  NLP   Pytest Regex  Zod
──────────────────────────────────────────────────────────────────────────
01    Problem stated                       ·    T2     ✓     ✓     ·
02    Inversion stated                     ·    T2     ✓     ✓     ·
03    Principles with rationale            ·    T1     ✓     ✓     ·
04    Entity schemas complete              ✓    ·      ✓     ✓     ·
05    Enums closed                         ✓    ·      ✓     ✓     ✓
06    Relationships bidirectional          ✓    ·      ✓     ✓     ·
07    Lifecycle state machine              ✓    ·      ✓     ✓     ✓
08    Achieved/aspirational distinct       ✓    ·      ✓     ✓     ·
08a   Contradiction → supersession         ·    T3     ✓     ✓     ·
08b   Pre-transition resolution check      ✓    ·      ✓     ✓     ·
08c   Scope overlap detectable             ·    T3     ✓     ✓     ·
09    Repo structure specified             ·    T1     ✓     ✓     ·
10    Reader can create _repo/             ·    T3     ✓     ✓     ·
11    Plugin architecture + example        ·    T3     ✓     ✓     ·
12    Extension surface semantics          ·    T3     ✓     ✓     ·
13    Adoption sequence actionable         ·    T1     ✓     ✓     ·
14    Legacy without audit                 ·    T3     ✓     ✓     ·
15    ≥3 practical entry points            ·    T1     ✓     ✓     ·
16    No external concepts                 ·    T2     ✓     ✓     ·
17    Daily practice concrete              ·    T1     ✓     ✓     ·
18    Self-conformance (bootstrap)         ✓    ·      ✓     ✓     ✓
19    declares quality guidance            ·    T2     ✓     ✓     ·
20    Tooling surface section              ·    T3     ✓     ✓     ·
21    Adoption ramp                        ·    T2     ✓     ✓     ·
23    Tension staleness contract           ✓    ·      ✓     ✓     ·
25    Deprecation ceremonies               ✓    ·      ✓     ✓     ·
26    Failure mode catalogue               ·    T1     ✓     ✓     ·
27    Transition log integrity             ✓    ·      ✓     ✓     ✓
──────────────────────────────────────────────────────────────────────────
TOTALS                                    12   16     30     28     4

Legend:
  ✓  = covered (Lean: proven; Pytest: tested; Regex: heuristic; Zod: validated)
  T1 = NLP Tier 1 — regex→semantic, high uplift
  T2 = NLP Tier 2 — entailment, medium uplift
  T3 = NLP Tier 3 — LLM-as-judge, reasoning required
  ·  = not covered by this layer
```

## The Pytest Layer

The pytest suite (`tools/tests/`) implements test-driven prose validation.
Three files define the architecture:

**`criteria.py`** — the registry. All 30 criteria declared as frozen
dataclasses BEFORE any tests or prose exist. Each carries `id`,
`category`, `tier`, `test`, `verifiable_by`, and `depends_on`.

**`evidence.py`** — the check functions. Each `check_cc*()` returns an
`Evidence` object with `passed`, `markers` (what was found), and `gaps`
(what was missing). Failure messages are actionable.

**`test_*.py`** — one file per category. Pytest markers enable slicing:
`-m conflict`, `-m core`, `-m deferred`. CLI options make the suite
portable: `--manifesto`, `--spec`, `--criteria-yml`.

Deferred criteria (CC-22, CC-24) are marked `@pytest.mark.xfail` — they
show as XFAIL in green runs. When a promotion condition is met, remove
the marker; the test goes red, forcing the prose to be written.

**The TDD workflow for prose:**
1. Declare a new criterion in `criteria.py`
2. Write the evidence check in `evidence.py`
3. Add the test in the appropriate `test_*.py`
4. Run pytest → see red
5. Write the prose that satisfies it
6. Run pytest → see green

The invariant: prose never gets ahead of criteria.

## NLP Tier Definitions

**Tier 1 — HIGH confidence (6 CC):** Regex checks keyword existence.
NLP checks whether the *concept* is present and *well-formed*. These
gain the most from NLP — going from "does the word exist?" to "is the
rationale genuine?" CC-03, CC-09, CC-13, CC-15, CC-17, CC-26.

**Tier 2 — MEDIUM confidence (5 CC):** Entailment checks — "does
passage X *entail* claim Y?" CC-01, CC-02, CC-16, CC-19, CC-21.

**Tier 3 — LOW confidence (5 CC):** Multi-step sufficiency reasoning.
NLP helps marginally; human judgment dominates. CC-08a, CC-08c, CC-10,
CC-14, CC-20.

## Running

```bash
# Layer 1: Zod schema + structural validators + flaw tracking
cd tools && npm install && npm run validate

# Layer 2: Regex scorer (fast, deterministic, no API)
npm run score

# Layer 3: Pytest suite (standard runner, CI-native)
pip install pytest pyyaml
npm run test                               # full suite
python3 -m pytest tests/ -v -m conflict    # single category
python3 -m pytest tests/ -v -m deferred    # deferred only

# Layer 4: NLP semantic scorer (requires ANTHROPIC_API_KEY)
export ANTHROPIC_API_KEY=sk-...
npm run score:nlp

# Layer 4 dry run (shows prompts, no API calls)
npm run score:nlp:dry

# Layer 5: Lean 4 formal proofs
cd ../lean && lake build
```

## Disagreement Resolution

When layers agree, confidence is highest. When they disagree:

| Conflict | Resolution |
|---|---|
| Regex ✓, NLP ✗ | NLP wins — regex had a false positive (keyword matched but concept absent) |
| Regex ✗, NLP ✓ | NLP wins — regex had a false negative (keyword variant missed) |
| Lean ✓, anything ✗ | Lean wins — kernel-checked proof is strongest |
| Pytest ✗ (evidence gaps listed) | Actionable — fix the prose where gaps are identified |
| NLP uncertain (low confidence) | Fall back to human judgment |
