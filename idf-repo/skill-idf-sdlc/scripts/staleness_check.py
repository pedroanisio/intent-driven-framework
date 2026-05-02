#!/usr/bin/env python3
"""
IDF SDLC v1.7.0 — Tension resolution staleness checker.
Checks whether a version bump on an intent invalidates any tension resolutions.

Usage: python staleness_check.py <tensions-dir> <intent-id> <old-version> <new-version>
"""

import sys
import glob
from pathlib import Path

try:
    import yaml
except ImportError:
    print("pip install pyyaml")
    sys.exit(1)


def bump_level(old, new):
    o = [int(x) for x in old.split("-")[0].split(".")]
    n = [int(x) for x in new.split("-")[0].split(".")]
    if n[0] > o[0]:
        return "MAJOR"
    elif n[1] > o[1]:
        return "MINOR"
    return "PATCH"


def check(tensions_dir, intent_id, old_ver, new_ver):
    level = bump_level(old_ver, new_ver)
    results = []

    for path in glob.glob(f"{tensions_dir}/**/*.yml", recursive=True) + glob.glob(f"{tensions_dir}/**/*.yaml", recursive=True):
        try:
            doc = yaml.safe_load(Path(path).read_text())
        except Exception:
            continue
        t = doc.get("tension", {})
        between = t.get("between", [])
        refs = [b.get("intent_id", "") for b in between if isinstance(b, dict)]
        if intent_id not in refs:
            continue

        res = t.get("resolution", t.get("current_resolution", {}))
        applies_to = res.get("applies_to", [])
        tid = t.get("id", Path(path).stem)

        if level == "MAJOR":
            results.append(("BLOCK", tid, path, f"MAJOR bump invalidates resolution (applies_to: {applies_to})"))
        elif level == "MINOR":
            results.append(("REVIEW", tid, path, f"MINOR bump — review resolution (applies_to: {applies_to})"))
        else:
            results.append(("OK", tid, path, "PATCH bump — no action needed"))

    return level, results


def main():
    if len(sys.argv) < 5:
        print("Usage: python staleness_check.py <tensions-dir> <intent-id> <old-version> <new-version>")
        sys.exit(1)

    tensions_dir, intent_id, old_ver, new_ver = sys.argv[1:5]
    level, results = check(tensions_dir, intent_id, old_ver, new_ver)

    print(f"Bump: {old_ver} -> {new_ver} ({level})")
    print(f"Intent: {intent_id}")
    print()

    blocked = False
    for action, tid, path, msg in results:
        icon = {"BLOCK": "BLOCK", "REVIEW": "REVIEW", "OK": "OK"}.get(action, "?")
        print(f"  [{icon}] {tid}: {msg}")
        if action == "BLOCK":
            blocked = True

    if not results:
        print("  No tensions reference this intent.")

    sys.exit(1 if blocked else 0)


if __name__ == "__main__":
    main()
