# The Intent Manifesto

## Systems carry intent. It's time we made it visible.

---

## I. The Problem

Every purposeful system embodies intent — goals, commitments, orientations that shape what the system is and what it resists becoming. But this intent is invisible. It lives in the heads of people who may have already left. It is buried in meeting notes nobody reads, in messages that scroll away, in the unspoken assumptions behind decisions that shaped the system years ago.

When intent is invisible, organizations lose the ability to reason about *why* their systems are the way they are. They can see *what* exists. They can trace *when* things changed. But the *why* — the purpose that justified the structure — disappears the moment the last person who remembers it moves on.

"System" here is broad. A codebase is a system. So is a product strategy, a regulatory compliance framework, a design system, an organizational governance structure, an AI agent's operating boundaries. Any domain where decisions are made in service of goals that degrade, drift, or become invisible as people and context change — that domain carries intent, and that intent is currently unmanaged.

This creates a cascade of failures:

- **Decisions are made without context.** People modify systems they don't understand the orientation of, introducing contradictions nobody can see.
- **Structure degrades silently.** Former intents leave residue that nobody has permission to clean up because nobody knows if it still matters.
- **Disciplines talk past each other.** One group holds tacit knowledge about what the system is committed to, but can't articulate it in terms that create organizational authority. So it loses every negotiation against an explicit demand from another group.
- **Accumulated friction is unnamed.** What organizations call "legacy burden" or "process debt" is often the friction between active intent and residual intent — but without a language for intent, they can't diagnose it, prioritize it, or explain it.

We have tools for managing artifacts. We have trackers for work. We have monitoring for behavior. We have nothing for intent.

---

## II. The Inversion

We propose a fundamental inversion in how systems are understood and governed.

**Today's model:** Artifacts are primary. Decisions explain the artifacts. Intent is implicit, scattered, and impermanent.

**The intent model:** Intent is primary. Decisions are made in service of intent. Artifacts implement decisions. Everything is traceable back to a declared purpose.

```
Intent
  └── governs Decisions
        └── shape Artifacts
              └── produce Behavior
```

This is not documentation. Documentation describes what exists. Intent declares what the system is *oriented toward* — what properties it is committed to maintaining, what tradeoffs it has chosen, what future it is building toward.

Intent is a **first-class entity**: structured, addressable, versioned, and versionable.

---

## III. Core Principles

### 1. Intent exists independently — and every discipline generates it

Intent is not derived from any single discipline's requirements. It is not derived from artifacts. It is not derived from past decisions. It has its own existence, its own authority, and its own lifecycle.

Every discipline that shapes a system carries intent that is structurally real, that constrains what the system can become, and that is currently invisible.

In a software system, this means DevOps holds deployment intent, UX holds experience intent, Data holds integrity intent, Security holds boundary intent — each shaping artifacts owned by other disciplines. In an organization, Finance holds fiscal intent, Legal holds compliance intent, Product holds market intent — each constraining the others. In a regulatory body, different divisions hold safety intent, market fairness intent, consumer protection intent — each creating tensions the regulated entities must navigate. In an AI agent system, Safety holds alignment intent, Capability holds task-completion intent, Privacy holds data-handling intent — each binding the agent's behavior from a different angle.

The pattern is universal: multiple disciplines generate intent that crosses ownership boundaries. That is precisely why it must be declared — so the crossing is visible, not discovered in failure.

No discipline derives from another. Each has its own authority. Intent sits at the table. Every discipline has a seat.

### 2. Intent evolves and its evolution is tracked

Intent is not static. A system's orientation shifts as the organization learns, as the domain changes, as scale introduces new forces. The intent of a payment system at ten transactions per day is different from its intent at ten million. The intent of a startup's compliance posture is different after an IPO. The intent governing an AI agent shifts as its capabilities expand.

This evolution must be captured — not just the current state, but the transitions. When intent changes, we record what changed, why it changed, what forced the change, and what residue the former intent left behind.

