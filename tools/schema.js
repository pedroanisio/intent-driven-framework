const z = require("zod");

// ═══════════════════════════════════════════════════════════════════
// Intent Driven Framework — Zod Schema v0.5.0
// ═══════════════════════════════════════════════════════════════════
//
// Transition from 0.4.0:
//   - Extended Status enum with accepted, deprecated (universal lifecycle)
//   - Added enums: TensionStatus, BoundaryType
//   - Added sub-schemas: TensionResolution, ManifestDependency, ManifestServes
//   - Added entity schemas: StandaloneTransition, Decision, StandaloneTension,
//     OriginRecord, Manifest
//   - Added EntitySchemaMap for multi-entity auto-detection
//   - Added validators: validateDecisionIntegrity, validateStandaloneTensionIntegrity,
//     validateOriginRecordIntegrity, validateManifestIntegrity,
//     validateStandaloneTransitionIntegrity
//   - All changes backward-compatible
//
// Cumulative from 0.1.0:
//   0.2.0: Tension, FalsifiableClaim, FailureMode, CoOrigin, CurrentReality
//          union, TransitionLogEntry union, expanded enums/fields
//   0.3.0: OperationalCycle, OperationalPhase, OperationalConstraint,
//          TddDivergence, TddIsomorphismStatus
//   0.4.0: ProvidesItem, provides, design_stance
//   0.5.0: Multi-entity SDLC validation (Decision, StandaloneTension,
//          OriginRecord, Manifest, StandaloneTransition)
//
// ═══════════════════════════════════════════════════════════════════

// ─── CANONICAL ENUMS ──────────────────────────────────────────────

const ChangeType = z.enum([
  "clarification", "correction", "extension",
  "reclassification", "breaking", "deprecation",
  "MAJOR", "MINOR", "PATCH",
]);

const IntentType = z.enum(["aspirational", "achieved"]);
const Priority = z.enum(["critical", "high", "medium", "low"]);
// v0.5.0: added accepted, deprecated — universal lifecycle for decisions
const Status = z.enum([
  "proposed", "active", "evolving", "superseded", "residual", "retracted",
  "accepted", "deprecated",
]);
const Confidence = z.enum(["high", "medium", "low"]);
const Tier = z.enum(["core", "deferred"]);
const AchievedCoverage = z.enum(["none", "minimal", "partial", "substantial", "full"]);

const OriginType = z.enum([
  "engineering", "product", "incident", "discovery",
  "regulatory", "organizational", "devops", "ux", "data", "sre", "security",
]);

const OriginRelationship = z.enum([
  "derived_from", "motivated_by", "constrained_by",
  "triggered_by", "discovered_in",
]);

const FalsifiableClaimStatus = z.enum([
  "supported", "partially_verified", "supported_in_theory",
  "unverified", "falsified",
]);

const TddIsomorphismStatus = z.enum([
  "claimed", "structural", "analogical_only",
]);

// ─── v0.5.0 ENUMS ──────────────────────────────────────────────

const TensionStatus = z.enum(["active", "resolved", "dormant", "escalated"]);
const BoundaryType = z.enum(["service", "library", "platform", "gateway"]);

// ─── PRIMITIVES ───────────────────────────────────────────────────

const SemVer = z.string().regex(/^\d+\.\d+\.\d+$/, "Must be valid semver (MAJOR.MINOR.PATCH)");
const DateString = z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Must be YYYY-MM-DD");

// ─── CURRENT REALITY ──────────────────────────────────────────────

const RemainingWorkItem = z.object({
  id: z.string().min(1),
  description: z.string().min(1),
  blocks: z.string().min(1).optional(),
  priority: Priority.optional(),
  note: z.string().optional(),
});

const CurrentReality = z.object({
  state: z.string().min(1, "current_reality.state must be non-empty"),
  last_assessed: DateString.optional(),
  assessed: DateString.optional(),
  status: z.string().min(1).optional(),
  remaining_work: z.union([
    z.string().min(1),
    z.array(RemainingWorkItem).min(1),
  ]).optional(),
  gap_assessment: z.string().min(1).optional(),
  gap: z.string().min(1).optional(),
}).refine(
  (data) => data.last_assessed || data.assessed,
  { message: "current_reality must have either 'last_assessed' or 'assessed' date field" }
).refine(
  (data) => data.gap || (data.status && data.remaining_work) || data.gap_assessment,
  { message: "current_reality must have either 'gap', 'status'+'remaining_work', or 'gap_assessment'" }
);

