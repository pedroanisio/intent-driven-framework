"""
SDLC App Plugin
---------------
Adds a minimal full-stack app (GraphQL API + React web + CLI) to operate
the SDLC intent model/data. Uses SQLite, Yoga (GraphQL), Zod, Zustand,
Tailwind, and a minimal shadcn-style UI component.
"""

from textwrap import dedent
from types import SimpleNamespace


def _api_package_json() -> str:
    return dedent("""\
    {
      "name": "idf-sdlc-api",
      "private": true,
      "type": "commonjs",
      "scripts": {
        "dev": "node server.js",
        "start": "node server.js"
      },
      "dependencies": {
        "graphql": "^16.8.1",
        "graphql-yoga": "^5.7.0",
        "sql.js": "^1.11.0",
        "zod": "^3.23.8"
      }
    }
    """)


def _api_server_js() -> str:
    return dedent("""\
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

    const SEMVER = /^\\d+\\.\\d+\\.\\d+$/;
    const DATE = /^\\d{4}-\\d{2}-\\d{2}$/;

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
    """)


def _api_env_example() -> str:
    return dedent("""\
    # GraphQL API config
    PORT=8081
    IDF_DB=../../data/idf.db
    """)


def _cli_package_json() -> str:
    return dedent("""\
    {
      "name": "idf-sdlc-cli",
      "private": true,
      "type": "commonjs",
      "scripts": {
        "start": "node cli.js"
      },
      "dependencies": {
        "sql.js": "^1.11.0",
        "zod": "^3.23.8"
      }
    }
    """)


def _cli_js() -> str:
    return dedent("""\
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

    const SEMVER = /^\\d+\\.\\d+\\.\\d+$/;
    const DATE = /^\\d{4}-\\d{2}-\\d{2}$/;

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
        process.stdout.write(JSON.stringify({ ok: true, data, meta }, null, 2) + "\\n");
        process.exit(0);
      }
      return data;
    }

    function fail(error, code, details = []) {
      if (!textMode) {
        process.stdout.write(JSON.stringify({ ok: false, error, code, details }, null, 2) + "\\n");
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
        "IDF SDLC CLI \\u2014 Intent-Driven Framework",
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
        "  Success: { \\"ok\\": true,  \\"data\\": ..., \\"meta\\": {...} }",
        "  Failure: { \\"ok\\": false, \\"error\\": \\"...\\", \\"code\\": \\"...\\", \\"details\\": [...] }"
      ].join("\\n"));
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
    """)


def _web_package_json() -> str:
    return dedent("""\
    {
      "name": "idf-sdlc-web",
      "private": true,
      "type": "module",
      "scripts": {
        "dev": "vite",
        "build": "vite build",
        "preview": "vite preview"
      },
      "dependencies": {
        "class-variance-authority": "^0.7.0",
        "clsx": "^2.1.1",
        "graphql-request": "^7.1.0",
        "react": "^18.3.1",
        "react-dom": "^18.3.1",
        "tailwind-merge": "^2.5.2",
        "zustand": "^4.5.5",
        "zod": "^3.23.8"
      },
      "devDependencies": {
        "@vitejs/plugin-react": "^4.3.1",
        "autoprefixer": "^10.4.20",
        "postcss": "^8.4.41",
        "tailwindcss": "^3.4.10",
        "vite": "^5.4.2"
      }
    }
    """)


def _web_vite_config() -> str:
    return dedent("""\
    import { defineConfig } from "vite";
    import react from "@vitejs/plugin-react";

    export default defineConfig({
      plugins: [react()]
    });
    """)


def _web_index_html() -> str:
    return dedent("""\
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
        <title>IDF SDLC Console</title>
      </head>
      <body>
        <div id="root"></div>
        <script type="module" src="/src/main.jsx"></script>
      </body>
    </html>
    """)


def _web_main_jsx() -> str:
    return dedent("""\
    import React from "react";
    import { createRoot } from "react-dom/client";
    import App from "./App.jsx";
    import "./index.css";

    createRoot(document.getElementById("root")).render(<App />);
    """)


def _web_utils_js() -> str:
    return dedent("""\
    import { clsx } from "clsx";
    import { twMerge } from "tailwind-merge";

    export function cn(...inputs) {
      return twMerge(clsx(inputs));
    }
    """)


def _web_button_jsx() -> str:
    return dedent("""\
    import React from "react";
    import { cn } from "../../lib/utils";

    const variants = {
      primary:
        "bg-[hsl(220,90%,56%)] text-white hover:bg-[hsl(220,90%,48%)] shadow-sm shadow-blue-500/20",
      secondary:
        "bg-white text-[hsl(220,14%,20%)] border border-[hsl(220,13%,88%)] hover:bg-[hsl(220,14%,97%)] shadow-sm",
      ghost:
        "text-[hsl(220,8%,46%)] hover:text-[hsl(220,14%,20%)] hover:bg-[hsl(220,14%,95%)]",
      danger:
        "bg-red-50 text-red-600 border border-red-200 hover:bg-red-100",
    };

    const sizes = {
      sm: "h-7 px-2.5 text-xs gap-1",
      md: "h-8 px-3 text-sm gap-1.5",
      lg: "h-9 px-4 text-sm gap-2",
    };

    export function Button({
      className,
      variant = "primary",
      size = "md",
      ...props
    }) {
      return (
        <button
          className={cn(
            "inline-flex items-center justify-center rounded-lg font-medium",
            "transition-all duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-400/40 focus-visible:ring-offset-1",
            "disabled:opacity-40 disabled:pointer-events-none",
            "active:scale-[0.97]",
            variants[variant] || variants.primary,
            sizes[size] || sizes.md,
            className
          )}
          {...props}
        />
      );
    }
    """)


