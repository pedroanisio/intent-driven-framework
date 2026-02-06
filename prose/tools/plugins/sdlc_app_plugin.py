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
        "better-sqlite3": "^9.4.3",
        "graphql": "^16.8.1",
        "graphql-yoga": "^5.7.0",
        "zod": "^3.23.8"
      }
    }
    """)


def _api_server_js() -> str:
    return dedent("""\
    const { createServer } = require("node:http");
    const path = require("node:path");
    const fs = require("node:fs");
    const Database = require("better-sqlite3");
    const { createYoga, createSchema } = require("graphql-yoga");
    const { z } = require("zod");

    const DB_PATH = process.env.IDF_DB || path.join(__dirname, "..", "..", "data", "idf.db");
    fs.mkdirSync(path.dirname(DB_PATH), { recursive: true });
    const db = new Database(DB_PATH);

    const KINDS = [
      "intent_aspirational",
      "intent_achieved",
      "tension",
      "decision",
      "transition",
      "plugin",
      "manifest"
    ];

    for (const k of KINDS) {
      db.exec(`
        CREATE TABLE IF NOT EXISTS ${k} (
          id TEXT PRIMARY KEY,
          payload TEXT NOT NULL,
          created_at TEXT DEFAULT (datetime('now'))
        )
      `);
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
      if (kind === "plugin" && payload.plugin) return payload.plugin;
      if (kind === "manifest" && payload.manifest) return payload.manifest;
      return payload;
    }

    function validate(kind, payload) {
      const schema = SCHEMAS[kind];
      if (!schema) throw new Error(`Unknown kind: ${kind}`);
      return schema.parse(payload);
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
            if (!KINDS.includes(kind)) throw new Error("Invalid kind");
            return db.prepare(`SELECT id, payload, created_at FROM ${kind} ORDER BY created_at DESC`).all()
              .map(r => ({ ...r, kind }));
          },
          get: (_, { kind, id }) => {
            if (!KINDS.includes(kind)) throw new Error("Invalid kind");
            const row = db.prepare(`SELECT id, payload, created_at FROM ${kind} WHERE id = ?`).get(id);
            return row ? { ...row, kind } : null;
          }
        },
        Mutation: {
          upsert: (_, { kind, payload }) => {
            if (!KINDS.includes(kind)) throw new Error("Invalid kind");
            let parsed;
            try {
              parsed = JSON.parse(payload);
            } catch {
              throw new Error("Payload must be valid JSON");
            }
            const normalized = normalizePayload(kind, parsed);
            const data = validate(kind, normalized);
            const id = data.id;
            db.prepare(
              `INSERT INTO ${kind} (id, payload) VALUES (?, ?) ` +
              `ON CONFLICT(id) DO UPDATE SET payload=excluded.payload`
            ).run(id, JSON.stringify(data));
            const row = db.prepare(`SELECT id, payload, created_at FROM ${kind} WHERE id = ?`).get(id);
            return { ...row, kind };
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
    const port = process.env.PORT || 4000;
    server.listen(port, () => {
      console.log(`GraphQL API running at http://localhost:${port}/graphql`);
    });
    """)


def _api_env_example() -> str:
    return dedent("""\
    # GraphQL API config
    PORT=4000
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
        "better-sqlite3": "^9.4.3",
        "zod": "^3.23.8"
      }
    }
    """)


def _cli_js() -> str:
    return dedent("""\
    const path = require("node:path");
    const fs = require("node:fs");
    const Database = require("better-sqlite3");
    const { z } = require("zod");

    const DB_PATH = process.env.IDF_DB || path.join(__dirname, "..", "..", "data", "idf.db");
    fs.mkdirSync(path.dirname(DB_PATH), { recursive: true });
    const db = new Database(DB_PATH);

    const KINDS = [
      "intent_aspirational",
      "intent_achieved",
      "tension",
      "decision",
      "transition",
      "plugin",
      "manifest"
    ];

    for (const k of KINDS) {
      db.exec(`
        CREATE TABLE IF NOT EXISTS ${k} (
          id TEXT PRIMARY KEY,
          payload TEXT NOT NULL,
          created_at TEXT DEFAULT (datetime('now'))
        )
      `);
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
      if (kind === "plugin" && payload.plugin) return payload.plugin;
      if (kind === "manifest" && payload.manifest) return payload.manifest;
      return payload;
    }

    function validate(kind, payload) {
      const schema = SCHEMAS[kind];
      if (!schema) throw new Error(`Unknown kind: ${kind}`);
      return schema.parse(payload);
    }

    const args = process.argv.slice(2);
    const cmd = args[0];

    function usage() {
      console.log("Usage:");
      console.log("  node cli.js list --kind KIND");
      console.log("  node cli.js get --kind KIND --id ID");
      console.log("  node cli.js add --kind KIND --file PATH");
      console.log("  node cli.js add --kind KIND --json '{...}'");
      console.log("Kinds:", KINDS.join(", "));
    }

    if (!cmd) {
      usage();
      process.exit(1);
    }

    if (cmd === "list") {
      const kind = args.includes("--kind") ? args[args.indexOf("--kind") + 1] : null;
      if (!kind || !KINDS.includes(kind)) {
        console.log("Missing or invalid --kind");
        usage();
        process.exit(1);
      }
      const rows = db.prepare(`SELECT * FROM ${kind} ORDER BY created_at DESC`).all();
      if (!rows.length) {
        console.log("No intents found.");
        process.exit(0);
      }
      for (const r of rows) {
        console.log(`${r.id}  ${r.created_at}`);
      }
      process.exit(0);
    }

    if (cmd === "add") {
      const kind = args.includes("--kind") ? args[args.indexOf("--kind") + 1] : null;
      if (!kind || !KINDS.includes(kind)) {
        console.log("Missing or invalid --kind");
        usage();
        process.exit(1);
      }
      const fileIdx = args.indexOf("--file");
      const jsonIdx = args.indexOf("--json");
      let payloadText = null;
      if (fileIdx !== -1) {
        payloadText = fs.readFileSync(args[fileIdx + 1], "utf-8");
      } else if (jsonIdx !== -1) {
        payloadText = args[jsonIdx + 1];
      }
      if (!payloadText) {
        console.log("Missing --file or --json payload");
        usage();
        process.exit(1);
      }
      let parsed;
      try {
        parsed = JSON.parse(payloadText);
      } catch (e) {
        console.log("Invalid JSON payload:", e.message);
        process.exit(1);
      }
      const data = validate(kind, normalize(kind, parsed));
      db.prepare(
        `INSERT INTO ${kind} (id, payload) VALUES (?, ?) ` +
        `ON CONFLICT(id) DO UPDATE SET payload=excluded.payload`
      ).run(data.id, JSON.stringify(data));
      console.log(`Saved ${kind} ${data.id}`);
      process.exit(0);
    }

    usage();
    process.exit(1);
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
            "h-9 px-4 py-2 bg-black text-white hover:bg-black/80",
            "transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2",
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
            id: "transition-001",
            from_version: "1.0.0",
            to_version: "1.1.0",
            change_type: "MINOR",
            summary: "Added field"
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

    const endpoint = import.meta.env.VITE_API_URL || "http://localhost:4000/graphql";
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
      loading: false,
      setKind(kind) {
        set({ kind });
      },
      async refresh() {
        const kind = get().kind;
        set({ loading: true });
        const records = await listRecords(kind);
        set({ records, loading: false });
      },
      async saveRecord(payload) {
        const kind = get().kind;
        const saved = await upsertRecord(kind, payload);
        set({ records: [saved, ...get().records.filter(r => r.id !== saved.id)] });
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
      const { kind, records, loading, setKind, refresh, saveRecord } = useRecords();
      const [payload, setPayload] = useState(JSON.stringify(sample("intent_aspirational"), null, 2));
      const [error, setError] = useState("");

      useEffect(() => { refresh(); }, []);
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

      return (
        <div className="min-h-screen bg-neutral-50 text-neutral-900 p-8">
          <div className="max-w-3xl mx-auto space-y-8">
            <header className="space-y-2">
              <h1 className="text-2xl font-semibold">IDF SDLC Console</h1>
              <p className="text-sm text-neutral-600">Operate SDLC artifacts with schema validation.</p>
            </header>

            <section className="rounded-lg border bg-white p-4">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-sm font-semibold">Create / Update Record</h2>
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
                  className="border rounded px-3 py-2 text-sm font-mono min-h-[220px]"
                  value={payload}
                  onChange={(e) => setPayload(e.target.value)}
                />
                {error ? <div className="text-sm text-red-600">{error}</div> : null}
                <div>
                  <Button type="submit">Save</Button>
                  <Button type="button" className="ml-2 bg-neutral-700" onClick={() => setPayload(JSON.stringify(sample(kind), null, 2))}>
                    Load Sample
                  </Button>
                </div>
              </form>
            </section>

            <section className="rounded-lg border bg-white p-4">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-semibold">Records</h2>
                <Button className="bg-neutral-900" onClick={refresh} disabled={loading}>
                  {loading ? "Loading..." : "Refresh"}
                </Button>
              </div>
              <div className="mt-3 space-y-2">
                {records.length === 0 && (
                  <div className="text-sm text-neutral-600">No intents yet.</div>
                )}
                {records.map((r) => (
                  <div key={r.id} className="border rounded px-3 py-2 text-sm">
                    <div className="font-medium">{r.id}</div>
                    <div className="text-neutral-600">{r.created_at}</div>
                  </div>
                ))}
              </div>
            </section>
          </div>
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
      font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
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
    node cli.js list --kind intent_aspirational
    node cli.js add --kind intent_aspirational --json '{ "intent": { ... } }'
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