// ─── SCOPE ────────────────────────────────────────────────────────

const Scope = z.object({
  primary: z.array(z.string().min(1)).min(1, "scope.primary must have at least one entry"),
  implicit: z.array(z.string().min(1)).optional(),
});

// ─── ORIGIN ───────────────────────────────────────────────────────

const Origin = z.object({
  type: OriginType,
  ref: z.string().min(1),
  relationship: OriginRelationship,
  accessibility: z.string().optional(),
  note: z.string().optional(),
});

const CoOrigin = z.object({
  type: OriginType,
  ref: z.string().min(1),
  relationship: OriginRelationship,
  note: z.string().optional(),
});

// ─── TRANSITION LOG ───────────────────────────────────────────────

const LegacyTransitionLogEntry = z.object({
  from: SemVer, to: SemVer,
  change_type: ChangeType, summary: z.string().min(1),
});

const CanonicalTransitionLogEntry = z.object({
  from_version: SemVer, to_version: SemVer,
  change_type: ChangeType, date: DateString.optional(),
  reason: z.string().min(1), forcing_function: z.string().optional(),
  what_changed: z.array(z.string().min(1)).optional(),
  residue: z.string().optional(),
});

const TransitionLogEntry = z.union([CanonicalTransitionLogEntry, LegacyTransitionLogEntry]);

// ─── TENSIONS ─────────────────────────────────────────────────────

const ResolutionStrategy = z.object({
  type: z.enum(["policy", "priority_ordering", "delegation"]),
  rule: z.string().min(1),
});

const Tension = z.object({
  id: z.string().regex(/^T-\d{2}$/, "Must match T-NN pattern"),
  name: z.string().min(1),
  between: z.array(z.string().min(1)).length(2, "Tensions must be between exactly two concerns"),
  resolution_strategy: ResolutionStrategy,
  resolution_owner: z.string().min(1),
  last_reviewed: DateString,
  staleness_threshold_days: z.number().int().positive(),
});

// ─── FALSIFIABLE CLAIMS ───────────────────────────────────────────

const FalsifiableClaim = z.object({
  id: z.string().regex(/^FC-\d{2}$/, "Must match FC-NN pattern"),
  claim: z.string().min(1),
  falsified_when: z.string().min(1),
  status: FalsifiableClaimStatus,
  evidence: z.string().min(1),
});

// ─── FAILURE MODES ────────────────────────────────────────────────

const FailureMode = z.object({
  id: z.string().regex(/^FM-\d{2}$/, "Must match FM-NN pattern"),
  name: z.string().min(1),
  description: z.string().min(1),
  diagnostic: z.string().min(1),
  mitigation: z.string().min(1),
});

// ─── OPERATIONAL CYCLE (v0.3.0) ───────────────────────────────────

const OperationalPhase = z.object({
  id: z.enum(["red", "green", "refactor"]),
  name: z.string().min(1),
  definition: z.string().min(1),
  tdd_parallel: z.string().optional(),
  rule: z.string().min(1),
  outputs: z.array(z.string().min(1)).min(1),
});

const OperationalConstraint = z.object({
  id: z.string().regex(/^OC-\d{2}$/, "Must match OC-NN pattern"),
  rule: z.string().min(1),
  violation: z.string().min(1),
});

const TddDivergenceItem = z.object({
  aspect: z.string().min(1),
  tdd: z.string().min(1),
  intent_driven: z.string().min(1),
});

const TddDivergence = z.object({
  note: z.string().optional(),
  differences: z.array(TddDivergenceItem).min(1),
});

const OperationalCycle = z.object({
  name: z.string().min(1),
  tdd_isomorphism: TddIsomorphismStatus,
  isomorphism_claim: z.string().optional(),
  phases: z.array(OperationalPhase).length(3, "Operational cycle must have exactly 3 phases"),
  constraints: z.array(OperationalConstraint).min(1),
  divergence_from_tdd: TddDivergence.optional(),
});

