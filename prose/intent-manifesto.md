# Intent Driven Framework

<!-- source: intent.id, intent.version, intent.schema_version -->

**Version 1.3.0** | Schema version 0.4.0

---

## Declaration

<!-- source: intent.declares -->

This manifesto intends to be a self-contained declaration of the Intent Driven Framework — a purpose governance model that treats intent as a first-class entity: structured, versioned, and verifiable — across any domain where decisions serve goals that degrade, drift, or become invisible over time.

The domain is a parameter: software, policy, strategy, regulation, or the framework's own specification documents. The mechanics of declaring, versioning, tracking, and tension-checking purpose are invariant across these domains. What changes is the scope syntax, the artifact types, and the verification methods. The core does not.

---

## What This Framework Provides

<!-- source: intent.provides -->

The framework delivers six concrete capabilities, each traceable to one or more falsifiable claims.

### (a) A data model for intent

A data model sufficient to declare, version, and relate intents. Tested by FC-01.

### (b) A lifecycle model

A lifecycle model for intent evolution with semantic versioning. Tested by FC-06.

### (c) Structural traceability

A structural relationship between intent, decisions, and artifacts that is mechanically traversable, not merely documented. Tested by FC-02.

### (d) A tension model

A tension model that makes conflicts between intents explicit, owned, and resolvable before they surface as failures. Tested by FC-08.

### (e) Adoption pathways

Adoption pathways that do not require comprehensive audit of existing systems — aspirational intent can be declared without understanding the current state. Tested by FC-03 and FC-05.

### (f) An operational cycle

An operational cycle — Red / Green / Refactor — that governs how intent is declared, satisfied, and evolved. No decision is justified without a red intent demanding it. No intent is evolved without the prior state being green. The cycle is the framework's discipline, not a metaphor. Tested by FC-07.

---

## Design Stance

<!-- source: intent.design_stance -->

Domain-specific adaptation is achieved through instantiation (domain-specific forks with native scope syntax and verification methods), not generalization (abstracting the core until it commits to nothing). Neither domain of origin is privileged. All are instantiations of the same model.

---

## Classification

<!-- source: intent.intent_type, intent.status, intent.priority, intent.confidence, intent.confidence_rationale -->

| Field | Value |
|---|---|
| Intent type | aspirational |
| Status | proposed |
| Priority | critical |
| Confidence | medium |
| Needs verification | true |
| Achieved coverage | minimal |

**Confidence rationale.** Medium reflects the absence of external validation, not weakness of internal evidence. The bootstrap proof (six transitions, 28 criteria, Lean proofs, Zod validation) is strong for mechanic invariance. Confidence remains medium because no adopter outside the authorship context has attempted the framework. Internal rigor cannot substitute for external survivability.

---

## Scope

<!-- source: intent.scope -->

**Primary scope** (what this intent directly governs):

- `intent-driven-framework-definition.yml` — this file
- `prose/intent-manifesto.md` — the philosophy
- `prose/intent-spec-core.md` — the universal data model

**Implicit scope** (what must exist for primary scope to be satisfied):

- `schemas/` — entity schemas (Zod, YAML)
- `criteria/` — completeness criteria
- `core_principles.yaml` — principle declarations

---

## Ownership

<!-- source: intent.owner, intent.last_affirmed, intent.created -->

| Field | Value |
|---|---|
| Owner | authors |
| Last affirmed | 2026-02-06 |
| Created | 2025-02-06 |

---

## Provenance

<!-- source: intent.origin, intent.co_origins -->

**Origin.** The framework originated in a conversation on 2025-02-06 (ref: `conversation-2025-02-06`). The origin conversation is not publicly resolvable. For a framework that requires mechanical traversability (FC-02), this is an acknowledged gap at the root level. A publishable origin digest summarizing the key design decisions and forcing functions is tracked as RW-07.

**Co-origins:**

