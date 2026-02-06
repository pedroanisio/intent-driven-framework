# Intent Framework — Domain Instantiations

This folder contains domain-specific instantiations of the Intent Framework. The framework itself is domain-agnostic, but its application is domain-specific.

## Overview

The **general framework** (root-level `prose/` and general `tools/`) defines:
- The manifesto (philosophy, problem, inversion, principles)
- The core specification (data model, schema, lifecycle, 28 criteria)
- The five-layer verification stack (Zod, regex, pytest, NLP, Lean)

Each **domain folder** specializes the framework for a specific context by adding:
- Domain-specific specification (how scope, verification, tensions work in the domain)
- Domain-specific criteria YAML (the bootstrap proof)
- Domain-specific examples
- Domain-specific verification setup

## Domains

### 1. **software/** — Software Engineering

**Status**: v1.6.1 (mature, proven bootstrap)
**Applicability**: Code systems, architectures, decisions
**Verification**: All 5 layers applicable

The canonical instantiation. Demonstrates that the framework can govern its own evolution through 9 versioned transitions (v1.0.0 → v1.6.1).

→ See [software/README.md](software/README.md)

---

### 2. **regulatory/** — Regulatory Compliance (Proposed)

**Status**: v0.0.0 (pilot not started)
**Applicability**: Compliance requirements, standards, regulations
**Verification**: Layers 1, 2, 3, 4 applicable

Compliance requirements are intents imposed by external authorities. They have versions, grace periods, amendments, and the chronic problem of residual artifacts (processes shaped by obsolete rules).

**Candidate standards to pilot**: WCAG (accessibility), GDPR (data privacy), SOC 2 (trust services), PCI-DSS (payment)

→ See [regulatory/README.md](regulatory/README.md)

---

### 3. **product/** — Product Strategy (Proposed)

**Status**: v0.0.0 (pilot not started)
**Applicability**: OKRs, north stars, product principles, metrics
**Verification**: Layers 1, 2, 4 applicable

Product teams already maintain intent-like artifacts (OKRs, north stars) but these are disconnected from the decisions they govern. Intent versioning makes product strategy explicit and traceable through organizational change.

→ See [product/README.md](product/README.md)

---

### 4. **ai-agent/** — AI Agent Guardrails (Proposed)

**Status**: v0.0.0 (pilot not started)
**Applicability**: Agent boundaries, capabilities, constraints
**Verification**: Layers 1, 2, 4 applicable (real-time evaluation)

AI agents operating within declared intent boundaries can self-verify: "Does my proposed action violate any intent governing this scope?" Intent becomes the semantic contract between system designer and agent.

**Challenge**: The gap between "falsifiable in principle" and "mechanically evaluable by an LLM" is nontrivial.

→ See [ai-agent/README.md](ai-agent/README.md)

---

### 5. **governance/** — Organizational Governance (Proposed)

**Status**: v0.0.0 (pilot not started)
**Applicability**: Cross-functional tensions, departmental conflicts, organizational strategy
**Verification**: Layers 1, 2 applicable (human judgment required)

Cross-department tensions (sales vs. engineering, legal vs. product) are the operating system of organizations. Currently invisible, resolved ad hoc, re-litigated quarterly. Explicit versioning prevents institutional memory loss.

**Challenge**: Enforcement is social/political, not technical.

→ See [governance/README.md](governance/README.md)

---

### 6. **_template/** — Domain Instantiation Template

**Status**: v0.1.0 (starter kit for new domains)
**Applicability**: Any domain where intent matters
**Verification**: Choose applicable layers

Boilerplate for creating new domain instantiations. Contains:
- `README.md` — step-by-step checklist
- `prose/intent-spec-DOMAIN.md` — specification template
- `criteria/intent-DOMAIN-v0.1.0.yml` — criteria block template
- `examples/example-intent.yml` — example intent structure

→ See [_template/README.md](_template/README.md)

---

## Quick Start: Adding a New Domain