// ─── PROVIDES (v0.4.0) ───────────────────────────────────────────
// Concrete deliverables that satisfy the declares commitment.
// Each item maps to falsifiable claims via tested_by.

const ProvidesItem = z.object({
  id: z.string().regex(/^provides-[a-z]$/, "Must match provides-X pattern"),
  description: z.string().min(1),
  tested_by: z.array(z.string().regex(/^(FC-\d{2}|CC-\d{2}[a-z]?)$/)).default([]),
});

// ─── v0.5.0 SUB-SCHEMAS ─────────────────────────────────────────
// Tension resolution entry — used by StandaloneTension's
// current_resolution and resolution_history[].

const TensionResolution = z.object({
  strategy: z.string().min(1),
  decided: DateString,
  applies_to: z.array(SemVer).length(2, "applies_to must be a pair of semver versions"),
  decision_ref: z.string().optional(),
  superseded: DateString.optional(),
  reason: z.string().optional(),
});

const ManifestDependency = z.object({
  repo: z.string().min(1),
  intent: z.string().min(1),
  minimum_version: SemVer,
});

const ManifestServes = z.object({
  org_intent: z.string().min(1),
});

// ─── v0.5.0 ENTITY SCHEMAS ──────────────────────────────────────
// Standalone entity schemas for SDLC multi-entity validation.
// The existing Tension (inline) stays as-is for IntentSchema.tensions[].

const StandaloneTransition = z.object({
  intent_id: z.string().min(1),
  from_version: SemVer,
  to_version: SemVer,
  date: DateString.optional(),
  author: z.string().min(1),
  change_type: ChangeType,
  reason: z.string().min(1),
  forcing_function: z.string().optional(),
  what_changed: z.array(z.string().min(1)).optional(),
  residue: z.string().optional(),
  ext: z.record(z.string(), z.any()).optional(),
});

const Decision = z.object({
  id: z.string().min(1),
  title: z.string().min(1),
  date: DateString.optional(),
  status: Status,
  owner: z.string().min(1),
  serves_intent: z.string().min(1),
  intent_version: SemVer,
  scope: z.array(z.string().min(1)).min(1),
  refs: z.array(z.string().min(1)).optional(),
  triggers_transition: z.string().optional(),
  context: z.string().optional(),
  decision: z.string().optional(),
  consequences: z.string().optional(),
  ext: z.record(z.string(), z.any()).optional(),
});

const StandaloneTension = z.object({
  id: z.string().regex(/^T-\d{2,}$/, "Must match T-NN pattern"),
  between: z.array(z.string().min(1)).length(2, "Tensions must be between exactly two intent refs"),
  declared: DateString.optional(),
  status: TensionStatus,
  description: z.string().min(1),
  cross_discipline: z.boolean(),
  disciplines: z.array(z.string().min(1)).min(1),
  current_resolution: TensionResolution.optional(),
  resolution_history: z.array(TensionResolution).optional(),
  resolution_owner: z.string().min(1),
  escalation_path: z.string().optional(),
  last_reviewed: DateString.optional(),
  ext: z.record(z.string(), z.any()).optional(),
});

const OriginRecord = z.object({
  id: z.string().min(1),
  type: OriginType,
  external_ref: z.string().min(1),
  external_system: z.string().min(1),
  date: DateString.optional(),
  summary: z.string().min(1),
  generated_intents: z.array(z.string().min(1)).optional(),
  constrained_intents: z.array(z.string().min(1)).optional(),
  ext: z.record(z.string(), z.any()).optional(),
});

const Manifest = z.object({
  name: z.string().min(1),
  declares: z.string().min(1),
  domain: z.string().min(1),
  boundary_type: BoundaryType,
  version: SemVer,
  schema_version: SemVer,
  serves: z.array(ManifestServes).optional(),
  depends_on_intents: z.array(ManifestDependency).optional(),
  plugins: z.string().optional(),
  ext: z.record(z.string(), z.any()).optional(),
});

// ─── COMPLETENESS CRITERIA ────────────────────────────────────────

