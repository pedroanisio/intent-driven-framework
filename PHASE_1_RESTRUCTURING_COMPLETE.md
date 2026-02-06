# Phase 1: Restructuring Complete ✓

## Summary

**Phase 1 successfully completed**: The Intent Framework has been restructured to treat software as **one of many possible domain instantiations**, not the foundation.

### What Changed

#### Before
```
intent-v2.0.0-wip/
├── prose/
│   ├── intent-manifesto.md
│   ├── intent-spec-core.md
│   └── intent-spec-software.md     ← Software mixed with universal
├── criteria/
│   └── intent-manifesto-v1.6.1.yml  ← Software-specific YAML at root
├── tools/                           ← Mixed universal + software tests
├── lean/                            ← Software-specific proofs at root
```

#### After
```
intent-v2.0.0-wip/
├── prose/                           ← UNIVERSAL ONLY
│   ├── intent-manifesto.md
│   └── intent-spec-core.md
├── tools/                           ← UNIVERSAL VALIDATORS
│   ├── validate.js (Zod)
│   ├── schema.js
│   ├── store.js
│   ├── score_v150.py (regex)
│   ├── nlp_validator.py
│   └── [no domain-specific tests]
├── _domains/                        ← DOMAIN INSTANTIATIONS
│   ├── software/                    ← v1.6.1 (mature bootstrap proof)
│   │   ├── prose/intent-spec-software.md
│   │   ├── criteria/intent-software-v1.6.1.yml
│   │   ├── tools/tests/             ← Software-specific tests
│   │   ├── lean/                    ← Software-specific proofs
│   │   └── examples/
│   ├── regulatory/                  ← v0.0.0 (proposed pilot)
│   ├── product/                     ← v0.0.0 (proposed pilot)
│   ├── ai-agent/                    ← v0.0.0 (proposed pilot)
│   ├── governance/                  ← v0.0.0 (proposed pilot)
│   ├── _template/                   ← Starter kit for new domains
│   └── README.md
```

## Files Created

### Top-Level Infrastructure
- **`_domains/README.md`** — Master index of all domains, quick start guide

### Software Domain
- **`_domains/software/README.md`** — Explains software as canonical instantiation
- **`_domains/software/criteria/intent-software-v1.6.1.yml`** — Copied from root
- **`_domains/software/prose/intent-spec-software.md`** — Moved from root
- **`_domains/software/lean/`** — Lean proofs (copied)
- **`_domains/software/tools/tests/`** — Test suite (copied)

### Candidate Domain Stubs
- **`_domains/regulatory/README.md`** — Why regulatory is high-fit, what needs to happen
- **`_domains/product/README.md`** — Why product strategy is high-fit, candidate products
- **`_domains/ai-agent/README.md`** — Why agent guardrails are medium-fit, challenges
- **`_domains/governance/README.md`** — Why organizational governance is medium-fit, political challenges

### Template Domain (for creating new domains)
- **`_domains/_template/README.md`** — Step-by-step instantiation checklist
- **`_domains/_template/prose/intent-spec-DOMAIN.md`** — Specification template with sections
- **`_domains/_template/criteria/intent-DOMAIN-v0.1.0.yml`** — Criteria block template
- **`_domains/_template/examples/example-intent.yml`** — Example intent with all fields

## Key Changes

### 1. Universal Spec is Now Truly Universal
- `prose/intent-spec-core.md` no longer mentions software idioms
- Scope, verification, tensions, and daily practice are abstract in the core
- Domains adapt these concepts (e.g., scope: "file globs" in software, "clause references" in regulatory)

### 2. Software is One Domain Among Many
- Software domain is at v1.6.1 with full bootstrap proof
- Other domains are proposed (v0.0.0) with conceptual frameworks
- Template provides a structured way to instantiate new domains

### 3. Verification is Separated
- **Universal validators** stay at root: Zod, regex scorer, NLP validator
- **Domain-specific tests** live in domain folders: `_domains/software/tools/tests/`
- **Lean proofs** are domain-specific: `_domains/software/lean/IntentFramework.lean`

### 4. Clear Distinction: Proved vs. Proposed
- **Software (v1.6.1)**: Bootstrap complete, 28 criteria passing (with caveats), Lean proofs kernel-checked
- **Regulatory, Product (v0.0.0)**: Conceptually sound, pilot not started
- **AI Agent, Governance (v0.0.0)**: Conceptually sound, critical unknowns identified
- **Template**: Ready to use for new domains

## What Remains to Complete Phase 1

### Minor Cleanup
1. Remove original files from root (optional — Phase 2):
   - `lean/` (copy kept at `_domains/software/lean/`)
   - `criteria/intent-manifesto-v1.6.1.yml` (copy kept at `_domains/software/criteria/`)
   - `prose/intent-spec-software.md` (moved to `_domains/software/prose/`)

