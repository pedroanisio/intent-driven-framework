const fs = require("fs");
const YAML = require("yaml");
const {
  IntentSchema,
  AspirationalIntent,
  validateTransitionLogIntegrity,
  validateCriterionIdUniqueness,
  validateScopeCoverage,
  validateDeferredCriteria,
  validateSelfConformance,
  validateDependsOnRefs,
  validateTensionIntegrity,
  validateFalsifiableClaimsIntegrity,
  validateFailureModeIntegrity,
  validateRetirementConditions,
  validateCoOriginConsistency,
  validateDeclaresQuality,
  validateAffirmationStaleness,
  validateOperationalCycleIntegrity,
  validateCycleConstraintCoverage,
  validateProvidesFcRefs,
  validateProvidesCompleteness,
} = require("./schema");
const { createFlawStore, Severity, FlawStatus } = require("./store");

// ─── STATE PERSISTENCE ────────────────────────────────────────────

const STATE_FILE = process.env.FLAW_STATE || ".flaw-state.json";

function loadStore() {
  const store = createFlawStore();
  if (fs.existsSync(STATE_FILE)) {
    try {
      const saved = JSON.parse(fs.readFileSync(STATE_FILE, "utf8"));
      store.setState(saved);
    } catch {
      // corrupt state file — start fresh
    }
  }
  return store;
}

function saveStore(store) {
  const state = store.getState();
  const serializable = {
    flaws: state.flaws,
    runs: state.runs,
    patterns: state.patterns,
  };
  fs.writeFileSync(STATE_FILE, JSON.stringify(serializable, null, 2));
}

// ─── COLLECT FLAWS ────────────────────────────────────────────────

function collectFlaws(intent) {
  const flaws = [];

  // Phase 1: Schema validation
  const baseResult = IntentSchema.safeParse(intent);
  if (!baseResult.success) {
    for (const issue of baseResult.error.issues) {
      const path = issue.path.length > 0 ? issue.path.join(".") : "(root)";
      flaws.push({
        criterion: "SCHEMA",
        message: `${path}: ${issue.message}`,
        severity: Severity.CRITICAL,
        phase: "schema",
      });
    }
  }

  // Aspirational refinement
  if (intent.intent_type === "aspirational") {
    const aspResult = AspirationalIntent.safeParse(intent);
    if (!aspResult.success) {
      for (const issue of aspResult.error.issues) {
        if (!flaws.some((f) => f.message.includes(issue.message))) {
          const path = issue.path.length > 0 ? issue.path.join(".") : "(root)";
          flaws.push({
            criterion: "CC-08",
            message: `${path}: ${issue.message}`,
            severity: Severity.CRITICAL,
            phase: "schema",
          });
        }
      }
    }
  }

  // Phase 2: Structural validators
  const structuralChecks = [
    // v0.1.0 validators
    { fn: validateTransitionLogIntegrity, severity: Severity.ERROR },
    { fn: validateCriterionIdUniqueness, severity: Severity.ERROR },
    { fn: validateScopeCoverage, severity: Severity.WARNING },
    { fn: validateDeferredCriteria, severity: Severity.ERROR },
    { fn: validateSelfConformance, severity: Severity.CRITICAL },
    { fn: validateDependsOnRefs, severity: Severity.ERROR },
    // v0.2.0 validators
    { fn: validateTensionIntegrity, severity: Severity.ERROR },
    { fn: validateFalsifiableClaimsIntegrity, severity: Severity.ERROR },
    { fn: validateFailureModeIntegrity, severity: Severity.WARNING },
    { fn: validateRetirementConditions, severity: Severity.WARNING },
    { fn: validateCoOriginConsistency, severity: Severity.WARNING },
    { fn: validateDeclaresQuality, severity: Severity.ERROR },
    { fn: validateAffirmationStaleness, severity: Severity.WARNING },
    // v0.3.0 validators
    { fn: validateOperationalCycleIntegrity, severity: Severity.ERROR },
    { fn: validateCycleConstraintCoverage, severity: Severity.ERROR },
    // v0.4.0 validators
    { fn: validateProvidesFcRefs, severity: Severity.ERROR },
    { fn: validateProvidesCompleteness, severity: Severity.WARNING },
  ];

  for (const check of structuralChecks) {
    const errors = check.fn(intent);
    for (const err of errors) {
      flaws.push({
        criterion: err.criterion,
        message: err.message,
        severity: check.severity,
        phase: "structural",
      });
    }
  }

  // CC-27(b) advisory: not automatable in single-file mode
  // This is a validator limitation note, not a flaw — tracked separately
  const advisories = [
    {
      criterion: "CC-27(b)",
      message: "Transition summary completeness requires cross-version diff — not automatable in single-file validation",
    },
  ];

  return { flaws, advisories };
}

// ─── DISPLAY ──────────────────────────────────────────────────────

const SEVERITY_ICON = {
  [Severity.CRITICAL]: "🔴",
  [Severity.ERROR]: "🟠",
  [Severity.WARNING]: "🟡",
  [Severity.INFO]: "🔵",
};