const BaseCriterion = z.object({
  id: z.string().regex(/^CC-\d{2}[a-z]?$/, "Must match CC-NN or CC-NNx pattern"),
  tier: Tier.default("core"),
  test: z.string().min(1),
  verifiable_by: z.string().min(1),
  rationale: z.string().optional(),
  implementation_note: z.string().optional(),
  scope_boundary: z.string().optional(),
  note: z.string().optional(),
});

const CoreCriterion = BaseCriterion.extend({
  tier: z.literal("core").default("core"),
  eval_order: z.enum(["first", "last"]).optional(),
  depends_on: z.array(z.string().regex(/^CC-\d{2}[a-z]?$/)).optional(),
});

const DeferredCriterion = BaseCriterion.extend({
  tier: z.literal("deferred"),
  promote_when: z.string().min(1, "Deferred criteria must have a promote_when condition"),
  downstream_dependents: z.array(z.string().regex(/^CC-\d{2}[a-z]?$/)).optional(),
});

const CriteriaCategories = z.object({
  philosophy: z.array(CoreCriterion).optional(),
  model: z.array(CoreCriterion).optional(),
  conflict: z.array(CoreCriterion).optional(),
  structure: z.array(CoreCriterion).optional(),
  extensibility: z.array(CoreCriterion).optional(),
  adoption: z.array(CoreCriterion).optional(),
  "self-sufficiency": z.array(CoreCriterion).optional(),
  "self-conformance": z.array(CoreCriterion).optional(),
  operational: z.array(CoreCriterion).optional(),
  deferred: z.array(DeferredCriterion).optional(),
});

// ─── TOP-LEVEL INTENT SCHEMA ──────────────────────────────────────

const IntentSchema = z.object({
  id: z.string().min(1),
  version: SemVer,
  schema_version: SemVer.optional(),
  declares: z.string().min(1),
  intent_type: IntentType,

  priority: Priority,
  status: Status,
  confidence: Confidence,
  confidence_rationale: z.string().optional(),
  needs_verification: z.boolean().optional(),
  achieved_coverage: AchievedCoverage.optional(),

  scope: Scope,

  owner: z.string().min(1),
  last_affirmed: DateString.optional(),
  created: DateString.optional(),

  origin: Origin,
  co_origins: z.array(CoOrigin).optional(),

  serves: z.array(z.string()).optional(),
  supersedes: z.array(z.string()).optional(),
  dependencies: z.array(z.string()).default([]),

  current_reality: CurrentReality.optional(),

  retirement_conditions: z.string().optional(),

  // v0.3.0
  operational_cycle: OperationalCycle.optional(),

  // v0.4.0
  provides: z.array(ProvidesItem).optional(),
  design_stance: z.string().optional(),

  // Governance
  tensions: z.array(Tension).optional(),
  falsifiable_claims: z.array(FalsifiableClaim).optional(),
  failure_modes: z.array(FailureMode).optional(),

  transition_log: z.array(TransitionLogEntry).optional(),
  completeness_criteria: CriteriaCategories.optional(),

  ext: z.record(z.string(), z.any()).optional(),
});

// ─── ASPIRATIONAL REFINEMENT ──────────────────────────────────────

const AspirationalIntent = IntentSchema.refine(
  (data) => {
    if (data.intent_type === "aspirational" && !data.current_reality) return false;
    return true;
  },
  { message: "Aspirational intents must include a current_reality block (CC-08)", path: ["current_reality"] }
);

// ═══════════════════════════════════════════════════════════════════
// STRUCTURAL VALIDATORS
// ═══════════════════════════════════════════════════════════════════

// ─── v0.1.0 ───────────────────────────────────────────────────────

function validateTransitionLogIntegrity(intent) {
  const errors = [];
  const log = intent.transition_log;
  if (!log || log.length === 0) return errors;

  const getFrom = (e) => e.from || e.from_version;
  const getTo = (e) => e.to || e.to_version;

  function checkChain(entries) {
    const ce = [];
    for (let i = 0; i < entries.length - 1; i++) {
      if (getTo(entries[i]) !== getFrom(entries[i + 1])) {
        ce.push({ criterion: "CC-27(a)", message: `Gap in transition log: ${getTo(entries[i])} → ${getFrom(entries[i + 1])}` });
      }
    }
    const last = entries[entries.length - 1];
    if (getTo(last) !== intent.version) {
      ce.push({ criterion: "CC-27(a)", message: `Transition log ends at ${getTo(last)} but intent version is ${intent.version}` });
    }
    return ce;
  }

  const ce = checkChain([...log]);
  const re = checkChain([...log].reverse());
  if (ce.length === 0 || re.length === 0) return [];
  return ce.length <= re.length ? ce : re;
}