Intent has a lifecycle:

```
PROPOSED → ACTIVE → EVOLVING → SUPERSEDED → RESIDUAL
              ↓         ↓
           RETRACTED  RETRACTED
```

**Proposed** intent is a candidate — declared but not yet governing. **Active** intent is the current orientation. **Evolving** intent is under revision — the system is transitioning between versions. **Superseded** intent has been replaced by a successor. **Residual** is the state that matters most: intent that is no longer active but whose artifacts still shape the system. Most of what organizations call "legacy burden" lives here — structure that serves a purpose nobody has confirmed in years, shaped by commitments nobody remembers making.

**Retracted** is the state nobody plans for but every organization encounters. It describes intent that was declared but turned out to be wrong — not superseded by a better intent, just mistaken. Retracted intent is distinct from superseded: superseded means "this was real and has been replaced." Retracted means "this was never right." The distinction matters because retracted intent should not leave residual artifacts — anything shaped by it should be evaluated for removal, not preservation.

### 3. Intent has two modes: achieved and aspirational

Not all intent describes what the system currently does. Some intent describes what the system *should become*. This distinction is fundamental — and it is what makes the intent model practical for any inherited system.

**Achieved intent** is descriptive. It captures what the system currently intends — the properties it maintains, the commitments it honors, the orientation it embodies today. Declaring achieved intent requires understanding the existing system, which is hard, especially for inherited systems where the original authors are gone and the reasoning is opaque. Achieved intent is the archaeological work. It accumulates slowly through examination, through incident forensics, through inference. It starts at `0.x.x` confidence and stabilizes over time.

**Aspirational intent** is directional. It captures what we want the system to intend — the properties we are committed to building toward, even if the system does not satisfy them today. Declaring aspirational intent does not require understanding the existing system. It requires only a decision about the future. "We intend billing to be fully auditable" or "We intend this agent to refuse requests outside its declared scope" — these are statements you can make right now, without understanding the current state in detail. They are available immediately, to any team, at any moment.

This distinction is liberating because it means you can **start with intent even when you cannot understand the existing system**. The aspiration comes first. Understanding the current state is work done *in service of* the aspiration, not a precondition for it.

When an aspirational intent is declared, it carries an honest assessment of the gap between where the system is and where it should be. That gap — the distance between achieved and aspirational — is the most useful artifact in the model. It is the work to be done, decomposed and visible. It is not a vague backlog. It is a versioned, structured, measurable distance between current state and desired state.

The lifecycle of aspirational intent follows a natural progression: an intent starts as aspirational with a gap. As work is done in service of that intent, the gap narrows. When the gap closes — when the system fully satisfies the intent — it transitions from aspirational to achieved. The aspiration has been realized. The intent remains, now as a commitment to maintain what was built.

Intent is not just a snapshot of what exists. It is a vector — with a current position and a direction. The position is achieved intent. The direction is aspirational intent. The distance between them is the strategy.

### 4. Intent follows Semantic Versioning

Intent changes are not equal. A clarification is not the same as a fundamental reorientation. Semantic Versioning, applied to intent, communicates the *nature* of change:

- **PATCH** — the intent is the same, expressed more clearly. Artifacts serving this intent do not need to change.
- **MINOR** — the intent has extended in a backward-compatible way. Existing artifacts still satisfy it, but new work may be needed.
- **MAJOR** — the intent has fundamentally shifted. Artifacts serving the prior major version are now potentially serving a dead intent. This is where structural debt is born.

SemVer on intent gives teams a mechanical signal for impact. A major version bump on a core intent is a system-wide event. A patch is a footnote. The version number carries meaning that a timestamp alone never could.

### 5. Decisions serve intent, not the other way around

Decision records are valuable. But in the current model, they are orphans — freestanding decisions with no structural relationship to purpose. Six months after a decision is recorded, someone reads it and asks: "but why did this matter?" The intent is gone.