const STATUS_ICON = {
  [FlawStatus.DETECTED]: "⬜",
  [FlawStatus.ACKNOWLEDGED]: "🔲",
  [FlawStatus.RESOLVED]: "✅",
  [FlawStatus.WONT_FIX]: "⏭️ ",
  [FlawStatus.REGRESSED]: "🔁",
};

function renderReport(store, intent, runId, advisories) {
  const state = store.getState();
  const run = state.runs.find((r) => r.id === runId);
  const openFlaws = store.getState().getOpenFlaws();

  console.log();
  console.log("╔══════════════════════════════════════════════════════════╗");
  console.log("║  Intent Framework Validator                              ║");
  console.log(`║  Schema: 0.4.0 │ State: Zustand │ Target: ${(intent.version || "?").padEnd(9)}║`);
  console.log("╚══════════════════════════════════════════════════════════╝");

  console.log();
  console.log(`── Run: ${runId} ─────────────────────────────────`);
  console.log(`   Version:  ${intent.version}`);
  console.log(`   Time:     ${run.timestamp}`);
  console.log(`   Flaws:    ${run.flaw_count} total │ ${run.new_flaws.length} new │ ${run.resolved.length} resolved`);

  if (openFlaws.length > 0) {
    console.log();
    console.log("── Open Flaws ─────────────────────────────────────────────");
    console.log();

    for (const severity of [Severity.CRITICAL, Severity.ERROR, Severity.WARNING, Severity.INFO]) {
      const group = openFlaws.filter((f) => f.severity === severity);
      if (group.length === 0) continue;

      for (const flaw of group) {
        const icon = SEVERITY_ICON[severity];
        const statusIcon = STATUS_ICON[flaw.status];
        const regression = flaw.status === FlawStatus.REGRESSED ? " [REGRESSION]" : "";
        console.log(
          `  ${icon} ${statusIcon} [${flaw.criterion}] ${flaw.message}${regression}`
        );
        console.log(
          `        first: ${flaw.first_seen_version} │ last: ${flaw.last_seen_version} │ seen: ${flaw.occurrences}x`
        );
      }
    }
  } else {
    console.log();
    console.log("── No Open Flaws ──────────────────────────────────────────");
  }

  if (state.patterns.length > 0) {
    console.log();
    console.log("── Detected Patterns ──────────────────────────────────────");
    console.log();
    for (const p of state.patterns) {
      const icon = p.type === "regression" ? "🔁" : p.type === "chronic" ? "♻️ " : "💥";
      console.log(`  ${icon} [${p.type}] ${p.message}`);
    }
  }

  if (state.runs.length > 1) {
    console.log();
    console.log("── Run History ────────────────────────────────────────────");
    console.log();
    console.log("  Version    Flaws  New  Resolved  Time");
    console.log("  ─────────  ─────  ───  ────────  ────────────────────");
    const summaries = store.getState().getRunSummary();
    for (const s of summaries.slice(-10)) {
      const marker = s.id === runId ? " ◀" : "";
      console.log(
        `  ${s.version.padEnd(9)}  ${String(s.total_flaws).padStart(5)}  ${String(s.new_flaws).padStart(3)}  ${String(s.resolved).padStart(8)}  ${s.timestamp.slice(0, 19)}${marker}`
      );
    }
  }

  if (advisories && advisories.length > 0) {
    console.log();
    console.log("── Advisories (not automatable) ───────────────────────────");
    console.log();
    for (const a of advisories) {
      console.log(`  🔵 [${a.criterion}] ${a.message}`);
    }
  }

  console.log();
  const criticals = openFlaws.filter((f) => f.severity === Severity.CRITICAL);
  const errors = openFlaws.filter((f) => f.severity === Severity.ERROR);

  if (openFlaws.length === 0) {
    console.log("  ╔════════════════════════════════════════════╗");
    console.log("  ║  ✅  ALL CHECKS PASSED                     ║");
    console.log("  ╚════════════════════════════════════════════╝");
  } else {
    console.log("  ╔════════════════════════════════════════════╗");
    console.log(
      `  ║  ❌  ${criticals.length} critical │ ${errors.length} error │ ${openFlaws.length - criticals.length - errors.length} warning${" ".repeat(Math.max(0, 9 - String(criticals.length + errors.length).length))}║`
    );
    console.log("  ╚════════════════════════════════════════════╝");
  }

  console.log();
  console.log(`  State saved to ${STATE_FILE}`);
  console.log();
}

// ─── CLI ──────────────────────────────────────────────────────────

const args = process.argv.slice(2);
const command = args[0];