1. **ADR governance failure patterns** (motivated_by). The observation that ADRs accumulate without structural relationship to purpose, becoming unreadable within months, was the initial forcing function.

2. **Legacy system adoption barrier** (constrained_by). The requirement that the framework be adoptable without comprehensive audit shaped the achieved/aspirational duality and the "next touch" rule.

3. **Self-referential bootstrap v1.5.0** (discovered_in). The framework's generality was discovered — not planned — when the model was applied to its own prose documents and the mechanics transferred without modification. This self-application constitutes the framework's most rigorous proof of concept to date: six versioned transitions, 28 completeness criteria, Lean proofs, and Zod validation — all on a non-software target. The bootstrap is not a recursive novelty. It is empirical evidence that the core mechanics (declare, version, check, evolve) are domain-invariant.

4. **TDD isomorphism discovery** (discovered_in). The structural parallel between TDD and intent-driven practice was recognized during the 1.2.0 cycle: both enforce a constraint-first discipline where the unsatisfied condition (failing test / red intent) must exist before any work is justified. The isomorphism is not a marketing analogy — it is a structural claim that the Red/Green/Refactor cycle operates at the purpose layer exactly as it operates at the behavior layer. This discovery provides both an adoption bridge (teams already practicing TDD recognize the discipline) and a falsifiable structural commitment (see FC-07).

---

## Relational

<!-- source: intent.serves, intent.supersedes, intent.dependencies, intent.retirement_conditions -->

This is the root intent. It serves no parent, supersedes nothing, and has no dependencies — self-contained by design.

**Retirement conditions.** The root intent is retracted if: (a) the core claim — that purpose can be made explicit, versioned, and verifiable — is falsified across multiple domains (not merely unadopted, but structurally refuted); (b) a successor model subsumes the framework's commitments with strictly fewer assumptions or strictly better adoptability; (c) the authors abandon maintenance and no stewardship transfer occurs within 12 months of last_affirmed. Absence of adoption is not grounds for retraction. Structural refutation is. The distinction matters: a correct model that nobody uses is a distribution failure, not a model failure.

---

## The Operational Cycle: Red / Green / Refactor

<!-- source: intent.operational_cycle -->

The discipline that governs how intent is declared, satisfied, and evolved. Adopted from TDD by structural isomorphism, not by analogy. The cycle is the framework's answer to "what do I do next?"

**TDD isomorphism status:** claimed (structural, pending FC-07 validation).

**Isomorphism claim.** The operational cycle is claimed to be isomorphic to Test-Driven Development. TDD says: no production code without a failing test. Intent Driven X says: no decision without an unsatisfied intent. In both models, the constraint comes first, the work exists to satisfy it, and restructuring happens only after satisfaction is demonstrated. Both are instances of the same pattern: declare a falsifiable constraint, satisfy it minimally, then improve without breaking the constraint. This claim is structural, not analogical — but it is unverified in practice. FC-07 defines the conditions under which it would be falsified.

### Phase 1: Red (Declare)

Declare an intent that is currently unsatisfied. The intent's current_reality shows a gap between what is declared and what exists. The intent is "failing" — it has been stated but not achieved. This is the only legitimate entry point for new work.

**TDD parallel.** Write a failing test. The test defines the behavior before the code exists. The red state is not a problem — it is the authorization to build.

**Rule.** No decision is justified without a red intent that demands it. If there is no unsatisfied intent, there is no mandate to act. Work without a red intent is drift.

**Outputs:**
- An intent declaration with intent_type: aspirational, status: proposed
- A current_reality block that honestly describes the gap
- Scope defined — what this intent governs

### Phase 2: Green (Satisfy)

Make decisions and produce artifacts that serve the declared intent until the gap closes. achieved_coverage moves. The intent transitions from proposed to active, or aspirational narrows its gap. Every decision records which intent it serves. Every artifact is traceable to a decision.