In the intent model, every decision is made *in service of* a declared intent. The record references the intent it serves and the version of that intent at the time of the decision. This creates traceability:

- When intent evolves, you know which decisions may be stale.
- When decisions accumulate, you can see what intent they collectively serve.
- When a decision has no parent intent, it's a signal — either the intent is undeclared, or the decision is untethered from purpose.

Decisions can also *trigger* intent transitions. A decision that fundamentally changes an approach is the forcing function for a major version bump on the intent it serves. The relationship is bidirectional — but intent remains the governing entity.

### 6. Tensions are declared, not discovered in failure

Real systems serve multiple intents that are often in tension. Speed versus safety. Growth versus risk. Consistency versus flexibility. Compliance versus agility. These tensions are *the* central challenge of governance.

Today, these tensions are invisible until they produce a failure. Someone introduces a change that serves one intent and violates another, and nobody knows until something breaks. The tension existed — it just wasn't written down.

The most consequential tensions are **cross-discipline**. They exist between intents owned by different disciplines, which is why they are hardest to see and most damaging when missed. In a software system: UX intent versus Security intent. In an organization: Sales intent versus Engineering intent. In regulation: consumer protection intent versus market innovation intent. In an AI agent: capability intent versus safety intent — the agent should be maximally helpful *and* refuse harmful requests, and the boundary is where the real design decisions live.

These cross-discipline tensions are the **real architecture** of any system. They are where the hardest decisions live. Making them visible, versioned, and attached to a declared resolution strategy transforms them from landmines into navigable tradeoffs.

But visibility alone is not resolution. A tension made explicit is a tension that now demands a decision — and that decision requires authority. The intent model does not prescribe who holds that authority. What the model *does* require is that the authority is **named on the tension itself**. Every declared tension must have a resolution owner — not the person who will do the work, but the person or role authorized to decide how the tradeoff is balanced when the disciplines involved cannot agree. If a tension has no resolution owner, it is not a managed tradeoff. It is a structured artifact to fight over.

This is the uncomfortable acknowledgment: making tensions explicit without an accompanying authority model can increase friction rather than reduce it. The model earns its value only when that visibility is paired with a clear path to resolution — and that path must include a named authority who can break deadlocks.

A specific case deserves attention: what happens when a new intent directly contradicts an existing active intent? This is not a tension — tensions describe co-existing intents that pull in different directions but can both be honored through a resolution strategy. A contradiction is stronger: the new intent cannot be satisfied while the existing one is active. In that case, the new intent is a **supersession proposal**. It is declared with status `proposed`, explicitly referencing the intent it would supersede, and the resolution owner decides whether the supersession proceeds. The key is that contradiction is not silently overwritten — it is surfaced as a decision that requires authority.

### 7. Intent is declared, not inferred

The foundational practice is explicit declaration. A human with context and judgment declares what a part of the system intends. This is the ground truth. Each discipline declares intent within its domain of expertise, using a shared model that makes all declarations visible to all other disciplines.

Inference (an AI reading artifacts and proposing intent) and derivation (extracting intent from the delta between versions) are valuable but secondary. They depend on a corpus of declared intent to calibrate against. Without ground truth, inference has nothing to validate itself with.

Declaration must be low-friction. If it feels like documentation, it will die. Intent declarations live alongside the system they govern, in structured files that are versioned with every change. They are verified mechanically where possible. They are part of the workflow, not a parallel artifact.

### 8. The governed system has a self-model

Every governed system maintains a structured, version-controlled self-model that answers seven questions:

- **Who am I** — the manifest, declaring the system's identity and top-level intent.
- **What do I intend** — the active, proposed, and superseded intents that govern this system.
- **How have I changed** — the transition log, recording every shift in orientation.
- **What am I balancing** — the declared tensions between competing intents.
- **What did I choose and why** — the decisions made in service of intent.
- **Where did my intents come from** — the provenance links to external events, requirements, incidents, and expert judgment.
- **What else do I know about myself** — the extension surface, where domain-specific knowledge attaches to the core model without altering it.

