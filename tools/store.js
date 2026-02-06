const { createStore } = require("zustand/vanilla");

// ─── FLAW SEVERITY ────────────────────────────────────────────────

const Severity = {
  CRITICAL: "critical",   // blocks self-conformance (CC-18)
  ERROR: "error",         // fails a core criterion
  WARNING: "warning",     // fails a deferred criterion or advisory check
  INFO: "info",           // observation, no failure
};

// ─── FLAW STATUS LIFECYCLE ────────────────────────────────────────
//
//   detected ──→ acknowledged ──→ resolved
//                     │                │
//                     └──→ wont_fix    └──→ regressed (if reappears)

const FlawStatus = {
  DETECTED: "detected",
  ACKNOWLEDGED: "acknowledged",
  RESOLVED: "resolved",
  WONT_FIX: "wont_fix",
  REGRESSED: "regressed",
};

// ─── STORE ────────────────────────────────────────────────────────
//
// LIMITATIONS:
//   - The runs array and per-flaw history arrays grow unboundedly.
//     For the meta-intent (single file, occasional runs), this is fine.
//     For domain-scale usage (hundreds of intents, daily CI), a 
//     compaction or retention policy should be added — e.g., keep 
//     last N runs, archive older entries, or roll up consecutive
//     "persisted" entries into a count.
//   - Pattern detection is computed fresh per run and not persisted
//     with its own lifecycle. Patterns can't be queried historically
//     ("when did this chronic pattern first appear?"). If patterns 
//     become alertable, they'll need timestamps and their own history.

function createFlawStore() {
  return createStore((set, get) => ({
    // ── State ──────────────────────────────────────────────────────

    // All flaws, keyed by a stable fingerprint
    flaws: {},

    // Ordered validation run history
    runs: [],

    // Patterns detected across runs
    patterns: [],

    // ── Actions ────────────────────────────────────────────────────

    // Record a full validation run
    recordRun: (version, flawList) => {
      const runId = `run-${Date.now()}`;
      const timestamp = new Date().toISOString();

      set((state) => {
        const nextFlaws = { ...state.flaws };
        const runFlawIds = [];

        for (const flaw of flawList) {
          const fingerprint = buildFingerprint(flaw);
          runFlawIds.push(fingerprint);

          const existing = nextFlaws[fingerprint];

          if (!existing) {
            // New flaw
            nextFlaws[fingerprint] = {
              fingerprint,
              criterion: flaw.criterion,
              message: flaw.message,
              severity: flaw.severity || Severity.ERROR,
              status: FlawStatus.DETECTED,
              first_seen_version: version,
              first_seen_at: timestamp,
              last_seen_version: version,
              last_seen_at: timestamp,
              occurrences: 1,
              history: [
                {
                  action: "detected",
                  version,
                  timestamp,
                  run_id: runId,
                },
              ],
            };
          } else if (
            existing.status === FlawStatus.RESOLVED ||
            existing.status === FlawStatus.WONT_FIX
          ) {
            // Regression — was resolved/wont_fix, appeared again
            nextFlaws[fingerprint] = {
              ...existing,
              status: FlawStatus.REGRESSED,
              last_seen_version: version,
              last_seen_at: timestamp,
              occurrences: existing.occurrences + 1,
              history: [
                ...existing.history,
                {
                  action: "regressed",
                  version,
                  timestamp,
                  run_id: runId,
                },
              ],
            };
          } else {
            // Still open — update last_seen
            nextFlaws[fingerprint] = {
              ...existing,
              last_seen_version: version,
              last_seen_at: timestamp,
              occurrences: existing.occurrences + 1,
              history: [
                ...existing.history,
                {
                  action: "persisted",
                  version,
                  timestamp,
                  run_id: runId,
                },
              ],
            };
          }
        }

        // Mark resolved: flaws that were open but not in this run
        for (const [fp, flaw] of Object.entries(nextFlaws)) {
          if (
            !runFlawIds.includes(fp) &&
            (flaw.status === FlawStatus.DETECTED ||
              flaw.status === FlawStatus.ACKNOWLEDGED ||
              flaw.status === FlawStatus.REGRESSED)
          ) {
            nextFlaws[fp] = {
              ...flaw,
              status: FlawStatus.RESOLVED,
              history: [
                ...flaw.history,
                {
                  action: "resolved",
                  version,
                  timestamp,
                  run_id: runId,
                },
              ],
            };
          }
        }

        const run = {
          id: runId,
          version,
          timestamp,
          flaw_count: flawList.length,
          flaw_ids: runFlawIds,
          new_flaws: flawList
            .filter((f) => !state.flaws[buildFingerprint(f)])
            .map((f) => buildFingerprint(f)),
          resolved: Object.keys(nextFlaws).filter(
            (fp) =>
              nextFlaws[fp].status === FlawStatus.RESOLVED &&
              state.flaws[fp]?.status !== FlawStatus.RESOLVED
          ),
        };

        const nextPatterns = detectPatterns(nextFlaws, [...state.runs, run]);

        return {
          flaws: nextFlaws,
          runs: [...state.runs, run],
          patterns: nextPatterns,
        };
      });

      return runId;
    },

    // Manually acknowledge a flaw
    acknowledgeFlaw: (fingerprint) => {
      set((state) => {
        const flaw = state.flaws[fingerprint];
        if (!flaw || flaw.status !== FlawStatus.DETECTED) return state;

        return {
          flaws: {
            ...state.flaws,
            [fingerprint]: {
              ...flaw,
              status: FlawStatus.ACKNOWLEDGED,
              history: [
                ...flaw.history,
                {
                  action: "acknowledged",
                  version: flaw.last_seen_version,
                  timestamp: new Date().toISOString(),
                },
              ],
            },
          },
        };
      });
    },

    // Mark a flaw as wont_fix
    wontFixFlaw: (fingerprint, reason) => {
      set((state) => {
        const flaw = state.flaws[fingerprint];
        if (!flaw) return state;

        return {
          flaws: {
            ...state.flaws,
            [fingerprint]: {
              ...flaw,
              status: FlawStatus.WONT_FIX,
              history: [
                ...flaw.history,
                {
                  action: "wont_fix",
                  version: flaw.last_seen_version,
                  timestamp: new Date().toISOString(),
                  reason,
                },
              ],
            },
          },
        };
      });
    },

    // ── Selectors ──────────────────────────────────────────────────

    getOpenFlaws: () => {
      const { flaws } = get();
      return Object.values(flaws).filter(
        (f) =>
          f.status === FlawStatus.DETECTED ||
          f.status === FlawStatus.ACKNOWLEDGED ||
          f.status === FlawStatus.REGRESSED
      );
    },

    getFlawsByCriterion: (criterionId) => {
      const { flaws } = get();
      return Object.values(flaws).filter(
        (f) => f.criterion === criterionId
      );
    },

    getFlawsByVersion: (version) => {
      const { runs, flaws } = get();
      const run = runs.find((r) => r.version === version);
      if (!run) return [];
      return run.flaw_ids.map((fp) => flaws[fp]).filter(Boolean);
    },

    getRegressions: () => {
      const { flaws } = get();
      return Object.values(flaws).filter(
        (f) => f.status === FlawStatus.REGRESSED
      );
    },

    getRunSummary: () => {
      const { runs } = get();
      return runs.map((r) => ({
        id: r.id,
        version: r.version,
        timestamp: r.timestamp,
        total_flaws: r.flaw_count,
        new_flaws: r.new_flaws.length,
        resolved: r.resolved.length,
      }));
    },
  }));
}