**TDD parallel.** Write the minimum code to make the test pass. No more than the test demands. The test constrains the implementation.

**Rule.** Build only what the red intent demands. Decisions that do not reference an intent are unjustified. Artifacts that do not trace to a decision are orphans. The chain Intent -> Decision -> Artifact must be traversable at every step.

**Outputs:**
- Decisions with explicit intent_ref
- Artifacts within the intent's declared scope
- Updated achieved_coverage and current_reality

### Phase 3: Refactor (Evolve)

Once an intent is satisfied (green), it can be evolved: scope adjusted, tensions surfaced, version bumped. The transition log captures what changed and why. Refactoring happens from a position of satisfaction, not deficit. You do not evolve a red intent — you satisfy it first, then reshape it.

**TDD parallel.** Refactor the code while keeping the tests green. The tests protect the behavior. The refactoring improves the structure without breaking what works.

**Rule.** No evolution without a green state to protect. Version bumps require a transition log entry. MAJOR bumps trigger artifact review. The prior green state is the safety net — if the evolution breaks satisfaction, the intent goes red again, and the cycle restarts.

**Outputs:**
- A transition_log entry with reason, forcing_function, what_changed
- A version bump (MAJOR / MINOR / PATCH)
- Updated tensions if the evolution surfaces new conflicts

### Constraints

| ID | Rule | Violation |
|---|---|---|
| OC-01 | Red before Green — no work without a declared unsatisfied intent | Drift: work exists that serves no declared purpose |
| OC-02 | Green before Refactor — no evolution without demonstrated satisfaction | Premature abstraction: reshaping what was never proven to work |
| OC-03 | Every Green must be evidenced — achieved_coverage or current_reality must move | Green-washing: claiming satisfaction without updating evidence |
| OC-04 | Refactor produces a transition, not a new intent — the identity persists | Intent sprawl: evolving by creating new intents instead of versioning existing ones |

### Divergence from TDD

The isomorphism is structural but not total. The framework operates at a higher altitude than TDD and must carry ambiguity that tests do not:

| Aspect | TDD | Intent Driven |
|---|---|---|
| Binary vs. graduated | Tests are pass/fail. There is no "partially passing" test. | Intents can be partially satisfied. achieved_coverage can be minimal, partial, or substantial before reaching full. The Red/Green boundary is a threshold, not binary. |
| Scope of constraint | A test constrains a function, a module, or an integration boundary. | An intent constrains a capability, a commitment, or a governance boundary. The scope is broader, the feedback loop is longer. |
| Speed of cycle | Red/Green/Refactor can complete in minutes. | Red/Green/Refactor for an intent may span weeks or months. The discipline is the same. The clock speed is different. |
| Refactor safety net | The test suite protects against regression mechanically. | The transition log and falsifiable_claims protect structurally, but verification may require human review rather than automated execution. |

---

## Current Reality

<!-- source: intent.current_reality -->

**Assessed:** 2026-02-06

### State

The framework exists as prose (manifesto + spec), a YAML criteria system (v1.6.1, 28 criteria, all passing), a Zod validation schema, Lean 4 proofs for structural properties, and a regex-based evidence scorer. The core principles have been expanded to seven with full defensibility apparatus (counter-arguments, rebuttals, testability).

The model has been validated against exactly one non-trivial target: itself. The self-referential bootstrap (applying the framework to its own documents through six versioned transitions) demonstrated that the core mechanics — declare, version, check, evolve — operate on structured prose, not only on code. This is itself a non-software application: the target was specification documents, criteria YAML, and principles — not a codebase. Every field in this file functions on that non-software target without modification. The framework's own self-application is the strongest evidence that the domain is a parameter, not a constraint.

What remains unproven: whether the model survives adoption by someone who did not design it, on a system they did not build, in an organization with real political constraints on tension declaration. The self-application proves domain-invariance of mechanics. It does not prove adoptability by strangers.

### Status

