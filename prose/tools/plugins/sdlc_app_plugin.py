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
        <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
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

    export function Button({ className, ...props }) {
      return (
        <button
          className={cn(
            "inline-flex items-center justify-center rounded-md text-sm font-medium",
            "h-9 px-4 py-2 bg-black text-white hover:bg-black/85",
            "transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 ring-neutral-400",
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
      setKind(kind) {
        set({ kind });
      },
      async refresh() {
        const kind = get().kind;
        set({ loading: true });
        const records = await listRecords(kind);
        set({ records, loading: false });
      },
      async refreshIntents() {
        set({ intentsLoading: true });
        const [asp, ach] = await Promise.all([
          listRecords("intent_aspirational"),
          listRecords("intent_achieved"),
        ]);
        const merged = [...asp, ...ach].map((r) => ({
          ...r,
          kind: r.kind || (asp.includes(r) ? "intent_aspirational" : "intent_achieved"),
        }));
        set({ intents: merged, intentsLoading: false });
      },
      async saveRecord(payload) {
        const kind = get().kind;
        const saved = await upsertRecord(kind, payload);
        set({ records: [saved, ...get().records.filter(r => r.id !== saved.id)] });
        if (kind === "intent_aspirational" || kind === "intent_achieved") {
          set({ intents: [saved, ...get().intents.filter(r => r.id !== saved.id)] });
        }
      }
    }));
    """)


def _web_app_jsx() -> str:
    return dedent("""\
import React, { useEffect, useState } from "react";
import { useRecords } from "./store";
import { Button } from "./components/ui/button";
import { KINDS, SCHEMAS, normalize, sample } from "./schema";

export default function App() {
  const {
    kind,
    records,
    intents,
    loading,
    intentsLoading,
    setKind,
    refresh,
    refreshIntents,
    saveRecord,
  } = useRecords();
  const [payload, setPayload] = useState(JSON.stringify(sample("intent_aspirational"), null, 2));
  const [error, setError] = useState("");
  const [selected, setSelected] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    refresh();
    refreshIntents();
  }, []);
  useEffect(() => {
    setPayload(JSON.stringify(sample(kind), null, 2));
  }, [kind]);

  const onSubmit = async (e) => {
    e.preventDefault();
    let parsed;
    try {
      parsed = JSON.parse(payload);
    } catch (err) {
      setError("Invalid JSON");
      return;
    }
    const normalized = normalize(kind, parsed);
    const schema = SCHEMAS[kind];
    const result = schema.safeParse(normalized);
    if (!result.success) {
      setError(result.error.issues[0]?.message || "Invalid input");
      return;
    }
    setError("");
    await saveRecord(JSON.stringify(parsed));
  };

  const exportJson = () => {
    const blob = new Blob([payload], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${kind}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  const copyJson = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      const textarea = document.createElement("textarea");
      textarea.value = text;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      textarea.remove();
    }
  };

  const openDetail = (record) => {
    setSelected(record);
    setModalOpen(true);
  };

  const parsePayload = (record) => {
    if (!record || !record.payload) return null;
    try {
      return JSON.parse(record.payload);
    } catch {
      return null;
    }
  };

  const selectedPayload = parsePayload(selected);
  const selectedCore =
    selectedPayload?.intent ||
    selectedPayload?.tension ||
    selectedPayload?.decision ||
    selectedPayload?.plugin ||
    selectedPayload?.manifest ||
    selectedPayload;
  const selectedKind =
    selectedPayload?.intent
      ? "intent"
      : selectedPayload?.tension
      ? "tension"
      : selectedPayload?.decision
      ? "decision"
      : selectedPayload?.plugin
      ? "plugin"
      : selectedPayload?.manifest
      ? "manifest"
      : selected?.kind || "record";

  return (
    <div className="min-h-screen text-neutral-900 p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        <header className="space-y-2">
          <div className="inline-flex items-center gap-2 rounded-full bg-neutral-900 text-white px-3 py-1 text-xs">
            SDLC Console
          </div>
          <h1 className="text-3xl font-semibold tracking-tight">Intent Operations Hub</h1>
          <p className="text-sm text-neutral-600">Operate SDLC artifacts with schema validation and instant inspection.</p>
        </header>

        <section className="rounded-xl border bg-white/90 backdrop-blur p-3 shadow-sm">
          <div className="flex flex-wrap items-center gap-2">
            <Button className="bg-neutral-900" onClick={refreshIntents} disabled={intentsLoading}>
              {intentsLoading ? "Loading intents..." : "Refresh intents"}
            </Button>
            <Button className="bg-neutral-900" onClick={refresh} disabled={loading}>
              {loading ? "Loading records..." : "Refresh records"}
            </Button>
            <Button className="bg-neutral-700" onClick={exportJson}>
              Export editor JSON
            </Button>
            <Button
              className="bg-neutral-700"
              onClick={() => selectedPayload && copyJson(JSON.stringify(selectedPayload, null, 2))}
              disabled={!selectedPayload}
            >
              Copy selected JSON
            </Button>
          </div>
        </section>

        <div className="grid gap-6 lg:grid-cols-[1.2fr_1fr]">
          <section className="rounded-xl border bg-white/90 backdrop-blur p-4 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h2 className="text-sm font-semibold">Create / Update Record</h2>
                <p className="text-xs text-neutral-500">JSON payload validated by schema.</p>
              </div>
              <select
                className="border rounded px-2 py-1 text-sm bg-white"
                value={kind}
                onChange={(e) => setKind(e.target.value)}
              >
                {KINDS.map((k) => (
                  <option key={k} value={k}>{k}</option>
                ))}
              </select>
            </div>
            <form className="grid gap-3" onSubmit={onSubmit}>
              <textarea
                className="border rounded-lg px-3 py-2 text-sm font-mono min-h-[260px] bg-neutral-50/60 focus:outline-none focus:ring-2 focus:ring-neutral-300"
                value={payload}
                onChange={(e) => setPayload(e.target.value)}
              />
              {error ? <div className="text-sm text-red-600">{error}</div> : null}
              <div>
                <Button type="submit">Save</Button>
                <Button type="button" className="ml-2 bg-neutral-700" onClick={() => setPayload(JSON.stringify(sample(kind), null, 2))}>
                  Load Sample
                </Button>
                <Button type="button" className="ml-2 bg-neutral-900" onClick={exportJson}>
                  Export JSON
                </Button>
              </div>
            </form>
          </section>

          <section className="rounded-xl border bg-white/90 backdrop-blur p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-sm font-semibold">Intent Index</h2>
                <p className="text-xs text-neutral-500">All intents across kinds.</p>
              </div>
              <Button className="bg-neutral-900" onClick={refreshIntents} disabled={intentsLoading}>
                {intentsLoading ? "Loading..." : "Refresh"}
              </Button>
            </div>
            <div className="mt-3 space-y-2">
              {intents.length === 0 && (
                <div className="text-sm text-neutral-600">No intents yet.</div>
              )}
              {intents.map((r) => {
                const payload = parsePayload(r);
                const core = payload?.intent || payload;
                return (
                  <button
                    key={`${r.kind}-${r.id}`}
                    className="w-full text-left border rounded-lg px-3 py-2 text-sm hover:bg-neutral-50"
                    onClick={() => openDetail(r)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="font-medium">{core?.id || r.id}</div>
                      <span className="text-xs text-neutral-500">{r.kind}</span>
                    </div>
                    <div className="text-neutral-600 text-xs">{core?.version || "n/a"} · {core?.status || "n/a"}</div>
                  </button>
                );
              })}
            </div>
          </section>
        </div>

        <section className="rounded-xl border bg-white/90 backdrop-blur p-4 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-semibold">Records ({kind})</h2>
              <p className="text-xs text-neutral-500">All records for the selected kind.</p>
            </div>
            <Button className="bg-neutral-900" onClick={refresh} disabled={loading}>
              {loading ? "Loading..." : "Refresh"}
            </Button>
          </div>
          <div className="mt-3 space-y-2">
            {records.length === 0 && (
              <div className="text-sm text-neutral-600">No records yet.</div>
            )}
            {records.map((r) => (
              <button
                key={r.id}
                className="w-full text-left border rounded-lg px-3 py-2 text-sm hover:bg-neutral-50"
                onClick={() => openDetail(r)}
              >
                <div className="font-medium">{r.id}</div>
                <div className="text-neutral-600 text-xs">{r.created_at}</div>
              </button>
            ))}
          </div>
        </section>

        <section className="rounded-xl border bg-white/90 backdrop-blur p-4 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-semibold">Detail</h2>
              <p className="text-xs text-neutral-500">Click a record to open the modal.</p>
            </div>
          </div>
        </section>
      </div>

      {modalOpen && selected && (
        <div
          className="fixed inset-0 z-50 bg-black/40"
          onClick={() => setModalOpen(false)}
        >
          <div
            className="mx-auto mt-10 w-[min(1100px,92vw)] rounded-2xl bg-white shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b px-5 py-4 sticky top-0 bg-white rounded-t-2xl">
              <div>
                <div className="text-base font-semibold tracking-tight">{selectedCore?.id || selected.id}</div>
                <div className="text-xs text-neutral-500">{selected.kind}</div>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  className="bg-neutral-700"
                  onClick={() => selectedPayload && copyJson(JSON.stringify(selectedPayload, null, 2))}
                >
                  Copy JSON
                </Button>
                <Button
                  className="bg-neutral-700"
                  onClick={() => {
                    if (!selectedPayload) return;
                    setKind(selected.kind || kind);
                    setPayload(JSON.stringify(selectedPayload, null, 2));
                    setModalOpen(false);
                  }}
                >
                  Load Into Editor
                </Button>
                <Button className="bg-neutral-900" onClick={() => setModalOpen(false)}>
                  Close
                </Button>
              </div>
            </div>
            <div className="grid gap-4 p-5 lg:grid-cols-[1.2fr_0.8fr] max-h-[72vh] overflow-hidden">
              <div className="space-y-3 overflow-auto pr-1">
                <div className="rounded-lg border bg-neutral-50 p-3 text-sm">
                  <div className="text-xs uppercase tracking-wide text-neutral-500">Summary</div>
                  <div className="mt-2 grid gap-1 text-xs text-neutral-700">
                    <div>ID: {selectedCore?.id || selected.id}</div>
                    <div>Version: {selectedCore?.version || "n/a"}</div>
                    <div>Status: {selectedCore?.status || "n/a"}</div>
                    <div>Owner: {selectedCore?.owner || "n/a"}</div>
                    <div>Priority: {selectedCore?.priority || "n/a"}</div>
                  </div>
                </div>
                {selectedCore?.declares && (
                  <div className="rounded-lg border p-3 text-sm">
                    <div className="text-xs uppercase tracking-wide text-neutral-500">Declares</div>
                    <div className="mt-2 text-sm text-neutral-700">{selectedCore.declares}</div>
                  </div>
                )}
                {selectedCore?.scope && (
                  <div className="rounded-lg border p-3 text-sm">
                    <div className="text-xs uppercase tracking-wide text-neutral-500">Scope</div>
                    <div className="mt-2 text-xs text-neutral-700">
                      Primary: {(selectedCore.scope.primary || []).join(", ") || "n/a"}
                    </div>
                    <div className="mt-1 text-xs text-neutral-700">
                      Implicit: {(selectedCore.scope.implicit || []).join(", ") || "n/a"}
                    </div>
                  </div>
                )}
                {selectedCore?.origin && (
                  <div className="rounded-lg border p-3 text-sm">
                    <div className="text-xs uppercase tracking-wide text-neutral-500">Origin</div>
                    <div className="mt-2 text-xs text-neutral-700">
                      {selectedCore.origin.type} · {selectedCore.origin.relationship}
                    </div>
                    <div className="text-xs text-neutral-700">Ref: {selectedCore.origin.ref}</div>
                  </div>
                )}
                {selectedCore?.current_reality && (
                  <div className="rounded-lg border p-3 text-sm">
                    <div className="text-xs uppercase tracking-wide text-neutral-500">Current Reality</div>
                    <div className="mt-2 text-xs text-neutral-700">{selectedCore.current_reality.state}</div>
                    <div className="mt-1 text-xs text-neutral-700">Status: {selectedCore.current_reality.status}</div>
                    <div className="mt-1 text-xs text-neutral-700">Remaining: {selectedCore.current_reality.remaining_work}</div>
                  </div>
                )}
                {selectedKind === "tension" && selectedCore && (
                  <div className="rounded-lg border p-3 text-sm">
                    <div className="text-xs uppercase tracking-wide text-neutral-500">Tension</div>
                    <div className="mt-2 text-xs text-neutral-700">
                      Between: {(selectedCore.between || [])
                        .map((b) => `${b.intent_id}@${b.version}`)
                        .join(" ↔ ") || "n/a"}
                    </div>
                    <div className="mt-1 text-xs text-neutral-700">Status: {selectedCore.status || "n/a"}</div>
                    <div className="mt-1 text-xs text-neutral-700">Created: {selectedCore.created || "n/a"}</div>
                    {selectedCore.resolution && (
                      <div className="mt-2 text-xs text-neutral-700">
                        Resolution: {selectedCore.resolution.strategy || "n/a"} · {selectedCore.resolution.resolution_owner || "n/a"}
                      </div>
                    )}
                  </div>
                )}
                {selectedKind === "decision" && selectedCore && (
                  <div className="rounded-lg border p-3 text-sm">
                    <div className="text-xs uppercase tracking-wide text-neutral-500">Decision</div>
                    <div className="mt-2 text-xs text-neutral-700">Date: {selectedCore.date || "n/a"}</div>
                    <div className="mt-1 text-xs text-neutral-700">Status: {selectedCore.status || "n/a"}</div>
                    <div className="mt-1 text-xs text-neutral-700">
                      Intents: {(selectedCore.intent_refs || []).join(", ") || "n/a"}
                    </div>
                  </div>
                )}
                {selectedKind === "transition" && selectedCore && (
                  <div className="rounded-lg border p-3 text-sm">
                    <div className="text-xs uppercase tracking-wide text-neutral-500">Transition</div>
                    <div className="mt-2 text-xs text-neutral-700">
                      {selectedCore.from_version} → {selectedCore.to_version}
                    </div>
                    <div className="mt-1 text-xs text-neutral-700">Type: {selectedCore.change_type || "n/a"}</div>
                  </div>
                )}
                {selectedKind === "plugin" && selectedCore && (
                  <div className="rounded-lg border p-3 text-sm">
                    <div className="text-xs uppercase tracking-wide text-neutral-500">Plugin</div>
                    <div className="mt-2 text-xs text-neutral-700">Name: {selectedCore.name || "n/a"}</div>
                    <div className="mt-1 text-xs text-neutral-700">Version: {selectedCore.version || "n/a"}</div>
                  </div>
                )}
                {selectedKind === "manifest" && selectedCore && (
                  <div className="rounded-lg border p-3 text-sm">
                    <div className="text-xs uppercase tracking-wide text-neutral-500">Manifest</div>
                    <div className="mt-2 text-xs text-neutral-700">Repo: {selectedCore.repo || "n/a"}</div>
                    <div className="mt-1 text-xs text-neutral-700">Generated: {selectedCore.generated || "n/a"}</div>
                    <div className="mt-1 text-xs text-neutral-700">Schema: {selectedCore.schema_version || "n/a"}</div>
                  </div>
                )}
              </div>
              <div className="flex flex-col min-h-0">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-xs uppercase tracking-wide text-neutral-500">JSON (secondary)</div>
                </div>
                <pre className="border rounded-lg px-3 py-2 text-xs overflow-auto bg-neutral-50 flex-1 opacity-80">
                  {JSON.stringify(selectedPayload, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        </div>
      )}
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
    }

    body {
      font-family: "Space Grotesk", ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
      background: radial-gradient(1200px 600px at 10% -10%, #f5f5f4 0%, #fafaf9 40%, #ffffff 100%);
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
