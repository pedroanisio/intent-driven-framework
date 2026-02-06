const { createServer } = require("node:http");
const path = require("node:path");
const fs = require("node:fs");
const { createYoga, createSchema } = require("graphql-yoga");
const { z } = require("zod");
const initSqlJs = require("sql.js");

const DB_PATH = process.env.IDF_DB || path.join(__dirname, "..", "..", "data", "idf.db");
fs.mkdirSync(path.dirname(DB_PATH), { recursive: true });

function locateFile(file) {
  return path.join(__dirname, "node_modules", "sql.js", "dist", file);
}

const KINDS = [
  "intent_aspirational",
  "intent_achieved",
  "tension",
  "decision",
  "transition",
  "plugin",
  "manifest"
];

async function initDb() {
  const SQL = await initSqlJs({ locateFile });
  const buf = fs.existsSync(DB_PATH) ? fs.readFileSync(DB_PATH) : null;
  const db = buf ? new SQL.Database(buf) : new SQL.Database();
  for (const k of KINDS) {
    db.exec(`
      CREATE TABLE IF NOT EXISTS ${k} (
        id TEXT PRIMARY KEY,
        payload TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now'))
      )
    `);
  }
  return db;
}

function persist(db) {
  const data = db.export();
  fs.writeFileSync(DB_PATH, Buffer.from(data));
}

const ENUMS = {
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

const SCHEMAS = {
  intent_aspirational: IntentAspirational,
  intent_achieved: IntentAchieved,
  tension: Tension,
  decision: Decision,
  transition: Transition,
  plugin: Plugin,
  manifest: Manifest
};

function normalizePayload(kind, payload) {
  if (kind.startsWith("intent") && payload.intent) return payload.intent;
  if (kind === "tension" && payload.tension) return payload.tension;
  if (kind === "decision" && payload.decision) return payload.decision;
  if (kind === "transition" && payload.transition) return payload.transition;
  if (kind === "plugin" && payload.plugin) return payload.plugin;
  if (kind === "manifest" && payload.manifest) return payload.manifest;
  return payload;
}

function validate(kind, payload) {
  const schema = SCHEMAS[kind];
  if (!schema) throw new Error(`Unknown kind: ${kind}`);
  return schema.parse(payload);
}

async function main() {
  const db = await initDb();

    const DEFAULT_KIND = "intent_aspirational";
    function normalizeKind(kind) {
      const k = (kind || "").trim();
      if (!k) return DEFAULT_KIND;
      if (!KINDS.includes(k)) {
        throw new Error(`Invalid kind: ${k}. Expected one of: ${KINDS.join(", ")}`);
      }
      return k;
    }

    const schema = createSchema({
  typeDefs: /* GraphQL */ `
    type Record {
      id: ID!
      kind: String!
      payload: String!
      created_at: String
    }

    type Query {
      list(kind: String!): [Record!]!
      get(kind: String!, id: ID!): Record
    }

    type Mutation {
      upsert(kind: String!, payload: String!): Record!
    }
  `,
  resolvers: {
    Query: {
          list: (_, { kind }) => {
            const k = normalizeKind(kind);
            const stmt = db.prepare(`SELECT id, payload, created_at FROM ${k} ORDER BY created_at DESC`);
            const rows = [];
            while (stmt.step()) {
              rows.push(stmt.getAsObject());
            }
            stmt.free();
            return rows.map(r => ({ ...r, kind: k }));
          },
          get: (_, { kind, id }) => {
            const k = normalizeKind(kind);
            const stmt = db.prepare(`SELECT id, payload, created_at FROM ${k} WHERE id = ?`);
            stmt.bind([id]);
            const row = stmt.step() ? stmt.getAsObject() : null;
            stmt.free();
            return row ? { ...row, kind: k } : null;
          }
        },
        Mutation: {
          upsert: (_, { kind, payload }) => {
            const k = normalizeKind(kind);
            let parsed;
            try {
              parsed = JSON.parse(payload);
            } catch {
              throw new Error("Payload must be valid JSON");
            }
            const normalized = normalizePayload(k, parsed);
            const data = validate(k, normalized);
            const id = data.id;
            const stmt = db.prepare(
              `INSERT INTO ${k} (id, payload) VALUES (?, ?) ` +
              `ON CONFLICT(id) DO UPDATE SET payload=excluded.payload`
            );
            stmt.run([id, JSON.stringify(data)]);
            stmt.free();
            persist(db);
            const fetch = db.prepare(`SELECT id, payload, created_at FROM ${k} WHERE id = ?`);
            fetch.bind([id]);
            const row = fetch.step() ? fetch.getAsObject() : null;
            fetch.free();
            return row ? { ...row, kind: k } : null;
          }
        }
      }
  });

  const yoga = createYoga({
    schema,
    graphqlEndpoint: "/graphql",
    cors: { origin: "*", methods: ["GET", "POST"] }
  });
  const server = createServer(yoga);
  const port = process.env.PORT || 8081;
  const host = process.env.HOST || "127.0.0.1";
  server.listen(port, host, () => {
    console.log(`GraphQL API running at http://${host}:${port}/graphql`);
  });
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