def _web_schema_js() -> str:
    return dedent("""\
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

    const SEMVER = /^\\d+\\.\\d+\\.\\d+$/;
    const DATE = /^\\d{4}-\\d{2}-\\d{2}$/;

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
    """)

def _web_api_js() -> str:
    return dedent("""\
    import { GraphQLClient, gql } from "graphql-request";

    const endpoint = import.meta.env.VITE_API_URL || "http://localhost:8081/graphql";
    const client = new GraphQLClient(endpoint);

    export async function listRecords(kind) {
      const query = gql`
        query($kind: String!) {
          list(kind: $kind) { id kind payload created_at }
        }
      `;
      const data = await client.request(query, { kind });
      return data.list || [];
    }

    export async function upsertRecord(kind, payload) {
      const mutation = gql`
        mutation($kind: String!, $payload: String!) {
          upsert(kind: $kind, payload: $payload) {
            id kind payload created_at
          }
        }
      `;
      const data = await client.request(mutation, { kind, payload });
      return data.upsert;
    }
    """)


def _web_store_js() -> str:
    return dedent("""\
    import { create } from "zustand";
    import { listRecords, upsertRecord } from "./lib/api";

    export const useRecords = create((set, get) => ({
      kind: "intent_aspirational",
      records: [],
      intents: [],
      loading: false,
      intentsLoading: false,
      toast: null,
      setKind(kind) {
        set({ kind });
      },
      showToast(message, type = "success") {
        set({ toast: { message, type, id: Date.now() } });
        setTimeout(() => set({ toast: null }), 3000);
      },
      async refresh() {
        const kind = get().kind;
        set({ loading: true });
        try {
          const records = await listRecords(kind);
          set({ records, loading: false });
        } catch (err) {
          set({ loading: false });
          get().showToast("Failed to load records: " + err.message, "error");
        }
      },
      async refreshIntents() {
        set({ intentsLoading: true });
        try {
          const [asp, ach] = await Promise.all([
            listRecords("intent_aspirational"),
            listRecords("intent_achieved"),
          ]);
          const merged = [...asp, ...ach].map((r) => ({
            ...r,
            kind: r.kind || (asp.includes(r) ? "intent_aspirational" : "intent_achieved"),
          }));
          set({ intents: merged, intentsLoading: false });
        } catch (err) {
          set({ intentsLoading: false });
          get().showToast("Failed to load intents: " + err.message, "error");
        }
      },
      async saveRecord(payload) {
        const kind = get().kind;
        try {
          const saved = await upsertRecord(kind, payload);
          set({ records: [saved, ...get().records.filter(r => r.id !== saved.id)] });
          if (kind === "intent_aspirational" || kind === "intent_achieved") {
            set({ intents: [saved, ...get().intents.filter(r => r.id !== saved.id)] });
          }
          get().showToast("Record saved successfully", "success");
          return saved;
        } catch (err) {
          get().showToast("Save failed: " + err.message, "error");
          throw err;
        }
      }
    }));
    """)


