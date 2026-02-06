"""
Evidence extraction — mechanical verification of prose against criteria.

Each function gathers evidence for one or more criteria. Returns an
Evidence object with a pass/fail verdict and the proof trail.

Design principle: evidence functions are DUMB. They look for structural
markers, keywords, patterns. They don't understand the prose. A passing
check means "the structural indicators are present," not "the prose is
good." Human judgment is still required — these checks raise the floor,
not the ceiling.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field


@dataclass
class Evidence:
    """Result of an evidence check."""
    passed: bool
    markers: list[str] = field(default_factory=list)   # what was found
    gaps: list[str] = field(default_factory=list)       # what was missing
    skipped: bool = False
    skip_reason: str = ""

    @property
    def summary(self) -> str:
        parts = []
        if self.skipped:
            return f"SKIPPED: {self.skip_reason}"
        if self.markers:
            parts.append("found: " + "; ".join(self.markers))
        if self.gaps:
            parts.append("missing: " + "; ".join(self.gaps))
        return " | ".join(parts) if parts else ("pass" if self.passed else "fail")

    def __str__(self) -> str:
        icon = "○" if self.skipped else ("✓" if self.passed else "✗")
        return f"{icon} {self.summary}"


# ── TEXT HELPERS ──────────────────────────────────────────────────────

def has(text: str, phrase: str) -> bool:
    """Case-insensitive substring check."""
    return phrase.lower() in text.lower()


def has_near(text: str, a: str, b: str, window: int = 120) -> bool:
    """True if phrase b appears within `window` chars of phrase a."""
    pattern = rf"(?i){re.escape(a)}.{{0,{window}}}{re.escape(b)}"
    return bool(re.search(pattern, text))


def yaml_blocks(md: str) -> list[str]:
    """Extract all ```yaml fenced code blocks."""
    return re.findall(r"```yaml\s*\n(.*?)```", md, re.S)


def yaml_top_fields(block: str) -> set[str]:
    """Extract top-level field names from a YAML block."""
    return {m.group(1) for m in re.finditer(r"^\s{0,6}(\w[\w_]*):", block, re.M)}


def section(md: str, heading_pattern: str) -> str | None:
    """Extract section content under a heading matching the pattern."""
    m = re.search(
        rf"(?i)##\s+[IVXLC]*\.?\s*{heading_pattern}(.*?)(?=\n##\s+[IVXLC]|\Z)",
        md, re.S
    )
    return m.group(1) if m else None


# ═══════════════════════════════════════════════════════════════════════
#  PHILOSOPHY
# ═══════════════════════════════════════════════════════════════════════

def check_cc01(manifesto: str, spec: str) -> Evidence:
    """CC-01: Manifesto states the problem it solves."""
    e = Evidence(passed=False)

    sec = bool(re.search(r"(?i)##\s+[IVXLC]*\.?\s*the\s+problem", manifesto))
    if sec:
        e.markers.append("problem section exists")
    else:
        e.gaps.append("no 'The Problem' section")

    content = has(manifesto, "invisible") or has(manifesto, "we have nothing for intent")
    if content:
        e.markers.append("describes current state without model")
    else:
        e.gaps.append("no description of current state")

    e.passed = sec and content
    return e


def check_cc02(manifesto: str, spec: str) -> Evidence:
    """CC-02: Manifesto states the inversion explicitly."""
    e = Evidence(passed=False)

    sec = bool(re.search(r"(?i)##\s+[IVXLC]*\.?\s*the\s+inversion", manifesto))
    old = has(manifesto, "today's model")
    new = has(manifesto, "the intent model")

    if sec: e.markers.append("inversion section exists")
    else: e.gaps.append("no 'The Inversion' section")
    if old: e.markers.append("old orientation named")
    else: e.gaps.append("old orientation not named")
    if new: e.markers.append("new orientation named")
    else: e.gaps.append("new orientation not named")

    e.passed = sec and old and new
    return e


def check_cc03(manifesto: str, spec: str) -> Evidence:
    """CC-03: Every principle is named, numbered, and explained."""
    e = Evidence(passed=False)

    headings = list(re.finditer(r"^###\s+\d+\.\s+.+$", manifesto, re.M))
    all_have_body = True
    for i, h in enumerate(headings):
        end = headings[i + 1].start() if i + 1 < len(headings) else len(manifesto)
        if len(manifesto[h.end():end].strip()) < 100:
            all_have_body = False
            break

    e.markers.append(f"{len(headings)} numbered principles")
    if all_have_body:
        e.markers.append("all have substantive body text")
    else:
        e.gaps.append("some principles lack body (< 100 chars)")

    e.passed = len(headings) >= 3 and all_have_body
    return e


# ═══════════════════════════════════════════════════════════════════════
#  MODEL
# ═══════════════════════════════════════════════════════════════════════

def check_cc04(manifesto: str, spec: str) -> Evidence:
    """CC-04: Every first-class entity has a complete schema."""
    required = {"intent", "transition", "decision", "tension", "repo"}
    yamls = yaml_blocks(spec)
    found = set()
    for y in yamls:
        for entity in required:
            if y.strip().startswith(entity + ":") or ("\n" + entity + ":") in y:
                if len(yaml_top_fields(y)) >= 3:
                    found.add(entity)
    if any("origin_record:" in y for y in yamls):
        found.add("origin_record")

    missing = required - found
    e = Evidence(passed=not missing)
    e.markers.append(f"entities found: {sorted(found)}")
    if missing:
        e.gaps.append(f"missing schemas: {sorted(missing)}")
    return e


def check_cc05(manifesto: str, spec: str) -> Evidence:
    """CC-05: Every enum field has all valid values listed."""
    enums = re.findall(r"(\w+):\s*enum\s*#\s*(.+)", spec)
    if not enums:
        return Evidence(passed=False, gaps=["no enum fields found in spec"])

    bad = [n for n, v in enums if "|" not in v or re.search(r"(?i)etc|\.{3}|…", v)]
    e = Evidence(passed=not bad)
    e.markers.append(f"{len(enums)} enum fields found")
    if bad:
        e.gaps.append(f"unbounded enums: {bad}")
    else:
        e.markers.append("all have explicit value lists")
    return e


def check_cc06(manifesto: str, spec: str) -> Evidence:
    """CC-06: Relationships are bidirectionally defined."""
    fwd = has(spec, "origin:") and has(spec, "ref: string")
    rev = has(spec, "generated_intents") or has(spec, "constrained_intents")

    e = Evidence(passed=fwd and rev)
    if fwd: e.markers.append("forward refs (origin → external)")
    else: e.gaps.append("missing forward refs")
    if rev: e.markers.append("reverse index (external → intents)")
    else: e.gaps.append("missing reverse index")
    return e


def check_cc07(manifesto: str, spec: str) -> Evidence:
    """CC-07: Intent lifecycle is complete."""
    states = {"proposed", "active", "evolving", "superseded", "residual", "retracted"}
    combined = (manifesto + spec).lower()
    found = {st for st in states if re.search(rf"\b{st}\b", combined)}
    missing = states - found

    diagram = bool(re.search(r"PROPOSED.*→.*ACTIVE.*→.*EVOLVING", manifesto))
    transitions = has(spec, "change_type: enum")

    e = Evidence(passed=not missing and diagram and transitions)
    e.markers.append(f"states: {sorted(found)}")
    if diagram: e.markers.append("lifecycle diagram")
    else: e.gaps.append("no lifecycle diagram")
    if transitions: e.markers.append("transition triggers defined")
    else: e.gaps.append("transition triggers missing")
    if missing: e.gaps.append(f"missing states: {sorted(missing)}")
    return e


def check_cc08(manifesto: str, spec: str) -> Evidence:
    """CC-08: Achieved/aspirational have distinct schemas."""
    type_enum = has(spec, "intent_type: enum") and has(spec, "achieved | aspirational")
    reality = has(spec, "current_reality:")
    context = has(spec, "for aspirational intents")

    e = Evidence(passed=type_enum and reality and context)
    if type_enum: e.markers.append("intent_type enum")
    else: e.gaps.append("no intent_type enum")
    if reality: e.markers.append("current_reality block")
    else: e.gaps.append("no current_reality")
    if context: e.markers.append("aspirational context documented")
    else: e.gaps.append("aspirational context missing")
    return e


# ═══════════════════════════════════════════════════════════════════════
#  CONFLICT
# ═══════════════════════════════════════════════════════════════════════

def check_cc08a(manifesto: str, spec: str) -> Evidence:
    """CC-08a: Contradiction → supersession proposal."""
    a = has(manifesto, "supersession proposal")
    b = has(manifesto, "resolution owner") or has(manifesto, "resolution_owner")
    c = has(manifesto, "superseded") and has(manifesto, "transition")

    e = Evidence(passed=a and b and c)
    if a: e.markers.append("supersession proposal")
    else: e.gaps.append("no supersession mechanism")
    if b: e.markers.append("authority named")
    else: e.gaps.append("no resolution authority")
    if c: e.markers.append("transition outcome recorded")
    else: e.gaps.append("no transition recording")
    return e


def check_cc08b(manifesto: str, spec: str) -> Evidence:
    """CC-08b: Transitions checked against active resolutions."""
    a = has(spec, "applies_to") and has(spec, "resolution")
    b = has(spec, "re-evaluated") or has(spec, "invalidat") or has(spec, "checked before")
    c = (has(spec, "block") and has(spec, "transition")) or \
        (has(spec, "resolution") and has(spec, "must be updated"))

    e = Evidence(passed=a and b and c)
    if a: e.markers.append("applies_to on resolutions")
    else: e.gaps.append("no applies_to field")
    if b: e.markers.append("re-evaluation contract")
    else: e.gaps.append("no re-evaluation rule")
    if c: e.markers.append("blocking/update enforcement")
    else: e.gaps.append("no enforcement mechanism")
    return e


def check_cc08c(manifesto: str, spec: str) -> Evidence:
    """CC-08c: Scope overlap is detectable."""
    a = has(spec, "scope crossing") or has(manifesto, "scope overlap") or has(spec, "scope overlap")
    b = has(spec, "intents with scope crossing domain boundaries must declare") or \
        (has(manifesto, "overlapping") and has(manifesto, "tension"))
    c = has(spec, "validators") and (a or b)

    e = Evidence(passed=a and b and c)
    if a: e.markers.append("overlap heuristic")
    else: e.gaps.append("no overlap detection")
    if b: e.markers.append("tension required for overlap")
    else: e.gaps.append("no overlap → tension rule")
    if c: e.markers.append("validator exists")
    else: e.gaps.append("no validator for overlap")
    return e


# ═══════════════════════════════════════════════════════════════════════
#  STRUCTURE
# ═══════════════════════════════════════════════════════════════════════

def check_cc09(manifesto: str, spec: str) -> Evidence:
    """CC-09: Repository structure is fully specified."""
    tree = has(spec, "_repo/") and has(spec, "├──") and has(spec, "└──")
    dirs = ["intents/", "transitions/", "tensions/", "decisions/", "origins/", "plugins/"]
    found = [d for d in dirs if has(spec, d)]

    e = Evidence(passed=tree and len(found) == len(dirs))
    if tree: e.markers.append("directory tree present")
    else: e.gaps.append("no directory tree")
    e.markers.append(f"{len(found)}/{len(dirs)} directories documented")
    missing = set(dirs) - set(found)
    if missing: e.gaps.append(f"missing dirs: {missing}")
    return e


def check_cc10(manifesto: str, spec: str) -> Evidence:
    """CC-10: Reader can create _repo/ from docs alone."""
    c = manifesto + "\n" + spec
    checks = {
        "tree": has(c, "_repo/"),
        "manifest": has(c, "manifest.yaml") and has(c, "repo:"),
        "intent_example": any("intent:" in y and "id:" in y for y in yaml_blocks(c)),
        "plugin_structure": has(c, "plugin.yaml") and has(c, "registry.yaml"),
    }
    missing = [k for k, v in checks.items() if not v]
    e = Evidence(passed=not missing)
    for k, v in checks.items():
        (e.markers if v else e.gaps).append(k)
    return e


# ═══════════════════════════════════════════════════════════════════════
#  EXTENSIBILITY
# ═══════════════════════════════════════════════════════════════════════

def check_cc11(manifesto: str, spec: str) -> Evidence:
    """CC-11: Plugin architecture with concrete example."""
    yamls = yaml_blocks(spec)
    manifest = any("plugin:" in y and "name:" in y for y in yamls)
    registry = any("plugins:" in y and "name:" in y and "version:" in y for y in yamls)
    worked = sum(1 for y in yamls if "ext:" in y and "<namespace>" not in y)

    e = Evidence(passed=manifest and registry and worked >= 1)
    if manifest: e.markers.append("plugin manifest schema")
    else: e.gaps.append("no plugin manifest")
    if registry: e.markers.append("plugin registry schema")
    else: e.gaps.append("no plugin registry")
    e.markers.append(f"{worked} worked examples")
    if worked < 1: e.gaps.append("no worked example")
    return e


def check_cc12(manifesto: str, spec: str) -> Evidence:
    """CC-12: Extension surface with semantics."""
    yamls = yaml_blocks(spec)
    schema = any(y.strip().startswith("intent:") and "ext:" in y for y in yamls)
    example = any("ext:" in y and "compliance:" in y for y in yamls)
    shadow = has(spec, "no extension can override core") or has(spec, "must not override")
    ns = has(spec, "<namespace>:") or has(spec, "namespaced")
    ignore = has(spec, "skip it") or has(spec, "ignore")

    e = Evidence(passed=schema and example and shadow and ns)
    for label, check in [("ext in schema", schema), ("example", example),
                         ("no-shadow rule", shadow), ("namespaced", ns),
                         ("graceful ignore", ignore)]:
        (e.markers if check else e.gaps).append(label)
    return e


# ═══════════════════════════════════════════════════════════════════════
#  ADOPTION
# ═══════════════════════════════════════════════════════════════════════

def check_cc13(manifesto: str, spec: str) -> Evidence:
    """CC-13: Adoption sequence is ordered and actionable."""
    steps = re.findall(r"^\d+\.\s+\*\*(.+?)\*\*", manifesto, re.M)
    e = Evidence(passed=len(steps) >= 5)
    e.markers.append(f"{len(steps)} numbered steps")
    if len(steps) < 5:
        e.gaps.append("fewer than 5 steps")
    return e


def check_cc14(manifesto: str, spec: str) -> Evidence:
    """CC-14: Legacy strategy doesn't require comprehensive audit."""
    anti_audit = has(manifesto, "worst possible approach")
    aspirational_first = (
        has(manifesto, "aspirational intent is always available") or
        has(manifesto, "does not require understanding the existing code")
    )
    e = Evidence(passed=anti_audit and aspirational_first)
    if anti_audit: e.markers.append("anti-audit stance")
    else: e.gaps.append("no anti-audit statement")
    if aspirational_first: e.markers.append("aspirational-first documented")
    else: e.gaps.append("aspirational-first not stated")
    return e


def check_cc15(manifesto: str, spec: str) -> Evidence:
    """CC-15: At least three practical entry points."""
    techniques = {
        "pain_first": r"(?i)start\s+with\s+pain|forensic",
        "next_touch": r"(?i)next.touch.*rule",
        "declare_unknown": r"(?i)declare\s+the\s+unknown|UNVERIFIED",
        "llm_inference": r"(?i)llm.assisted|inference.*scaffolding",
        "amnesty": r"(?i)intent\s+amnesty",
    }
    found = [n for n, p in techniques.items() if re.search(p, manifesto)]
    e = Evidence(passed=len(found) >= 3)
    e.markers.append(f"{len(found)} entry points: {found}")
    if len(found) < 3:
        e.gaps.append(f"need ≥3, found {len(found)}")
    return e


# ═══════════════════════════════════════════════════════════════════════
#  SELF-SUFFICIENCY
# ═══════════════════════════════════════════════════════════════════════

def check_cc16(manifesto: str, spec: str) -> Evidence:
    """CC-16: No principle references external-only concepts."""
    sec = section(manifesto, r"core\s+principles")
    if not sec:
        return Evidence(passed=False, gaps=["no 'Core Principles' section found"])

    ext_refs = has(sec, "see external") or (has(sec, "refer to") and has(sec, "http"))
    e = Evidence(passed=not ext_refs)
    if ext_refs:
        e.gaps.append("external references found in principles")
    else:
        e.markers.append("self-contained (no external refs)")
    return e


def check_cc17(manifesto: str, spec: str) -> Evidence:
    """CC-17: Daily practice is stated concretely."""
    sec = section(manifesto, r"the\s+practice")
    if not sec:
        return Evidence(passed=False, gaps=["no 'The Practice' section found"])

    behaviors = {
        "declare": has(sec, "declare") and has(sec, "intent"),
        "link": has(sec, "link") and has(sec, "decision"),
        "record": has(sec, "record") and has(sec, "transition"),
        "check": has(sec, "check") or has(sec, "encounter resistance"),
    }
    found = [k for k, v in behaviors.items() if v]

    e = Evidence(passed=len(found) >= 3)
    e.markers.append(f"{len(found)}/4 behaviors: {found}")
    missing = [k for k, v in behaviors.items() if not v]
    if missing:
        e.gaps.append(f"missing behaviors: {missing}")
    return e


# ═══════════════════════════════════════════════════════════════════════
#  SELF-CONFORMANCE
# ═══════════════════════════════════════════════════════════════════════

def check_cc18(manifesto: str, spec: str, cc08_passed: bool = True) -> Evidence:
    """CC-18: Intent block conforms to its own model."""
    if not cc08_passed:
        return Evidence(
            passed=False, skipped=True,
            skip_reason="CC-08 failed — cannot evaluate self-conformance"
        )

    a = has(spec, "current_reality:") and has(manifesto, "current_reality")
    b = has(spec, "scope:") or has(spec, "scope: string[]")
    c = has(spec, "id: string") and has(spec, "version: semver") and has(spec, "declares: string")
    d = has(spec, "schema_version")

    e = Evidence(passed=a and b and c and d)
    for label, check in [("current_reality", a), ("scope", b),
                         ("required fields", c), ("schema_version", d)]:
        (e.markers if check else e.gaps).append(label)
    return e


def check_cc27(yml_text: str) -> Evidence:
    """CC-27: Transition log integrity."""
    ver_match = re.search(r"version:\s*(\d+\.\d+\.\d+)", yml_text)
    current = ver_match.group(1) if ver_match else None
    if not current:
        return Evidence(passed=False, gaps=["cannot determine current version"])

    pairs = re.findall(r"from:\s*(\d+\.\d+\.\d+)\s*\n\s*to:\s*(\d+\.\d+\.\d+)", yml_text)
    change_types = re.findall(r"change_type:\s*(\w+)", yml_text)

    if not pairs:
        return Evidence(passed=False, gaps=["no transition entries found"])

    # (a) Continuous chain
    chain = {f: t for f, t in pairs}
    visited = []
    cursor = "1.0.0"
    while cursor in chain:
        visited.append((cursor, chain[cursor]))
        cursor = chain[cursor]
    chain_complete = (cursor == current)

    # (b) Summaries exist
    summaries = re.findall(
        r"change_type:\s*(\w+)\s*\n\s*summary:\s*>?\s*\n(.+?)(?=\n\s*-\s+from:|\n\s+completeness|\Z)",
        yml_text, re.S)
    has_all_summaries = len(summaries) == len(pairs)

    # (c) Canonical enum
    canonical = {"clarification", "correction", "extension",
                 "reclassification", "breaking", "deprecation"}
    invalid = [ct for ct in change_types if ct not in canonical]
    enum_valid = not invalid

    e = Evidence(passed=chain_complete and has_all_summaries and enum_valid)
    chain_str = "→".join([p[0] for p in visited] + [cursor])
    e.markers.append(f"chain: {chain_str}")

    if chain_complete: e.markers.append(f"reaches {current}")
    else: e.gaps.append(f"stops at {cursor}, expected {current}")

    e.markers.append(f"{len(summaries)}/{len(pairs)} summaries")
    if not has_all_summaries: e.gaps.append("missing summaries")

    if enum_valid: e.markers.append("all change_types canonical")
    else: e.gaps.append(f"invalid change_types: {invalid}")
    return e


# ═══════════════════════════════════════════════════════════════════════
#  OPERATIONAL
# ═══════════════════════════════════════════════════════════════════════

def check_cc19(manifesto: str, spec: str) -> Evidence:
    """CC-19: declares field has quality guidance."""
    falsif = has(manifesto, "falsif")
    pos = has(manifesto, "idempotent") or has(manifesto, "reversible")
    neg = has(manifesto, "platitude") or has(manifesto, "reliable and maintainable")

    e = Evidence(passed=falsif and neg)
    if falsif: e.markers.append("falsifiability test")
    else: e.gaps.append("no falsifiability test")
    if pos: e.markers.append("positive example")
    else: e.gaps.append("no positive example")
    if neg: e.markers.append("negative example")
    else: e.gaps.append("no negative example")
    return e


def check_cc20(manifesto: str, spec: str) -> Evidence:
    """CC-20: Spec defines tooling surface."""
    sec_exists = bool(re.search(r"(?i)##\s+[IVXLC]*\.?\s*tooling", spec))
    ci = has(spec, "lintable in CI") or has(spec, "schema validation")
    scope = has(spec, "scope") and (has(spec, "query") or has(spec, "lookup") or has(spec, "governs"))
    hooks = has(spec, "on_intent_") and has(spec, "hooks")

    e = Evidence(passed=sec_exists and ci and hooks)
    for label, check in [("dedicated section", sec_exists), ("CI validation", ci),
                         ("scope lookup", scope), ("lifecycle hooks", hooks)]:
        (e.markers if check else e.gaps).append(label)
    return e


def check_cc21(manifesto: str, spec: str) -> Evidence:
    """CC-21: Next-touch rule has adoption ramp."""
    ramp = has(manifesto, "ramp") or has(manifesto, "advisory")
    enforce = has(manifesto, "gate becomes") or has(manifesto, "enforcement")
    cold = has(manifesto, "cold-start") or has(manifesto, "double burden") or \
           has(manifesto, "critical mass")

    e = Evidence(passed=ramp and enforce)
    if ramp: e.markers.append("ramp/advisory phase")
    else: e.gaps.append("no ramp described")
    if enforce: e.markers.append("enforcement transition")
    else: e.gaps.append("no enforcement transition")
    if cold: e.markers.append("cold-start rationale")
    else: e.gaps.append("no cold-start rationale")
    return e


def check_cc23(manifesto: str, spec: str) -> Evidence:
    """CC-23: Tension resolution staleness contract."""
    major = (
        bool(re.search(r"(?i)major.{0,80}(invalidat|re-evaluat|stale).*resolution", spec)) or
        bool(re.search(r"(?i)resolution.{0,80}(invalidat|re-evaluat|stale).{0,80}major", spec))
    )
    minor = (
        bool(re.search(r"(?i)minor.{0,80}review.{0,80}resolution", spec)) or
        bool(re.search(r"(?i)resolution.{0,80}minor.{0,80}review", spec))
    )
    patch = bool(re.search(r"(?i)patch.{0,80}(exclud|does not|no.{0,20}trigger)", spec))
    hook = has(spec, "on_tension_resolution_stale") or \
           bool(re.search(r"(?i)staleness.{0,40}hook", spec))

    e = Evidence(passed=major and minor)
    for label, check in [("MAJOR → invalidation", major), ("MINOR → review flag", minor),
                         ("PATCH excluded", patch), ("enforcement hook", hook)]:
        (e.markers if check else e.gaps).append(label)
    return e


def check_cc25(manifesto: str, spec: str) -> Evidence:
    """CC-25: Deprecation ceremonies defined."""
    notify = has(spec, "depends_on") and (has(spec, "notif") or has(spec, "downstream"))
    migration = (has(spec, "successor") or has(spec, "re-point")) and \
                (has(spec, "supersed") or has(spec, "residual"))
    grace = has(spec, "grace period") or has(spec, "deadline") or has(spec, "intent owner")
    unresolved = has(spec, "tension") and \
                 (has(spec, "unresolved") or has(spec, "zombie") or has(spec, "orphan"))

    e = Evidence(passed=notify and migration)
    for label, check in [("dependents notified", notify), ("migration path", migration),
                         ("grace period", grace), ("unresolved → tension", unresolved)]:
        (e.markers if check else e.gaps).append(label)
    return e


def check_cc26(manifesto: str, spec: str) -> Evidence:
    """CC-26: Failure mode catalogue."""
    sec = section(manifesto, r"how\s+this\s+fails")
    if not sec:
        return Evidence(passed=False, gaps=["no 'How This Fails' section"])

    performative = has(sec, "performative")
    bureaucratic = has(sec, "bureaucratic") or has(sec, "over-specification")
    drift = (has(sec, "drift") or has(sec, "blur") or
             has(sec, "no longer reflect") or has(sec, "nobody reads"))

    modes = re.findall(r"\*\*([^*]+)\*\*", sec)
    has_structure = (
        (has(sec, "remedy") or has(sec, "mitigation")) and
        (has(sec, "symptom") or has(sec, "easy to spot") or has(sec, "signal"))
    )

    e = Evidence(
        passed=performative and bureaucratic and drift and len(modes) >= 3 and has_structure
    )
    for label, check in [("performative", performative), ("bureaucratic", bureaucratic),
                         ("intent drift/blur", drift)]:
        (e.markers if check else e.gaps).append(label)
    e.markers.append(f"{len(modes)} named modes")
    if has_structure: e.markers.append("symptoms + remedies")
    else: e.gaps.append("missing symptoms/remedies structure")
    return e


# ═══════════════════════════════════════════════════════════════════════
#  DEFERRED
# ═══════════════════════════════════════════════════════════════════════

def check_cc22(manifesto: str, spec: str) -> Evidence:
    """CC-22: Cross-repo discovery protocol (deferred)."""
    mech = has(spec, "pull-based") or has(spec, "push-based") or has(spec, "central registry")
    notif = has(spec, "signal") or has(spec, "notification") or has(spec, "issue")
    fail = has(spec, "unacknowledged") or has(spec, "does not respond")

    e = Evidence(passed=mech and notif)
    for label, check in [("discovery mechanism", mech),
                         ("notification", notif), ("failure mode", fail)]:
        (e.markers if check else e.gaps).append(label)
    return e


def check_cc24(manifesto: str, spec: str) -> Evidence:
    """CC-24: Schema evolution semantics (deferred)."""
    ver = has(spec, "schema_version")
    schema_semver = (
        bool(re.search(r"(?i)schema.{0,120}(PATCH|MINOR|MAJOR).{0,60}(PATCH|MINOR|MAJOR)", spec)) or
        bool(re.search(r"(?i)(PATCH|MINOR|MAJOR).{0,60}schema.{0,60}(PATCH|MINOR|MAJOR)", spec))
    )
    migration = bool(re.search(r"(?i)schema.{0,80}migration.{0,80}(level|requirement|transform)", spec))

    e = Evidence(passed=ver and schema_semver)
    for label, check in [("schema_version field", ver),
                         ("PATCH/MINOR/MAJOR for schema", schema_semver),
                         ("migration requirements", migration)]:
        (e.markers if check else e.gaps).append(label)
    return e


# ── DISPATCH TABLE ────────────────────────────────────────────────────
# Maps criterion ID → check function. Used by conftest to parametrize.

CHECKS = {
    "CC-01": check_cc01,
    "CC-02": check_cc02,
    "CC-03": check_cc03,
    "CC-04": check_cc04,
    "CC-05": check_cc05,
    "CC-06": check_cc06,
    "CC-07": check_cc07,
    "CC-08": check_cc08,
    "CC-08a": check_cc08a,
    "CC-08b": check_cc08b,
    "CC-08c": check_cc08c,
    "CC-09": check_cc09,
    "CC-10": check_cc10,
    "CC-11": check_cc11,
    "CC-12": check_cc12,
    "CC-13": check_cc13,
    "CC-14": check_cc14,
    "CC-15": check_cc15,
    "CC-16": check_cc16,
    "CC-17": check_cc17,
    "CC-18": check_cc18,
    "CC-19": check_cc19,
    "CC-20": check_cc20,
    "CC-21": check_cc21,
    "CC-23": check_cc23,
    "CC-25": check_cc25,
    "CC-26": check_cc26,
    "CC-27": check_cc27,     # signature differs — handled in test
    "CC-22": check_cc22,
    "CC-24": check_cc24,
}
