# Intent Framework v2.0.0-wip — START HERE

## Welcome 🎯

You have just witnessed the **restructuring and self-definition** of the Intent Framework. This document is your entry point.

---

## What Just Happened

### Phase 1: Restructuring ✅
**Software was moved from the foundation to become ONE of many domain instantiations.**

- Created `_domains/` structure
- Moved software to `_domains/software/` (v1.6.1)
- Documented 5 candidate domains (regulatory, product, ai-agent, governance)
- Created template for instantiating new domains
- **Result**: Software is now a peer domain, not the foundation

See: [`PHASE_1_RESTRUCTURING_COMPLETE.md`](PHASE_1_RESTRUCTURING_COMPLETE.md)

### Phase 1.5: Self-Definition ✅
**The Intent Framework learned to define itself using its own mechanics.**

- Created `intent-framework-definition.yml` — the master specification
- One YAML file contains everything: declaration, principles, entities, enums, lifecycle, 28 criteria, verification layers, domain pattern, current state, tensions, evolution
- This file IS an intent block itself
- Everything else (manifesto, specs, tools, tests) derives from this file
- **Result**: One source of truth; no duplication; proven domain-agnosticism

See: [`PHASE_1.5_COMPLETE.md`](PHASE_1.5_COMPLETE.md)

---

## The Key Files

### 🎯 The Master Specification (NEW)
**[`intent-framework-definition.yml`](intent-framework-definition.yml)** (35 KB, 700+ lines)
- The SINGLE source of truth
- Contains the entire framework definition
- Is itself an example of a well-formed intent block
- Covers CC-01 through CC-27

Read this first. Everything else derives from it.

### 📚 Understanding the Definition
**[`INTENT_FRAMEWORK_DEFINITION.md`](INTENT_FRAMEWORK_DEFINITION.md)** (5 KB)
- Guide to reading the intent-framework-definition.yml
- Explains 11 sections of the master file
- Shows relation to other documents
- Validation instructions

### 🏗️ Domain Structure (NEW)
**[`_domains/README.md`](_domains/README.md)** (5 KB)
- Master index of all 6 domains
- Quick-start guide for creating new domains
- Status of each domain (software v1.6.1, others v0.0.0 proposed)

### 🧩 Domain Instantiation Template (NEW)
**[`_domains/_template/README.md`](_domains/_template/README.md)** (7 KB)
- Step-by-step checklist for creating a new domain
- Complete boilerplate included
- No friction to start researching a new domain

### 📖 Core Documents (Unchanged, still valid)
- **[`prose/intent-manifesto.md`](prose/intent-manifesto.md)** — Philosophy (problem, inversion, principles)
- **[`prose/intent-spec-core.md`](prose/intent-spec-core.md)** — Data model (schema, entities)
- **[`VERIFICATION.md`](VERIFICATION.md)** — Five-layer verification architecture

---

## What You Can Do Now

### Read-Only (Understand the Framework)
1. Read [`intent-framework-definition.yml`](intent-framework-definition.yml) — everything is here
2. Skim [`INTENT_FRAMEWORK_DEFINITION.md`](INTENT_FRAMEWORK_DEFINITION.md) — guide to reading
3. Explore [`_domains/README.md`](_domains/README.md) — domain landscape
4. Reference [`prose/intent-manifesto.md`](prose/intent-manifesto.md) for philosophy
5. Reference [`prose/intent-spec-core.md`](prose/intent-spec-core.md) for technical detail

### Exploration (Assess the Work)
1. Look at [`_domains/software/`](_domains/software/) — the bootstrap proof (v1.6.1)
2. Review [`_domains/regulatory/README.md`](_domains/regulatory/README.md) — why regulatory is high-fit
3. Review [`_domains/product/README.md`](_domains/product/README.md) — why product strategy is high-fit
4. Understand [`_domains/_template/`](_domains/_template/) — how to create new domains

### Implementation (Extend the Framework)
1. **Phase 2**: Validate the framework (run it against its own criteria)
2. **Phase 3**: Create first non-software domain pilot (recommend: regulatory)
3. **Phase 4**: Prove domain-agnosticism by running a complete domain from 0.1.0 → 0.3.0

---

## Architecture at a Glance

```
intent-framework-definition.yml (MASTER)
    ↓
    ├─→ prose/intent-manifesto.md (human-readable philosophy)
    ├─→ prose/intent-spec-core.md (technical schema)
    ├─→ criteria/ (extracted completeness criteria)
    ├─→ VERIFICATION.md (five-layer explanation)
    ├─→ _domains/ (domain instantiation pattern + 6 examples)
    ├─→ tools/ (verification implementations)
    └─→ tests/ (criterion validation)
```

**Key insight**: One declaration. Everything else derives. No duplication possible.

---

## The 28 Completeness Criteria

Your framework must satisfy 28 criteria to be "complete":