| Component | State |
|---|---|
| Bootstrap proof | complete (self-referential, six transitions) |
| Core principles | complete (7/7, all carry falsifiability) |
| Data model | complete (intent, decision, transition, tension, origin, manifest) |
| Lifecycle model | complete (proposed -> active -> evolving -> superseded / residual / retracted) |
| SemVer for intent | complete (MAJOR/MINOR/PATCH with governance consequences defined) |
| Adoption pathways | complete (pain-first, next-touch, amnesty) |
| Operational cycle | complete (Red/Green/Refactor defined, TDD isomorphism declared) |
| Tension model | complete (declared, owned, resolution strategies typed) |
| Declares decomposition | complete (core commitment separated from provides list) |
| Domain transfer | partial (self-application proves mechanic invariance; no external pilot) |
| Tooling surface | partial (validators exist, no CLI, no CI integration package) |
| External validation | none (no adopter outside the authorship context) |

### Remaining Work

| ID | Description | Blocks | Priority |
|---|---|---|---|
| RW-01 | Pilot the framework in an external domain (not authored by the framework's creators). Self-application proves mechanic invariance. External application proves adoptability and domain fit. | External adoption claim; moves FC-04 from partially_verified to supported | critical |
| RW-02 | Pilot the framework on a real software codebase with a team that did not design it. | Self-contained adoption claim in declares field | critical |
| RW-03 | Build CLI tooling (intent init, intent declare, intent transition, intent lint). | Practical adoptability at scale | high |
| RW-04 | Define cross-repo intent discovery and notification protocol. | Multi-repo governance | high |
| RW-05 | Produce an adopter-facing failure mode guide with worked examples, decision trees, and severity calibration. FM-01 through FM-05 define the modes and diagnostics. RW-05 is the packaging into a standalone document. | Adopters cannot self-diagnose misuse without a standalone guide | high |
| RW-06 | Schema governance protocol — how the schema itself versions and migrates. | Long-term schema stability | medium |
| RW-07 | Publish an origin digest summarizing key design decisions and forcing functions from the founding conversation, making the root origin ref resolvable by non-authors. | Origin traversability for external adopters (FC-02 compliance at root) | medium |

### Gap Assessment

The framework is conceptually complete and has one empirical proof: its own self-application on non-software targets (specification prose, criteria YAML, principle declarations). This proof demonstrates that the core mechanics are domain-invariant — the same fields, lifecycle, versioning, and tension model work on prose documents as on codebases.

What the self-proof does not demonstrate: adoptability by strangers, survival under organizational politics, or behavior at scale. The distance between current state and the declares field is no longer purely conceptual — it is partially empirical, partially untested. The model needs to be used by someone else, on something they own, and the result needs to be evaluated honestly.

---

## Tensions

<!-- source: intent.tensions -->

These are the real structural conflicts within this intent. Each tension exists between two legitimate goals. Declaring them prevents re-litigation and makes the tradeoffs visible.

### T-01: Instantiation depth vs. Core abstraction

**Between:**
- Each domain instantiation needs enough specificity to be actionable (concrete scope syntax, domain-native verification, real examples)
- The core framework must remain domain-invariant — it cannot accumulate domain-specific fields or assumptions

**Resolution** (policy): The core spec defines the invariant mechanics: data model, lifecycle, versioning semantics, tension model. It uses domain-neutral language (scope is "what this intent governs", not "which files"). Each domain produces its own instantiation document that maps core concepts to domain-native primitives. Software maps scope to file globs. Regulation maps scope to section identifiers. Strategy maps scope to initiative names. The core never absorbs domain-specific syntax. Instantiations never modify core field semantics. Depth grows at the edges. The center stays thin.

Owner: authors | Last reviewed: 2026-02-06 | Staleness threshold: 180 days

### T-02: Rigor vs. Adoptability

**Between:**
- Completeness of the model (every field, every lifecycle state, every edge case)
- Willingness of practitioners to actually use it (ceremony must be proportional to value)

**Resolution** (priority_ordering): Adoptability wins when the two conflict. A model that is theoretically complete but practically abandoned is worth nothing. Concretely: the minimum viable intent declaration must require no more than five fields (id, version, declares, scope, owner). Everything else is available but not mandatory at first declaration. Rigor grows as the intent matures — a proposed intent has fewer requirements than an active one.

Owner: authors | Last reviewed: 2026-02-06 | Staleness threshold: 180 days

### T-03: Prescriptive vs. Descriptive

**Between:**
- Telling adopters exactly how to structure their _repo/, name their files, run their CI
- Describing the principles and letting adopters make their own structural choices

**Resolution** (delegation): The core spec is prescriptive about the data model (field names, types, enums, relationships) and descriptive about structure (directory layout, file naming, CI integration). The data model must be interoperable — tools need to parse it. The structure can vary — teams have different workflows. Domain-specific specs may be more prescriptive about structure where their domain demands it (e.g., regulatory compliance may require specific file naming for audit trails).

Owner: authors | Last reviewed: 2026-02-06 | Staleness threshold: 180 days

### T-04: Self-referential integrity vs. Forward progress

**Between:**
- The framework must conform to its own model at every stage (eat your own cooking)
- Enforcing full self-conformance at every step blocks iteration on the model itself

**Resolution** (policy): Self-conformance is required at release boundaries, not at every commit. Work-in-progress versions (0.x.x, -wip suffix) may temporarily violate self-conformance. The violation must be declared in the current_reality block — it is visible, not hidden. Before any version is published or shared, all self-conformance checks must pass. This allows iteration without allowing permanent hypocrisy.

Owner: authors | Last reviewed: 2026-02-06 | Staleness threshold: 90 days

### T-05: Cycle discipline vs. Intent ambiguity

**Between:**
- The Red/Green/Refactor cycle demands clear phase boundaries — you must know when an intent is red, when it is green, and when refactoring is safe
- Intent satisfaction is inherently graduated and judgment-dependent — unlike tests, intents do not produce binary pass/fail signals

**Resolution** (policy): The cycle boundary is a threshold, not a binary. An intent is red when its current_reality shows a gap that the owner judges material. An intent is green when the owner affirms (via last_affirmed and achieved_coverage update) that the declares field is operationally met for the current scope. The judgment is the owner's, but the judgment must be recorded — it is not implicit. If an owner cannot articulate why the intent is green, it is not green. The cycle's discipline is: make the phase transition explicit even when the evidence is qualitative. TDD has the compiler. Intent Driven X has the owner's recorded judgment. Both are accountable. Neither is hidden.

Owner: authors | Last reviewed: 2026-02-06 | Staleness threshold: 180 days

---

## Falsifiable Claims

<!-- source: intent.falsifiable_claims -->

The declares field makes claims. These are the conditions under which those claims are falsified. If any of these become true, the intent must either evolve (version bump) or be retracted.

### FC-01: Intent is a first-class entity with its own lifecycle

**Falsified when:** Intent cannot be created, versioned, queried, or retired independently of the artifacts it governs. If deleting an artifact deletes the intent, the claim fails.

**Status:** supported | **Evidence:** Schema defines intent with independent id, version, and lifecycle states.

### FC-02: The chain Intent -> Decision -> Artifact is mechanically traversable

**Falsified when:** Given an artifact, there is no mechanical path (queryable, not requiring human interpretation) to the decision that produced it and the intent that decision serves. If the chain requires reading prose to traverse, it is documented but not mechanical.

**Status:** supported | **Evidence:** Decision schema carries serves_intent ref; artifact scope is declared on intent.

### FC-03: Aspirational intent can be declared without understanding the current state

**Falsified when:** The schema or process requires any field that can only be populated by examining the existing system before an aspirational intent can be declared. If current_reality is mandatory for proposed intents, this claim fails.

**Status:** supported | **Evidence:** current_reality is required for active aspirational intents but not for proposed ones. A team can declare intent at proposed status with only id, version, declares, scope, owner.

### FC-04: The framework is domain-invariant — domain is a parameter, not a constraint

**Falsified when:** A domain that meets the preconditions (has purpose, evolves over time, suffers from purpose degradation) attempts adoption and the core data model requires fields specific to another domain to function. If scope must be expressed as file globs, or artifacts must be code, or verification must be automated tests, the core has absorbed domain assumptions and the claim fails for any non-software domain.

**Status:** partially_verified | **Evidence:** The framework has been applied to its own specification documents — a non-software target — through six versioned transitions with mechanical verification (28 completeness criteria, Zod schema validation, Lean proofs, regex evidence scoring). Every core field functioned on this target without modification. This constitutes a single non-software proof of concept. It demonstrates mechanic invariance but not breadth of domain applicability. No external domain pilot has been conducted.

### FC-05: The framework is self-contained for adoption

**Falsified when:** A practitioner who was not involved in the framework's creation attempts adoption using only the published documents and cannot (a) declare their first intent, (b) structure a repository, (c) record a transition, or (d) resolve a tension without contacting the authors. If any of these four require author involvement, the claim fails.

**Status:** unverified | **Evidence:** No external adopter has been tested.

### FC-06: Semantic versioning on intent communicates governance-relevant impact

**Falsified when:** Teams using the framework cannot reliably distinguish MAJOR from MINOR intent changes, or the distinction does not produce different governance responses (MAJOR triggers artifact review, MINOR does not). If the version numbers are applied but ignored in practice, the claim is technically satisfied but operationally falsified.

**Status:** supported_in_theory | **Evidence:** The framework defines MAJOR/MINOR/PATCH with clear backward-compatibility criteria and governance consequences. No team has tested whether the distinction holds under real conditions.

### FC-07: The Red/Green/Refactor cycle is operationally isomorphic to TDD

**Falsified when:** The cycle fails to constrain work in the way TDD constrains code. Specifically: (a) teams produce decisions that do not reference a red intent and no one notices (Red constraint fails); (b) teams evolve intents that were never demonstrated as satisfied and the transition log does not flag this (Green constraint fails); (c) the cycle phases cannot be mechanically or procedurally distinguished in practice — teams cannot tell what phase they are in. If any of these hold, the isomorphism is analogical, not structural, and the claim must be downgraded to a pedagogical metaphor.

**Status:** supported_in_theory | **Evidence:** The cycle is defined with explicit phase rules, constraint IDs (OC-01 through OC-04), and divergence documentation. The structural parallel holds at the specification level. No team has tested whether the cycle produces TDD-like constraint discipline in practice.

### FC-08: Tensions between intents are made explicit and their resolution is tracked

**Falsified when:** Conflicting intents coexist without an explicit resolution strategy, resolution owner, or staleness threshold. If tensions can exist unacknowledged in the system, or if a tension has no documented resolution strategy, the framework fails to make conflicts visible.

**Status:** supported | **Evidence:** Schema defines tensions as a first-class array with required fields: resolution_strategy (with type and rule), resolution_owner, and staleness_threshold_days. The root intent declares five tensions (T-01 through T-05) with explicit strategies. Every tension has an owner and staleness threshold.

---

## Failure Modes

<!-- source: intent.failure_modes -->

How the framework fails when adopted badly. A model that cannot diagnose its own misuse is a model that will be misused silently.

### FM-01: Performative intent

Intent declarations exist but are never checked, never versioned, and never referenced in decisions. The _repo/ directory is populated on day one and never touched again. Intent becomes documentation that rots.

**Diagnostic:** last_affirmed dates older than staleness threshold across >50% of active intents. Zero transitions logged in the past N months. No decisions reference any intent.

**Mitigation:** CI linting that flags stale intents. Require intent_ref on decision records. Make staleness visible in dashboards.

### FM-02: Over-specification

Every function, every endpoint, every configuration value has its own declared intent. The intent layer becomes as complex as the system it governs, defeating the purpose of abstraction. Signal drowns in noise.

**Diagnostic:** Intent count exceeds decision count. Average scope of an intent is a single file or function. Teams spend more time maintaining intent declarations than writing code.

**Mitigation:** Guidance on intent granularity: intents should govern capabilities or commitments, not implementation details. "Payments are idempotent" is an intent. "This function retries three times" is not.

### FM-03: Version inflation

Teams bump MAJOR versions for changes that are actually MINOR or PATCH. Every clarification becomes a breaking change. The governance signal (MAJOR = review everything) triggers so frequently that teams learn to ignore it.

**Diagnostic:** MAJOR bump frequency exceeds once per quarter per intent. Transition logs show MAJOR bumps with rationales that describe backward-compatible changes. Teams report "review fatigue."

**Mitigation:** Clear examples of MAJOR vs. MINOR vs. PATCH in adoption guide. Lint rule that flags MAJOR bumps and requires explicit backward-incompatibility evidence in the transition log.

### FM-04: Tension avoidance

Teams declare intents but refuse to declare tensions between them, because naming a tension means naming a political conflict. The tension model exists but is empty. Conflicts continue to surface as incidents rather than as governance.

**Diagnostic:** Zero tensions declared across a system with >10 active intents. Post-incident reviews repeatedly identify conflicting intents that were not declared as tensions.

**Mitigation:** Normalize tension declaration as a sign of maturity, not conflict. Include tension declaration in the adoption sequence. Make tension-free systems a linting warning, not an achievement.

### FM-05: Cargo cult structure

Teams create the _repo/ directory, populate it with template-generated intent files, and never modify them. The structure exists. The practice doesn't. The framework becomes a checkbox exercise.

**Diagnostic:** All intent files have the same created and last_affirmed date. Zero transitions. All declares fields are generic ("this service intends to work correctly"). No decisions reference intents.

**Mitigation:** Adoption guide emphasizes starting with one real intent driven by a real pain point (pain-first strategy), not a comprehensive declaration. Lint rules that flag generic declares fields.

### FM-06: Green-washing

Teams declare intents green without updating evidence. achieved_coverage stays at the same value, current_reality is never reassessed, but the team proceeds to refactor (evolve the intent) as if satisfaction were demonstrated. The cycle degrades: Red -> "Green" -> Refactor becomes Red -> Skip -> Mutate. Intent evolution loses its safety net.

**Diagnostic:** Transition logs show version bumps (refactor phase) on intents whose current_reality and achieved_coverage have not been updated since initial declaration. last_affirmed dates advance but gap_assessment text is unchanged.

**Mitigation:** Lint rule: transition log entries of type MINOR or MAJOR on intents whose achieved_coverage has not changed since the prior version should trigger a warning. The operational cycle constraint OC-03 makes this explicit — green must be evidenced, not declared by fiat.

---

## Evolution History

<!-- source: intent.transition_log -->

### 1.0.0 -> 1.1.0 (MINOR, 2026-02-06)

**Reason.** The framework's self-application contradicted its own framing. The file declared achieved_coverage: none and FC-04 status: unverified while simultaneously being a functioning non-software application of the framework. The declares field listed software first, implying it was the primary domain, when the strongest empirical evidence was on a non-software target.

**Forcing function.** Internal consistency violation: the file's metadata contradicted the evidence produced by the file's own existence.

**What changed:**
- declares field rewritten: domain is now a parameter, not a list with software first
- achieved_coverage: none -> minimal
- FC-04 status: unverified -> partially_verified with self-application evidence
- FC-04 claim reworded: "applies beyond software" -> "domain-invariant"
- T-01 reframed: "Depth vs. Breadth" -> "Instantiation depth vs. Core abstraction"
- current_reality.state updated to acknowledge self-application as non-software proof
- RW-01 reframed: "pilot non-software domain" -> "pilot external domain"
- gap_assessment updated: "purely conceptual" -> "partially empirical"

### 1.1.0 -> 1.1.1 (PATCH, 2026-02-06)

**Reason.** External review identified five internal consistency issues: (1) confidence: medium was unjustified; (2) the origin ref is opaque to non-authors; (3) RW-05 appeared to duplicate failure_modes content; (4) the root intent had no retirement conditions; (5) no remaining work item tracked the origin accessibility gap.

**Forcing function.** A framework that insists on self-conformance cannot leave its own root intent with an unjustified confidence field, an unresolvable origin, and an undeclared retirement policy.

**What changed:**
- Added confidence_rationale field
- Added accessibility and note to origin
- Added RW-07: publish origin digest
- Clarified RW-05: distinguished FM source material from adopter-facing delivery artifact
- Added retirement_conditions to root intent

### 1.1.1 -> 1.2.0 (MINOR, 2026-02-06)

**Reason.** The framework lacked an operational discipline — it defined what to declare but not how to work. The structural isomorphism between the framework's practice and TDD's Red/Green/Refactor was recognized as a first-class commitment.

**Forcing function.** A framework that governs purpose evolution but does not define the operational discipline for evolving purpose leaves adopters with a data model and no workflow.

**What changed:**
- declares: condensed three paragraphs into one
- declares: added item (f) — operational cycle
- Added operational_cycle section with phases, constraints, and TDD divergence
- Added isomorphism_claim to operational_cycle
- tdd_isomorphism set to "claimed" not "structural"
- Added co_origin: tdd-isomorphism-discovery
- Added T-05: Cycle discipline vs. Intent ambiguity
- Added FC-07: Red/Green/Refactor isomorphism
- Added FM-06: Green-washing
- current_reality.status: added Operational cycle line

### 1.2.0 -> 1.3.0 (MINOR, 2026-02-06)

**Reason.** The declares field was carrying four distinct concerns: core commitment, feature list, methodology stance, and origin evidence. A field that does four things is testable against none of them precisely.

**Forcing function.** The provides list items (a)-(f) are the framework's concrete deliverables, each falsifiable by a specific FC. But embedded in a prose block, the mapping was implicit. Extracting provides as a structured field converts implicit traceability into mechanical traceability.

**What changed:**
- declares: tightened to core falsifiable commitment only
- provides: new field — items (a)-(f) extracted as structured array with FC cross-references
- design_stance: new field — instantiation-over-generalization extracted from declares
- Origin evidence removed from declares — redundant with co_origins[2]
- current_reality.status: added Declares decomposition line
- Version: 1.3.0 MINOR (provides with tested_by is new structural meaning)
- schema_version: 0.4.0 (provides and design_stance are new top-level fields)

**Residue.** The provides.tested_by cross-references create a new invariant: every provides item should map to at least one FC. provides-d (tension model) currently has tested_by: [FC-08] — but was originally empty. This gap was addressed by referencing FC-08 directly.

---

## Extension Surface

<!-- source: intent.ext -->

The extension surface (`ext:`) carries domain-specific metadata without polluting the core schema.

This root intent's extension surface is self-referential:

| Key | Value |
|---|---|
| is_self_referential | true |
| is_non_software_application | true |

This file uses the framework to declare the framework. It is simultaneously the root intent declaration AND evidence for FC-04 (domain-invariance): the target governed by this file is prose, YAML, and criteria — not software. The fact that every field functions here without modification is the proof that the domain is a parameter. Self-conformance is required at release boundaries per T-04.

---

*This document is a derived rendering of the root intent YAML declaration at `criteria/intent-driven-framework-definition.yml`. The YAML is authoritative. If this prose diverges from the YAML, the YAML wins.*
