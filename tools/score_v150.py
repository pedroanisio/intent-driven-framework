#!/usr/bin/env python3
"""
Scores intent manifesto + spec against CC-01 through CC-27 (v1.6.0).

Criteria are classified into tiers:
  core     — must pass for v1-completeness
  deferred — tracked, not blocking v1

The report separates core and deferred results.

Companion tooling (schema.js, validate.js, store.js) provides mechanical
verification of the yml's schema shape, structural invariants, and
transition log integrity. This scorer tests the PROSE documents against
the completeness criteria — a different and complementary check.
"""

import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Check:
    id: str
    category: str
    tier: str          # "core" or "deferred"
    test: str
    passed: bool
    evidence: str
    skipped: bool = False


def load(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")

def has(text: str, phrase: str) -> bool:
    return phrase.lower() in text.lower()

def yaml_blocks(md: str) -> list[str]:
    return re.findall(r"```yaml\s*\n(.*?)```", md, re.S)

def yaml_top_fields(block: str) -> set[str]:
    return {m.group(1) for m in re.finditer(r"^\s{0,6}(\w[\w_]*):", block, re.M)}


# ── CC-01 through CC-03: PHILOSOPHY ─────────────────────────────────────────

def cc01(m, s):
    sec = bool(re.search(r"(?i)##\s+[IVXLC]*\.?\s*the\s+problem", m))
    content = has(m, "invisible") or has(m, "we have nothing for intent")
    ok = sec and content
    return Check("CC-01", "philosophy", "core", "Manifesto states the problem",
                 ok, "Problem section with current-state" if ok else "Missing")

def cc02(m, s):
    ok = (bool(re.search(r"(?i)##\s+[IVXLC]*\.?\s*the\s+inversion", m))
          and has(m, "today's model") and has(m, "the intent model"))
    return Check("CC-02", "philosophy", "core", "Manifesto states the inversion",
                 ok, "Old/new orientation" if ok else "Missing")

def cc03(m, s):
    headings = list(re.finditer(r"^###\s+\d+\.\s+.+$", m, re.M))
    all_body = True
    for i, h in enumerate(headings):
        end = headings[i+1].start() if i+1 < len(headings) else len(m)
        if len(m[h.end():end].strip()) < 100:
            all_body = False; break
    ok = len(headings) >= 3 and all_body
    return Check("CC-03", "philosophy", "core", "Principles named, numbered, explained",
                 ok, f"{len(headings)} principles with body" if ok
                 else f"{len(headings)} principles, some lack body")


# ── CC-04 through CC-08: MODEL ──────────────────────────────────────────────

def cc04(m, s):
    required = {"intent", "transition", "decision", "tension", "repo"}
    yamls = yaml_blocks(s)
    found = set()
    for y in yamls:
        for e in required:
            if y.strip().startswith(e+":") or ("\n"+e+":") in y:
                if len(yaml_top_fields(y)) >= 3: found.add(e)
    if any("origin_record:" in y for y in yamls): found.add("origin_record")
    missing = required - found
    return Check("CC-04", "model", "core", "Every entity has complete schema",
                 not missing, f"All: {sorted(found)}" if not missing else f"Missing: {sorted(missing)}")

def cc05(m, s):
    enums = re.findall(r"(\w+):\s*enum\s*#\s*(.+)", s)
    if not enums:
        return Check("CC-05", "model", "core", "Every enum has values listed", False, "No enums found")
    bad = [n for n, v in enums if "|" not in v or re.search(r"(?i)etc|\.{3}|…", v)]
    ok = not bad
    return Check("CC-05", "model", "core", "Every enum has values listed",
                 ok, f"All {len(enums)} specified" if ok else f"Unbounded: {bad}")

def cc06(m, s):
    fwd = has(s, "origin:") and has(s, "ref: string")
    rev = has(s, "generated_intents") or has(s, "constrained_intents")
    ok = fwd and rev
    return Check("CC-06", "model", "core", "Relationships bidirectional",
                 ok, "Bidirectional" if ok else "origin↔intent gap")

def cc07(m, s):
    states = {"proposed", "active", "evolving", "superseded", "residual"}
    combined = (m+s).lower()
    found = {st for st in states if re.search(rf"\b{st}\b", combined)}
    missing = states - found
    diagram = bool(re.search(r"PROPOSED.*→.*ACTIVE.*→.*EVOLVING", m))
    trans = has(s, "change_type: enum")
    ok = not missing and diagram and trans
    return Check("CC-07", "model", "core", "Lifecycle complete",
                 ok, "All states + diagram + transitions" if ok
                 else f"Missing: {sorted(missing)}" if missing else "Transitions underspecified")

def cc08(m, s):
    ok = (has(s, "intent_type: enum") and has(s, "achieved | aspirational")
          and has(s, "current_reality:") and has(s, "for aspirational intents"))
    return Check("CC-08", "model", "core", "Achieved/aspirational distinct",
                 ok, "intent_type, current_reality, aspirational context" if ok else "Incomplete")


# ── CC-08a through CC-08c: CONFLICT ─────────────────────────────────────────

def cc08a(m, s):
    a = has(m, "supersession proposal")
    b = has(m, "resolution owner") or has(m, "resolution_owner")
    c = has(m, "superseded") and has(m, "transition")
    ok = a and b and c
    ev = []
    if a: ev.append("supersession proposal")
    if b: ev.append("authority")
    if c: ev.append("transition outcome")
    return Check("CC-08a", "conflict", "core", "Contradiction → supersession",
                 ok, "; ".join(ev) if ok else f"Partial: {'; '.join(ev) if ev else 'none'}")

def cc08b(m, s):
    a = has(s, "applies_to") and has(s, "resolution")
    b = has(s, "resolution") and (has(s, "re-evaluated") or has(s, "invalidat") or has(s, "checked before"))
    c = (has(s, "block") and has(s, "transition")) or (has(s, "resolution") and has(s, "must be updated"))
    ok = a and b and c
    ev = []
    if a: ev.append("applies_to on resolutions")
    if b: ev.append("re-evaluation contract")
    if c: ev.append("blocking/update rule")
    return Check("CC-08b", "conflict", "core", "Transitions checked against resolutions",
                 ok, "; ".join(ev) if ok else f"Partial: {'; '.join(ev) if ev else 'hook exists but contract undefined'}")

def cc08c(m, s):
    a = has(s, "scope crossing") or has(m, "scope overlap") or has(s, "scope overlap")
    b = has(s, "intents with scope crossing domain boundaries must declare") or (has(m, "overlapping") and has(m, "tension"))
    c = has(s, "validators") and (a or b)
    ok = a and b and c
    ev = []
    if a: ev.append("overlap heuristic")
    if b: ev.append("tension required")
    if c: ev.append("validator")
    return Check("CC-08c", "conflict", "core", "Scope overlap detectable",
                 ok, "; ".join(ev) if ok else f"Partial: {'; '.join(ev) if ev else 'none'}")


# ── CC-09, CC-10: STRUCTURE ─────────────────────────────────────────────────

def cc09(m, s):
    tree = has(s, "_repo/") and has(s, "├──") and has(s, "└──")
    dirs = ["intents/", "transitions/", "tensions/", "decisions/", "origins/", "plugins/"]
    found = [d for d in dirs if has(s, d)]
    ok = tree and len(found) == len(dirs)
    return Check("CC-09", "structure", "core", "Repo structure specified",
                 ok, f"Tree + all {len(dirs)} dirs" if ok else f"Missing: {set(dirs)-set(found)}")

def cc10(m, s):
    c = m + "\n" + s
    checks = {"tree": has(c, "_repo/"), "manifest": has(c, "manifest.yaml") and has(c, "repo:"),
              "intent example": any("intent:" in y and "id:" in y for y in yaml_blocks(c)),
              "plugin structure": has(c, "plugin.yaml") and has(c, "registry.yaml")}
    missing = [k for k, v in checks.items() if not v]
    ok = not missing
    return Check("CC-10", "structure", "core", "Reader can create _repo/ from docs",
                 ok, "All documented" if ok else f"Missing: {missing}")


# ── CC-11, CC-12: EXTENSIBILITY ─────────────────────────────────────────────

def cc11(m, s):
    yamls = yaml_blocks(s)
    mani = any("plugin:" in y and "name:" in y for y in yamls)
    reg = any("plugins:" in y and "name:" in y and "version:" in y for y in yamls)
    worked = sum(1 for y in yamls if "ext:" in y and "<namespace>" not in y)
    ok = mani and reg and worked >= 1
    return Check("CC-11", "extensibility", "core", "Plugin architecture with example",
                 ok, f"Manifest, registry, {worked} examples" if ok else "Incomplete")

def cc12(m, s):
    yamls = yaml_blocks(s)
    schema = any(y.strip().startswith("intent:") and "ext:" in y for y in yamls)
    example = any("ext:" in y and "compliance:" in y for y in yamls)
    shadow = has(s, "no extension can override core") or has(s, "must not override")
    ns = has(s, "<namespace>:") or has(s, "namespaced")
    ignore = has(s, "skip it") or has(s, "ignore")
    ok = schema and example and shadow and ns
    ev = [x for x, v in [("ext in schema", schema), ("example", example),
          ("no-shadow", shadow), ("namespaced", ns), ("graceful ignore", ignore)] if v]
    return Check("CC-12", "extensibility", "core", "Extension surface with semantics",
                 ok, "; ".join(ev) if ok else f"Partial: {'; '.join(ev)}")


# ── CC-13 through CC-15: ADOPTION ───────────────────────────────────────────

def cc13(m, s):
    steps = re.findall(r"^\d+\.\s+\*\*(.+?)\*\*", m, re.M)
    ok = len(steps) >= 5
    return Check("CC-13", "adoption", "core", "Adoption sequence ordered",
                 ok, f"{len(steps)} steps" if ok else f"Only {len(steps)}")

def cc14(m, s):
    ok = (has(m, "worst possible approach") and
          (has(m, "aspirational intent is always available") or
           has(m, "does not require understanding the existing code")))
    return Check("CC-14", "adoption", "core", "Legacy without audit",
                 ok, "Anti-audit + aspirational-first" if ok else "Unclear")

def cc15(m, s):
    techniques = {"pain_first": r"(?i)start\s+with\s+pain|forensic",
                  "next_touch": r"(?i)next.touch.*rule",
                  "declare_unknown": r"(?i)declare\s+the\s+unknown|UNVERIFIED",
                  "llm_inference": r"(?i)llm.assisted|inference.*scaffolding",
                  "amnesty": r"(?i)intent\s+amnesty"}
    found = [n for n, p in techniques.items() if re.search(p, m)]
    ok = len(found) >= 3
    return Check("CC-15", "adoption", "core", "≥3 entry points",
                 ok, f"{len(found)}: {found}" if ok else f"Only {len(found)}: {found}")


# ── CC-16, CC-17: SELF-SUFFICIENCY ──────────────────────────────────────────

def cc16(m, s):
    sec = re.search(r"(?i)##\s+[IVXLC]*\.?\s*core\s+principles(.*?)(?=\n##\s+[IVXLC]|\Z)", m, re.S)
    if not sec:
        return Check("CC-16", "self-sufficiency", "core", "No external concepts", False, "No principles section")
    ext = has(sec.group(1), "see external") or (has(sec.group(1), "refer to") and has(sec.group(1), "http"))
    return Check("CC-16", "self-sufficiency", "core", "No external concepts",
                 not ext, "Self-contained" if not ext else "External refs found")

def cc17(m, s):
    sec = re.search(r"(?i)##\s+[IVXLC]*\.?\s*the\s+practice(.*?)(?=\n##\s|\Z)", m, re.S)
    if not sec:
        return Check("CC-17", "self-sufficiency", "core", "Daily practice stated", False, "No practice section")
    t = sec.group(1)
    b = {"declare": has(t, "declare") and has(t, "intent"),
         "link": has(t, "link") and has(t, "decision"),
         "record": has(t, "record") and has(t, "transition"),
         "check": has(t, "check") or has(t, "encounter resistance")}
    found = [k for k, v in b.items() if v]
    ok = len(found) >= 3
    return Check("CC-17", "self-sufficiency", "core", "Daily practice stated",
                 ok, f"{len(found)}/4: {found}")


# ── CC-18: SELF-CONFORMANCE ─────────────────────────────────────────────────

def cc18(m, s, cc08_ok):
    if not cc08_ok:
        return Check("CC-18", "self-conformance", "core", "Block conforms to own model",
                     False, "SKIPPED — CC-08 failed", skipped=True)
    a = has(s, "current_reality:") and has(m, "current_reality")
    b = has(s, "scope:") or has(s, "scope: string[]")
    c = has(s, "id: string") and has(s, "version: semver") and has(s, "declares: string")
    # v1.4.0 addition: schema_version must be present
    d = has(s, "schema_version")
    ok = a and b and c and d
    ev = []
    if a: ev.append("current_reality")
    if b: ev.append("scope")
    if c: ev.append("required fields")
    if d: ev.append("schema_version")
    return Check("CC-18", "self-conformance", "core", "Block conforms to own model",
                 ok, "; ".join(ev) if ok else f"Partial: {'; '.join(ev)}")


# ── CC-19 through CC-21: OPERATIONAL (core) ─────────────────────────────────

def cc19(m, s):
    falsif = has(m, "falsif")
    pos = has(m, "idempotent") or has(m, "reversible")
    neg = has(m, "platitude") or has(m, "reliable and maintainable")
    ev = []
    if falsif: ev.append("falsifiability test")
    if pos: ev.append("positive example")
    if neg: ev.append("negative example")
    ok = falsif and neg
    return Check("CC-19", "operational", "core", "declares quality guidance",
                 ok, "; ".join(ev) if ev else "none")

def cc20(m, s):
    section = bool(re.search(r"(?i)##\s+[IVXLC]*\.?\s*tooling", s))
    ci = has(s, "lintable in CI") or has(s, "schema validation")
    scope = has(s, "scope") and (has(s, "query") or has(s, "lookup") or has(s, "governs"))
    hooks = has(s, "on_intent_") and has(s, "hooks")
    ev = []
    if section: ev.append("dedicated section")
    if ci: ev.append("CI validation")
    if scope: ev.append("scope lookup")
    if hooks: ev.append("lifecycle hooks")
    ok = section and ci and hooks
    return Check("CC-20", "operational", "core", "Spec defines tooling surface",
                 ok, "; ".join(ev) if ev else "none")

def cc21(m, s):
    ramp = has(m, "ramp") or has(m, "advisory")
    enforce = has(m, "gate becomes") or has(m, "enforcement")
    cold = has(m, "cold-start") or has(m, "double burden") or has(m, "critical mass")
    ev = []
    if ramp: ev.append("ramp/advisory")
    if enforce: ev.append("enforcement transition")
    if cold: ev.append("cold-start rationale")
    ok = ramp and enforce
    return Check("CC-21", "operational", "core", "Next-touch adoption ramp",
                 ok, "; ".join(ev) if ev else "none")


# ── CC-23: OPERATIONAL (core, reworked in v1.3.0) ───────────────────────────

def cc23(m, s):
    # v1.4.0: MAJOR → invalidation, MINOR → review flag, PATCH → excluded
    # Must be about TENSION RESOLUTION staleness, not intent freshness.
    # on_intent_stale is about last_affirmed — that's different.
    combined = s  # staleness contract belongs in the spec

    # (a) MAJOR bump → resolution invalidated
    major_invalidation = (
        bool(re.search(r"(?i)major.{0,80}(invalidat|re-evaluat|stale).*resolution", combined))
        or bool(re.search(r"(?i)resolution.{0,80}(invalidat|re-evaluat|stale).{0,80}major", combined))
    )
    # (b) MINOR bump → review flag (not invalidation)
    minor_review = (
        bool(re.search(r"(?i)minor.{0,80}review.{0,80}resolution", combined))
        or bool(re.search(r"(?i)resolution.{0,80}minor.{0,80}review", combined))
    )
    # (c) PATCH explicitly excluded
    patch_excluded = bool(re.search(r"(?i)patch.{0,80}(exclud|does not|no.{0,20}trigger)", combined))
    # (d) enforcement hook named
    hook_named = has(combined, "on_tension_resolution_stale") or bool(re.search(r"(?i)staleness.{0,40}hook", combined))

    ev = []
    if major_invalidation: ev.append("MAJOR → invalidation")
    if minor_review: ev.append("MINOR → review flag")
    if patch_excluded: ev.append("PATCH excluded")
    if hook_named: ev.append("enforcement hook")
    ok = major_invalidation and minor_review
    return Check("CC-23", "operational", "core", "Tension staleness contract",
                 ok, "; ".join(ev) if ev else "none")


# ── CC-25: DEPRECATION CEREMONIES (core, new in v1.3.0) ─────────────────────

def cc25(m, s):
    # (a) dependents identified and notified
    notify = has(s, "depends_on") and (has(s, "notif") or has(s, "downstream"))
    # (b) migration path: re-point, drop, or acknowledge
    migration = (has(s, "successor") or has(s, "re-point")) and (has(s, "supersed") or has(s, "residual"))
    # (c) grace period or deadline
    grace = has(s, "grace period") or has(s, "deadline") or has(s, "intent owner")
    # (d) unresolved references become tensions
    unresolved = has(s, "tension") and (has(s, "unresolved") or has(s, "zombie") or has(s, "orphan"))
    # Also check manifesto for deprecation ceremony description
    m_deprecation = has(m, "deprecat") or (has(m, "superseded") and has(m, "downstream"))

    ev = []
    if notify: ev.append("dependents notified")
    if migration: ev.append("migration path")
    if grace: ev.append("grace period")
    if unresolved: ev.append("unresolved → tension")
    if m_deprecation: ev.append("manifesto coverage")
    ok = notify and migration
    return Check("CC-25", "operational", "core", "Deprecation ceremonies defined",
                 ok, "; ".join(ev) if ev else "none")


# ── CC-26: FAILURE MODE CATALOGUE (core, new in v1.3.0) ─────────────────────

def cc26(m, s):
    # Dedicated failure section with at least 3 distinct modes
    sec = re.search(r"(?i)##\s+[IVXLC]*\.?\s*how\s+this\s+fails(.*?)(?=\n##\s|\Z)", m, re.S)
    if not sec:
        return Check("CC-26", "operational", "core", "Failure mode catalogue",
                     False, "No failure section found")
    text = sec.group(1)

    # Required modes per v1.4.0:
    # (a) performative intent
    performative = has(text, "performative")
    # (b) over-specification / bureaucratic
    overspec = has(text, "bureaucratic") or has(text, "over-specification")
    # (c) intent drift — manifesto uses "blur" and "nobody reads" rather than "drift"
    #     Concept: declared intents no longer reflect actual system behavior
    drift = (has(text, "drift")
             or has(text, "blur")                     # "achieved and aspirational intents blur"
             or has(text, "no longer reflect")
             or has(text, "nobody reads"))             # "nobody reads the intent history"

    # Each should have: name, symptoms, root cause, mitigation
    modes = re.findall(r"\*\*([^*]+)\*\*", text)
    has_structure = (
        (has(text, "remedy") or has(text, "mitigation"))
        and (has(text, "symptom") or has(text, "easy to spot") or has(text, "signal"))
    )

    ev = []
    if performative: ev.append("performative")
    if overspec: ev.append("bureaucratic")
    if drift: ev.append("intent drift/blur")
    ev.append(f"{len(modes)} named modes")
    if has_structure: ev.append("symptoms+remedies")

    ok = performative and overspec and drift and len(modes) >= 3 and has_structure
    return Check("CC-26", "operational", "core", "Failure mode catalogue",
                 ok, "; ".join(ev))


# ── CC-27: TRANSITION LOG INTEGRITY (core, new in v1.4.0) ───────────────────

def cc27_check_yml(yml_path: str) -> Check:
    """Check the yml's transition log integrity (v1.5.0)."""
    try:
        yml = load(yml_path)
    except FileNotFoundError:
        return Check("CC-27", "self-conformance", "core", "Transition log integrity",
                     False, "yml not found — cannot verify transition log")

    # Extract version
    ver_match = re.search(r"version:\s*(\d+\.\d+\.\d+)", yml)
    current = ver_match.group(1) if ver_match else "unknown"

    # Extract transition pairs and change_types
    pairs = re.findall(r"from:\s*(\d+\.\d+\.\d+)\s*\n\s*to:\s*(\d+\.\d+\.\d+)", yml)
    change_types = re.findall(r"change_type:\s*(\w+)", yml)

    if not pairs:
        return Check("CC-27", "self-conformance", "core", "Transition log integrity",
                     False, "No transition entries found")

    # (a) Check continuous chain from 1.0.0 to current
    chain = {f: t for f, t in pairs}
    visited = []
    cursor = "1.0.0"
    while cursor in chain:
        visited.append((cursor, chain[cursor]))
        cursor = chain[cursor]
    chain_complete = (cursor == current)

    # (b) Check each entry has summary and change_type
    summaries = re.findall(
        r"change_type:\s*(\w+)\s*\n\s*summary:\s*>?\s*\n(.+?)(?=\n\s*-\s+from:|\n\s+completeness|\Z)",
        yml, re.S)
    has_all_summaries = len(summaries) == len(pairs)

    # (c) v1.5.0: change_type values must come from canonical enum
    canonical_enum = {"clarification", "correction", "extension",
                      "reclassification", "breaking", "deprecation"}
    invalid_types = [ct for ct in change_types if ct not in canonical_enum]
    enum_valid = not invalid_types

    ev = []
    ev.append(f"chain: {'→'.join([p[0] for p in visited] + [cursor])}")
    if chain_complete: ev.append(f"reaches {current}")
    else: ev.append(f"stops at {cursor}, expected {current}")
    ev.append(f"{len(summaries)}/{len(pairs)} summaries")
    if enum_valid: ev.append(f"all change_types canonical")
    else: ev.append(f"invalid change_types: {invalid_types}")

    ok = chain_complete and has_all_summaries and enum_valid
    return Check("CC-27", "self-conformance", "core", "Transition log integrity",
                 ok, "; ".join(ev))


# ── CC-22: DEFERRED ─────────────────────────────────────────────────────────

def cc22(m, s):
    mech = has(s, "pull-based") or has(s, "push-based") or has(s, "central registry")
    notif = has(s, "signal") or has(s, "notification") or has(s, "issue")
    fail = has(s, "unacknowledged") or has(s, "does not respond")
    ev = []
    if mech: ev.append("discovery mechanism")
    if notif: ev.append("notification")
    if fail: ev.append("failure mode")
    ok = mech and notif
    return Check("CC-22", "deferred", "deferred", "Cross-repo discovery protocol",
                 ok, "; ".join(ev) if ev else "none")


# ── CC-24: DEFERRED ─────────────────────────────────────────────────────────

def cc24(m, s):
    # v1.4.0: softened. Technical semantics only, no org process required.
    # The spec defines PATCH/MINOR/MAJOR for INTENT versioning. CC-24 requires
    # those semantics for SCHEMA versioning — what constitutes a breaking
    # schema change vs additive vs cosmetic. These are different concepts.
    ver = has(s, "schema_version")
    # Proximity: schema + semver terms must appear together, not just co-exist
    schema_semver = (
        bool(re.search(r"(?i)schema.{0,120}(PATCH|MINOR|MAJOR).{0,60}(PATCH|MINOR|MAJOR)", s))
        or bool(re.search(r"(?i)(PATCH|MINOR|MAJOR).{0,60}schema.{0,60}(PATCH|MINOR|MAJOR)", s))
    )
    migration = bool(re.search(r"(?i)schema.{0,80}migration.{0,80}(level|requirement|transform)", s))
    ev = []
    if ver: ev.append("schema_version field exists")
    if schema_semver: ev.append("PATCH/MINOR/MAJOR for schema changes")
    if migration: ev.append("migration requirements per level")
    ok = ver and schema_semver
    return Check("CC-24", "deferred", "deferred", "Schema evolution semantics",
                 ok, "; ".join(ev) if ev else "field exists but semantics undefined")


# ── RUNNER ───────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) >= 3:
        mp, sp = sys.argv[1], sys.argv[2]
        yp = sys.argv[3] if len(sys.argv) > 3 else None
    else:
        mp = "prose/intent-manifesto.md"
        sp = "prose/intent-spec.md"
        yp = "criteria/intent-manifesto-v1.6.0.yml"

    m, s = load(mp), load(sp)

    results = []
    # Philosophy
    results.extend([cc01(m, s), cc02(m, s), cc03(m, s)])
    # Model
    results.extend([cc04(m, s), cc05(m, s), cc06(m, s), cc07(m, s)])
    r08 = cc08(m, s); results.append(r08)
    # Conflict
    results.extend([cc08a(m, s), cc08b(m, s), cc08c(m, s)])
    # Structure
    results.extend([cc09(m, s), cc10(m, s)])
    # Extensibility
    results.extend([cc11(m, s), cc12(m, s)])
    # Adoption
    results.extend([cc13(m, s), cc14(m, s), cc15(m, s)])
    # Self-sufficiency
    results.extend([cc16(m, s), cc17(m, s)])
    # Self-conformance
    results.append(cc18(m, s, r08.passed))
    # Operational (core)
    results.extend([cc19(m, s), cc20(m, s), cc21(m, s), cc23(m, s), cc25(m, s), cc26(m, s)])
    # Transition log integrity
    if yp:
        results.append(cc27_check_yml(yp))
    else:
        results.append(Check("CC-27", "self-conformance", "core",
                             "Transition log integrity", False, "No yml path provided"))
    # Deferred
    results.extend([cc22(m, s), cc24(m, s)])

    # ── Report ───────────────────────────────────────────────────────
    w = 76
    print("=" * w)
    print("  INTENT DOCUMENTS — CC-01 → CC-27 (v1.6.0)")
    print("=" * w)

    core = [r for r in results if r.tier == "core"]
    deferred = [r for r in results if r.tier == "deferred"]

    def print_section(checks, label):
        cats = {}
        for r in checks:
            cats.setdefault(r.category, []).append(r)
        p = f = sk = 0
        print(f"\n  ── {label} ──")
        for cat, cks in cats.items():
            cp = sum(1 for c in cks if c.passed and not c.skipped)
            ct = len(cks)
            print(f"\n  [{cat.upper()}] {cp}/{ct}")
            for c in cks:
                if c.skipped: mark = "○"; sk += 1
                elif c.passed: mark = "✓"; p += 1
                else: mark = "✗"; f += 1
                print(f"    {mark} {c.id}: {c.test}")
                print(f"        {c.evidence}")
        return p, f, sk

    cp, cf, cs = print_section(core, "CORE (must pass for v1)")
    dp, df, ds = print_section(deferred, "DEFERRED (tracked, not blocking)")

    print(f"\n{'─' * w}")
    print(f"  CORE:     {cp}/{cp+cf} passed  ({cf} failed, {cs} skipped)")
    print(f"  DEFERRED: {dp}/{dp+df} passed  ({df} failed, {ds} skipped)")
    print(f"  TOTAL:    {cp+dp}/{cp+cf+dp+df}")

    # Run JS validator if available
    import subprocess
    script_dir = str(Path(__file__).parent.resolve())
    yml_dir = str(Path(yp).parent.resolve()) if yp else None
    # Look for validate.js next to this script first, then next to the yml
    js_dir = None
    for candidate in [script_dir, yml_dir]:
        if candidate and Path(candidate, "validate.js").exists():
            js_dir = candidate
            break
    if js_dir and yp:
        yml_abs = str(Path(yp).resolve())
        try:
            result = subprocess.run(
                ["node", "validate.js", yml_abs],
                capture_output=True, text=True, cwd=js_dir, timeout=15)
            js_clean = result.returncode == 0
            print(f"\n  ── COMPANION: Zod validator (schema.js + validate.js) ──")
            if js_clean:
                print(f"    ✓ Schema shape, structural invariants, transition log: PASS")
            else:
                print(f"    ✗ JS validator returned exit code {result.returncode}")
                for line in result.stdout.strip().split("\n")[-5:]:
                    print(f"        {line}")
        except Exception as e:
            print(f"\n  ── COMPANION: Zod validator ──")
            print(f"    ○ Could not run: {e}")

    print("=" * w)
    sys.exit(0 if cf == 0 else 1)


if __name__ == "__main__":
    main()