The self-model's physical structure depends on the domain. In a codebase, it is a directory in the repository. In an agent system, it may be a structured configuration alongside the agent's tool definitions. In an organizational governance system, it may be a shared document store. The seven questions are universal. How and where they are stored is defined by each domain layer.

This self-model is the foundation for all downstream tooling — verification, visualization, inference, compatibility checking, organizational intent maps. But it exists first as a practice, not a tool.

### 9. The model is extensible by design

The intent model must itself embody the principle it advocates: a small, stable core with a clear orientation, and the ability to evolve at the edges without breaking the center.

The core schema defines the minimum viable structure for an intent to be an intent — identity, version, declaration, scope, status, lifecycle, and relationships. This is the contract. It is deliberately small. It does not try to anticipate every domain, every compliance framework, every organizational need.

Everything beyond the core is an **extension**. Extensions are typed, namespaced, and scoped. They add structured data to intents, new validation rules, new relationship types, and lifecycle hooks — without modifying or polluting the core schema. An organization can adopt the core with zero extensions and get value immediately.

The same extensibility operates at the domain level. The core specification defines the universal model. Domain layers — software engineering, AI agent guardrails, regulatory compliance, organizational governance — instantiate the model with domain-specific scope semantics, verification mechanisms, and operational conventions. Each domain layer is an extension of the core, not a modification.

The core makes one guarantee to both extensions and domain layers: **lifecycle events are reliable**. When intent transitions between states, the core emits well-defined events. The core does not know or care what consumers do. It guarantees only that the events are reliable and the lifecycle is sovereign.

---

## IV. The Minimal Valid Intent

The full data model, self-model structure, and extension surface are specified in the companion document, *The Intent Specification (Core)*. But the reader should see the floor before the ceiling.

A valid intent declaration requires four fields:

```yaml
intent:
  id: intent-checkout-reversibility
  version: 1.0.0
  declares: "Users can reverse any checkout action within 24 hours"
  scope: [checkout]
```

That is enough to start. It is a searchable, versioned commitment attached to a part of the system. It can be found by anyone working in that scope. It can be referenced by decisions. It can be checked against incoming changes. It can be the seed that grows into a richer declaration over time — with provenance, tensions, confidence levels, extension data — or it can stay exactly this simple and still be more useful than what existed before, which was nothing.

Scope is domain-specific. In a codebase, scope might be file paths: `[src/checkout/**]`. In an AI agent, scope might be capabilities: `[tool:web-search, tool:code-execution]`. In a product strategy, scope might be user journeys: `[onboarding, activation]`. In a regulatory framework, scope might be clause references: `[§4.2, §4.3]`. The core schema requires that scope exists and identifies what the intent binds. How scope references are resolved is defined by the domain layer.

Everything in the specification — the full schema, the self-model structure, the plugin architecture — is enrichment built on top of this floor. An organization that declares fifty four-field intents across its most painful areas has done more for its self-knowledge than one that designs a perfect schema and never fills it in.

---

## V. Adopting in the Real World

The intent model is not only for greenfield systems. Most systems are inherited — partially understood, built by people who have left, carrying intent that nobody can articulate but everybody feels when they try to change something and it resists.

The worst possible approach is a comprehensive audit. Nobody has the time, the knowledge, or the organizational will to retroactively declare achieved intent for an entire inherited system. Any attempt to do so will produce documentation that is immediately stale.

The right approach recognizes that **aspirational intent is always available, even when achieved intent is not.** You don't need to understand the inherited system to declare where you want it to go. And the moment you declare an aspiration, the gap between current reality and desired state becomes the work — visible, structured, and measurable.

### Start with pain, not with structure

Every organization knows where it hurts. The process that always breaks. The area nobody wants to touch. The initiative that took six months instead of six weeks. The failure that keeps recurring.