function validateCriterionIdUniqueness(intent) {
  const errors = [];
  const cc = intent.completeness_criteria;
  if (!cc) return errors;
  const ids = new Set(), dupes = [];
  for (const [, criteria] of Object.entries(cc)) {
    if (!Array.isArray(criteria)) continue;
    for (const c of criteria) { if (ids.has(c.id)) dupes.push(c.id); ids.add(c.id); }
  }
  if (dupes.length > 0) errors.push({ criterion: "CC-05", message: `Duplicate criterion IDs: ${dupes.join(", ")}` });
  return errors;
}

function validateScopeCoverage(intent) {
  const errors = [];
  const primary = new Set(intent.scope.primary || []);
  const dupes = (intent.scope.implicit || []).filter((i) => primary.has(i));
  if (dupes.length > 0) errors.push({ criterion: "CC-18(b)", message: `Scope items in both primary and implicit: ${dupes.join(", ")}` });
  return errors;
}

function validateDeferredCriteria(intent) {
  const errors = [];
  const cc = intent.completeness_criteria;
  if (!cc || !cc.deferred) return errors;
  for (const c of cc.deferred) {
    if (!c.promote_when) errors.push({ criterion: c.id, message: `Deferred criterion ${c.id} missing promote_when` });
  }
  return errors;
}

function validateSelfConformance(intent) {
  const errors = [];
  if (intent.intent_type === "aspirational" && !intent.current_reality) {
    errors.push({ criterion: "CC-18(a)", message: "Aspirational intent missing current_reality block" });
  }
  if (!intent.schema_version) {
    errors.push({ criterion: "CC-18(d)", message: "Intent block missing schema_version field" });
  }
  return errors;
}

function validateDependsOnRefs(intent) {
  const errors = [];
  const cc = intent.completeness_criteria;
  if (!cc) return errors;
  const allIds = new Set();
  for (const [, criteria] of Object.entries(cc)) {
    if (!Array.isArray(criteria)) continue;
    for (const c of criteria) allIds.add(c.id);
  }
  for (const [, criteria] of Object.entries(cc)) {
    if (!Array.isArray(criteria)) continue;
    for (const c of criteria) {
      for (const dep of c.depends_on || []) { if (!allIds.has(dep)) errors.push({ criterion: "CC-18", message: `${c.id} depends_on ${dep} which does not exist` }); }
      for (const dep of c.downstream_dependents || []) { if (!allIds.has(dep)) errors.push({ criterion: "CC-18", message: `${c.id} downstream_dependent ${dep} does not exist` }); }
    }
  }
  return errors;
}

// ─── v0.2.0 ───────────────────────────────────────────────────────

function validateTensionIntegrity(intent) {
  const errors = [];
  if (!intent.tensions || intent.tensions.length === 0) return errors;
  const ids = new Set();
  for (const t of intent.tensions) {
    if (ids.has(t.id)) errors.push({ criterion: "P-07", message: `Duplicate tension ID: ${t.id}` });
    ids.add(t.id);
    if (t.resolution_strategy && t.resolution_strategy.rule && t.resolution_strategy.rule.trim().length < 20) {
      errors.push({ criterion: "P-07", message: `${t.id}: resolution_strategy.rule too brief` });
    }
    if (t.last_reviewed && t.staleness_threshold_days) {
      const d = Math.floor((new Date() - new Date(t.last_reviewed)) / 864e5);
      if (d > t.staleness_threshold_days) errors.push({ criterion: "P-07", message: `${t.id} "${t.name}": stale — ${d}d since review (threshold: ${t.staleness_threshold_days}d)` });
    }
  }
  return errors;
}

