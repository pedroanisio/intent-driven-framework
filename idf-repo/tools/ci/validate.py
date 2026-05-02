#!/usr/bin/env python3
"""
IDF CI Validator — Tooling Surface (CC-20)
===========================================
Validates intent files against the IDF schema.

Contracts (per CC-20):
  (a) Schema validation: every intent YAML conforms to its type schema
  (b) Scope lookup: intents can be queried by file path
  (c) Lifecycle hooks: transitions propagate events

Usage:
    python validate.py [intents_dir]
"""

import sys
import glob
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip install pyyaml")
    sys.exit(1)


REQUIRED_FIELDS_COMMON = [
    "id", "version", "schema_version", "intent_type",
    "declares", "scope", "priority", "status", "confidence",
    "owner", "origin", "transition_log",
]

REQUIRED_CURRENT_REALITY = ["state", "status", "remaining_work", "last_assessed"]

VALID_ENUMS = {
    "change_type": [
        "clarification", "correction", "extension",
        "reclassification", "breaking", "deprecation",
        "MAJOR", "MINOR", "PATCH",
    ],
    "intent_type": ["aspirational", "achieved"],
    "priority": ["critical", "high", "medium", "low"],
    "status": [
        "proposed", "active", "evolving",
        "superseded", "residual", "retracted",
        "accepted", "deprecated",
    ],
    "confidence": ["high", "medium", "low"],
    "tier": ["core", "deferred"],
    "origin_type": [
        "engineering", "product", "incident", "discovery", "regulatory",
        "organizational", "devops", "ux", "data", "sre", "security",
    ],
    "origin_relationship": [
        "derived_from", "motivated_by", "constrained_by",
        "triggered_by", "discovered_in",
    ],
    "achieved_coverage": ["none", "minimal", "partial", "substantial", "full"],
}


class ValidationError:
    def __init__(self, file: str, field: str, message: str):
        self.file = file
        self.field = field
        self.message = message

    def __str__(self):
        return f"  [{self.file}] {self.field}: {self.message}"


def validate_intent(filepath: str) -> list[ValidationError]:
    """Validate a single intent YAML file."""
    errors = []
    path = Path(filepath)

    try:
        with open(path) as f:
            doc = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return [ValidationError(path.name, "yaml", f"Parse error: {e}")]

    if not doc or "intent" not in doc:
        return [ValidationError(path.name, "root", "Missing 'intent' key")]

    intent = doc["intent"]

    # ── Required fields ──
    for field in REQUIRED_FIELDS_COMMON:
        if field not in intent:
            errors.append(ValidationError(path.name, field, "Required field missing"))

    # ── Enum validation (CC-05) ──
    for field, valid in [
        ("intent_type", VALID_ENUMS["intent_type"]),
        ("priority", VALID_ENUMS["priority"]),
        ("status", VALID_ENUMS["status"]),
        ("confidence", VALID_ENUMS["confidence"]),
    ]:
        val = intent.get(field)
        if val and val not in valid:
            errors.append(ValidationError(
                path.name, field, f"Invalid value '{val}'. Must be one of: {valid}"
            ))

    # ── Origin validation ──
    origin = intent.get("origin", {})
    if origin:
        otype = origin.get("type")
        if otype and otype not in VALID_ENUMS["origin_type"]:
            errors.append(ValidationError(
                path.name, "origin.type",
                f"Invalid origin type '{otype}'. Must be one of: {VALID_ENUMS['origin_type']}"
            ))
        orel = origin.get("relationship")
        if orel and orel not in VALID_ENUMS["origin_relationship"]:
            errors.append(ValidationError(
                path.name, "origin.relationship",
                f"Invalid relationship '{orel}'. Must be one of: {VALID_ENUMS['origin_relationship']}"
            ))

    # ── Aspirational-specific: current_reality (CC-08) ──
    if intent.get("intent_type") == "aspirational":
        cr = intent.get("current_reality")
        if not cr:
            errors.append(ValidationError(
                path.name, "current_reality",
                "Aspirational intents must include current_reality block"
            ))
        else:
            for field in REQUIRED_CURRENT_REALITY:
                if field not in cr:
                    errors.append(ValidationError(
                        path.name, f"current_reality.{field}",
                        "Required field missing in current_reality"
                    ))

    # ── Declares quality hint (CC-19) ──
    declares = intent.get("declares", "")
    if declares and "TODO" in str(declares):
        errors.append(ValidationError(
            path.name, "declares",
            "WARNING: declares field still contains TODO placeholder"
        ))

    # ── Achieved coverage validation ──
    ac = intent.get("achieved_coverage")
    if ac and ac not in VALID_ENUMS["achieved_coverage"]:
        errors.append(ValidationError(
            path.name, "achieved_coverage",
            f"Invalid value '{ac}'. Must be one of: {VALID_ENUMS['achieved_coverage']}"
        ))

    # ── Transition log integrity (CC-27) ──
    tlog = intent.get("transition_log", [])
    if tlog:
        versions_seen = set()
        for entry in tlog:
            ct = entry.get("change_type", "")
            valid_ct = [
                "clarification", "correction", "extension",
                "reclassification", "breaking", "deprecation",
                "MAJOR", "MINOR", "PATCH",
            ]
            if ct and ct not in valid_ct:
                errors.append(ValidationError(
                    path.name, "transition_log.change_type",
                    f"Invalid change_type '{ct}'. Must be one of: {valid_ct}"
                ))
            frm = entry.get("from")
            to = entry.get("to")
            if frm:
                versions_seen.add(frm)
            if to:
                versions_seen.add(to)

    return errors


def validate_directory(intents_dir: str) -> int:
    """Validate all intent YAML files in a directory tree."""
    pattern = f"{intents_dir}/**/*.yml"
    files = glob.glob(pattern, recursive=True)

    if not files:
        print(f"No .yml files found in {intents_dir}")
        return 0

    total_errors = 0
    for filepath in sorted(files):
        errors = validate_intent(filepath)
        if errors:
            print(f"\n✗ {filepath}")
            for e in errors:
                print(f"  {e}")
            total_errors += len(errors)
        else:
            print(f"✓ {filepath}")

    print(f"\n{'─' * 50}")
    print(f"Files scanned: {len(files)}")
    print(f"Errors found:  {total_errors}")
    return total_errors


def scope_lookup(intents_dir: str, query_path: str) -> list[dict]:
    """
    CC-20(b): Query intents by file path.
    Returns all intents whose scope covers the given path.
    """
    results = []
    pattern = f"{intents_dir}/**/*.yml"
    for filepath in glob.glob(pattern, recursive=True):
        try:
            with open(filepath) as f:
                doc = yaml.safe_load(f)
            if not doc or "intent" not in doc:
                continue
            intent = doc["intent"]
            scope = intent.get("scope", {})
            all_paths = scope.get("primary", []) + scope.get("implicit", [])
            for p in all_paths:
                if p and query_path in str(p):
                    results.append({
                        "intent_id": intent.get("id"),
                        "file": filepath,
                        "matched_scope": p,
                    })
        except Exception:
            continue
    return results


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "intents"
    exit_code = validate_directory(target)
    sys.exit(1 if exit_code > 0 else 0)
