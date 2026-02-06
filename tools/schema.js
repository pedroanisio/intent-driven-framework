const z = require("zod");

// ─── CANONICAL ENUMS ──────────────────────────────────────────────

const ChangeType = z.enum([
  "clarification",
  "correction",
  "extension",
  "reclassification",
  "breaking",
  "deprecation",
]);

const IntentType = z.enum(["aspirational", "achieved"]);

const Priority = z.enum(["critical", "high", "medium", "low"]);

const Status = z.enum(["proposed", "active", "evolving", "superseded", "residual", "retracted"]);

const Confidence = z.enum(["high", "medium", "low"]);

const Tier = z.enum(["core", "deferred"]);

const AchievedCoverage = z.enum(["none", "minimal", "partial", "substantial", "full"]);

// All origin types — closed enum per CC-05. New values require a
// schema_version bump per CC-24. Plugins extend via ext: namespace,
// not by adding origin_type values.
const OriginType = z.enum([
  "engineering", "product", "incident", "discovery",
  "regulatory", "organizational", "devops", "ux", "data", "sre", "security",
]);

// ─── SEMVER ───────────────────────────────────────────────────────

const SemVer = z
  .string()
  .regex(/^\d+\.\d+\.\d+$/, "Must be valid semver (MAJOR.MINOR.PATCH)");

// ─── SUB-SCHEMAS ──────────────────────────────────────────────────

const CurrentReality = z.object({
  state: z.string().min(1, "current_reality.state must be non-empty"),
  // v1.3.0+: gap was split into status + remaining_work
  status: z.string().min(1).optional(),
  remaining_work: z.string().min(1).optional(),
  // pre-v1.3.0 format
  gap: z.string().min(1).optional(),
  last_assessed: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Must be YYYY-MM-DD"),
}).refine(
  (data) => data.gap || (data.status && data.remaining_work),
  {
    message:
      "current_reality must have either 'gap' (pre-v1.3.0) or both 'status' and 'remaining_work' (v1.3.0+)",
  }
);

const Scope = z.object({
  primary: z.array(z.string().min(1)).min(1, "scope.primary must have at least one entry"),
  implicit: z.array(z.string().min(1)).optional(),
});

const Origin = z.object({
  type: OriginType,
  ref: z.string().min(1),
  relationship: z.enum([
    "derived_from",
    "motivated_by",
    "constrained_by",
    "triggered_by",
    "discovered_in",
  ]),
});

const TransitionLogEntry = z.object({
  from: SemVer,
  to: SemVer,
  change_type: ChangeType,
  summary: z.string().min(1),
});

// ─── COMPLETENESS CRITERION ───────────────────────────────────────

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

// ─── CRITERIA CATEGORIES ──────────────────────────────────────────

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

  // Required for aspirational, forbidden for achieved
  current_reality: CurrentReality.optional(),

  // Optional for achieved intents — tracks implementation coverage
  achieved_coverage: AchievedCoverage.optional(),

  scope: Scope,
  priority: Priority,
  status: Status,
  owner: z.string().min(1),
  confidence: Confidence,
  origin: Origin,
  dependencies: z.array(z.string()).default([]),

  transition_log: z.array(TransitionLogEntry).optional(),
  completeness_criteria: CriteriaCategories.optional(),
});

// ─── ASPIRATIONAL-SPECIFIC REFINEMENTS ────────────────────────────

const AspirationalIntent = IntentSchema.refine(
  (data) => {
    if (data.intent_type === "aspirational" && !data.current_reality) {
      return false;
    }
    return true;
  },
  {
    message:
      "Aspirational intents must include a current_reality block (CC-08)",
    path: ["current_reality"],
  }
);

// ─── STRUCTURAL VALIDATORS ────────────────────────────────────────
// These go beyond schema shape and test the model's own rules.

function validateTransitionLogIntegrity(intent) {
  const errors = [];
  const log = intent.transition_log;
  if (!log || log.length === 0) return errors;

  // CC-27(a): No gaps in version sequence
  for (let i = 0; i < log.length - 1; i++) {
    if (log[i].to !== log[i + 1].from) {
      errors.push({
        criterion: "CC-27(a)",
        message: `Gap in transition log: ${log[i].to} → ${log[i + 1].from}`,
      });
    }
  }

  // CC-27(a): Last entry's 'to' should match current version
  const lastTo = log[log.length - 1].to;
  if (lastTo !== intent.version) {
    errors.push({
      criterion: "CC-27(a)",
      message: `Transition log ends at ${lastTo} but intent version is ${intent.version}`,
    });
  }

  return errors;
}