function validateFalsifiableClaimsIntegrity(intent) {
  const errors = [];
  if (!intent.falsifiable_claims || intent.falsifiable_claims.length === 0) return errors;
  const ids = new Set();
  for (const fc of intent.falsifiable_claims) {
    if (ids.has(fc.id)) errors.push({ criterion: "FC-INTEGRITY", message: `Duplicate claim ID: ${fc.id}` });
    ids.add(fc.id);
    if (fc.status === "unverified" && (!fc.evidence || fc.evidence.trim().length < 10)) {
      errors.push({ criterion: "FC-INTEGRITY", message: `${fc.id}: unverified but evidence doesn't explain why` });
    }
    if (fc.status === "falsified") {
      errors.push({ criterion: "FC-INTEGRITY", message: `${fc.id}: FALSIFIED — intent must evolve or be retracted` });
    }
  }
  return errors;
}

function validateFailureModeIntegrity(intent) {
  const errors = [];
  if (!intent.failure_modes || intent.failure_modes.length === 0) return errors;
  const ids = new Set();
  for (const fm of intent.failure_modes) {
    if (ids.has(fm.id)) errors.push({ criterion: "FM-INTEGRITY", message: `Duplicate failure mode ID: ${fm.id}` });
    ids.add(fm.id);
    if (fm.diagnostic && fm.diagnostic.trim().length < 20) errors.push({ criterion: "FM-INTEGRITY", message: `${fm.id} "${fm.name}": diagnostic too brief` });
    if (fm.mitigation && fm.mitigation.trim().length < 20) errors.push({ criterion: "FM-INTEGRITY", message: `${fm.id} "${fm.name}": mitigation too brief` });
  }
  return errors;
}

function validateRetirementConditions(intent) {
  const errors = [];
  const isRoot = !intent.serves || intent.serves.length === 0;
  if (isRoot && !intent.retirement_conditions) errors.push({ criterion: "LIFECYCLE", message: "Root intent should declare retirement_conditions" });
  return errors;
}

function validateCoOriginConsistency(intent) {
  const errors = [];
  if (!intent.co_origins || intent.co_origins.length === 0) return errors;
  const refs = new Set();
  if (intent.origin) refs.add(intent.origin.ref);
  for (const co of intent.co_origins) {
    if (refs.has(co.ref)) errors.push({ criterion: "PROVENANCE", message: `co_origin ref "${co.ref}" duplicates another ref` });
    refs.add(co.ref);
  }
  return errors;
}

function validateDeclaresQuality(intent) {
  const errors = [];
  if (!intent.declares) return errors;
  if (intent.declares.trim().length < 50) errors.push({ criterion: "CC-19", message: "declares field suspiciously brief" });
  for (const p of [/intends to work correctly/i, /intends to be good/i, /aims to provide value/i, /strives for excellence/i]) {
    if (p.test(intent.declares)) errors.push({ criterion: "CC-19", message: `declares matches generic pattern: ${p.source}` });
  }
  return errors;
}

function validateAffirmationStaleness(intent) {
  const errors = [];
  if (!intent.last_affirmed) return errors;
  const d = Math.floor((new Date() - new Date(intent.last_affirmed)) / 864e5);
  if (intent.status === "active" && d > 365) errors.push({ criterion: "STALENESS", message: `Last affirmed ${intent.last_affirmed} (${d}d ago)` });
  return errors;
}

// ─── v0.3.0 ───────────────────────────────────────────────────────

function validateOperationalCycleIntegrity(intent) {
  const errors = [];
  const cycle = intent.operational_cycle;
  if (!cycle) return errors;

  const expected = ["red", "green", "refactor"];
  if (cycle.phases) {
    const actual = cycle.phases.map((p) => p.id);
    for (let i = 0; i < expected.length; i++) {
      if (actual[i] !== expected[i]) {
        errors.push({ criterion: "OC-INTEGRITY", message: `Phase ordering must be red → green → refactor, got: ${actual.join(" → ")}` });
        break;
      }
    }
    for (const phase of cycle.phases) {
      if (!phase.rule || phase.rule.trim().length < 20) errors.push({ criterion: "OC-INTEGRITY", message: `Phase "${phase.id}": rule too brief` });
    }
  }

  if (cycle.constraints) {
    const ids = new Set();
    for (const c of cycle.constraints) {
      if (ids.has(c.id)) errors.push({ criterion: "OC-INTEGRITY", message: `Duplicate constraint ID: ${c.id}` });
      ids.add(c.id);
    }
  }

  if (cycle.tdd_isomorphism === "structural" && intent.falsifiable_claims) {
    const fc07 = intent.falsifiable_claims.find((fc) => fc.id === "FC-07");
    if (fc07 && fc07.status !== "supported") {
      errors.push({ criterion: "OC-INTEGRITY", message: `tdd_isomorphism is "structural" but FC-07 status is "${fc07.status}"` });
    }
  }

  return errors;
}

