#!/usr/bin/env python3
"""
IDF Lifecycle Hooks (CC-07, CC-20c)
====================================
Defines how lifecycle state transitions propagate.

States: proposed → active → evolving → superseded → residual
                                                  → retracted (terminal, from proposed only)

CC-23: Tension resolution staleness
  - MAJOR bump → invalidate resolutions (re-evaluate required)
  - MINOR bump → review flag (surfaced for human assessment)
  - PATCH bump → no action

CC-25: Deprecation ceremonies
  Step 1: Identify all intents with depends_on references
  Step 2: State migration path (re-point, drop, or acknowledge)
  Step 3: Grace period or deadline
  Step 4: Surface unresolved references as tensions
"""

import sys

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required.")
    sys.exit(1)


# ─── CC-07: Lifecycle State Machine ─────────────────────────────────

VALID_TRANSITIONS = {
    "proposed":   ["active", "retracted", "accepted"],
    "active":     ["evolving", "superseded", "residual", "deprecated"],
    "evolving":   ["active", "superseded", "residual"],
    "superseded": ["residual"],
    "residual":   [],          # terminal
    "retracted":  [],          # terminal
    "accepted":   [],          # terminal (decision-lifecycle)
    "deprecated": [],          # terminal (decision-lifecycle)
}


def validate_transition(current: str, target: str) -> tuple[bool, str]:
    """Check if a lifecycle transition is valid per CC-07."""
    if current not in VALID_TRANSITIONS:
        return False, f"Unknown state: {current}"
    allowed = VALID_TRANSITIONS[current]
    if target not in allowed:
        return False, (
            f"Invalid transition: {current} → {target}. "
            f"Allowed from {current}: {allowed}"
        )
    return True, f"OK: {current} → {target}"


# ─── CC-23: Staleness Detection ─────────────────────────────────────

def parse_semver(version: str) -> tuple[int, int, int]:
    parts = version.split(".")
    return int(parts[0]), int(parts[1]), int(parts[2])


def detect_staleness(old_version: str, new_version: str) -> str:
    """
    Determine staleness action for tension resolutions.
    Returns: 'invalidate', 'review', or 'none'
    """
    old = parse_semver(old_version)
    new = parse_semver(new_version)

    if new[0] > old[0]:
        return "invalidate"   # MAJOR bump → full re-evaluation
    elif new[1] > old[1]:
        return "review"       # MINOR bump → human review flag
    else:
        return "none"         # PATCH bump → no action


# ─── CC-25: Deprecation Ceremony ────────────────────────────────────

def deprecation_ceremony(intent_id: str, successor_id: str = None) -> dict:
    """
    Generate a deprecation ceremony checklist for a superseded/residual intent.
    Returns a structured checklist.
    """
    return {
        "intent_id": intent_id,
        "successor": successor_id,
        "steps": [
            {
                "step": 1,
                "action": "identify_dependents",
                "description": f"Find all intents with depends_on referencing '{intent_id}'",
                "status": "pending",
            },
            {
                "step": 2,
                "action": "state_migration_path",
                "description": (
                    f"Each dependent must: re-point to '{successor_id}', "
                    "drop the dependency, or acknowledge residual state"
                    if successor_id else
                    "Each dependent must: drop the dependency or acknowledge residual state"
                ),
                "status": "pending",
            },
            {
                "step": 3,
                "action": "define_grace_period",
                "description": "Set deadline for dependent migration (or delegate to intent owner)",
                "status": "pending",
            },
            {
                "step": 4,
                "action": "surface_unresolved",
                "description": "After grace period, surface unresolved downstream references as tensions",
                "status": "pending",
            },
        ],
    }


if __name__ == "__main__":
    # Quick demo
    print("=== Lifecycle Transition Validation (CC-07) ===")
    for curr, tgt in [("proposed", "active"), ("active", "retracted"), ("residual", "active")]:
        ok, msg = validate_transition(curr, tgt)
        print(f"  {'✓' if ok else '✗'} {msg}")

    print("\n=== Staleness Detection (CC-23) ===")
    for old, new in [("1.0.0", "2.0.0"), ("1.0.0", "1.1.0"), ("1.0.0", "1.0.1")]:
        action = detect_staleness(old, new)
        print(f"  {old} → {new}: {action}")

    print("\n=== Deprecation Ceremony (CC-25) ===")
    ceremony = deprecation_ceremony("intent-old-api", "intent-new-api")
    for step in ceremony["steps"]:
        print(f"  Step {step['step']}: {step['action']}")
        print(f"    {step['description']}")