function validateCriterionIdUniqueness(intent) {
  const errors = [];
  const cc = intent.completeness_criteria;
  if (!cc) return errors;

  const ids = new Set();
  const duplicates = [];

  for (const [category, criteria] of Object.entries(cc)) {
    if (!Array.isArray(criteria)) continue;
    for (const c of criteria) {
      if (ids.has(c.id)) {
        duplicates.push(c.id);
      }
      ids.add(c.id);
    }
  }

  if (duplicates.length > 0) {
    errors.push({
      criterion: "CC-05",
      message: `Duplicate criterion IDs: ${duplicates.join(", ")}`,
    });
  }

  return errors;
}

function validateScopeCoverage(intent) {
  const errors = [];
  const cc = intent.completeness_criteria;
  if (!cc) return errors;

  const scopeEntries = [
    ...(intent.scope.primary || []),
    ...(intent.scope.implicit || []),
  ];

  // Check that primary scope items don't also appear in implicit
  const primary = new Set(intent.scope.primary || []);
  const implicit = intent.scope.implicit || [];
  const duplicates = implicit.filter((item) => primary.has(item));

  if (duplicates.length > 0) {
    errors.push({
      criterion: "CC-18(b)",
      message: `Scope items appear in both primary and implicit: ${duplicates.join(", ")}`,
    });
  }

  return errors;
}

function validateDeferredCriteria(intent) {
  const errors = [];
  const cc = intent.completeness_criteria;
  if (!cc || !cc.deferred) return errors;

  for (const criterion of cc.deferred) {
    if (!criterion.promote_when) {
      errors.push({
        criterion: criterion.id,
        message: `Deferred criterion ${criterion.id} missing promote_when condition`,
      });
    }
  }

  return errors;
}

function validateSelfConformance(intent) {
  const errors = [];

  // CC-18(a): current_reality present and non-empty for aspirational
  if (intent.intent_type === "aspirational") {
    if (!intent.current_reality) {
      errors.push({
        criterion: "CC-18(a)",
        message: "Aspirational intent missing current_reality block",
      });
    }
  }

  // CC-18(d): schema_version present
  if (!intent.schema_version) {
    errors.push({
      criterion: "CC-18(d)",
      message: "Intent block missing schema_version field",
    });
  }

  return errors;
}

function validateDependsOnRefs(intent) {
  const errors = [];
  const cc = intent.completeness_criteria;
  if (!cc) return errors;

  // Collect all criterion IDs
  const allIds = new Set();
  for (const [category, criteria] of Object.entries(cc)) {
    if (!Array.isArray(criteria)) continue;
    for (const c of criteria) {
      allIds.add(c.id);
    }
  }

  // Check depends_on references resolve
  for (const [category, criteria] of Object.entries(cc)) {
    if (!Array.isArray(criteria)) continue;
    for (const c of criteria) {
      if (c.depends_on) {
        for (const dep of c.depends_on) {
          if (!allIds.has(dep)) {
            errors.push({
              criterion: "CC-18",
              message: `${c.id} has depends_on reference to ${dep} which does not exist in criteria set`,
            });
          }
        }
      }
      // Also check downstream_dependents on deferred criteria
      if (c.downstream_dependents) {
        for (const dep of c.downstream_dependents) {
          if (!allIds.has(dep)) {
            errors.push({
              criterion: "CC-18",
              message: `${c.id} has downstream_dependent reference to ${dep} which does not exist in criteria set`,
            });
          }
        }
      }
    }
  }

  return errors;
}

// ─── EXPORTS ──────────────────────────────────────────────────────

module.exports = {
  // Enums
  ChangeType,
  IntentType,
  Priority,
  Status,
  Confidence,
  Tier,
  OriginType,

  // Schemas
  SemVer,
  CurrentReality,
  Scope,
  Origin,
  TransitionLogEntry,
  CoreCriterion,
  DeferredCriterion,
  CriteriaCategories,
  IntentSchema,
  AspirationalIntent,

  // Structural validators
  validateTransitionLogIntegrity,
  validateCriterionIdUniqueness,
  validateScopeCoverage,
  validateDeferredCriteria,
  validateSelfConformance,
  validateDependsOnRefs,
};