function validateCycleConstraintCoverage(intent) {
  const errors = [];
  const cycle = intent.operational_cycle;
  if (!cycle || !cycle.constraints) return errors;
  const ids = new Set(cycle.constraints.map((c) => c.id));
  for (const req of [
    { id: "OC-01", why: "Red before Green — the cycle's primary discipline" },
    { id: "OC-02", why: "Green before Refactor — prevents premature evolution" },
    { id: "OC-03", why: "Green must be evidenced — prevents green-washing (FM-06)" },
  ]) {
    if (!ids.has(req.id)) errors.push({ criterion: "OC-COVERAGE", message: `Missing required constraint ${req.id}: ${req.why}` });
  }
  return errors;
}

// ─── v0.4.0 ───────────────────────────────────────────────────────

function validateProvidesFcRefs(intent) {
  const errors = [];
  if (!intent.provides) return errors;

  // Collect all FC and CC IDs available in this intent
  const fcIds = new Set();
  if (intent.falsifiable_claims) {
    for (const fc of intent.falsifiable_claims) fcIds.add(fc.id);
  }
  const ccIds = new Set();
  if (intent.completeness_criteria) {
    for (const [, criteria] of Object.entries(intent.completeness_criteria)) {
      if (!Array.isArray(criteria)) continue;
      for (const c of criteria) ccIds.add(c.id);
    }
  }
  const allTestableIds = new Set([...fcIds, ...ccIds]);

  // Check provides ID uniqueness
  const provIds = new Set();
  for (const item of intent.provides) {
    if (provIds.has(item.id)) {
      errors.push({ criterion: "PROVIDES", message: `Duplicate provides ID: ${item.id}` });
    }
    provIds.add(item.id);

    // Check tested_by refs resolve
    for (const ref of item.tested_by || []) {
      if (!allTestableIds.has(ref)) {
        errors.push({
          criterion: "PROVIDES",
          message: `${item.id}: tested_by references "${ref}" which does not exist in falsifiable_claims or completeness_criteria`,
        });
      }
    }
  }

  return errors;
}

function validateProvidesCompleteness(intent) {
  const errors = [];
  if (!intent.provides) return errors;

  for (const item of intent.provides) {
    if (!item.tested_by || item.tested_by.length === 0) {
      errors.push({
        criterion: "PROVIDES",
        message: `${item.id}: has no tested_by references — deliverable is not linked to any falsifiable claim or criterion`,
      });
    }
  }

  return errors;
}

// ─── v0.5.0 ENTITY SCHEMA MAP ────────────────────────────────────
// Maps YAML top-level key → Zod schema for auto-detection in validate.js.

const EntitySchemaMap = {
  intent: IntentSchema,
  transition: StandaloneTransition,
  decision: Decision,
  tension: StandaloneTension,
  origin_record: OriginRecord,
  repo: Manifest,
};

// ─── v0.5.0 STRUCTURAL VALIDATORS ───────────────────────────────

function validateDecisionIntegrity(decision) {
  const errors = [];
  if (decision.status === "accepted" && (!decision.context || decision.context.trim().length < 20)) {
    errors.push({ criterion: "DECISION", message: "accepted decision should have substantive context (>=20 chars)" });
  }
  if (decision.status === "accepted" && (!decision.refs || decision.refs.length === 0)) {
    errors.push({ criterion: "DECISION", message: "accepted decision has no refs (commit SHAs, PR URLs)" });
  }
  return errors;
}