Each of these pain points is an undeclared intent making itself known through failure. Something was supposed to be true about the system — some property, some invariant, some commitment — and it wasn't written down, so someone violated it.

The first intents you declare are not aspirational. They are forensic: they capture the intent that the failure revealed. Every failure review should produce at least one declared intent. This is the highest-value moment for declaration because the pain is fresh, the context is present, and the cost of *not* declaring is obvious to everyone in the room.

### The "next touch" rule

You do not retroactively declare intent for areas you are not touching. But when you touch an area — to fix a problem, make a change, restructure, respond to an incident — you declare the intent that shapes the area you are working in *before* you change it. Not after. Before.

Over time, intent coverage grows organically toward the parts of the system that are actually alive — the parts that get touched, that change, that matter. Dormant areas never get intent declared, and that is fine.

**The adoption ramp.** The rule starts as **advisory** — changes to undeclared areas trigger a warning, not a block. This advisory phase lasts until the team has built critical mass. The transition to **enforcement** should be an explicit decision, recorded as a transition on the team's adoption intent.

### Declare the unknown explicitly

For inherited systems where nobody knows the intent, the answer is not silence. It is an explicit declaration of uncertainty:

```yaml
intent:
  id: intent-pricing-engine-legacy
  version: 0.1.0
  declares: "UNVERIFIED — this area appears to implement tiered 
             pricing with volume discounts, but the logic has not 
             been fully traced."
  scope: [pricing/engine]
  confidence: low
  needs_verification: true
```

Version `0.x.x` signals this intent is not yet stable. Applied to intent, it means "we think this is what this area intends, but we are not sure." A system with fifty `0.x.x` intents is not a failure. It is a system that knows where its own understanding is thin. That self-awareness is the precondition for improvement.

### AI-assisted inference as scaffolding

For inherited systems, inference is a practical accelerator. Point an AI at a system area and ask: "What does this intend?" The answer will not be ground truth. But it is a starting proposal that a human can validate in five minutes instead of spending two hours on archaeology.

The human remains the authority. The AI is a first-draft machine for intent.

### Intent amnesty

Legacy intent is not only in the artifacts. It is in people's heads. The practical approach is an **intent amnesty**: a structured, time-boxed exercise where team members declare the intents they carry. The prompt is simple: *"What do you know about this system that isn't written down anywhere, that would hurt us if you were gone?"*

Two hours per team. Five to fifteen declared intents, most at `0.x.x` confidence. The difference between zero and fifteen — and those fifteen are the ones that matter most.

### The adoption sequence

1. **Pick one area that hurts.** Not the most important one. The most painful one.
2. **Declare aspirational intents first.** Before trying to understand the existing structure, ask: "What do we *want* this system to intend?"
3. **Run an intent amnesty.** Capture every achieved intent someone can name. Write them as `0.x.x` declarations.
4. **Create the self-model.** Add the manifest, the aspirational intents, and the amnesty intents.
5. **Adopt the "next touch" rule.** Every change must either reference an existing intent or declare a new one.
6. **Feed failures into the model.** Every postmortem produces at least one intent declaration or transition.
7. **Let the gap close naturally.** Achieved coverage grows toward aspirational targets. `0.x.x` intents get verified and promoted to `1.0.0`.
8. **Expand to the next area.** Not by mandate — by demonstration.

The goal is not full coverage. The goal is that the parts of the system that matter most — the parts that change, that break, that hurt — have declared intent. Coverage grows toward pain. That is the right direction.

---

## VI. Second-Order Effects

The first-order effects are clear: traceability, shared language, nameable debt, a practical path into inherited systems. The more interesting question is what emerges once intent is widely declared. These are speculative — none have been tested at scale — but the structural properties of the model make them plausible.

**Onboarding changes shape.** A new team member who reads the self-model can understand the system's orientation in an hour — not just what it does, but what it is committed to, what it is in tension about, and where its understanding of itself is thin.

