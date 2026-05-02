import { z } from "zod";

export const KINDS = [
  "intent_aspirational",
  "intent_achieved",
  "tension",
  "decision",
  "transition",
  "plugin",
  "manifest"
];

export const ENUMS = {
  change_type: [
    "clarification", "correction", "extension",
    "reclassification", "breaking", "deprecation",
    "MAJOR", "MINOR", "PATCH"
  ],
  origin_type: [
    "engineering", "product", "incident", "discovery",
    "regulatory", "organizational", "devops", "ux",
    "data", "sre", "security"
  ],
  origin_relationship: [
    "derived_from", "motivated_by", "constrained_by",
    "triggered_by", "discovered_in"
  ],
  priority: ["critical", "high", "medium", "low"],
  confidence: ["high", "medium", "low"],
  status: [
    "proposed", "active", "evolving", "superseded", "residual", "retracted",
    "accepted", "deprecated"
  ],
  tier: ["core", "deferred"],
  achieved_coverage: ["none", "minimal", "partial", "substantial", "full"],
  intent_type: ["aspirational", "achieved"]
};

const SEMVER = /^\d+\.\d+\.\d+$/;
const DATE = /^\d{4}-\d{2}-\d{2}$/;

const Scope = z.object({
  primary: z.array(z.string().min(1)).min(1),
  implicit: z.array(z.string().min(1)).optional()
});

const Origin = z.object({
  type: z.enum(ENUMS.origin_type),
  ref: z.string().min(1),
  relationship: z.enum(ENUMS.origin_relationship),
  accessibility: z.string().optional(),
  note: z.string().optional()
});

const CurrentReality = z.object({
  state: z.string().min(1),
  status: z.string().min(1),
  remaining_work: z.string().min(1),
  last_assessed: z.string().regex(DATE, "date must be YYYY-MM-DD")
});

const TransitionLog = z.object({
  from_version: z.string().regex(SEMVER).optional(),
  to_version: z.string().regex(SEMVER).optional(),
  change_type: z.enum(ENUMS.change_type).optional(),
  summary: z.string().optional(),
  reason: z.string().optional(),
  date: z.string().optional()
}).passthrough();

const IntentBase = z.object({
  id: z.string().min(1),
  version: z.string().regex(SEMVER),
  schema_version: z.string().regex(SEMVER),
  intent_type: z.enum(ENUMS.intent_type),
  declares: z.string().min(1),
  scope: Scope,
  priority: z.enum(ENUMS.priority),
  status: z.enum(ENUMS.status),
  confidence: z.enum(ENUMS.confidence),
  owner: z.string().min(1),
  origin: Origin,
  transition_log: z.array(TransitionLog).default([]),
  serves: z.array(z.string()).optional(),
  dependencies: z.array(z.string()).optional(),
  achieved_coverage: z.enum(ENUMS.achieved_coverage).optional(),
  ext: z.record(z.any()).optional(),
  current_reality: CurrentReality.optional()
}).passthrough();

const IntentAspirational = IntentBase.extend({
  intent_type: z.literal("aspirational"),
  current_reality: CurrentReality
});

const IntentAchieved = IntentBase.extend({
  intent_type: z.literal("achieved")
});

const Tension = z.object({
  id: z.string().min(1),
  between: z.array(z.object({ intent_id: z.string().min(1), version: z.string().regex(SEMVER) })).length(2),
  description: z.string().min(1),
  resolution: z.object({
    strategy: z.string().min(1),
    resolution_owner: z.string().min(1),
    applies_to: z.array(z.string().regex(SEMVER)).min(2)
  }),
  status: z.enum(["proposed", "active", "superseded", "residual"]),
  created: z.string().regex(DATE, "date must be YYYY-MM-DD")
}).passthrough();

const Decision = z.object({
  id: z.string().min(1),
  date: z.string().regex(DATE, "date must be YYYY-MM-DD"),
  intent_refs: z.array(z.string()),
  context: z.string().min(1),
  decision: z.string().min(1),
  consequences: z.string().min(1),
  status: z.enum(["proposed", "accepted", "superseded", "deprecated"])
}).passthrough();

