#!/usr/bin/env python3
"""
IDF SDLC v1.7.0 — Quick intent validator.
Validates a single intent YAML file against the v1.7.0 schema.

Usage: python validate_intent.py <path-to-intent.yml>
"""

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("pip install pyyaml")
    sys.exit(1)

REQUIRED = ["id", "version", "declares", "scope"]
FULL_REQUIRED = [
    "id", "version", "schema_version", "intent_type", "declares",
    "scope", "priority", "status", "confidence", "owner", "origin",
]

ENUMS = {
    "intent_type": ["aspirational", "achieved"],
    "priority": ["critical", "high", "medium", "low"],
    "status": ["proposed", "active", "evolving", "superseded", "residual", "retracted"],
    "confidence": ["high", "medium", "low"],
    "achieved_coverage": ["none", "minimal", "partial", "substantial", "full"],
    "origin_type": [
        "engineering", "product", "incident", "discovery", "regulatory",
        "organizational", "devops", "ux", "data", "sre", "security",
    ],
    "origin_relationship": [
        "derived_from", "motivated_by", "constrained_by",
        "triggered_by", "discovered_in",
    ],
    "change_type": [
        "clarification", "correction", "extension",
        "reclassification", "breaking", "deprecation",
        "MAJOR", "MINOR", "PATCH",
    ],
}


def validate(path):
    errors = []
    warnings = []

    try:
        doc = yaml.safe_load(Path(path).read_text())
    except Exception as e:
        return [f"YAML parse error: {e}"], []

    if not doc or "intent" not in doc:
        return ["Missing root 'intent' key"], []

    i = doc["intent"]

    # required fields
    for f in REQUIRED:
        if f not in i:
            errors.append(f"Missing required field: {f}")

    # enum checks
    for field, valid in ENUMS.items():
        val = i.get(field)
        if val and val not in valid:
            errors.append(f"{field}: '{val}' not in {valid}")

    # nested enum: origin.type, origin.relationship
    origin = i.get("origin", {})
    if isinstance(origin, dict):
        ot = origin.get("type")
        if ot and ot not in ENUMS["origin_type"]:
            errors.append(f"origin.type: '{ot}' not in {ENUMS['origin_type']}")
        orel = origin.get("relationship")
        if orel and orel not in ENUMS["origin_relationship"]:
            errors.append(f"origin.relationship: '{orel}' not in {ENUMS['origin_relationship']}")

    # CC-08: aspirational requires current_reality
    if i.get("intent_type") == "aspirational" and i.get("status") != "proposed":
        if not i.get("current_reality"):
            errors.append("Aspirational intent (non-proposed) requires current_reality block")
        else:
            cr = i["current_reality"]
            if not cr.get("state"):
                errors.append("current_reality.state is required and must be non-empty")

    # transition_log change_type check
    for entry in i.get("transition_log", []):
        ct = entry.get("change_type", "")
        if ct and ct not in ENUMS["change_type"]:
            errors.append(f"transition_log.change_type: '{ct}' not in {ENUMS['change_type']}")
        if not entry.get("summary", "").strip():
            warnings.append("transition_log entry has empty summary")

    # scope structure
    scope = i.get("scope")
    if isinstance(scope, dict):
        if not scope.get("primary"):
            warnings.append("scope.primary is empty")
    elif isinstance(scope, list):
        if not scope:
            warnings.append("scope is empty list")

    # warns
    if "TODO" in str(i.get("declares", "")):
        warnings.append("declares still contains TODO placeholder")

    for f in FULL_REQUIRED:
        if f not in i and f not in REQUIRED:
            warnings.append(f"Recommended field missing: {f}")

    return errors, warnings


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_intent.py <path-to-intent.yml>")
        sys.exit(1)

    path = sys.argv[1]
    errors, warnings = validate(path)

    if errors:
        print(f"FAIL: {path}")
        for e in errors:
            print(f"  ERROR: {e}")
    else:
        print(f"PASS: {path}")

    for w in warnings:
        print(f"  WARN: {w}")

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