def _web_app_jsx() -> str:
    return dedent("""\
import React, { useEffect, useState, useCallback, useRef } from "react";
import { useRecords } from "./store";
import { Button } from "./components/ui/button";
import { KINDS, SCHEMAS, normalize, sample } from "./schema";

/* ── Helpers ── */
const KIND_LABELS = {
  intent_aspirational: "Aspirational",
  intent_achieved: "Achieved",
  tension: "Tensions",
  decision: "Decisions",
  transition: "Transitions",
  plugin: "Plugins",
  manifest: "Manifests",
};

const KIND_ICONS = {
  intent_aspirational: "\\u2728",
  intent_achieved: "\\u2705",
  tension: "\\u26A1",
  decision: "\\u2696\\uFE0F",
  transition: "\\u27A1\\uFE0F",
  plugin: "\\uD83E\\uDDE9",
  manifest: "\\uD83D\\uDCCB",
};

const STATUS_COLORS = {
  proposed: "bg-amber-50 text-amber-700 border-amber-200",
  active: "bg-emerald-50 text-emerald-700 border-emerald-200",
  evolving: "bg-blue-50 text-blue-700 border-blue-200",
  superseded: "bg-slate-100 text-slate-500 border-slate-200",
  residual: "bg-orange-50 text-orange-600 border-orange-200",
  retracted: "bg-red-50 text-red-600 border-red-200",
  accepted: "bg-emerald-50 text-emerald-700 border-emerald-200",
  deprecated: "bg-slate-100 text-slate-500 border-slate-200",
};

const PRIORITY_COLORS = {
  critical: "bg-red-500",
  high: "bg-orange-400",
  medium: "bg-blue-400",
  low: "bg-slate-300",
};

function Badge({ children, className = "" }) {
  return (
    <span className={"inline-flex items-center rounded-md border px-1.5 py-0.5 text-[10px] font-medium leading-none " + className}>
      {children}
    </span>
  );
}

function StatusBadge({ status }) {
  if (!status) return null;
  return <Badge className={STATUS_COLORS[status] || "bg-gray-50 text-gray-600 border-gray-200"}>{status}</Badge>;
}

function PriorityDot({ priority }) {
  if (!priority) return null;
  return (
    <span className="flex items-center gap-1 text-[10px] text-[hsl(220,8%,46%)]">
      <span className={"w-1.5 h-1.5 rounded-full " + (PRIORITY_COLORS[priority] || "bg-slate-300")} />
      {priority}
    </span>
  );
}

function EmptyState({ icon, title, subtitle }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center animate-fade-in">
      <div className="text-3xl mb-3 opacity-40">{icon}</div>
      <div className="text-sm font-medium text-[hsl(220,8%,46%)]">{title}</div>
      {subtitle && <div className="text-xs text-[hsl(220,8%,60%)] mt-1">{subtitle}</div>}
    </div>
  );
}

function Toast({ toast }) {
  if (!toast) return null;
  const bg = toast.type === "error" ? "bg-red-600" : "bg-emerald-600";
  return (
    <div className="fixed bottom-5 right-5 z-[100] animate-slide-up">
      <div className={bg + " text-white px-4 py-2.5 rounded-lg shadow-lg text-sm font-medium flex items-center gap-2"}>
        <span>{toast.type === "error" ? "\\u2716" : "\\u2714"}</span>
        {toast.message}
      </div>
    </div>
  );
}

/* ── Main App ── */
export default function App() {
  const {
    kind, records, intents, loading, intentsLoading, toast,
    setKind, refresh, refreshIntents, saveRecord, showToast,
  } = useRecords();

  const [payload, setPayload] = useState(JSON.stringify(sample("intent_aspirational"), null, 2));
  const [error, setError] = useState("");
  const [selected, setSelected] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [saving, setSaving] = useState(false);
  const [editorCollapsed, setEditorCollapsed] = useState(false);
  const textareaRef = useRef(null);

  useEffect(() => {
    refresh();
    refreshIntents();
  }, []);

  useEffect(() => {
    refresh();
  }, [kind]);

  useEffect(() => {
    setPayload(JSON.stringify(sample(kind), null, 2));
    setError("");
  }, [kind]);

  /* Keyboard */
  useEffect(() => {
    const handler = (e) => {
      if (e.key === "Escape" && modalOpen) setModalOpen(false);
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [modalOpen]);

  const onSubmit = async (e) => {
    e.preventDefault();
    let parsed;
    try { parsed = JSON.parse(payload); } catch {
      setError("Invalid JSON \\u2014 check syntax");
      return;
    }
    const normalized = normalize(kind, parsed);
    const schema = SCHEMAS[kind];
    const result = schema.safeParse(normalized);
    if (!result.success) {
      setError(result.error.issues.map(i => (i.path.length ? i.path.join(".") + ": " : "") + i.message).join("\\n"));
      return;
    }
    setError("");
    setSaving(true);
    try {
      await saveRecord(JSON.stringify(parsed));
    } catch {}
    setSaving(false);
  };

  const exportJson = () => {
    const blob = new Blob([payload], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = kind + ".json";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    showToast("JSON exported");
  };

  const copyJson = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      showToast("Copied to clipboard");
    } catch {
      const ta = document.createElement("textarea");
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      ta.remove();
      showToast("Copied to clipboard");
    }
  };

  const openDetail = (record) => {
    setSelected(record);
    setModalOpen(true);
  };

  const parsePayload = (record) => {
    if (!record?.payload) return null;
    try { return JSON.parse(record.payload); } catch { return null; }
  };

  /* Filters */
  const filteredRecords = records.filter((r) => {
    if (!search.trim()) return true;
    const s = search.toLowerCase();
    const p = parsePayload(r);
    const core = p?.intent || p?.tension || p?.decision || p?.plugin || p?.manifest || p;
    return (
      r.id?.toLowerCase().includes(s) ||
      core?.declares?.toLowerCase().includes(s) ||
      core?.description?.toLowerCase().includes(s) ||
      core?.name?.toLowerCase().includes(s) ||
      core?.status?.toLowerCase().includes(s)
    );
  });

  const filteredIntents = intents.filter((r) => {
    if (!search.trim()) return true;
    const s = search.toLowerCase();
    const p = parsePayload(r);
    const core = p?.intent || p;
    return (
      r.id?.toLowerCase().includes(s) ||
      core?.declares?.toLowerCase().includes(s) ||
      core?.status?.toLowerCase().includes(s) ||
      core?.owner?.toLowerCase().includes(s)
    );
  });

  /* Selected item */
  const selectedPayload = parsePayload(selected);
  const selectedCore = selectedPayload?.intent || selectedPayload?.tension ||
    selectedPayload?.decision || selectedPayload?.plugin ||
    selectedPayload?.manifest || selectedPayload;
  const selectedKind = selectedPayload?.intent ? "intent"
    : selectedPayload?.tension ? "tension"
    : selectedPayload?.decision ? "decision"
    : selectedPayload?.plugin ? "plugin"
    : selectedPayload?.manifest ? "manifest"
    : selected?.kind || "record";

  return (
    <div className="min-h-screen">
      {/* ── Top Bar ── */}
      <header className="sticky top-0 z-30 bg-white/80 backdrop-blur-lg border-b border-[hsl(220,13%,91%)]">
        <div className="max-w-[1400px] mx-auto px-5 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-7 h-7 rounded-lg bg-[hsl(220,90%,56%)] flex items-center justify-center text-white text-xs font-bold shadow-sm shadow-blue-500/25">I</div>
            <div>
              <div className="text-sm font-semibold leading-none">IDF Console</div>
              <div className="text-[10px] text-[hsl(220,8%,56%)] mt-0.5">Intent-Driven Framework</div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="relative">
              <input
                type="text"
                placeholder="Search records..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="h-8 w-52 rounded-lg border border-[hsl(220,13%,88%)] bg-white pl-8 pr-3 text-xs placeholder:text-[hsl(220,8%,64%)]"
              />
              <svg className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[hsl(220,8%,56%)]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
              </svg>
            </div>
            <Button variant="secondary" size="sm" onClick={() => { refresh(); refreshIntents(); }} disabled={loading || intentsLoading}>
              {loading || intentsLoading ? "\\u21BB" : "\\u21BB"} Sync
            </Button>
          </div>
        </div>
      </header>

      <div className="max-w-[1400px] mx-auto px-5 py-5">
        {/* ── Kind Tabs ── */}
        <nav className="flex items-center gap-1 mb-5 overflow-x-auto pb-1">
          {KINDS.map((k) => (
            <button
              key={k}
              data-active={kind === k}
              onClick={() => setKind(k)}
              className="kind-tab flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap"
            >
              <span>{KIND_ICONS[k]}</span>
              {KIND_LABELS[k] || k}
              {kind === k && records.length > 0 && (
                <span className="ml-0.5 bg-white/30 rounded px-1 text-[10px]">{records.length}</span>
              )}
            </button>
          ))}
        </nav>

        <div className="grid gap-5 lg:grid-cols-[1fr_380px]">
          {/* ── Left Column: Editor + Records ── */}
          <div className="space-y-5">
            {/* Editor Card */}
            <section className="rounded-xl bg-white border border-[hsl(220,13%,91%)] shadow-sm overflow-hidden animate-fade-in">
              <button
                className="w-full flex items-center justify-between px-4 py-3 hover:bg-[hsl(220,14%,98%)] transition-colors"
                onClick={() => setEditorCollapsed(!editorCollapsed)}
              >
                <div className="flex items-center gap-2">
                  <span className="text-xs">{editorCollapsed ? "\\u25B6" : "\\u25BC"}</span>
                  <span className="text-sm font-semibold">Create / Update</span>
                  <Badge className="bg-[hsl(220,80%,96%)] text-[hsl(220,90%,46%)] border-[hsl(220,80%,88%)]">
                    {KIND_LABELS[kind] || kind}
                  </Badge>
                </div>
                <div className="flex items-center gap-1.5">
                  <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); setPayload(JSON.stringify(sample(kind), null, 2)); }}>
                    Sample
                  </Button>
                  <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); exportJson(); }}>
                    Export
                  </Button>
                </div>
              </button>
              {!editorCollapsed && (
                <form className="px-4 pb-4 space-y-3 animate-fade-in" onSubmit={onSubmit}>
                  <textarea
                    ref={textareaRef}
                    className="w-full border border-[hsl(220,13%,88%)] rounded-lg px-3 py-2.5 text-xs font-mono min-h-[220px] bg-[hsl(220,14%,98%)] resize-y leading-relaxed"
                    value={payload}
                    onChange={(e) => setPayload(e.target.value)}
                    spellCheck="false"
                  />
                  {error && (
                    <div className="rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-xs text-red-700 whitespace-pre-wrap font-mono">
                      {error}
                    </div>
                  )}
                  <div className="flex items-center gap-2">
                    <Button type="submit" disabled={saving}>
                      {saving ? "Saving..." : "Save Record"}
                    </Button>
                  </div>
                </form>
              )}
            </section>

            {/* Records List */}
            <section className="rounded-xl bg-white border border-[hsl(220,13%,91%)] shadow-sm overflow-hidden">
              <div className="px-4 py-3 border-b border-[hsl(220,13%,93%)] flex items-center justify-between">
                <div>
                  <h2 className="text-sm font-semibold">{KIND_LABELS[kind] || kind} Records</h2>
                  <p className="text-[11px] text-[hsl(220,8%,56%)] mt-0.5">
                    {filteredRecords.length} record{filteredRecords.length !== 1 ? "s" : ""}
                    {search && " matching \\u201C" + search + "\\u201D"}
                  </p>
                </div>
              </div>
              <div className="divide-y divide-[hsl(220,13%,95%)] max-h-[420px] overflow-auto">
                {loading ? (
                  <div className="p-4 space-y-3">
                    {[1,2,3].map(i => <div key={i} className="skeleton h-14 w-full" />)}
                  </div>
                ) : filteredRecords.length === 0 ? (
                  <EmptyState
                    icon={KIND_ICONS[kind] || "\\uD83D\\uDCC4"}
                    title={search ? "No matching records" : "No records yet"}
                    subtitle={search ? "Try a different search term" : "Create one using the editor above"}
                  />
                ) : (
                  filteredRecords.map((r, i) => {
                    const p = parsePayload(r);
                    const core = p?.intent || p?.tension || p?.decision || p?.plugin || p?.manifest || p;
                    return (
                      <button
                        key={r.id + "-" + i}
                        className="w-full text-left px-4 py-3 hover:bg-[hsl(220,14%,98%)] transition-colors group"
                        onClick={() => openDetail(r)}
                        style={{ animationDelay: i * 30 + "ms" }}
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div className="min-w-0 flex-1">
                            <div className="text-sm font-medium truncate group-hover:text-[hsl(220,90%,46%)] transition-colors">
                              {core?.id || r.id}
                            </div>
                            {core?.declares && (
                              <div className="text-xs text-[hsl(220,8%,52%)] truncate mt-0.5">{core.declares}</div>
                            )}
                          </div>
                          <div className="flex items-center gap-2 flex-shrink-0">
                            <PriorityDot priority={core?.priority} />
                            <StatusBadge status={core?.status} />
                          </div>
                        </div>
                        <div className="flex items-center gap-3 mt-1.5">
                          {core?.version && <span className="text-[10px] font-mono text-[hsl(220,8%,56%)]">v{core.version}</span>}
                          {core?.owner && <span className="text-[10px] text-[hsl(220,8%,56%)]">{core.owner}</span>}
                          <span className="text-[10px] text-[hsl(220,8%,64%)]">{r.created_at}</span>
                        </div>
                      </button>
                    );
                  })
                )}
              </div>
            </section>
          </div>

          {/* ── Right Column: Intent Index ── */}
          <div className="space-y-5">
            <section className="rounded-xl bg-white border border-[hsl(220,13%,91%)] shadow-sm overflow-hidden lg:sticky lg:top-[76px]">
              <div className="px-4 py-3 border-b border-[hsl(220,13%,93%)] flex items-center justify-between">
                <div>
                  <h2 className="text-sm font-semibold">Intent Index</h2>
                  <p className="text-[11px] text-[hsl(220,8%,56%)] mt-0.5">
                    {filteredIntents.length} intent{filteredIntents.length !== 1 ? "s" : ""} across all kinds
                  </p>
                </div>
              </div>
              <div className="divide-y divide-[hsl(220,13%,95%)] max-h-[600px] overflow-auto">
                {intentsLoading ? (
                  <div className="p-4 space-y-3">
                    {[1,2,3].map(i => <div key={i} className="skeleton h-12 w-full" />)}
                  </div>
                ) : filteredIntents.length === 0 ? (
                  <EmptyState
                    icon="\\u2728"
                    title="No intents yet"
                    subtitle="Create aspirational or achieved intents to see them here"
                  />
                ) : (
                  filteredIntents.map((r, i) => {
                    const p = parsePayload(r);
                    const core = p?.intent || p;
                    const isAspirational = r.kind === "intent_aspirational";
                    return (
                      <button
                        key={r.kind + "-" + r.id + "-" + i}
                        className="w-full text-left px-4 py-2.5 hover:bg-[hsl(220,14%,98%)] transition-colors group"
                        onClick={() => openDetail(r)}
                      >
                        <div className="flex items-center justify-between gap-2">
                          <div className="min-w-0 flex-1">
                            <div className="text-xs font-medium truncate group-hover:text-[hsl(220,90%,46%)] transition-colors">
                              {core?.id || r.id}
                            </div>
                          </div>
                          <Badge className={isAspirational ? "bg-violet-50 text-violet-600 border-violet-200" : "bg-emerald-50 text-emerald-600 border-emerald-200"}>
                            {isAspirational ? "aspirational" : "achieved"}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-2 mt-1">
                          <StatusBadge status={core?.status} />
                          <PriorityDot priority={core?.priority} />
                          {core?.version && <span className="text-[10px] font-mono text-[hsl(220,8%,60%)]">v{core.version}</span>}
                        </div>
                      </button>
                    );
                  })
                )}
              </div>
            </section>
          </div>
        </div>
      </div>

      {/* ── Modal ── */}
      {modalOpen && selected && (
        <div
          className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm animate-fade-in flex items-start justify-center pt-[5vh] pb-8 overflow-auto"
          onClick={() => setModalOpen(false)}
        >
          <div
            className="w-[min(1100px,94vw)] rounded-2xl bg-white shadow-2xl animate-scale-in"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-[hsl(220,13%,93%)] px-6 py-4">
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-lg font-semibold tracking-tight truncate">{selectedCore?.id || selected.id}</span>
                  <StatusBadge status={selectedCore?.status} />
                </div>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-xs text-[hsl(220,8%,56%)]">{selected.kind}</span>
                  {selectedCore?.version && <span className="text-xs font-mono text-[hsl(220,8%,56%)]">v{selectedCore.version}</span>}
                  <PriorityDot priority={selectedCore?.priority} />
                </div>
              </div>
              <div className="flex items-center gap-2 flex-shrink-0">
                <Button variant="secondary" size="sm" onClick={() => selectedPayload && copyJson(JSON.stringify(selectedPayload, null, 2))}>
                  Copy JSON
                </Button>
                <Button variant="secondary" size="sm" onClick={() => {
                  if (!selectedPayload) return;
                  setKind(selected.kind || kind);
                  setPayload(JSON.stringify(selectedPayload, null, 2));
                  setModalOpen(false);
                  setEditorCollapsed(false);
                }}>
                  Edit
                </Button>
                <Button variant="ghost" size="sm" onClick={() => setModalOpen(false)}>
                  \\u2715
                </Button>
              </div>
            </div>

            {/* Modal Body */}
            <div className="grid gap-5 p-6 lg:grid-cols-[1.2fr_0.8fr] max-h-[74vh] overflow-hidden">
              <div className="space-y-3 overflow-auto pr-2">
                {/* Summary Card */}
                <div className="rounded-xl bg-[hsl(220,14%,98%)] border border-[hsl(220,13%,93%)] p-4">
                  <div className="text-[10px] uppercase tracking-widest text-[hsl(220,8%,52%)] font-medium mb-3">Summary</div>
                  <div className="grid grid-cols-2 gap-x-6 gap-y-2 text-xs">
                    <div><span className="text-[hsl(220,8%,52%)]">ID</span><div className="font-medium font-mono mt-0.5">{selectedCore?.id || selected.id}</div></div>
                    <div><span className="text-[hsl(220,8%,52%)]">Version</span><div className="font-medium font-mono mt-0.5">{selectedCore?.version || "\\u2014"}</div></div>
                    <div><span className="text-[hsl(220,8%,52%)]">Owner</span><div className="font-medium mt-0.5">{selectedCore?.owner || "\\u2014"}</div></div>
                    <div><span className="text-[hsl(220,8%,52%)]">Confidence</span><div className="font-medium mt-0.5">{selectedCore?.confidence || "\\u2014"}</div></div>
                  </div>
                </div>

                {selectedCore?.declares && (
                  <div className="rounded-xl border border-[hsl(220,13%,93%)] p-4">
                    <div className="text-[10px] uppercase tracking-widest text-[hsl(220,8%,52%)] font-medium mb-2">Declares</div>
                    <div className="text-sm text-[hsl(220,14%,20%)] leading-relaxed">{selectedCore.declares}</div>
                  </div>
                )}

                {selectedCore?.scope && (
                  <div className="rounded-xl border border-[hsl(220,13%,93%)] p-4">
                    <div className="text-[10px] uppercase tracking-widest text-[hsl(220,8%,52%)] font-medium mb-2">Scope</div>
                    <div className="flex flex-wrap gap-1.5 mt-1">
                      {(selectedCore.scope.primary || []).map((s, i) => (
                        <Badge key={i} className="bg-[hsl(220,80%,96%)] text-[hsl(220,90%,42%)] border-[hsl(220,80%,88%)]">{s}</Badge>
                      ))}
                      {(selectedCore.scope.implicit || []).map((s, i) => (
                        <Badge key={"i-"+i} className="bg-slate-50 text-slate-500 border-slate-200">{s}</Badge>
                      ))}
                    </div>
                  </div>
                )}

                {selectedCore?.origin && (
                  <div className="rounded-xl border border-[hsl(220,13%,93%)] p-4">
                    <div className="text-[10px] uppercase tracking-widest text-[hsl(220,8%,52%)] font-medium mb-2">Origin</div>
                    <div className="flex items-center gap-2 text-xs">
                      <Badge className="bg-indigo-50 text-indigo-600 border-indigo-200">{selectedCore.origin.type}</Badge>
                      <span className="text-[hsl(220,8%,52%)]">\\u2192</span>
                      <Badge className="bg-slate-50 text-slate-600 border-slate-200">{selectedCore.origin.relationship}</Badge>
                    </div>
                    <div className="text-xs font-mono text-[hsl(220,8%,52%)] mt-2">ref: {selectedCore.origin.ref}</div>
                  </div>
                )}

                {selectedCore?.current_reality && (
                  <div className="rounded-xl border border-[hsl(220,13%,93%)] p-4">
                    <div className="text-[10px] uppercase tracking-widest text-[hsl(220,8%,52%)] font-medium mb-2">Current Reality</div>
                    <div className="space-y-1.5 text-xs">
                      <div><span className="text-[hsl(220,8%,52%)]">State:</span> <span className="font-medium">{selectedCore.current_reality.state}</span></div>
                      <div><span className="text-[hsl(220,8%,52%)]">Status:</span> <span className="font-medium">{selectedCore.current_reality.status}</span></div>
                      <div><span className="text-[hsl(220,8%,52%)]">Remaining:</span> <span className="font-medium">{selectedCore.current_reality.remaining_work}</span></div>
                      <div><span className="text-[hsl(220,8%,52%)]">Assessed:</span> <span className="font-mono">{selectedCore.current_reality.last_assessed}</span></div>
                    </div>
                  </div>
                )}

                {selectedKind === "tension" && selectedCore && (
                  <div className="rounded-xl border border-[hsl(220,13%,93%)] p-4">
                    <div className="text-[10px] uppercase tracking-widest text-[hsl(220,8%,52%)] font-medium mb-2">Tension</div>
                    <div className="text-xs space-y-1.5">
                      <div className="flex items-center gap-2 font-mono">
                        {(selectedCore.between || []).map((b, i) => (
                          <React.Fragment key={i}>
                            {i > 0 && <span className="text-amber-500 font-bold">\\u26A1</span>}
                            <Badge className="bg-amber-50 text-amber-700 border-amber-200">{b.intent_id}@{b.version}</Badge>
                          </React.Fragment>
                        ))}
                      </div>
                      <div><span className="text-[hsl(220,8%,52%)]">Created:</span> <span className="font-mono">{selectedCore.created}</span></div>
                      {selectedCore.resolution && (
                        <div className="mt-2 rounded-lg bg-[hsl(220,14%,98%)] p-2.5">
                          <div className="text-[10px] font-medium text-[hsl(220,8%,52%)] mb-1">Resolution</div>
                          <div>{selectedCore.resolution.strategy} \\u00B7 {selectedCore.resolution.resolution_owner}</div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {selectedKind === "decision" && selectedCore && (
                  <div className="rounded-xl border border-[hsl(220,13%,93%)] p-4">
                    <div className="text-[10px] uppercase tracking-widest text-[hsl(220,8%,52%)] font-medium mb-2">Decision</div>
                    <div className="text-xs space-y-1.5">
                      <div><span className="text-[hsl(220,8%,52%)]">Date:</span> <span className="font-mono">{selectedCore.date}</span></div>
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <span className="text-[hsl(220,8%,52%)]">Refs:</span>
                        {(selectedCore.intent_refs || []).map((ref, i) => (
                          <Badge key={i} className="bg-blue-50 text-blue-600 border-blue-200">{ref}</Badge>
                        ))}
                      </div>
                      {selectedCore.context && <div className="mt-2 text-[hsl(220,14%,20%)]"><span className="text-[hsl(220,8%,52%)]">Context:</span> {selectedCore.context}</div>}
                      {selectedCore.consequences && <div className="text-[hsl(220,14%,20%)]"><span className="text-[hsl(220,8%,52%)]">Consequences:</span> {selectedCore.consequences}</div>}
                    </div>
                  </div>
                )}

                {selectedKind === "transition" && selectedCore && (
                  <div className="rounded-xl border border-[hsl(220,13%,93%)] p-4">
                    <div className="text-[10px] uppercase tracking-widest text-[hsl(220,8%,52%)] font-medium mb-2">Transition</div>
                    <div className="flex items-center gap-2 text-xs font-mono">
                      <Badge className="bg-slate-100 text-slate-600 border-slate-200">{selectedCore.from_version}</Badge>
                      <span className="text-[hsl(220,90%,56%)] font-bold">\\u2192</span>
                      <Badge className="bg-emerald-50 text-emerald-600 border-emerald-200">{selectedCore.to_version}</Badge>
                    </div>
                    <div className="text-xs mt-2"><span className="text-[hsl(220,8%,52%)]">Type:</span> <Badge className="bg-blue-50 text-blue-600 border-blue-200">{selectedCore.change_type}</Badge></div>
                  </div>
                )}

                {selectedKind === "plugin" && selectedCore && (
                  <div className="rounded-xl border border-[hsl(220,13%,93%)] p-4">
                    <div className="text-[10px] uppercase tracking-widest text-[hsl(220,8%,52%)] font-medium mb-2">Plugin</div>
                    <div className="text-xs space-y-1.5">
                      <div className="font-medium text-sm">{selectedCore.name}</div>
                      <div className="font-mono text-[hsl(220,8%,52%)]">v{selectedCore.version}</div>
                      {selectedCore.description && <div className="text-[hsl(220,14%,20%)]">{selectedCore.description}</div>}
                    </div>
                  </div>
                )}

                {selectedKind === "manifest" && selectedCore && (
                  <div className="rounded-xl border border-[hsl(220,13%,93%)] p-4">
                    <div className="text-[10px] uppercase tracking-widest text-[hsl(220,8%,52%)] font-medium mb-2">Manifest</div>
                    <div className="text-xs space-y-1.5">
                      <div><span className="text-[hsl(220,8%,52%)]">Repo:</span> <span className="font-mono font-medium">{selectedCore.repo}</span></div>
                      <div><span className="text-[hsl(220,8%,52%)]">Generated:</span> <span className="font-mono">{selectedCore.generated}</span></div>
                      <div><span className="text-[hsl(220,8%,52%)]">Schema:</span> <span className="font-mono">{selectedCore.schema_version}</span></div>
                    </div>
                  </div>
                )}
              </div>

              {/* JSON Pane */}
              <div className="flex flex-col min-h-0">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-[10px] uppercase tracking-widest text-[hsl(220,8%,52%)] font-medium">Raw JSON</div>
                  <Button variant="ghost" size="sm" onClick={() => selectedPayload && copyJson(JSON.stringify(selectedPayload, null, 2))}>
                    Copy
                  </Button>
                </div>
                <pre className="border border-[hsl(220,13%,91%)] rounded-xl px-4 py-3 text-[11px] font-mono overflow-auto bg-[hsl(220,14%,98%)] flex-1 leading-relaxed text-[hsl(220,14%,30%)]">
                  {JSON.stringify(selectedPayload, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Toast */}
      <Toast toast={toast} />
    </div>
  );
}
    """)


