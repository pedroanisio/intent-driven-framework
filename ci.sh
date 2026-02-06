#!/usr/bin/env bash
set -euo pipefail

# ═══════════════════════════════════════════════════════════════════
# Intent Framework — Validation Pipeline
#
# Each stage gates the next. Fail fast, fail cheap.
# Later layers assume earlier guarantees hold.
#
#   Stage 0  Cross-layer drift      (ms)
#   Stage 1  Schema validation     (ms)
#   Stage 2  Lean proofs           (sec)
#   Stage 3  Self-conformance      (sec)
#   Stage 4  NLP semantic checks   (sec-min, optional)
#
# Usage:
#   ./ci.sh              # Stages 0-3
#   ./ci.sh --with-nlp   # Stages 0-4
# ═══════════════════════════════════════════════════════════════════

ROOT="$(cd "$(dirname "$0")" && pwd)"

WITH_NLP=false
for arg in "$@"; do
  case "$arg" in
    --with-nlp) WITH_NLP=true ;;
    *) echo "Unknown argument: $arg"; exit 1 ;;
  esac
done

# ── Ensure node is available (nvm lazy-load) ─────────────────────
if ! command -v node &>/dev/null; then
  export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
  if [ -s "$NVM_DIR/nvm.sh" ]; then
    \. "$NVM_DIR/nvm.sh"
  else
    echo "ERROR: node not found and nvm not available"
    exit 1
  fi
fi

passed=0
failed=0

run_stage() {
  local num="$1" name="$2"
  shift 2
  echo ""
  echo "═══ Stage $num: $name ═══"
  if "$@"; then
    echo "  ✓ $name passed"
    passed=$((passed + 1))
  else
    echo "  ✗ $name FAILED (exit $?)"
    failed=$((failed + 1))
    echo ""
    echo "Pipeline stopped at Stage $num."
    echo "  Passed: $passed  Failed: $failed"
    exit 1
  fi
}

# ── Stage 0: Cross-Layer Drift Detection ─────────────────────────
run_stage 0 "Cross-layer drift check" \
  python3 "$ROOT/tools/drift_check.py"

# ── Stage 1: Schema Validation ───────────────────────────────────
run_stage 1 "Schema validation" \
  node "$ROOT/tools/validate.js" "$ROOT/criteria/intent-driven-framework-definition.yml"

# ── Stage 2: Lean Proofs ─────────────────────────────────────────
run_stage 2 "Lean proofs" \
  lake build -d "$ROOT/lean"

# ── Stage 3: Self-Conformance Tests ──────────────────────────────
run_stage 3 "Self-conformance tests" \
  pytest "$ROOT/tools/tests" -x --tb=short -q

# ── Stage 4: NLP Semantic Checks (optional) ──────────────────────
if [ "$WITH_NLP" = true ]; then
  if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
    echo ""
    echo "═══ Stage 4: NLP semantic checks ═══"
    echo "  ⚠ Skipped: ANTHROPIC_API_KEY not set"
  else
    run_stage 4 "NLP semantic checks" \
      python "$ROOT/tools/nlp_validator.py" \
        "$ROOT/prose/intent-manifesto.md" \
        "$ROOT/prose/intent-spec-core.md"
  fi
fi

# ── Summary ──────────────────────────────────────────────────────
echo ""
echo "═══ All automated stages green ═══"
echo "  Passed: $passed  Failed: $failed"