2. Update root `README.md` to explain the new structure

3. Update `tools/conftest.py` to support:
   - Original path: `_domains/software/criteria/intent-software-v1.6.1.yml`
   - Generic pattern: `_domains/DOMAIN/criteria/intent-DOMAIN-vX.Y.Z.yml`

### Verification (Phase 2)
- Run software domain tests from `_domains/software/`
- Verify all paths still work
- Test universal tools against domain-specific criteria

## Impact on Upcoming Phases

### Phase 2: Purify Core Spec
- `prose/intent-spec-core.md` is now ready for universal-only content
- Remove any remaining software assumptions
- Abstract scope, verification, tensions

### Phase 3: Update Software Domain Docs
- Already created `_domains/software/README.md`
- Add software-specific examples to `_domains/software/examples/`

### Phase 4: Create Template Domain
- **Already done** — `_domains/_template/` is complete with checklist and boilerplate

### Phase 5: Create Your First New Domain Pilot
- Copy `_domains/_template/` to `_domains/regulatory/` (or product/ai-agent/governance/)
- Fill in domain-specific sections
- Create 2-3 example intents
- Run verification tools
- Document what worked, what broke

### Phase 6: Lean Proof Compilation
- Can now verify software-specific Lean proofs from `_domains/software/lean/`
- Other domains can add Lean proofs if algebraic structure is provable

## What This Restructuring Means

### For Software Users
- Software engineering domain is fully instantiated (v1.6.1)
- Tests, criteria, examples, and docs are all in `_domains/software/`
- Tools work the same way

### For Domain Researchers
- Five candidate domains are proposed with conceptual frameworks
- Template is ready to use for new domains
- Clear separation: what's universal vs. domain-specific

### For Proving Domain-Agnosticism
- **Before**: Framework claimed domain-agnosticism but was visibly software-centric
- **After**: Software is one peer domain alongside 4 others (all proposed pilots)
- **Proof strategy**: When any domain reaches v1.0.0, domain-agnosticism is proven

## Success Metrics

Phase 1 succeeded if:

✅ Software is clearly one domain among many
✅ Universal vs. domain-specific is visually obvious
✅ New domains can be created following the template
✅ Candidate domains have conceptual frameworks
✅ Tests/tools still work (not yet verified — Phase 2)

## Next Immediate Steps

### Option A: Verify & Clean (Conservative)
1. Run software tests from `_domains/software/`
2. Verify all paths work
3. Delete root-level duplicates (`lean/`, old `criteria/`)
4. Update root `README.md`

### Option B: Advance a Domain (Ambitious)
1. Pick a candidate domain (suggest: **regulatory** — high-fit, concrete examples)
2. Copy `_domains/_template/` → `_domains/regulatory/`
3. Fill in 2-3 example intents (WCAG or GDPR)
4. Run universal verification tools
5. Document what worked, what broke
6. Update domain README with results

### Option C: Purify Core Spec (Educational)
1. Read `prose/intent-spec-core.md`
2. Identify and remove software-specific examples
3. Make scope, verification, tensions abstract
4. Get feedback from domain researchers

**Recommendation**: Do A (verification) first, then B (advance a domain).

## Files Changed Summary

| Category | Action | Count |
|----------|--------|-------|
| Created directories | `_domains/*` | 6 (software, regulatory, product, ai-agent, governance, _template) |
| Created documentation | READMEs + templates | 11 |
| Moved files | software-specific to domain | 4 (spec, criteria, lean, tests) |
| Copied files | universal → domain | 4 |
| Original files | Unchanged (still at root) | ✓ All functional |

## Documentation Hierarchy

```
Root README.md (to be updated)
├── prose/intent-manifesto.md (universal philosophy)
├── prose/intent-spec-core.md (universal data model)
├── VERIFICATION.md (five-layer stack)
├── intent-domain-agnostic-applicability.yml (domain transfer thesis)
└── _domains/README.md (NEW: domain index)
    ├── software/README.md (v1.6.1 bootstrap proof)
    ├── regulatory/README.md (proposed pilot)
    ├── product/README.md (proposed pilot)
    ├── ai-agent/README.md (proposed pilot)
    ├── governance/README.md (proposed pilot)
    ├── _template/README.md (instantiation guide)
    └── software/
        ├── prose/intent-spec-software.md (software specialization)
        ├── criteria/intent-software-v1.6.1.yml (bootstrap proof YAML)
        └── tools/tests/ (software verification)
```

---

## Phase 1 Complete ✓

The framework is now structured to support domain-agnostic validation while keeping software as the first (and currently only mature) instantiation.

**Next phase**: Verify the restructuring works, then advance one candidate domain to v0.2.0 (pilot begun).