const Transition = z.object({
  id: z.string().min(1),
  from_version: z.string().regex(SEMVER),
  to_version: z.string().regex(SEMVER),
  change_type: z.enum(ENUMS.change_type),
  summary: z.string().min(1)
}).passthrough();

const Plugin = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
  version: z.string().regex(SEMVER),
  description: z.string().min(1),
  extends: z.record(z.any()).optional(),
  registry_entry: z.object({
    id: z.string().min(1),
    version: z.string().regex(SEMVER),
    compatible_schema_versions: z.array(z.string().regex(SEMVER)).min(1)
  }).optional()
}).passthrough();

const Manifest = z.object({
  repo: z.string().min(1),
  generated: z.string().regex(DATE, "date must be YYYY-MM-DD"),
  schema_version: z.string().regex(SEMVER),
  intents: z.array(z.any()).default([]),
  tensions: z.array(z.any()).default([]),
  decisions: z.array(z.any()).default([])
}).passthrough();

export const SCHEMAS = {
  intent_aspirational: IntentAspirational,
  intent_achieved: IntentAchieved,
  tension: Tension,
  decision: Decision,
  transition: Transition,
  plugin: Plugin,
  manifest: Manifest
};

export function normalize(kind, payload) {
  if (kind.startsWith("intent") && payload.intent) return payload.intent;
  if (kind === "tension" && payload.tension) return payload.tension;
  if (kind === "decision" && payload.decision) return payload.decision;
  if (kind === "transition" && payload.transition) return payload.transition;
  if (kind === "plugin" && payload.plugin) return payload.plugin;
  if (kind === "manifest" && payload.manifest) return payload.manifest;
  return payload;
}

export function sample(kind) {
  const today = new Date().toISOString().slice(0, 10);
  switch (kind) {
    case "intent_aspirational":
      return {
        intent: {
          id: "intent-example",
          version: "1.0.0",
          schema_version: "0.1.0",
          intent_type: "aspirational",
          declares: "Example intent",
          current_reality: {
            state: "Unknown",
            status: "Unassessed",
            remaining_work: "TBD",
            last_assessed: today
          },
          scope: { primary: ["README.md"], implicit: [] },
          priority: "medium",
          status: "proposed",
          confidence: "medium",
          owner: "team",
          origin: { type: "engineering", ref: "seed", relationship: "derived_from" },
          transition_log: []
        }
      };
    case "intent_achieved":
      return {
        intent: {
          id: "intent-achieved",
          version: "1.0.0",
          schema_version: "0.1.0",
          intent_type: "achieved",
          declares: "Achieved intent",
          scope: { primary: ["README.md"], implicit: [] },
          priority: "medium",
          status: "active",
          confidence: "high",
          owner: "team",
          origin: { type: "engineering", ref: "seed", relationship: "derived_from" },
          transition_log: []
        }
      };
    case "tension":
      return {
        tension: {
          id: "tension-001",
          between: [
            { intent_id: "intent-a", version: "1.0.0" },
            { intent_id: "intent-b", version: "1.0.0" }
          ],
          description: "A vs B",
          resolution: {
            strategy: "priority",
            resolution_owner: "owner",
            applies_to: ["1.0.0", "1.0.0"]
          },
          status: "proposed",
          created: today
        }
      };
    case "decision":
      return {
        decision: {
          id: "decision-001",
          date: today,
          intent_refs: ["intent-a"],
          context: "Context",
          decision: "Decision",
          consequences: "Consequences",
          status: "proposed"
        }
      };
    case "transition":
      return {
        transition: {
          id: "transition-001",
          from_version: "1.0.0",
          to_version: "1.1.0",
          change_type: "MINOR",
          summary: "Added field"
        }
      };
    case "plugin":
      return {
        plugin: {
          id: "plugin-example",
          name: "Example Plugin",
          version: "1.0.0",
          description: "Extends intent",
          registry_entry: {
            id: "plugin-example",
            version: "1.0.0",
            compatible_schema_versions: ["0.1.0"]
          }
        }
      };
    case "manifest":
      return {
        manifest: {
          repo: "repo-name",
          generated: today,
          schema_version: "0.1.0",
          intents: [],
          tensions: [],
          decisions: []
        }
      };
    default:
      return {};
  }
}