**System integration gains a new surface.** When two systems need to merge — whether through M&A, platform consolidation, or reorganization — their intent manifests can be compared before any artifacts are touched. Where intents align, integration is likely safe. Where they conflict, the conflict is named early.

**AI agents get purpose contracts.** As agents become more capable, intent declarations can serve as machine-readable boundaries. An agent working within a scope bound by declared intent has a contract for what the system is committed to — and can verify its own actions against that contract. The domain layer for AI agent guardrails explores this directly.

**Auditing shifts from artifacts to purpose.** Compliance teams currently audit artifacts and process. With declared intent, they could audit *purpose* — verifying that the system's declared commitments match requirements, that tensions with compliance intents are resolved, and that no critical intent has gone unaffirmed.

**Intent crosses organizational boundaries.** The spec's dependency model implies cross-system intent contracts. Shared platforms, vendor services, and standards bodies could declare their own intents, giving consumers a purpose contract alongside the interface contract.

---

## VII. How This Fails

A manifesto that describes only success is selling something. The intent model can fail, and teams that adopt it should know what failure looks like.

**Intent declarations become performative.** Teams write intents to satisfy a gate, not to capture real commitments. The symptom: intents that are vague, generic, and interchangeable between any two systems. The quality test is **falsifiability**: if no change could conceivably violate the declaration, it is not an intent — it is a wish. A good declaration follows the pattern *subject + commitment verb + observable predicate*. When reviewing a declaration, ask: "Can I describe a change that would break this?" If no, rewrite it.

**The model becomes a bureaucratic layer.** If declaring intent feels like filling out a form rather than making a commitment, adoption will be grudging. The model should spread by demonstrated value, not by policy.

**Achieved and aspirational intents blur.** When teams stop being honest about the gap, the model loses its most valuable property. An aspirational intent marked as achieved is a lie. When aspirational intents sit at `achieved_coverage: partial` for years without movement, that is a signal: either the aspiration is not real, or nobody is funding the work.

**Nobody reads the intent history.** If transitions accumulate but nobody consults them, the model is producing artifacts that carry no weight. The test: when someone makes a significant change, do they check the intent governing that scope?

**Tensions become permanent.** Declared tensions that are never resolved, revisited, or evolved become furniture. The `resolution_history` exists to detect this.

**Visibility without authority creates structured conflict.** Making tensions explicit is only valuable if someone is authorized to resolve them. The intent model requires that every declared tension names an authority. Without that, you have not created a governance structure. You have created a battlefield with better maps.

The intent model is a tool for honest self-knowledge. It fails whenever it becomes a tool for the appearance of self-knowledge.

---

## VIII. The Practice

This begins with a single act: someone declares what part of the system intends.

Not what it does. Not how it works. What it is *oriented toward*. What property it is committed to maintaining. What tradeoff it has chosen.

That someone might be an engineer, a designer, a policy maker, a safety researcher, a product manager, or any other practitioner. The model does not privilege any discipline. It gives each a surface to declare what matters in their domain — and makes that declaration visible to every other discipline that needs to account for it.

That declaration, versioned and structured, is the seed. Everything else — the transitions, the tensions, the decision traceability, the organizational intent map — grows from that seed.

The practice is:

1. **When you create a boundary, declare its intent** — regardless of which discipline you represent.
2. **When you make a significant decision, link it to the intent it serves.**
3. **When intent changes, record the transition.**
4. **When you encounter resistance, check whether it's bound by an intent — and whether that intent is still alive.**
5. **When your intent crosses into another discipline's territory, declare the tension.** The crossing is the architecture. Make it visible.

Intent is not documentation. Documentation is written after the fact and read reluctantly. Intent is a commitment made at the moment of decision, versioned as the system evolves, and referenced every time someone asks *why*.

---

*Systems carry intent. It was always there. We just never wrote it down.*