def _web_index_css() -> str:
    return dedent("""\
    @tailwind base;
    @tailwind components;
    @tailwind utilities;

    :root {
      color-scheme: light;
      --accent: 220 90% 56%;
      --accent-soft: 220 80% 96%;
      --success: 152 60% 42%;
      --warning: 38 92% 50%;
      --danger: 0 72% 51%;
      --surface: 0 0% 100%;
      --surface-raised: 220 14% 98%;
      --border: 220 13% 91%;
      --text: 220 14% 10%;
      --text-muted: 220 8% 46%;
      --radius: 10px;
    }

    body {
      font-family: "DM Sans", ui-sans-serif, system-ui, -apple-system, sans-serif;
      background: hsl(220 14% 96%);
      color: hsl(var(--text));
      -webkit-font-smoothing: antialiased;
    }

    .font-mono {
      font-family: "JetBrains Mono", ui-monospace, monospace;
    }

    * { scrollbar-width: thin; scrollbar-color: hsl(220 10% 80%) transparent; }
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: hsl(220 10% 80%); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: hsl(220 10% 68%); }

    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    @keyframes slideUp { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes scaleIn { from { opacity: 0; transform: scale(0.97); } to { opacity: 1; transform: scale(1); } }
    @keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }

    .animate-fade-in { animation: fadeIn 0.2s ease-out; }
    .animate-slide-up { animation: slideUp 0.25s ease-out; }
    .animate-scale-in { animation: scaleIn 0.2s ease-out; }
    .skeleton {
      background: linear-gradient(90deg, hsl(220 14% 93%) 25%, hsl(220 14% 97%) 50%, hsl(220 14% 93%) 75%);
      background-size: 200% 100%;
      animation: shimmer 1.5s infinite;
      border-radius: 6px;
    }

    .kind-tab {
      transition: all 0.15s ease;
    }
    .kind-tab:hover {
      background: hsl(220 14% 95%);
    }
    .kind-tab[data-active="true"] {
      background: hsl(var(--accent));
      color: white;
      font-weight: 500;
    }

    textarea:focus, select:focus, input:focus {
      outline: none;
      box-shadow: 0 0 0 2px hsl(var(--accent) / 0.25);
      border-color: hsl(var(--accent));
    }
    """)