// ─── HELPERS ──────────────────────────────────────────────────────

function buildFingerprint(flaw) {
  // Stable identity: criterion + normalized message
  const normalized = (flaw.message || "")
    .replace(/\d+\.\d+\.\d+/g, "X.X.X") // normalize semver in messages
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();
  return `${flaw.criterion}::${normalized}`;
}

function detectPatterns(flaws, runs) {
  const patterns = [];
  const flawList = Object.values(flaws);

  // Pattern: chronic flaw — same criterion failing 3+ consecutive runs
  const criterionStreaks = {};
  for (const flaw of flawList) {
    const cc = flaw.criterion;
    if (!criterionStreaks[cc]) criterionStreaks[cc] = 0;
    if (
      flaw.status === FlawStatus.DETECTED ||
      flaw.status === FlawStatus.ACKNOWLEDGED ||
      flaw.status === FlawStatus.REGRESSED
    ) {
      criterionStreaks[cc] = flaw.occurrences;
    }
  }
  for (const [cc, streak] of Object.entries(criterionStreaks)) {
    if (streak >= 3) {
      patterns.push({
        type: "chronic",
        criterion: cc,
        occurrences: streak,
        message: `${cc} has failed ${streak} consecutive validations`,
      });
    }
  }

  // Pattern: regression — resolved then reappeared
  for (const flaw of flawList) {
    if (flaw.status === FlawStatus.REGRESSED) {
      patterns.push({
        type: "regression",
        criterion: flaw.criterion,
        fingerprint: flaw.fingerprint,
        message: `${flaw.criterion} was resolved but has regressed`,
      });
    }
  }

  // Pattern: cascade — multiple flaws from same criterion in one run
  if (runs.length > 0) {
    const lastRun = runs[runs.length - 1];
    const criterionCounts = {};
    for (const fp of lastRun.flaw_ids) {
      const flaw = flaws[fp];
      if (flaw) {
        criterionCounts[flaw.criterion] =
          (criterionCounts[flaw.criterion] || 0) + 1;
      }
    }
    for (const [cc, count] of Object.entries(criterionCounts)) {
      if (count >= 3) {
        patterns.push({
          type: "cascade",
          criterion: cc,
          count,
          message: `${cc} has ${count} distinct flaws — possible systemic issue`,
        });
      }
    }
  }

  return patterns;
}

// ─── EXPORTS ──────────────────────────────────────────────────────

module.exports = {
  createFlawStore,
  buildFingerprint,
  Severity,
  FlawStatus,
};