if (command === "history") {
  const store = loadStore();
  const state = store.getState();

  console.log();
  console.log("── Flaw Registry ──────────────────────────────────────────");
  console.log();

  const allFlaws = Object.values(state.flaws);
  if (allFlaws.length === 0 && state.runs.length === 0) {
    console.log("  No flaws recorded yet. Run: node validate.js <file.yml>");
  } else if (allFlaws.length === 0) {
    console.log(`  No flaws detected across ${state.runs.length} run(s).`);
  } else {
    for (const flaw of allFlaws) {
      const icon = SEVERITY_ICON[flaw.severity];
      const statusIcon = STATUS_ICON[flaw.status];
      console.log(`  ${icon} ${statusIcon} [${flaw.criterion}] ${flaw.message}`);
      console.log(
        `        status: ${flaw.status} │ first: ${flaw.first_seen_version} │ last: ${flaw.last_seen_version} │ seen: ${flaw.occurrences}x`
      );
      console.log(
        `        fp: ${flaw.fingerprint}`
      );
      for (const h of flaw.history) {
        console.log(
          `        └─ ${h.action} @ ${h.version} (${h.timestamp.slice(0, 19)})`
        );
      }
      console.log();
    }
  }

  console.log("── Run Summary ────────────────────────────────────────────");
  console.log();
  const summaries = store.getState().getRunSummary();
  if (summaries.length === 0) {
    console.log("  No runs recorded yet.");
  } else {
    console.log("  Version    Flaws  New  Resolved  Time");
    console.log("  ─────────  ─────  ───  ────────  ────────────────────");
    for (const s of summaries) {
      console.log(
        `  ${s.version.padEnd(9)}  ${String(s.total_flaws).padStart(5)}  ${String(s.new_flaws).padStart(3)}  ${String(s.resolved).padStart(8)}  ${s.timestamp.slice(0, 19)}`
      );
    }
  }
  console.log();
  process.exit(0);

} else if (command === "reset") {
  if (fs.existsSync(STATE_FILE)) {
    fs.unlinkSync(STATE_FILE);
    console.log(`  Deleted ${STATE_FILE}`);
  } else {
    console.log("  No state file found.");
  }
  process.exit(0);

} else if (command === "ack" || command === "acknowledge") {
  const fingerprint = args[1];
  if (!fingerprint) {
    console.error("Usage: node validate.js ack <fingerprint>");
    console.error("  Use 'node validate.js history' to see fingerprints.");
    process.exit(1);
  }
  const store = loadStore();
  const state = store.getState();
  if (!state.flaws[fingerprint]) {
    console.error(`  No flaw found with fingerprint: ${fingerprint}`);
    process.exit(1);
  }
  store.getState().acknowledgeFlaw(fingerprint);
  saveStore(store);
  console.log(`  ✅ Acknowledged: ${fingerprint}`);
  process.exit(0);

} else if (command === "wontfix") {
  const fingerprint = args[1];
  const reason = args.slice(2).join(" ") || "(no reason given)";
  if (!fingerprint) {
    console.error("Usage: node validate.js wontfix <fingerprint> [reason]");
    console.error("  Use 'node validate.js history' to see fingerprints.");
    process.exit(1);
  }
  const store = loadStore();
  const state = store.getState();
  if (!state.flaws[fingerprint]) {
    console.error(`  No flaw found with fingerprint: ${fingerprint}`);
    process.exit(1);
  }
  store.getState().wontFixFlaw(fingerprint, reason);
  saveStore(store);
  console.log(`  ⏭️  Won't fix: ${fingerprint}`);
  console.log(`     Reason: ${reason}`);
  process.exit(0);

} else if (!command || command.startsWith("-")) {
  console.log("Usage:");
  console.log("  node validate.js <path-to-intent.yml>   Validate and track flaws");
  console.log("  node validate.js history                 Show flaw history");
  console.log("  node validate.js ack <fingerprint>       Acknowledge a flaw");
  console.log("  node validate.js wontfix <fp> [reason]   Mark flaw as won't fix");
  console.log("  node validate.js reset                   Clear flaw state");
  console.log();
  console.log("Environment:");
  console.log("  FLAW_STATE=<path>  Custom state file (default: .flaw-state.json)");
  process.exit(0);

} else {
  const filePath = command;

  let raw;
  try {
    raw = fs.readFileSync(filePath, "utf8");
  } catch {
    console.error(`❌ Cannot read file: ${filePath}`);
    process.exit(1);
  }

  let parsed;
  try {
    parsed = YAML.parse(raw);
  } catch (err) {
    console.error(`❌ YAML parse error: ${err.message}`);
    process.exit(1);
  }

  const intent = parsed.intent;
  if (!intent) {
    console.error("❌ Missing top-level 'intent:' key in YAML");
    process.exit(1);
  }

  const { flaws, advisories } = collectFlaws(intent);
  const store = loadStore();
  const runId = store.getState().recordRun(intent.version, flaws);
  saveStore(store);
  renderReport(store, intent, runId, advisories);

  const openFlaws = store.getState().getOpenFlaws();
  const hasCritical = openFlaws.some((f) => f.severity === Severity.CRITICAL);
  process.exit(hasCritical ? 2 : openFlaws.length > 0 ? 1 : 0);
}