def _web_tailwind_config() -> str:
    return dedent("""\
    /** @type {import('tailwindcss').Config} */
    export default {
      content: ["./index.html", "./src/**/*.{js,jsx}"],
      theme: {
        extend: {}
      },
      plugins: []
    };
    """)


def _web_postcss_config() -> str:
    return dedent("""\
    export default {
      plugins: {
        tailwindcss: {},
        autoprefixer: {}
      }
    };
    """)


def _docs_sdlc_app() -> str:
    return dedent("""\
    # SDLC App (Web + API + CLI)

    This plugin scaffolds a minimal operational console for SDLC data:
    intents, tensions, decisions, transitions, plugins, and manifest.

    ## Start API
    ```
    cd apps/api
    npm install
    npm run dev
    ```

    ## Start Web
    ```
    cd apps/web
    npm install
    npm run dev
    ```

    ## Use CLI
    ```
    cd apps/cli
    npm install
    node cli.js help
    ```

    ### CLI Commands
    | Command | Purpose |
    |---------|---------|
    | `kinds` | List all entity kinds |
    | `list --kind KIND [--full]` | List records (add `--full` for payloads) |
    | `get --kind KIND --id ID` | Get a single record |
    | `add --kind KIND (--file\\|--json\\|--stdin)` | Add or update a record |
    | `validate --kind KIND (--file\\|--json\\|--stdin)` | Validate without saving |
    | `schema --kind KIND` | Introspect Zod schema for a kind |
    | `delete --kind KIND --id ID` | Delete a record |
    | `search --kind KIND --field F --value V` | Search records by field value |

    ### Output Format
    By default all commands return JSON envelopes on stdout:
    ```json
    { "ok": true,  "data": ..., "meta": { "kind": "...", "count": 3 } }
    { "ok": false, "error": "...", "code": "NOT_FOUND", "details": [] }
    ```
    Add `--text` for human-readable output.

    ### Agent Usage Examples
    ```bash
    # Discover available entity kinds
    node cli.js kinds

    # Introspect schema to know required fields
    node cli.js schema --kind intent_aspirational

    # Validate a payload before writing (dry-run)
    node cli.js validate --kind intent_aspirational --json '{"intent":{...}}'

    # Add a record (from stdin for piping)
    cat payload.json | node cli.js add --kind intent_aspirational --stdin

    # List all records with full payloads
    node cli.js list --kind intent_aspirational --full

    # Search by field value
    node cli.js search --kind intent_aspirational --field status --value proposed

    # Delete a record
    node cli.js delete --kind intent_aspirational --id my-intent-id
    ```

    ## Payloads
    The API/UI/CLI accept JSON payloads. You can use the Web UI "Load Sample"
    button to generate a valid payload for each kind.
    """)


