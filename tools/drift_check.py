#!/usr/bin/env python3
"""
Cross-layer drift detector for the Intent Framework.

The same data lives in up to 5 representations:
  1. IDF (YAML)         — source of truth
  2. Lean proofs        — formal encoding
  3. Zod schema (JS)    — runtime validation
  4. Pytest evidence    — prose checks
  5. README.md          — human summary

This script reads the IDF as canonical and compares against the other
layers. Any discrepancy is a drift. Exits non-zero if drift is found.

Usage:
  python tools/drift_check.py              # from repo root
  python tools/drift_check.py --verbose    # show all comparisons
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────

ROOT = Path(__file__).parent.parent
IDF_PATH = ROOT / "criteria" / "intent-driven-framework-definition.yml"
SDLC_INTENT_PATH = ROOT / "criteria" / "intent-idf-sdlc-v1.7.0.yml"
SDLC_INIT_PATH = ROOT / "prose" / "tools" / "idf-sdlc-v1.7.0-init.py"
LEAN_PATH = ROOT / "lean" / "IntentDrivenFramework.lean"
SCHEMA_PATH = ROOT / "tools" / "schema.js"
README_PATH = ROOT / "README.md"

VERBOSE = "--verbose" in sys.argv


# ── Helpers ──────────────────────────────────────────────────────

class Drift:
    def __init__(self):
        self.issues: list[str] = []

    def add(self, layer: str, detail: str):
        self.issues.append(f"  [{layer}] {detail}")

    def ok(self) -> bool:
        return len(self.issues) == 0


def info(msg: str):
    if VERBOSE:
        print(f"  · {msg}")


# ── YAML parsing (minimal, no PyYAML dependency) ────────────────

def parse_idf_falsifiable_claims(text: str) -> dict[str, str]:
    """Extract FC id → status from YAML. Simple regex, no library needed."""
    claims = {}
    for m in re.finditer(
        r"-\s+id:\s+(FC-\d+)\s*\n(?:.*?\n)*?\s+status:\s+(\S+)",
        text,
    ):
        claims[m.group(1)] = m.group(2)
    return claims


def parse_idf_version(text: str) -> str | None:
    m = re.search(r"^\s+version:\s+(\d+\.\d+\.\d+)\s*$", text, re.MULTILINE)
    return m.group(1) if m else None


def parse_idf_schema_version(text: str) -> str | None:
    m = re.search(r"^\s+schema_version:\s+(\d+\.\d+\.\d+)\s*$", text, re.MULTILINE)
    return m.group(1) if m else None


def parse_init_constant(text: str, name: str) -> str | None:
    m = re.search(rf"^{name}\s*=\s*\"(\d+\.\d+\.\d+)\"\s*$", text, re.MULTILINE)
    return m.group(1) if m else None


def parse_init_doc_version(text: str) -> str | None:
    m = re.search(r"Intent Driven Framework v(\d+\.\d+\.\d+)", text)
    return m.group(1) if m else None


def parse_init_sdlc_version(text: str) -> str | None:
    m = re.search(r"IDF SDLC v(\d+\.\d+\.\d+)", text)
    return m.group(1) if m else None


def parse_init_enums(text: str) -> dict[str, list[str]] | None:
    m = re.search(r"ENUMS\s*=\s*\{(.*?)\n\}\s*", text, re.DOTALL)
    if not m:
        return None
    block = m.group(1)
    enums: dict[str, list[str]] = {}
    key_re = re.compile(r"^\s*\"([a-zA-Z_]+)\"\s*:\s*\[(.*?)\]\s*,?\s*$", re.MULTILINE | re.DOTALL)
    for km in key_re.finditer(block):
        key = km.group(1)
        raw = km.group(2)
        vals = [v.strip().strip("'\"") for v in raw.split(",") if v.strip()]
        enums[key] = vals
    return enums if enums else None


def parse_init_directories(text: str) -> list[str] | None:
    m = re.search(r"DIRECTORIES\s*=\s*\[(.*?)\n\]\s*", text, re.DOTALL)
    if not m:
        return None
    block = m.group(1)
    return [
        v.strip().strip("'\"")
        for v in re.findall(r"\"([^\"]+)\"|'([^']+)'", block)
        for v in v if v
    ]


def parse_intent_template_block(text: str) -> str | None:
    m = re.search(r"def\s+intent_template\(.*?\):\s*.*?return\s+\"\\n\"\.join\(lines\)", text, re.DOTALL)
    if not m:
        return None
    return m.group(0)


def parse_idf_provides(text: str) -> dict[str, list[str]]:
    """Extract provides id → tested_by list."""
    provides = {}
    for m in re.finditer(
        r"-\s+id:\s+(provides-[a-z])\s*\n(?:.*?\n)*?\s+tested_by:\s+\[([^\]]*)\]",
        text,
    ):
        refs = [r.strip().strip("'\"") for r in m.group(2).split(",") if r.strip()]
        provides[m.group(1)] = refs
    return provides


def parse_idf_transition_log(text: str) -> list[tuple[str, str]]:
    """Extract (from_version, to_version) pairs."""
    entries = []
    for m in re.finditer(
        r'from_version:\s*"?(\d+\.\d+\.\d+)"?\s*\n\s*to_version:\s*"?(\d+\.\d+\.\d+)"?',
        text,
    ):
        entries.append((m.group(1), m.group(2)))
    return entries


# ── Lean extraction ──────────────────────────────────────────────

def parse_lean_fc_statuses(text: str) -> dict[str, str]:
    """Extract FC id → status from root_fc_list in Lean."""
    claims = {}
    for m in re.finditer(
        r'id\s*:=\s*"(FC-\d+)".*?status\s*:=\s*\.(\w+)',
        text,
        re.DOTALL,
    ):
        claims[m.group(1)] = m.group(2)
    return claims


def parse_lean_version(text: str, ident: str) -> str | None:
    """Extract version from a named def (e.g. root_meta_intent)."""
    pattern = rf"def\s+{ident}.*?version\s*:=\s*\.v\s+(\d+)\s+(\d+)\s+(\d+)"
    m = re.search(pattern, text, re.DOTALL)
    return f"{m.group(1)}.{m.group(2)}.{m.group(3)}" if m else None


def parse_lean_schema_version(text: str, ident: str) -> str | None:
    pattern = rf"def\s+{ident}.*?schema_version\s*:=\s*some\s+\(\.v\s+(\d+)\s+(\d+)\s+(\d+)\)"
    m = re.search(pattern, text, re.DOTALL)
    return f"{m.group(1)}.{m.group(2)}.{m.group(3)}" if m else None


def parse_lean_provides_tested_by(text: str) -> dict[str, list[str]]:
    """Extract provides id → tested_by from root_provides_list."""
    provides = {}
    for m in re.finditer(
        r'id\s*:=\s*"(provides-[a-z])".*?tested_by\s*:=\s*\[([^\]]*)\]',
        text,
        re.DOTALL,
    ):
        refs = [r.strip().strip('"') for r in m.group(2).split(",") if r.strip().strip('"')]
        provides[m.group(1)] = refs
    return provides


def parse_lean_transition_log(text: str, ident: str) -> list[tuple[str, str]]:
    """Extract transition (from, to) pairs from a named log def."""
    block_match = re.search(
        rf"def\s+{ident}\s*:.*?\[(.*?)\n\]",
        text,
        re.DOTALL,
    )
    if not block_match:
        return []
    block = block_match.group(1)
    entries = []
    for m in re.finditer(
        r"from_version\s*:=\s*\.v\s+(\d+)\s+(\d+)\s+(\d+).*?to_version\s*:=\s*\.v\s+(\d+)\s+(\d+)\s+(\d+)",
        block,
        re.DOTALL,
    ):
        fv = f"{m.group(1)}.{m.group(2)}.{m.group(3)}"
        tv = f"{m.group(4)}.{m.group(5)}.{m.group(6)}"
        entries.append((fv, tv))
    return entries


# ── Zod schema extraction ───────────────────────────────────────

def parse_zod_enum(text: str, name: str) -> list[str] | None:
    pattern = rf"const\s+{name}\s*=\s*z\.enum\(\[(.*?)\]\)"
    m = re.search(pattern, text, re.DOTALL)
    if not m:
        return None
    return [v.strip().strip("'\"") for v in m.group(1).split(",") if v.strip().strip("'\"")]


def parse_lean_enum(text: str, name: str) -> list[str] | None:
    """Extract constructor names from a Lean inductive."""
    pattern = rf"inductive\s+{name}\s+where\s*\n(.*?)deriving"
    m = re.search(pattern, text, re.DOTALL)
    if not m:
        return None
    raw = m.group(1)
    # Strip comment lines
    lines = [ln for ln in raw.split("\n") if not ln.strip().startswith("--")]
    cleaned = " ".join(lines)
    # Split on | and extract constructor names (handle «guillemets»)
    constructors = []
    for part in re.split(r"\|", cleaned):
        for token in part.strip().split():
            clean = token.strip().strip("«»")
            if clean:
                constructors.append(clean)
                break
    return constructors


# ── README extraction ────────────────────────────────────────────

def parse_readme_fc_table(text: str) -> dict[str, str]:
    """Extract FC id → status from the markdown table."""
    claims = {}
    for m in re.finditer(
        r"\|\s*(FC-\d+)\s*\|.*?\|\s*`(\w+)`\s*\|",
        text,
    ):
        claims[m.group(1)] = m.group(2)
    return claims


def parse_readme_fc_count(text: str) -> str | None:
    m = re.search(r"makes\s+(\w+)\s+falsifiable\s+claims", text)
    return m.group(1) if m else None


# ── Comparisons ──────────────────────────────────────────────────

def check_fc_statuses(drift: Drift, idf: dict, lean: dict, readme: dict):
    all_ids = sorted(set(idf) | set(lean) | set(readme))
    for fc_id in all_ids:
        idf_status = idf.get(fc_id)
        lean_status = lean.get(fc_id)
        readme_status = readme.get(fc_id)

        if idf_status and lean_status and idf_status != lean_status:
            drift.add("Lean", f"{fc_id} status: IDF={idf_status}, Lean={lean_status}")
        if idf_status and readme_status and idf_status != readme_status:
            drift.add("README", f"{fc_id} status: IDF={idf_status}, README={readme_status}")
        if fc_id in idf and fc_id not in lean:
            drift.add("Lean", f"{fc_id} exists in IDF but missing from Lean root_fc_list")
        if fc_id in idf and fc_id not in readme:
            drift.add("README", f"{fc_id} exists in IDF but missing from README FC table")

        info(f"{fc_id}: IDF={idf_status} Lean={lean_status} README={readme_status}")


def check_versions(drift: Drift, idf_text: str, lean_text: str):
    idf_ver = parse_idf_version(idf_text)
    lean_ver = parse_lean_version(lean_text, "root_meta_intent")
    if idf_ver and lean_ver and idf_ver != lean_ver:
        drift.add("Lean", f"version: IDF={idf_ver}, Lean root_meta_intent={lean_ver}")
    info(f"version: IDF={idf_ver} Lean={lean_ver}")

    idf_sv = parse_idf_schema_version(idf_text)
    lean_sv = parse_lean_schema_version(lean_text, "root_meta_intent")
    if idf_sv and lean_sv and idf_sv != lean_sv:
        drift.add("Lean", f"schema_version: IDF={idf_sv}, Lean={lean_sv}")
    info(f"schema_version: IDF={idf_sv} Lean={lean_sv}")


def check_provides(drift: Drift, idf: dict, lean: dict):
    all_ids = sorted(set(idf) | set(lean))
    for pid in all_ids:
        idf_refs = idf.get(pid, [])
        lean_refs = lean.get(pid, [])
        if sorted(idf_refs) != sorted(lean_refs):
            drift.add("Lean", f"{pid} tested_by: IDF={idf_refs}, Lean={lean_refs}")
        info(f"{pid}: IDF={idf_refs} Lean={lean_refs}")


def check_transition_log(drift: Drift, idf_entries: list, lean_entries: list, label: str):
    if len(idf_entries) != len(lean_entries):
        drift.add("Lean", f"{label}: IDF has {len(idf_entries)} entries, Lean has {len(lean_entries)}")
        return
    for i, (idf_e, lean_e) in enumerate(zip(idf_entries, lean_entries)):
        if idf_e != lean_e:
            drift.add("Lean", f"{label}[{i}]: IDF={idf_e[0]}→{idf_e[1]}, Lean={lean_e[0]}→{lean_e[1]}")
    info(f"{label}: {len(idf_entries)} IDF entries, {len(lean_entries)} Lean entries")


# Known name mappings: Zod name → Lean name (for values that can't be
# valid Lean identifiers, e.g. MAJOR is uppercase)
ENUM_ALIASES: dict[str, dict[str, str]] = {
    "ChangeType": {"MAJOR": "major_bump", "MINOR": "minor_bump", "PATCH": "patch_bump"},
}

ENUM_PAIRS = [
    ("Status", "IntentStatus"),
    ("IntentType", "IntentType"),
    ("Priority", "Priority"),
    ("Confidence", "Confidence"),
    ("ChangeType", "ChangeType"),
    ("AchievedCoverage", "AchievedCoverage"),
    ("OriginType", "OriginType"),
    ("OriginRelationship", "OriginRelationship"),
    ("Tier", "Tier"),
    ("FalsifiableClaimStatus", "FalsifiableClaimStatus"),
    ("TddIsomorphismStatus", "TddIsomorphismStatus"),
    ("TensionStatus", "TensionStatus"),
    ("BoundaryType", "BoundaryType"),
]


def check_enums(drift: Drift, zod_text: str, lean_text: str):
    for zod_name, lean_name in ENUM_PAIRS:
        zod_vals = parse_zod_enum(zod_text, zod_name)
        lean_vals = parse_lean_enum(lean_text, lean_name)
        if zod_vals is None:
            info(f"enum {zod_name}: not found in Zod")
            continue
        if lean_vals is None:
            info(f"enum {lean_name}: not found in Lean")
            continue
        # Apply known aliases: normalize Zod names to Lean names
        aliases = ENUM_ALIASES.get(zod_name, {})
        normalized_zod = sorted(aliases.get(v, v) for v in zod_vals)
        if normalized_zod != sorted(lean_vals):
            drift.add("Zod↔Lean", f"enum {zod_name}: Zod={sorted(zod_vals)}, Lean={sorted(lean_vals)}")
        info(f"enum {zod_name}: Zod={len(zod_vals)} vals, Lean={len(lean_vals)} vals")


def check_readme_fc_count(drift: Drift, idf_fcs: dict, readme_text: str):
    word = parse_readme_fc_count(readme_text)
    if word is None:
        return
    word_to_num = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    }
    num = word_to_num.get(word)
    if num is not None and num != len(idf_fcs):
        drift.add("README", f"FC count: says '{word}' ({num}), IDF has {len(idf_fcs)}")
    info(f"README FC count word: '{word}', IDF count: {len(idf_fcs)}")


def check_sdlc_init_versions(drift: Drift, sdlc_text: str, init_text: str):
    sdlc_version = parse_idf_version(sdlc_text)
    sdlc_schema_version = parse_idf_schema_version(sdlc_text)
    init_framework = parse_init_constant(init_text, "FRAMEWORK_VERSION")
    init_schema = parse_init_constant(init_text, "SCHEMA_VERSION")
    init_sdlc_version = parse_init_sdlc_version(init_text)

    if sdlc_version and init_framework and sdlc_version != init_framework:
        drift.add("SDLC Init", f"FRAMEWORK_VERSION {init_framework} != criteria version {sdlc_version}")
    if sdlc_schema_version and init_schema and sdlc_schema_version != init_schema:
        drift.add("SDLC Init", f"SCHEMA_VERSION {init_schema} != criteria schema_version {sdlc_schema_version}")
    if init_sdlc_version and sdlc_version and init_sdlc_version != sdlc_version:
        drift.add("SDLC Init", f"docstring SDLC v{init_sdlc_version} != criteria version {sdlc_version}")


def check_sdlc_init_enums(drift: Drift, init_text: str, zod_text: str):
    init_enums = parse_init_enums(init_text)
    if not init_enums:
        drift.add("SDLC Init", "ENUMS block missing or unparsable")
        return

    enum_map = {
        "change_type": "ChangeType",
        "origin_type": "OriginType",
        "origin_relationship": "OriginRelationship",
        "priority": "Priority",
        "confidence": "Confidence",
        "status": "Status",
        "tier": "Tier",
        "achieved_coverage": "AchievedCoverage",
        "intent_type": "IntentType",
    }

    for init_name, zod_name in enum_map.items():
        init_vals = init_enums.get(init_name)
        zod_vals = parse_zod_enum(zod_text, zod_name)
        if not init_vals:
            drift.add("SDLC Init", f"ENUMS.{init_name} missing")
            continue
        if not zod_vals:
            drift.add("SDLC Init", f"Zod enum {zod_name} missing")
            continue
        if sorted(init_vals) != sorted(zod_vals):
            drift.add(
                "SDLC Init",
                f"ENUMS.{init_name} != Zod {zod_name} "
                f"(init={sorted(init_vals)}, zod={sorted(zod_vals)})",
            )


def check_sdlc_init_directories(drift: Drift, init_text: str):
    dirs = parse_init_directories(init_text)
    if dirs is None:
        drift.add("SDLC Init", "DIRECTORIES block missing or unparsable")
        return
    required = [
        "prose", "criteria", "schemas", "tools", "lean",
        "intents", "tensions", "decisions", "transitions",
        "plugins", "tests", "docs",
    ]
    missing = [r for r in required if r not in dirs]
    if missing:
        drift.add("SDLC Init", f"DIRECTORIES missing required entries: {', '.join(missing)}")


def check_sdlc_init_templates(drift: Drift, init_text: str):
    block = parse_intent_template_block(init_text)
    if not block:
        drift.add("SDLC Init", "intent_template definition missing or unparsable")
        return
    required_snippets = [
        "intent:",
        "id:",
        "version:",
        "schema_version:",
        "intent_type:",
        "declares:",
        "current_reality:",
        "scope:",
        "priority:",
        "status:",
        "confidence:",
        "owner:",
        "origin:",
        "serves:",
        "dependencies:",
        "transition_log:",
    ]
    missing = [s for s in required_snippets if s not in block]
    if missing:
        drift.add("SDLC Init", f"intent_template missing required fields: {', '.join(missing)}")


# ── Main ─────────────────────────────────────────────────────────

def main():
    drift = Drift()

    # Load files
    missing = []
    for path, label in [
        (IDF_PATH, "IDF"), (LEAN_PATH, "Lean"),
        (SDLC_INTENT_PATH, "SDLC intent"), (SDLC_INIT_PATH, "SDLC init"),
        (SCHEMA_PATH, "schema.js"), (README_PATH, "README"),
    ]:
        if not path.exists():
            missing.append(f"{label}: {path}")
    if missing:
        print("Missing files:")
        for m in missing:
            print(f"  {m}")
        sys.exit(2)

    idf_text = IDF_PATH.read_text()
    sdlc_text = SDLC_INTENT_PATH.read_text()
    sdlc_init_text = SDLC_INIT_PATH.read_text()
    lean_text = LEAN_PATH.read_text()
    zod_text = SCHEMA_PATH.read_text()
    readme_text = README_PATH.read_text()

    # ── 1. FC statuses ───────────────────────────────────────────
    print("Checking FC statuses (IDF → Lean, README)...")
    idf_fcs = parse_idf_falsifiable_claims(idf_text)
    lean_fcs = parse_lean_fc_statuses(lean_text)
    readme_fcs = parse_readme_fc_table(readme_text)
    check_fc_statuses(drift, idf_fcs, lean_fcs, readme_fcs)

    # ── 2. Versions ──────────────────────────────────────────────
    print("Checking versions (IDF → Lean)...")
    check_versions(drift, idf_text, lean_text)

    # ── 3. Provides cross-refs ───────────────────────────────────
    print("Checking provides tested_by (IDF → Lean)...")
    idf_provides = parse_idf_provides(idf_text)
    lean_provides = parse_lean_provides_tested_by(lean_text)
    check_provides(drift, idf_provides, lean_provides)

    # ── 4. Transition log ────────────────────────────────────────
    print("Checking transition log (IDF → Lean)...")
    idf_log = parse_idf_transition_log(idf_text)
    lean_log = parse_lean_transition_log(lean_text, "root_intent_log")
    # IDF log is newest-first, Lean is oldest-first — reverse IDF
    check_transition_log(drift, list(reversed(idf_log)), lean_log, "root transition_log")

    # ── 5. Enums ─────────────────────────────────────────────────
    print("Checking enums (Zod ↔ Lean)...")
    check_enums(drift, zod_text, lean_text)

    # ── 6. README FC count ───────────────────────────────────────
    print("Checking README FC count...")
    check_readme_fc_count(drift, idf_fcs, readme_text)

    # ── 7. SDLC init script versions ─────────────────────────────
    print("Checking SDLC init script versions...")
    check_sdlc_init_versions(drift, sdlc_text, sdlc_init_text)

    # ── 8. SDLC init enums ───────────────────────────────────────
    print("Checking SDLC init enums (vs Zod)...")
    check_sdlc_init_enums(drift, sdlc_init_text, zod_text)

    # ── 9. SDLC init directories ─────────────────────────────────
    print("Checking SDLC init directories...")
    check_sdlc_init_directories(drift, sdlc_init_text)

    # ── 10. SDLC init intent template ────────────────────────────
    print("Checking SDLC init intent template...")
    check_sdlc_init_templates(drift, sdlc_init_text)

    # ── Report ───────────────────────────────────────────────────
    print()
    if drift.ok():
        print("✅ No drift detected across layers.")
        return 0
    else:
        print(f"❌ {len(drift.issues)} drift(s) found:")
        for issue in drift.issues:
            print(issue)
        return 1


if __name__ == "__main__":
    sys.exit(main())