```bash
# 1. Copy the template
cp -r _domains/_template _domains/your-domain

# 2. Create the three required files:
cd _domains/your-domain
vi prose/intent-spec-your-domain.md        # Domain-specific spec
vi criteria/intent-your-domain-v0.1.0.yml  # Bootstrap proof
vi examples/example-intent.yml             # Real-world example

# 3. Test with general tools
python3 ../../tools/score_v150.py \
  prose/intent-spec-your-domain.md \
  ../../prose/intent-spec-core.md \
  criteria/intent-your-domain-v0.1.0.yml

# 4. Document lessons learned
vi README.md
```

See [_template/README.md](_template/README.md) for detailed checklist.

---

## Key Questions Each Domain Answers

### What makes your domain special?

Every domain answers these questions:

1. **What is scope in your domain?**
   - Software: File paths and modules
   - Regulatory: Clause references
   - Product: User journeys
   - AI Agent: Capabilities
   - Governance: Departments

2. **Which verification layers apply?**
   - All 5 for software
   - 1, 2, 3, 4 for regulatory
   - 1, 2, 4 for product
   - 1, 2, 4 for AI agent
   - 1, 2 for governance

3. **What are the typical tensions?**
   - Software: Performance vs. correctness
   - Regulatory: Compliance cost vs. agility
   - Product: Growth vs. risk
   - AI Agent: Helpfulness vs. safety
   - Governance: Innovation vs. stability

4. **How is intent created, linked, recorded, and checked?**
   Each domain has a daily practice workflow.

---

## The Domain-Agnostic Thesis

The file [../intent-domain-agnostic-applicability.yml](../intent-domain-agnostic-applicability.yml) declares the domain-agnostic intent:

> "The Intent Framework applies to any system that carries purpose and evolves over time — not only software codebases."

This thesis is **currently unproven** except for the software bootstrap. Each domain folder is working to prove (or disprove) aspects of this thesis.

---

## Domain Maturity Levels

Each domain instantiation has a version number reflecting maturity:

| Version | Status | Proof |
|---------|--------|-------|
| 0.0.0 | Not started | None |
| 0.1.0 | Bootstrap criteria | Spec written, examples sketched |
| 0.2.0 | Pilot begun | Real-world test with 1-3 intents |
| 0.3.0 | Pilot running | 3-6 month trial, feedback collected |
| 0.4.0 | Proof complete | Lessons documented, transfer thesis validated |
| 1.0.0 | Mature | Framework stable, adopted by domain |

Software is at **v1.6.1** (mature).
All others are at **v0.0.0** (not started).

---

## Next Steps

### To Advance the Software Domain
- Fix remaining self-conformance errors (CC-18)
- Complete missing documentation (CC-09, CC-10, CC-20)
- Get pytest suite running (fix spec file path)
- Verify Lean proof compilation

### To Start a New Domain
1. Choose a domain (suggest: regulatory or product)
2. Read the domain's README.md
3. Copy _template/ and start filling it out
4. Create 2-3 example intents
5. Test with general tools
6. Iterate until self-consistent

### To Contribute
- Submit domain instantiations (draft or complete)
- Report what transferred vs. what broke
- Document lessons learned
- Challenge the general thesis where it fails

---

## Files to Understand

**To understand the structure:**
- This file (`_domains/README.md`)

**To understand a specific domain:**
- `_domains/DOMAIN/README.md`

**To create a new domain:**
- `_domains/_template/README.md` (checklist)
- `_domains/_template/prose/intent-spec-DOMAIN.md` (spec template)
- `_domains/_template/criteria/intent-DOMAIN-v0.1.0.yml` (criteria template)

**To understand the general framework:**
- `../prose/intent-manifesto.md` (philosophy)
- `../prose/intent-spec-core.md` (data model)
- `../VERIFICATION.md` (five-layer verification)
- `../intent-domain-agnostic-applicability.yml` (domain-transfer thesis)
