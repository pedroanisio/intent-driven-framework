"""
Evidence extraction — mechanical verification of YAML against criteria.

Each check_cc* function gathers evidence for one criterion. Returns an
Evidence object with pass/fail verdict and proof trail.

PARADIGM SHIFT: The old evidence.py checked prose markdown via regex.
This version checks parsed YAML dicts mechanically. The YAML IS the
specification. Evidence functions receive parsed dicts, not raw text.

For criteria that are fundamentally prose-level (CC-01, CC-02, CC-03),
the declares field and other string fields are checked for structural
markers. True semantic assessment is delegated to the NLP layer (Stage 4).
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Any

from .helpers import (
    has_key, get_nested, text_contains, any_text_contains,
    collect_ids, count_items, deep_text_scan,
    parse_zod_enum_from_js, parse_lean_inductive,
)


@dataclass
class Evidence:
    """Result of an evidence check."""
    passed: bool
    markers: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
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
        icon = "O" if self.skipped else ("+" if self.passed else "-")
        return f"{icon} {self.summary}"


# ═══════════════════════════════════════════════════════════════════
#  PHILOSOPHY — CC-01, CC-02, CC-03
# ═══════════════════════════════════════════════════════════════════

def check_cc01(root_intent: dict) -> Evidence:
    """CC-01: Manifesto states the problem it solves.

    In YAML mode: the declares field must contain language describing
    the problem that exists without the framework.
    """
    e = Evidence(passed=False)
    declares = root_intent.get("declares", "")

    if not declares or len(declares.strip()) < 50:
        e.gaps.append("declares field missing or too brief")
        return e

    # Problem indicators: language about what goes wrong without the framework
    problem_terms = ["degrade", "drift", "invisible", "governance"]
    found_terms = [t for t in problem_terms if t.lower() in declares.lower()]
    if found_terms:
        e.markers.append(f"problem language: {found_terms}")
    else:
        e.gaps.append("declares lacks problem-describing language")

    # Must describe a condition, not just a solution
    if any_text_contains(declares, "purpose", "intent", "goal"):
        e.markers.append("references purpose/intent domain")
    else:
        e.gaps.append("no reference to purpose domain")

    e.passed = len(found_terms) >= 2 and not e.gaps
    return e


def check_cc02(root_intent: dict) -> Evidence:
    """CC-02: Manifesto states the inversion explicitly.

    In YAML mode: design_stance or declares names old vs new orientation.
    """
    e = Evidence(passed=False)
    design_stance = root_intent.get("design_stance", "")
    declares = root_intent.get("declares", "")
    combined = f"{declares} {design_stance}"

    if not design_stance:
        e.gaps.append("design_stance field missing")
        return e

    # Old orientation vs new orientation
    has_old = any_text_contains(combined, "generalization", "abstracting")
    has_new = any_text_contains(combined, "instantiation", "domain-specific")

    if has_old:
        e.markers.append("old orientation named")
    else:
        e.gaps.append("old orientation not named")
    if has_new:
        e.markers.append("new orientation named")
    else:
        e.gaps.append("new orientation not named")

    e.passed = has_old and has_new
    return e


def check_cc03(root_intent: dict) -> Evidence:
    """CC-03: Every principle is named, numbered, and explained.

    In YAML mode: a principles array must exist with named, explained entries.
    """
    e = Evidence(passed=False)
    principles = root_intent.get("principles", [])

    if not isinstance(principles, list) or len(principles) == 0:
        e.gaps.append("no principles section in root intent")
        return e

    e.markers.append(f"{len(principles)} principles declared")

    # Each should have a name/title and explanation
    for i, p in enumerate(principles):
        if isinstance(p, dict):
            if not p.get("name") and not p.get("title"):
                e.gaps.append(f"principle {i}: missing name/title")
            if not p.get("explanation") and not p.get("rationale") and not p.get("body"):
                e.gaps.append(f"principle {i}: missing explanation")
        elif isinstance(p, str):
            if len(p.strip()) < 20:
                e.gaps.append(f"principle {i}: too brief (<20 chars)")

    e.passed = len(principles) >= 3 and not e.gaps
    return e


# ═══════════════════════════════════════════════════════════════════
#  MODEL — CC-04, CC-05, CC-06, CC-07, CC-08
# ═══════════════════════════════════════════════════════════════════

def check_cc04(schema_js_text: str) -> Evidence:
    """CC-04: Every first-class entity has a complete schema.

    Checks that schema.js defines schemas for the core entities.
    Maps conceptual entities to actual Zod schema names:
      intent → IntentSchema, transition → TransitionLogEntry,
      tension → Tension, manifest → CriteriaCategories.
    Note: 'decision' is implicit (serves_intent refs, no standalone schema).
    """
    e = Evidence(passed=False)

    entity_schemas = {
        "intent": r"const\s+IntentSchema\s*=\s*z\.",
        "transition": r"const\s+(?:Canonical)?TransitionLogEntry\s*=\s*z\.",
        "tension": r"const\s+Tension\s*=\s*z\.",
        "manifest": r"const\s+CriteriaCategories\s*=\s*z\.",
    }

    found = set()
    for entity, pattern in entity_schemas.items():
        if re.search(pattern, schema_js_text):
            found.add(entity)

    missing = set(entity_schemas.keys()) - found
    e.markers.append(f"entities found: {sorted(found)}")
    if missing:
        e.gaps.append(f"missing schemas: {sorted(missing)}")
    else:
        e.markers.append("all 4 core entity schemas present in Zod")
    e.markers.append("decision: implicit (serves_intent refs, no standalone schema)")

    e.passed = not missing
    return e


def check_cc05(root_intent_text: str, schema_js_text: str, lean_text: str) -> Evidence:
    """CC-05: Every enum field has all valid values listed (closed enums).

    Cross-checks enum sets between YAML comments, Zod, and Lean.
    """
    e = Evidence(passed=False)

    # Core enums to verify
    enum_checks = [
        ("Status", "IntentStatus"),
        ("IntentType", "IntentType"),
        ("Priority", "Priority"),
        ("Confidence", "Confidence"),
        ("AchievedCoverage", "AchievedCoverage"),
        ("OriginType", "OriginType"),
        ("OriginRelationship", "OriginRelationship"),
        ("Tier", "Tier"),
    ]

    all_match = True
    for zod_name, lean_name in enum_checks:
        zod_vals = parse_zod_enum_from_js(schema_js_text, zod_name)
        lean_vals = parse_lean_inductive(lean_text, lean_name)

        if zod_vals is None:
            e.gaps.append(f"{zod_name}: not found in Zod")
            all_match = False
            continue
        if lean_vals is None:
            e.gaps.append(f"{lean_name}: not found in Lean")
            all_match = False
            continue

        # Normalize: Lean constructors are lowercase, Zod values vary
        zod_normalized = sorted(v.lower().replace("_", "") for v in zod_vals)
        lean_normalized = sorted(v.lower().replace("_", "") for v in lean_vals)

        if zod_normalized == lean_normalized:
            e.markers.append(f"{zod_name}: {len(zod_vals)} values match")
        else:
            e.gaps.append(f"{zod_name} drift: Zod={sorted(zod_vals)}, Lean={sorted(lean_vals)}")
            all_match = False

    e.passed = all_match
    return e


def check_cc06(schema_js_text: str) -> Evidence:
    """CC-06: Every relationship between entities is bidirectionally defined.

    Checks that schema.js has cross-references between related entities.
    """
    e = Evidence(passed=False)

    # Forward refs (entity A → entity B)
    has_serves = "serves" in schema_js_text or "serves_intent" in schema_js_text
    has_origin = "origin" in schema_js_text and "ref" in schema_js_text
    has_scope = "scope" in schema_js_text and "primary" in schema_js_text
    has_depends = "depends_on" in schema_js_text

    if has_serves:
        e.markers.append("forward ref: serves/serves_intent")
    else:
        e.gaps.append("no serves relationship")
    if has_origin:
        e.markers.append("forward ref: origin.ref")
    else:
        e.gaps.append("no origin reference")
    if has_scope:
        e.markers.append("scope binding: primary")
    if has_depends:
        e.markers.append("dependency: depends_on")

    e.passed = has_serves and has_origin and has_scope
    return e


def check_cc07(root_intent_text: str, schema_js_text: str) -> Evidence:
    """CC-07: Intent lifecycle is complete — 6 states with transitions.

    Checks the Status enum contains all required lifecycle states.
    """
    e = Evidence(passed=False)
    required_states = {"proposed", "active", "evolving", "superseded", "residual", "retracted"}

    zod_vals = parse_zod_enum_from_js(schema_js_text, "Status")
    if zod_vals is None:
        e.gaps.append("Status enum not found in Zod")
        return e

    found = {v.lower() for v in zod_vals}
    missing = required_states - found

    e.markers.append(f"states: {sorted(found)}")
    if missing:
        e.gaps.append(f"missing states: {sorted(missing)}")
    else:
        e.markers.append("all 6 lifecycle states present")

    e.passed = not missing
    return e


def check_cc08(root_intent: dict, schema_js_text: str) -> Evidence:
    """CC-08: Both intent types (achieved/aspirational) have distinct schemas."""
    e = Evidence(passed=False)

    # IntentType enum
    zod_vals = parse_zod_enum_from_js(schema_js_text, "IntentType")
    if zod_vals and set(v.lower() for v in zod_vals) >= {"aspirational", "achieved"}:
        e.markers.append("IntentType enum: aspirational, achieved")
    else:
        e.gaps.append("IntentType enum missing or incomplete")

    # Root intent is aspirational with current_reality
    if root_intent.get("intent_type") == "aspirational":
        e.markers.append("root intent is aspirational")
    else:
        e.gaps.append("root intent not typed as aspirational")

    if has_key(root_intent, "current_reality"):
        e.markers.append("current_reality present on aspirational intent")
    else:
        e.gaps.append("current_reality missing on aspirational intent")

    # Zod schema has AspirationalIntent refinement
    if "AspirationalIntent" in schema_js_text or "aspirational" in schema_js_text.lower():
        e.markers.append("AspirationalIntent refinement in Zod")

    e.passed = not e.gaps
    return e


# ═══════════════════════════════════════════════════════════════════
#  CONFLICT — CC-08a, CC-08b, CC-08c
# ═══════════════════════════════════════════════════════════════════

def check_cc08a(root_intent: dict) -> Evidence:
    """CC-08a: Contradiction between active intents is detected and resolved.

    In YAML mode: tensions array is non-empty with resolution strategies.
    """
    e = Evidence(passed=False)
    tensions = root_intent.get("tensions", [])

    if not tensions:
        e.gaps.append("no tensions declared")
        return e

    e.markers.append(f"{len(tensions)} tensions declared")

    # Each tension should have resolution_strategy with type and rule
    for t in tensions:
        tid = t.get("id", "?")
        rs = t.get("resolution_strategy", {})
        if not rs.get("type"):
            e.gaps.append(f"{tid}: no resolution_strategy.type")
        if not rs.get("rule"):
            e.gaps.append(f"{tid}: no resolution_strategy.rule")
        if not t.get("resolution_owner"):
            e.gaps.append(f"{tid}: no resolution_owner")

    if not e.gaps:
        e.markers.append("all tensions have resolution strategies")

    e.passed = len(tensions) > 0 and not e.gaps
    return e


def check_cc08b(root_intent: dict) -> Evidence:
    """CC-08b: Transitions that would violate active intents are caught.

    Checks for pre-transition check contract in the YAML.
    """
    e = Evidence(passed=False)
    all_text = deep_text_scan(root_intent)

    has_check = any_text_contains(all_text, "checked before", "re-evaluated", "must be updated")
    has_block = any_text_contains(all_text, "blocked", "flagged", "stale")

    if has_check:
        e.markers.append("pre-transition check language found")
    else:
        e.gaps.append("no pre-transition check contract")

    if has_block:
        e.markers.append("blocking/flagging mechanism referenced")
    else:
        e.gaps.append("no blocking mechanism described")

    e.passed = has_check and has_block
    return e


def check_cc08c(root_intent: dict) -> Evidence:
    """CC-08c: Scope overlap between intents is detectable.

    Checks for scope overlap detection mechanism.
    """
    e = Evidence(passed=False)
    all_text = deep_text_scan(root_intent)

    has_overlap = any_text_contains(all_text, "scope overlap", "scope crossing", "overlapping scope")
    has_detection = any_text_contains(all_text, "heuristic", "detect", "identify overlap")
    has_resolution = any_text_contains(all_text, "tension", "serves relationship")

    if has_overlap:
        e.markers.append("scope overlap concept present")
    else:
        e.gaps.append("no scope overlap concept")
    if has_detection:
        e.markers.append("detection mechanism described")
    else:
        e.gaps.append("no detection mechanism")
    if has_resolution:
        e.markers.append("resolution path described")
    else:
        e.gaps.append("no resolution path for overlap")

    e.passed = has_overlap and has_detection
    return e


# ═══════════════════════════════════════════════════════════════════
#  STRUCTURE — CC-09, CC-10
# ═══════════════════════════════════════════════════════════════════

def check_cc09(root_intent: dict) -> Evidence:
    """CC-09: Repository structure is fully specified.

    Checks for directory tree documentation in the YAML.
    """
    e = Evidence(passed=False)
    all_text = deep_text_scan(root_intent)

    has_repo = any_text_contains(all_text, "_repo/", "repository structure")
    has_dirs = sum(1 for d in ["intents/", "transitions/", "tensions/", "decisions/"]
                   if d.lower() in all_text.lower())

    if has_repo:
        e.markers.append("_repo/ structure referenced")
    else:
        e.gaps.append("no _repo/ structure in YAML")

    e.markers.append(f"{has_dirs}/4 standard directories mentioned")
    if has_dirs < 3:
        e.gaps.append("fewer than 3 standard directories documented")

    e.passed = has_repo and has_dirs >= 3
    return e


def check_cc10(root_intent: dict) -> Evidence:
    """CC-10: A reader can create the _repo/ folder from docs alone.

    Checks for sufficient structure documentation to bootstrap.
    """
    e = Evidence(passed=False)
    all_text = deep_text_scan(root_intent)

    has_tree = any_text_contains(all_text, "_repo/")
    has_example = any_text_contains(all_text, "example", "template", "minimal")
    has_manifest = any_text_contains(all_text, "manifest.yaml", "manifest.yml")

    if has_tree:
        e.markers.append("_repo/ referenced")
    else:
        e.gaps.append("no _repo/ reference")
    if has_example:
        e.markers.append("example/template referenced")
    else:
        e.gaps.append("no example or template for bootstrapping")
    if has_manifest:
        e.markers.append("manifest file referenced")
    else:
        e.gaps.append("no manifest file reference")

    e.passed = has_tree and has_example and has_manifest
    return e


# ═══════════════════════════════════════════════════════════════════
#  EXTENSIBILITY — CC-11, CC-12
# ═══════════════════════════════════════════════════════════════════

def check_cc11(root_intent: dict, schema_js_text: str) -> Evidence:
    """CC-11: Plugin architecture defined with at least one example.

    Checks for plugin manifest schema and worked example.
    """
    e = Evidence(passed=False)

    # Plugin schema in Zod
    has_plugin_schema = "plugin" in schema_js_text.lower() and "manifest" in schema_js_text.lower()
    has_registry = "registry" in schema_js_text.lower() and "plugin" in schema_js_text.lower()

    # Worked example in YAML
    ext = root_intent.get("ext", {})
    has_example = bool(ext) and len(ext) > 0

    if has_plugin_schema:
        e.markers.append("plugin schema in Zod")
    else:
        e.gaps.append("no plugin manifest schema in Zod")
    if has_registry:
        e.markers.append("plugin registry in Zod")
    else:
        e.gaps.append("no plugin registry schema")
    if has_example:
        e.markers.append(f"ext: block with {len(ext)} namespace(s)")
    else:
        e.gaps.append("no ext: example in root intent")

    e.passed = has_plugin_schema and has_example
    return e


def check_cc12(root_intent: dict, schema_js_text: str) -> Evidence:
    """CC-12: Extension surface on core entities defined with semantics.

    Checks that ext: namespace is demonstrated in root intent.
    """
    e = Evidence(passed=False)

    # ext: in Zod schema
    has_ext_schema = "ext:" in schema_js_text or "ext" in schema_js_text
    if has_ext_schema:
        e.markers.append("ext field in Zod schema")
    else:
        e.gaps.append("no ext field in Zod schema")

    # ext: demonstrated in root intent
    ext = root_intent.get("ext", {})
    if ext and isinstance(ext, dict):
        namespaces = list(ext.keys())
        e.markers.append(f"ext namespaces: {namespaces}")
        # Check at least one has content
        if any(ext[ns] for ns in namespaces):
            e.markers.append("ext namespace has content")
        else:
            e.gaps.append("ext namespaces are empty")
    else:
        e.gaps.append("no ext: block in root intent")

    e.passed = has_ext_schema and bool(ext)
    return e


# ═══════════════════════════════════════════════════════════════════
#  ADOPTION — CC-13, CC-14, CC-15
# ═══════════════════════════════════════════════════════════════════

def check_cc13(root_intent: dict) -> Evidence:
    """CC-13: Adoption sequence is ordered and actionable.

    Checks for numbered adoption steps.
    """
    e = Evidence(passed=False)

    # Look for adoption_sequence or similar structured field
    seq = root_intent.get("adoption_sequence", root_intent.get("adoption_steps", []))
    if isinstance(seq, list) and len(seq) >= 3:
        e.markers.append(f"{len(seq)} adoption steps")
        e.passed = True
        return e

    # Fallback: scan all text for numbered steps
    all_text = deep_text_scan(root_intent)
    numbered = re.findall(r"(?:^|\n)\s*\d+\.\s+", all_text)

    if numbered:
        e.markers.append(f"{len(numbered)} numbered items in text")
    else:
        e.gaps.append("no numbered adoption sequence")

    e.passed = len(numbered) >= 5
    return e


def check_cc14(root_intent: dict) -> Evidence:
    """CC-14: Legacy strategy does not require comprehensive audit.

    Checks for anti-audit adoption language.
    """
    e = Evidence(passed=False)
    all_text = deep_text_scan(root_intent)

    has_anti_audit = any_text_contains(
        all_text,
        "without", "audit"
    ) or any_text_contains(
        all_text,
        "without understanding", "existing"
    ) or any_text_contains(
        all_text,
        "aspirational intent can be declared"
    )

    has_provides_e = False
    provides = root_intent.get("provides", [])
    for p in provides:
        if isinstance(p, dict) and "audit" in str(p.get("description", "")).lower():
            has_provides_e = True
            break

    if has_anti_audit:
        e.markers.append("anti-audit language found")
    else:
        e.gaps.append("no anti-audit adoption language")

    if has_provides_e:
        e.markers.append("provides item addresses audit-free adoption")
    else:
        e.gaps.append("no provides item for audit-free adoption")

    e.passed = has_anti_audit or has_provides_e
    return e


def check_cc15(root_intent: dict) -> Evidence:
    """CC-15: At least three practical entry points described.

    Checks for pain-first, next-touch, amnesty (or similar).
    """
    e = Evidence(passed=False)
    all_text = deep_text_scan(root_intent)

    strategies = {
        "pain-first": any_text_contains(all_text, "pain-first") or any_text_contains(all_text, "pain first"),
        "next-touch": any_text_contains(all_text, "next-touch") or any_text_contains(all_text, "next touch"),
        "amnesty": any_text_contains(all_text, "amnesty"),
    }

    found = [name for name, present in strategies.items() if present]
    e.markers.append(f"{len(found)} entry points: {found}")

    if len(found) < 3:
        e.gaps.append(f"need >= 3 entry points, found {len(found)}")

    e.passed = len(found) >= 3
    return e


# ═══════════════════════════════════════════════════════════════════
#  SELF-SUFFICIENCY — CC-16, CC-17
# ═══════════════════════════════════════════════════════════════════

def check_cc16(root_intent: dict) -> Evidence:
    """CC-16: No principle references concepts defined only outside the document.

    Checks that the YAML is self-contained (no external-only references).
    """
    e = Evidence(passed=False)
    all_text = deep_text_scan(root_intent)

    # Check for external references that indicate non-self-sufficiency
    has_external_urls = bool(re.search(r"https?://", all_text))
    has_see_external = any_text_contains(all_text, "see external", "refer to external")

    if has_external_urls:
        e.gaps.append("external URLs found in YAML")
    else:
        e.markers.append("no external URLs")

    if has_see_external:
        e.gaps.append("explicit external references")
    else:
        e.markers.append("no 'see external' references")

    # Positive check: key concepts are defined within
    defines_intent = any_text_contains(all_text, "intent", "first-class entity")
    defines_lifecycle = any_text_contains(all_text, "lifecycle", "proposed", "active")
    defines_tension = any_text_contains(all_text, "tension", "resolution")

    if defines_intent and defines_lifecycle and defines_tension:
        e.markers.append("core concepts defined internally")
    else:
        e.gaps.append("some core concepts may not be defined internally")

    e.passed = not has_see_external and defines_intent and defines_lifecycle
    return e


def check_cc17(root_intent: dict) -> Evidence:
    """CC-17: The daily practice is stated concretely.

    In YAML mode: operational_cycle.phases provides behavioral instructions.
    """
    e = Evidence(passed=False)
    phases = get_nested(root_intent, "operational_cycle", "phases")

    if not phases or not isinstance(phases, list):
        e.gaps.append("no operational_cycle.phases")
        return e

    e.markers.append(f"{len(phases)} operational phases defined")

    behaviors = {
        "declare": False,
        "satisfy": False,
        "evolve": False,
    }

    for phase in phases:
        pid = phase.get("id", "")
        has_rule = bool(phase.get("rule"))
        has_outputs = bool(phase.get("outputs"))

        if pid == "red" and has_rule:
            behaviors["declare"] = True
        elif pid == "green" and has_rule:
            behaviors["satisfy"] = True
        elif pid == "refactor" and has_rule:
            behaviors["evolve"] = True

        if has_rule:
            e.markers.append(f"phase {pid}: has rule")
        if has_outputs:
            e.markers.append(f"phase {pid}: has outputs")

    found = [k for k, v in behaviors.items() if v]
    missing = [k for k, v in behaviors.items() if not v]

    if missing:
        e.gaps.append(f"missing behavioral rules: {missing}")

    e.passed = len(found) >= 3 and not e.gaps
    return e


# ═══════════════════════════════════════════════════════════════════
#  SELF-CONFORMANCE — CC-18, CC-27
# ═══════════════════════════════════════════════════════════════════

def check_cc18(root_intent: dict) -> Evidence:
    """CC-18: Root intent conforms to its own model.

    The bootstrap criterion. Verifies required fields, current_reality,
    scope coverage, and schema_version.
    """
    e = Evidence(passed=False)

    # (a) current_reality present and non-empty
    cr = root_intent.get("current_reality")
    if cr and isinstance(cr, dict) and cr.get("state"):
        e.markers.append("current_reality present with state")
    else:
        e.gaps.append("current_reality missing or empty")

    # (b) scope covers artifacts
    scope = root_intent.get("scope", {})
    if scope.get("primary") and len(scope["primary"]) > 0:
        e.markers.append(f"scope.primary: {len(scope['primary'])} entries")
    else:
        e.gaps.append("scope.primary empty or missing")

    # (c) required fields populated
    required = [
        "id", "version", "declares", "intent_type", "status",
        "priority", "confidence", "owner", "origin",
    ]
    missing = [f for f in required if not root_intent.get(f)]
    if not missing:
        e.markers.append(f"all {len(required)} required fields populated")
    else:
        e.gaps.append(f"missing required fields: {missing}")

    # (d) schema_version present
    if root_intent.get("schema_version"):
        e.markers.append(f"schema_version: {root_intent['schema_version']}")
    else:
        e.gaps.append("schema_version missing")

    e.passed = not e.gaps
    return e


def check_cc27(root_intent: dict) -> Evidence:
    """CC-27: Transition log is complete and consistent.

    Verifies continuous chain, summaries, and canonical change_types.
    """
    e = Evidence(passed=False)

    log = root_intent.get("transition_log", [])
    if not log:
        e.gaps.append("no transition_log entries")
        return e

    current_version = str(root_intent.get("version", ""))
    if not current_version:
        e.gaps.append("cannot determine current version")
        return e

    # Normalize field names (handles both from_version/to_version and from/to)
    def get_from(entry):
        return str(entry.get("from_version") or entry.get("from", ""))

    def get_to(entry):
        return str(entry.get("to_version") or entry.get("to", ""))

    # (a) Continuous chain
    chain = {get_from(entry): get_to(entry) for entry in log}
    # Also try reversed chain (newest-first ordering)
    reverse_chain = {get_to(entry): get_from(entry) for entry in log}

    # Find chain start (a version that appears as 'from' but not as 'to')
    all_froms = {get_from(e) for e in log}
    all_tos = {get_to(e) for e in log}
    starts = all_froms - all_tos

    chain_ok = False
    chain_str = ""
    for start in starts:
        visited = [start]
        cursor = start
        while cursor in chain:
            cursor = chain[cursor]
            visited.append(cursor)
        if cursor == current_version:
            chain_ok = True
            chain_str = " -> ".join(visited)
            break

    if chain_ok:
        e.markers.append(f"chain: {chain_str}")
    else:
        e.gaps.append(f"chain does not reach {current_version}")

    # (b) Summaries/reasons exist
    missing_summary = []
    for entry in log:
        has_text = entry.get("summary") or entry.get("reason")
        if not has_text:
            missing_summary.append(get_to(entry))

    if not missing_summary:
        e.markers.append(f"{len(log)}/{len(log)} entries have summaries")
    else:
        e.gaps.append(f"entries missing summaries: {missing_summary}")

    # (c) Canonical change_type enum
    canonical = {
        "clarification", "correction", "extension",
        "reclassification", "breaking", "deprecation",
        "MAJOR", "MINOR", "PATCH",
    }
    invalid = []
    for entry in log:
        ct = entry.get("change_type")
        if ct and ct not in canonical:
            invalid.append(ct)

    if not invalid:
        e.markers.append("all change_types canonical")
    else:
        e.gaps.append(f"invalid change_types: {invalid}")

    e.passed = not e.gaps
    return e


# ═══════════════════════════════════════════════════════════════════
#  OPERATIONAL — CC-19, CC-20, CC-21, CC-23, CC-25, CC-26
# ═══════════════════════════════════════════════════════════════════

def check_cc19(root_intent: dict) -> Evidence:
    """CC-19: The declares field has quality guidance.

    Checks that declares is substantive and falsifiable, not generic.
    """
    e = Evidence(passed=False)
    declares = root_intent.get("declares", "")

    if not declares:
        e.gaps.append("no declares field")
        return e

    # Length check: non-trivial
    if len(declares.strip()) >= 100:
        e.markers.append(f"declares: {len(declares.strip())} chars (substantive)")
    else:
        e.gaps.append("declares too brief (<100 chars)")

    # Falsifiability check: contains testable claims
    all_text = deep_text_scan(root_intent)
    has_falsifiable = any_text_contains(all_text, "falsif")
    has_claims = bool(root_intent.get("falsifiable_claims"))

    if has_falsifiable:
        e.markers.append("falsifiability language present")
    if has_claims:
        e.markers.append(f"{len(root_intent['falsifiable_claims'])} falsifiable claims")
    if not has_falsifiable and not has_claims:
        e.gaps.append("no falsifiability apparatus")

    # Anti-generic check: not a platitude
    generic_patterns = [
        "reliable and maintainable",
        "high quality",
        "best practices",
        "world class",
    ]
    is_generic = any(p in declares.lower() for p in generic_patterns)
    if is_generic:
        e.gaps.append("declares contains generic language")
    else:
        e.markers.append("declares is non-generic")

    e.passed = not e.gaps
    return e


def check_cc20(root_intent: dict, schema_js_text: str) -> Evidence:
    """CC-20: The spec defines a tooling surface.

    Checks for CI validation, scope lookup, and lifecycle hook contracts.
    """
    e = Evidence(passed=False)

    # CI validation contract
    has_ci = "validate" in schema_js_text.lower() and "export" in schema_js_text.lower()
    if has_ci:
        e.markers.append("validation functions in schema.js")
    else:
        e.gaps.append("no CI validation contract")

    # Scope lookup
    has_scope_lookup = "scope" in schema_js_text.lower() and "lookup" in schema_js_text.lower()
    has_scope_validation = "validateScope" in schema_js_text or "Scope" in schema_js_text
    if has_scope_lookup or has_scope_validation:
        e.markers.append("scope validation/lookup in schema.js")
    else:
        e.gaps.append("no scope lookup contract")

    # Lifecycle hooks
    has_hooks = any_text_contains(schema_js_text, "on_intent_", "lifecycle", "hook")
    all_text = deep_text_scan(root_intent)
    yaml_hooks = any_text_contains(all_text, "hook", "lifecycle event", "on_intent")

    if has_hooks or yaml_hooks:
        e.markers.append("lifecycle hooks referenced")
    else:
        e.gaps.append("no lifecycle hook contract")

    e.passed = not e.gaps
    return e


def check_cc21(root_intent: dict) -> Evidence:
    """CC-21: The next-touch rule has an adoption ramp.

    Checks for advisory phase, enforcement transition, cold-start rationale.
    """
    e = Evidence(passed=False)
    all_text = deep_text_scan(root_intent)

    has_ramp = any_text_contains(all_text, "ramp", "advisory", "grace period")
    has_enforce = any_text_contains(all_text, "enforcement", "gate becomes", "blocking")
    has_cold = any_text_contains(all_text, "cold-start", "cold start", "double burden", "critical mass")

    if has_ramp:
        e.markers.append("ramp/advisory phase described")
    else:
        e.gaps.append("no adoption ramp described")
    if has_enforce:
        e.markers.append("enforcement transition described")
    else:
        e.gaps.append("no enforcement transition")
    if has_cold:
        e.markers.append("cold-start rationale addressed")
    else:
        e.gaps.append("no cold-start rationale")

    e.passed = has_ramp and has_enforce
    return e


def check_cc23(root_intent: dict) -> Evidence:
    """CC-23: Tension resolution staleness is contractually defined.

    Checks that tensions have staleness_threshold_days and last_reviewed.
    """
    e = Evidence(passed=False)
    tensions = root_intent.get("tensions", [])

    if not tensions:
        e.gaps.append("no tensions declared")
        return e

    all_have_staleness = True
    all_have_review = True

    for t in tensions:
        tid = t.get("id", "?")
        if not t.get("staleness_threshold_days"):
            e.gaps.append(f"{tid}: no staleness_threshold_days")
            all_have_staleness = False
        if not t.get("last_reviewed"):
            e.gaps.append(f"{tid}: no last_reviewed")
            all_have_review = False

    if all_have_staleness:
        e.markers.append("all tensions have staleness_threshold_days")
    if all_have_review:
        e.markers.append("all tensions have last_reviewed")

    e.passed = all_have_staleness and all_have_review
    return e


def check_cc25(root_intent: dict) -> Evidence:
    """CC-25: Deprecation ceremonies for superseded/residual intents defined.

    Checks for downstream notification, migration path, grace period.
    """
    e = Evidence(passed=False)
    all_text = deep_text_scan(root_intent)

    has_notify = any_text_contains(all_text, "downstream", "dependents", "notify", "notification")
    has_migration = any_text_contains(all_text, "migration", "successor", "re-point")
    has_grace = any_text_contains(all_text, "grace period", "deadline")
    has_ceremony = any_text_contains(all_text, "deprecat", "supersed", "residual")

    if has_ceremony:
        e.markers.append("deprecation/supersession language present")
    else:
        e.gaps.append("no deprecation ceremony language")

    if has_notify:
        e.markers.append("downstream notification referenced")
    else:
        e.gaps.append("no downstream notification contract")

    if has_migration:
        e.markers.append("migration path referenced")
    else:
        e.gaps.append("no migration path described")

    if has_grace:
        e.markers.append("grace period referenced")
    else:
        e.gaps.append("no grace period defined")

    e.passed = has_ceremony and has_notify and has_migration
    return e


def check_cc26(root_intent: dict) -> Evidence:
    """CC-26: The manifesto names its own failure modes.

    Checks failure_modes array: >= 3, each with name/diagnostic/mitigation.
    """
    e = Evidence(passed=False)
    fms = root_intent.get("failure_modes", [])

    e.markers.append(f"{len(fms)} failure modes")

    if len(fms) < 3:
        e.gaps.append(f"need >= 3 failure modes, found {len(fms)}")
        return e

    # Check for the three required archetypes
    names = [fm.get("name", "").lower() for fm in fms]
    has_performative = any("performative" in n for n in names)
    has_overspec = any("over-specification" in n or "bureaucrat" in n for n in names)
    has_cargo = any("cargo" in n or "green-wash" in n or "drift" in n for n in names)

    if has_performative:
        e.markers.append("performative intent mode")
    else:
        e.gaps.append("no performative intent failure mode")
    if has_overspec:
        e.markers.append("over-specification mode")
    else:
        e.gaps.append("no over-specification failure mode")
    if has_cargo:
        e.markers.append("cargo-cult/green-washing mode")
    else:
        e.gaps.append("no cargo-cult or green-washing failure mode")

    # Check structure: each has name, diagnostic, mitigation
    for fm in fms:
        fid = fm.get("id", "?")
        if not fm.get("diagnostic") or len(str(fm["diagnostic"])) < 20:
            e.gaps.append(f"{fid}: diagnostic too brief")
        if not fm.get("mitigation") or len(str(fm["mitigation"])) < 20:
            e.gaps.append(f"{fid}: mitigation too brief")

    e.passed = not e.gaps
    return e


# ═══════════════════════════════════════════════════════════════════
#  DEFERRED — CC-22, CC-24
# ═══════════════════════════════════════════════════════════════════

def check_cc22(root_intent: dict) -> Evidence:
    """CC-22: Cross-repo intent dependencies have a discovery protocol."""
    e = Evidence(passed=False)
    all_text = deep_text_scan(root_intent)

    has_discovery = any_text_contains(all_text, "discovery", "cross-repo")
    has_notification = any_text_contains(all_text, "notification", "signal")

    if has_discovery:
        e.markers.append("cross-repo discovery referenced")
    else:
        e.gaps.append("no cross-repo discovery protocol")
    if has_notification:
        e.markers.append("notification mechanism referenced")
    else:
        e.gaps.append("no notification mechanism")

    e.passed = has_discovery and has_notification
    return e


def check_cc24(root_intent: dict) -> Evidence:
    """CC-24: The core schema has evolution semantics."""
    e = Evidence(passed=False)

    has_schema_version = bool(root_intent.get("schema_version"))
    all_text = deep_text_scan(root_intent)
    has_schema_semver = any_text_contains(all_text, "schema_version", "schema change")
    has_migration = any_text_contains(all_text, "migration", "schema evolution")

    if has_schema_version:
        e.markers.append(f"schema_version: {root_intent.get('schema_version')}")
    else:
        e.gaps.append("no schema_version field")
    if has_schema_semver:
        e.markers.append("schema versioning referenced")
    else:
        e.gaps.append("no schema versioning semantics")
    if has_migration:
        e.markers.append("migration semantics referenced")
    else:
        e.gaps.append("no migration semantics")

    e.passed = has_schema_version and has_schema_semver and has_migration
    return e
