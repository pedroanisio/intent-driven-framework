const path = require("node:path");
const fs = require("node:fs");
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

function normalize(kind, payload) {
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

// ─── Arg helpers ───
function getFlag(a, name) {
  const idx = a.indexOf("--" + name);
  return idx !== -1 && idx + 1 < a.length ? a[idx + 1] : null;
}
function hasFlag(a, name) { return a.includes("--" + name); }

// ─── Output envelopes ───
const textMode = process.argv.includes("--text");

function succeed(data, meta = {}) {
  if (!textMode) {
    process.stdout.write(JSON.stringify({ ok: true, data, meta }, null, 2) + "\n");
    process.exit(0);
  }
  return data;
}

function fail(error, code, details = []) {
  if (!textMode) {
    process.stdout.write(JSON.stringify({ ok: false, error, code, details }, null, 2) + "\n");
  } else {
    console.error("Error: " + error);
    for (const d of details) console.error("  " + (d.path ? d.path + ": " : "") + d.message);
  }
  process.exit(code === "INTERNAL_ERROR" ? 2 : 1);
}

// ─── Payload reader (--file, --json, --stdin) ───
function readPayload(a) {
  const fp = getFlag(a, "file");
  if (fp) return fs.readFileSync(fp, "utf-8");
  const js = getFlag(a, "json");
  if (js) return js;
  if (hasFlag(a, "stdin")) return fs.readFileSync(0, "utf-8");
  return null;
}

// ─── Zod error formatter ───
function formatZodError(ze) {
  return ze.issues.map(i => ({ path: i.path.join("."), message: i.message, code: i.code }));
}

// ─── Schema introspection ───
function describeZodType(schema, depth) {
  if ((depth || 0) > 6) return { type: "unknown" };
  const d = (depth || 0) + 1;
  const def = schema._def;
  if (!def) return { type: "unknown" };
  if (def.typeName === "ZodObject") {
    const fields = {};
    for (const [k, v] of Object.entries(schema.shape)) fields[k] = describeZodType(v, d);
    return { type: "object", fields };
  }
  if (def.typeName === "ZodArray") return { type: "array", items: describeZodType(def.type, d) };
  if (def.typeName === "ZodEnum") return { type: "enum", values: def.values };
  if (def.typeName === "ZodLiteral") return { type: "literal", value: def.value };
  if (def.typeName === "ZodString") {
    const checks = (def.checks || []).map(c => c.kind === "regex" ? { pattern: String(c.regex) } : { kind: c.kind, value: c.value });
    return { type: "string", constraints: checks.length ? checks : undefined };
  }
  if (def.typeName === "ZodOptional") return { ...describeZodType(def.innerType, d), optional: true };
  if (def.typeName === "ZodDefault") return { ...describeZodType(def.innerType, d), hasDefault: true };
  if (def.typeName === "ZodRecord") return { type: "record" };
  if (def.typeName === "ZodAny") return { type: "any" };
  return { type: def.typeName || "unknown" };
}

// ─── Kind descriptions ───
const KIND_DESC = {
  intent_aspirational: "Goals and desired states (aspirational mode)",
  intent_achieved: "Verified accomplished intents (achieved mode)",
  tension: "Conflicts between two intents",
  decision: "Architectural or design decisions",
  transition: "Version transitions with change type",
  plugin: "Registered IDF plugins",
  manifest: "Repository manifest summaries"
};

// ─── Commands ───
async function cmdKinds() {
  const data = KINDS.map(k => ({ kind: k, description: KIND_DESC[k] || "" }));
  const r = succeed(data, { count: data.length });
  if (r) for (const item of r) console.log(item.kind.padEnd(22) + " " + item.description);
}

async function cmdList(a) {
  const kind = getFlag(a, "kind");
  if (!kind || !KINDS.includes(kind)) fail("Missing or invalid --kind", "MISSING_ARGUMENT");
  const db = await initDb();
  const stmt = db.prepare("SELECT id, payload, created_at FROM " + kind + " ORDER BY created_at DESC");
  const rows = [];
  while (stmt.step()) rows.push(stmt.getAsObject());
  stmt.free();
  const full = hasFlag(a, "full");
  const data = rows.map(row => full
    ? { id: row.id, created_at: row.created_at, payload: JSON.parse(row.payload) }
    : { id: row.id, created_at: row.created_at }
  );
  const r = succeed(data, { kind, count: data.length });
  if (r) {
    if (!r.length) { console.log("No records found."); return; }
    for (const row of r) console.log(row.id + "  " + row.created_at);
  }
}

async function cmdGet(a) {
  const kind = getFlag(a, "kind");
  if (!kind || !KINDS.includes(kind)) fail("Missing or invalid --kind", "MISSING_ARGUMENT");
  const id = getFlag(a, "id");
  if (!id) fail("Missing --id", "MISSING_ARGUMENT");
  const db = await initDb();
  const stmt = db.prepare("SELECT id, payload, created_at FROM " + kind + " WHERE id = ?");
  stmt.bind([id]);
  const row = stmt.step() ? stmt.getAsObject() : null;
  stmt.free();
  if (!row) fail("Not found: " + kind + " " + id, "NOT_FOUND");
  const data = { id: row.id, created_at: row.created_at, payload: JSON.parse(row.payload) };
  const r = succeed(data, { kind });
  if (r) console.log(JSON.stringify(r.payload, null, 2));
}

async function cmdAdd(a) {
  const kind = getFlag(a, "kind");
  if (!kind || !KINDS.includes(kind)) fail("Missing or invalid --kind", "MISSING_ARGUMENT");
  const payloadText = readPayload(a);
  if (!payloadText) fail("Provide payload via --file, --json, or --stdin", "MISSING_ARGUMENT");
  let parsed;
  try { parsed = JSON.parse(payloadText); }
  catch (e) { fail("Invalid JSON: " + e.message, "INVALID_JSON"); }
  let data;
  try { data = validate(kind, normalize(kind, parsed)); }
  catch (e) {
    if (e instanceof z.ZodError) fail("Validation failed", "VALIDATION_ERROR", formatZodError(e));
    throw e;
  }
  const db = await initDb();
  const chk = db.prepare("SELECT id FROM " + kind + " WHERE id = ?");
  chk.bind([data.id]);
  const existed = chk.step();
  chk.free();
  const stmt = db.prepare(
    "INSERT INTO " + kind + " (id, payload) VALUES (?, ?) " +
    "ON CONFLICT(id) DO UPDATE SET payload=excluded.payload"
  );
  stmt.run([data.id, JSON.stringify(data)]);
  stmt.free();
  persist(db);
  const r = succeed({ id: data.id, payload: data }, { kind, action: existed ? "updated" : "created" });
  if (r) console.log((existed ? "Updated" : "Created") + " " + kind + " " + data.id);
}

async function cmdValidate(a) {
  const kind = getFlag(a, "kind");
  if (!kind || !KINDS.includes(kind)) fail("Missing or invalid --kind", "MISSING_ARGUMENT");
  const payloadText = readPayload(a);
  if (!payloadText) fail("Provide payload via --file, --json, or --stdin", "MISSING_ARGUMENT");
  let parsed;
  try { parsed = JSON.parse(payloadText); }
  catch (e) { fail("Invalid JSON: " + e.message, "INVALID_JSON"); }
  const result = SCHEMAS[kind].safeParse(normalize(kind, parsed));
  if (result.success) {
    succeed({ valid: true }, { kind });
  } else {
    fail("Validation failed", "VALIDATION_ERROR", formatZodError(result.error));
  }
}

async function cmdSchema(a) {
  const kind = getFlag(a, "kind");
  if (!kind || !KINDS.includes(kind)) fail("Missing or invalid --kind", "MISSING_ARGUMENT");
  succeed({ kind, schema: describeZodType(SCHEMAS[kind]) }, { kind });
}

async function cmdDelete(a) {
  const kind = getFlag(a, "kind");
  if (!kind || !KINDS.includes(kind)) fail("Missing or invalid --kind", "MISSING_ARGUMENT");
  const id = getFlag(a, "id");
  if (!id) fail("Missing --id", "MISSING_ARGUMENT");
  const db = await initDb();
  const chk = db.prepare("SELECT id FROM " + kind + " WHERE id = ?");
  chk.bind([id]);
  const exists = chk.step();
  chk.free();
  if (!exists) fail("Not found: " + kind + " " + id, "NOT_FOUND");
  db.run("DELETE FROM " + kind + " WHERE id = ?", [id]);
  persist(db);
  const r = succeed({ id, deleted: true }, { kind });
  if (r) console.log("Deleted " + kind + " " + id);
}

async function cmdSearch(a) {
  const kind = getFlag(a, "kind");
  if (!kind || !KINDS.includes(kind)) fail("Missing or invalid --kind", "MISSING_ARGUMENT");
  const field = getFlag(a, "field");
  if (!field) fail("Missing --field", "MISSING_ARGUMENT");
  if (!/^[a-zA-Z_][a-zA-Z0-9_.]*$/.test(field)) fail("Invalid field name", "INVALID_FIELD");
  const value = getFlag(a, "value");
  if (value === null || value === undefined) fail("Missing --value", "MISSING_ARGUMENT");
  const db = await initDb();
  const stmt = db.prepare(
    "SELECT id, payload, created_at FROM " + kind +
    " WHERE json_extract(payload, ?) = ? ORDER BY created_at DESC"
  );
  stmt.bind(["$." + field, value]);
  const rows = [];
  while (stmt.step()) rows.push(stmt.getAsObject());
  stmt.free();
  const data = rows.map(row => ({ id: row.id, created_at: row.created_at, payload: JSON.parse(row.payload) }));
  const r = succeed(data, { kind, field, value, count: data.length });
  if (r) {
    if (!r.length) { console.log("No matches."); return; }
    for (const row of r) console.log(row.id + "  " + row.created_at);
  }
}

// ─── Dispatch ───
const COMMANDS = {
  kinds: cmdKinds, list: cmdList, get: cmdGet, add: cmdAdd,
  validate: cmdValidate, schema: cmdSchema, delete: cmdDelete, search: cmdSearch
};

const cliArgs = process.argv.slice(2);
const command = cliArgs[0];

function usage() {
  console.log([
    "IDF SDLC CLI \u2014 Intent-Driven Framework",
    "",
    "Usage: node cli.js <command> [options]",
    "",
    "Commands:",
    "  kinds                                       List all entity kinds",
    "  list   --kind KIND [--full]                  List records",
    "  get    --kind KIND --id ID                   Get a single record",
    "  add    --kind KIND (--file|--json|--stdin)    Add or update a record",
    "  validate --kind KIND (--file|--json|--stdin)  Validate without saving",
    "  schema --kind KIND                           Introspect Zod schema",
    "  delete --kind KIND --id ID                   Delete a record",
    "  search --kind KIND --field F --value V       Search by field value",
    "  help                                         Show this help",
    "",
    "Global flags:",
    "  --text    Human-readable output (default: JSON envelope)",
    "",
    "Kinds: " + KINDS.join(", "),
    "",
    "JSON envelope:",
    "  Success: { \"ok\": true,  \"data\": ..., \"meta\": {...} }",
    "  Failure: { \"ok\": false, \"error\": \"...\", \"code\": \"...\", \"details\": [...] }"
  ].join("\n"));
}

if (!command || command === "help") {
  usage();
  process.exit(command ? 0 : 1);
}

async function main() {
  const handler = COMMANDS[command];
  if (!handler) fail("Unknown command: " + command, "UNKNOWN_COMMAND");
  await handler(cliArgs.slice(1));
}

main().catch(function(err) {
  try { fail("Internal error: " + err.message, "INTERNAL_ERROR"); }
  catch (_) { process.exit(2); }
});
