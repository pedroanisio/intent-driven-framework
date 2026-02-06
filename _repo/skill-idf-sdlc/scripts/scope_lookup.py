#!/usr/bin/env python3
"""
IDF SDLC v1.7.0 — Scope lookup.
Given a file path, returns all intents whose scope covers it.

Usage: python scope_lookup.py <intents-dir> <query-path>
"""

import sys
import glob
import fnmatch
from pathlib import Path

try:
    import yaml
except ImportError:
    print("pip install pyyaml")
    sys.exit(1)


def lookup(intents_dir, query_path):
    matches = []
    for filepath in glob.glob(f"{intents_dir}/**/*.yml", recursive=True) + glob.glob(f"{intents_dir}/**/*.yaml", recursive=True):
        try:
            doc = yaml.safe_load(Path(filepath).read_text())
        except Exception:
            continue
        if not doc or "intent" not in doc:
            continue
        i = doc["intent"]
        scope = i.get("scope", {})
        if isinstance(scope, dict):
            patterns = scope.get("primary", []) + scope.get("implicit", [])
        elif isinstance(scope, list):
            patterns = scope
        else:
            continue

        for pattern in patterns:
            if not pattern:
                continue
            if fnmatch.fnmatch(query_path, pattern) or query_path.startswith(pattern.rstrip("*/")):
                matches.append({
                    "intent_id": i.get("id", "?"),
                    "file": filepath,
                    "pattern": pattern,
                    "specificity": len(pattern),
                })
                break

    matches.sort(key=lambda m: m["specificity"], reverse=True)
    return matches


def main():
    if len(sys.argv) < 3:
        print("Usage: python scope_lookup.py <intents-dir> <query-path>")
        sys.exit(1)

    intents_dir, query_path = sys.argv[1], sys.argv[2]
    results = lookup(intents_dir, query_path)

    if results:
        print(f"Intents governing: {query_path}")
        for r in results:
            print(f"  {r['intent_id']} (scope: {r['pattern']}) — {r['file']}")
    else:
        print(f"GAP: No intent governs {query_path}")
        print("  Consider declaring one (next-touch rule).")

    sys.exit(0)


if __name__ == "__main__":
    main()