function validateStandaloneTensionIntegrity(tension) {
  const errors = [];
  if (tension.status === "active" && !tension.current_resolution && !tension.escalation_path) {
    errors.push({
      criterion: "TENSION",
      message: `${tension.id}: active tension has no current_resolution and no escalation_path`,
    });
  }
  if (tension.status === "resolved" && !tension.current_resolution) {
    errors.push({
      criterion: "TENSION",
      message: `${tension.id}: resolved tension has no current_resolution`,
    });
  }
  if (tension.resolution_history && tension.resolution_history.length > 1) {
    for (let i = 0; i < tension.resolution_history.length - 1; i++) {
      const curr = tension.resolution_history[i];
      const next = tension.resolution_history[i + 1];
      if (curr.decided && next.decided && curr.decided > next.decided) {
        errors.push({
          criterion: "TENSION",
          message: `${tension.id}: resolution_history not chronological at index ${i}`,
        });
      }
    }
  }
  if (tension.cross_discipline && tension.disciplines && tension.disciplines.length < 2) {
    errors.push({
      criterion: "TENSION",
      message: `${tension.id}: cross_discipline=true but fewer than 2 disciplines listed`,
    });
  }
  return errors;
}

function validateOriginRecordIntegrity(originRecord) {
  const errors = [];
  const gen = originRecord.generated_intents || [];
  const con = originRecord.constrained_intents || [];
  if (gen.length === 0 && con.length === 0) {
    errors.push({
      criterion: "ORIGIN",
      message: `${originRecord.id}: origin record has no generated_intents or constrained_intents (empty reverse index)`,
    });
  }
  return errors;
}

function validateManifestIntegrity(manifest) {
  const errors = [];
  if (manifest.declares && manifest.declares.trim().length < 30) {
    errors.push({ criterion: "MANIFEST", message: "manifest declares field is too brief (<30 chars)" });
  }
  return errors;
}

function validateStandaloneTransitionIntegrity(transition) {
  const errors = [];
  if (transition.reason && transition.reason.trim().length < 20) {
    errors.push({ criterion: "TRANSITION", message: "transition reason too brief (<20 chars)" });
  }
  if (transition.from_version === transition.to_version) {
    errors.push({
      criterion: "TRANSITION",
      message: `transition from ${transition.from_version} to ${transition.to_version}: versions must differ`,
    });
  }
  return errors;
}

// ─── EXPORTS ──────────────────────────────────────────────────────

module.exports = {
  // Enums
  ChangeType, IntentType, Priority, Status, Confidence, Tier,
  OriginType, OriginRelationship, FalsifiableClaimStatus,
  AchievedCoverage, TddIsomorphismStatus,
  // v0.5.0 enums
  TensionStatus, BoundaryType,
  // Primitives
  SemVer, DateString,
  // Sub-schemas
  CurrentReality, Scope, Origin, CoOrigin,
  TransitionLogEntry, LegacyTransitionLogEntry, CanonicalTransitionLogEntry,
  Tension, ResolutionStrategy, FalsifiableClaim, FailureMode,
  RemainingWorkItem, CoreCriterion, DeferredCriterion, CriteriaCategories,
  OperationalPhase, OperationalConstraint, TddDivergenceItem,
  TddDivergence, OperationalCycle,
  ProvidesItem,
  // v0.5.0 sub-schemas
  TensionResolution, ManifestDependency, ManifestServes,
  // Top-level
  IntentSchema, AspirationalIntent,
  // v0.5.0 entity schemas
  StandaloneTransition, Decision, StandaloneTension, OriginRecord, Manifest,
  // v0.5.0 entity map
  EntitySchemaMap,
  // v0.1.0 validators
  validateTransitionLogIntegrity, validateCriterionIdUniqueness,
  validateScopeCoverage, validateDeferredCriteria,
  validateSelfConformance, validateDependsOnRefs,
  // v0.2.0 validators
  validateTensionIntegrity, validateFalsifiableClaimsIntegrity,
  validateFailureModeIntegrity, validateRetirementConditions,
  validateCoOriginConsistency, validateDeclaresQuality,
  validateAffirmationStaleness,
  // v0.3.0 validators
  validateOperationalCycleIntegrity, validateCycleConstraintCoverage,
  // v0.4.0 validators
  validateProvidesFcRefs, validateProvidesCompleteness,
  // v0.5.0 validators
  validateDecisionIntegrity, validateStandaloneTensionIntegrity,
  validateOriginRecordIntegrity, validateManifestIntegrity,
  validateStandaloneTransitionIntegrity,
};