def register():
    plugin = SimpleNamespace(
        id="sdlc-app",
        name="SDLC Console (Web + API + CLI)",
        version="0.1.0",
        description="Scaffold a minimal operational console for SDLC intent data.",
        hooks={},
        extra_directories=[
            "apps",
            "apps/api",
            "apps/web",
            "apps/cli",
            "apps/web/src",
            "apps/web/src/lib",
            "apps/web/src/components",
            "apps/web/src/components/ui",
            "data"
        ],
        extra_files={
            "apps/api/package.json": _api_package_json,
            "apps/api/server.js": _api_server_js,
            "apps/api/.env.example": _api_env_example,
            "apps/cli/package.json": _cli_package_json,
            "apps/cli/cli.js": _cli_js,
            "apps/web/package.json": _web_package_json,
            "apps/web/vite.config.js": _web_vite_config,
            "apps/web/index.html": _web_index_html,
            "apps/web/src/main.jsx": _web_main_jsx,
            "apps/web/src/App.jsx": _web_app_jsx,
            "apps/web/src/index.css": _web_index_css,
            "apps/web/src/lib/api.js": _web_api_js,
            "apps/web/src/lib/utils.js": _web_utils_js,
            "apps/web/src/store.js": _web_store_js,
            "apps/web/src/schema.js": _web_schema_js,
            "apps/web/src/components/ui/button.jsx": _web_button_jsx,
            "apps/web/tailwind.config.js": _web_tailwind_config,
            "apps/web/postcss.config.js": _web_postcss_config,
            "docs/sdlc-app.md": _docs_sdlc_app
        }
    )
    PLUGIN_REGISTRY.register(plugin)


register()