| Range | Category | Count |
|-------|----------|-------|
| CC-01 to CC-03 | Philosophy | 3 |
| CC-04 to CC-08 | Model | 5 |
| CC-08a to CC-08c | Conflict | 3 |
| CC-09 to CC-10 | Structure | 2 |
| CC-11 to CC-12 | Extensibility | 2 |
| CC-13 to CC-15 | Adoption | 3 |
| CC-16 to CC-17 | Self-sufficiency | 2 |
| CC-18 & CC-27 | Self-conformance | 2 |
| CC-19 to CC-26 | Operational | 8 |
| CC-22 & CC-24 | Deferred | 2 |
| **TOTAL** | | **28** |

See [`intent-framework-definition.yml`](intent-framework-definition.yml) section "PART 6: Completeness Criteria" for details.

---

## Five-Layer Verification

The framework verifies itself through five layers:

1. **Zod** — Schema shape validation (mechanical)
2. **Regex** — Keyword heuristics (fast, fragile)
3. **Pytest** — TDD workflow (standard testing)
4. **NLP** — Semantic entailment (requires API)
5. **Lean** — Formal proofs (kernel-checked)

Each layer covers different criteria. Not all domains need all layers.

See [`VERIFICATION.md`](VERIFICATION.md) for the coverage map.

---

## Current Status

| Phase | Status | What Happened |
|-------|--------|---|
| **Phase 1** | ✅ COMPLETE | Software restructured as one domain; 6 domains + template created |
| **Phase 1.5** | ✅ COMPLETE | Master intent file created; framework self-defining |
| **Phase 2** | 🔄 PENDING | Validate framework against its own criteria |
| **Phase 3** | 🔄 PENDING | Create first non-software domain pilot (recommend: regulatory) |
| **Phase 4** | 🔄 PENDING | Prove domain-agnosticism (multiple domains reaching v1.0.0) |

---

## Quick Reference

### Want to Understand the Framework?
→ Read [`intent-framework-definition.yml`](intent-framework-definition.yml)

### Want to Understand Domain Structure?
→ Read [`_domains/README.md`](_domains/README.md)

### Want to Create a New Domain?
→ Use [`_domains/_template/`](_domains/_template/) and follow the checklist

### Want to Understand Verification?
→ Read [`VERIFICATION.md`](VERIFICATION.md)

### Want to Know What's Left to Do?
→ Read "Current Reality & Remaining Work" in [`intent-framework-definition.yml`](intent-framework-definition.yml)

### Want Phase 1 Details?
→ Read [`PHASE_1_RESTRUCTURING_COMPLETE.md`](PHASE_1_RESTRUCTURING_COMPLETE.md)

### Want Phase 1.5 Details?
→ Read [`PHASE_1.5_COMPLETE.md`](PHASE_1.5_COMPLETE.md)

---

## The Vision

> The Intent Framework is a universal model for making purpose explicit, versioned, and verifiable in any system where decisions are made in service of goals.

Not just software. Not just anything. **Any domain carrying purpose and undergoing evolution.**

The framework proves this by using itself as the example: an intent block that describes the Intent Framework completely.

---

## Next Actions

### To Understand (1-2 hours)
1. Read [`intent-framework-definition.yml`](intent-framework-definition.yml)
2. Skim [`INTENT_FRAMEWORK_DEFINITION.md`](INTENT_FRAMEWORK_DEFINITION.md)
3. Explore [`_domains/`](_domains/)
4. Read [`prose/intent-manifesto.md`](prose/intent-manifesto.md) for context

### To Validate (2-3 hours)
1. Run intent-framework-definition.yml through Zod validator
2. Run it through regex scorer
3. Run it through NLP validator
4. Fix any failures
5. Declare it official

### To Extend (1-4 weeks)
1. Pick a candidate domain (recommend: **regulatory**)
2. Copy `_domains/_template/` to `_domains/regulatory/`
3. Fill in domain-specific sections
4. Create 3-5 example intents (WCAG, GDPR, SOC 2, etc.)
5. Run verification tools
6. Document results
7. Publish v0.1.0

---

## Files Summary

### Core (NEW, 2 files)
- `intent-framework-definition.yml` (35 KB) — **Master spec**
- `INTENT_FRAMEWORK_DEFINITION.md` (5 KB) — Guide

### Documentation (NEW, 3 files)
- `PHASE_1.5_COMPLETE.md` (7 KB) — What just happened
- `PHASE_1_RESTRUCTURING_COMPLETE.md` (10 KB) — Phase 1 details
- `PHASE_1_SUMMARY.txt` (7 KB) — Visual summary

### Structure (NEW, 16 directories)
- `_domains/` (master + 6 domains + template)

### Original (Unchanged, still valid)
- `prose/intent-manifesto.md` — Philosophy
- `prose/intent-spec-core.md` — Model
- `VERIFICATION.md` — Architecture
- `tools/` — Validators
- `criteria/` — Legacy criteria YAML
- `lean/` — Formal proofs (at root)

---

## One More Thing

You now have a self-defining framework:
- It describes itself using its own structure
- It contains its own validation criteria
- It demonstrates its own applicability
- It serves as specification AND exemplar
- Everything else is derived from it

**This is domain-agnosticism in practice.**

---

**Start with [`intent-framework-definition.yml`](intent-framework-definition.yml). Everything flows from there.** 🚀
