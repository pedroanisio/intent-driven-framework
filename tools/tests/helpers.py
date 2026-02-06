"""
Shared helpers for YAML-native evidence extraction.

These replace the old prose-regex helpers. They operate on parsed
Python dicts from PyYAML, not raw markdown text.
"""

from __future__ import annotations
import re
from typing import Any


# ── Dict traversal ───────────────────────────────────────────────

def has_key(d: dict, *keys: str) -> bool:
    """Check if a nested key path exists in a dict."""
    current = d
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return False
        current = current[key]
    return True


def get_nested(d: dict, *keys: str, default=None) -> Any:
    """Get a nested value from a dict by key path."""
    current = d
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
    return current


# ── Text helpers ─────────────────────────────────────────────────

def text_contains(text: str | None, *phrases: str) -> bool:
    """Case-insensitive check that text contains ALL given phrases."""
    if text is None:
        return False
    lower = text.lower()
    return all(p.lower() in lower for p in phrases)


def any_text_contains(text: str | None, *phrases: str) -> bool:
    """Case-insensitive check that text contains ANY given phrase."""
    if text is None:
        return False
    lower = text.lower()
    return any(p.lower() in lower for p in phrases)


# ── Collection helpers ───────────────────────────────────────────

def collect_ids(items: list[dict], id_field: str = "id") -> set[str]:
    """Collect all id values from a list of dicts."""
    if not isinstance(items, list):
        return set()
    return {item[id_field] for item in items if isinstance(item, dict) and id_field in item}


def count_items(d: dict, key: str) -> int:
    """Count items in a list field, or 0 if missing/not a list."""
    val = d.get(key, [])
    return len(val) if isinstance(val, list) else 0


# ── Deep text scan ───────────────────────────────────────────────

def deep_text_scan(obj: Any) -> str:
    """Recursively collect all string values from a nested structure.

    Returns a single concatenated string of all text content,
    useful for keyword scanning across an entire YAML structure.
    """
    parts = []
    if isinstance(obj, str):
        parts.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            parts.append(deep_text_scan(v))
    elif isinstance(obj, list):
        for item in obj:
            parts.append(deep_text_scan(item))
    return " ".join(parts)


# ── Cross-layer parsing ─────────────────────────────────────────

def parse_zod_enum_from_js(js_text: str, enum_name: str) -> list[str] | None:
    """Extract enum values from a Zod z.enum([...]) definition in JS text."""
    pattern = rf"(?:const|let|var)\s+{re.escape(enum_name)}\s*=\s*z\.enum\(\[(.*?)\]\)"
    m = re.search(pattern, js_text, re.DOTALL)
    if not m:
        return None
    raw = m.group(1)
    return [v.strip().strip("'\"") for v in raw.split(",") if v.strip().strip("'\"")]


def parse_lean_inductive(lean_text: str, type_name: str) -> list[str] | None:
    """Extract constructor names from a Lean 4 inductive type.

    Handles both multi-line and single-line formats:
        inductive TypeName where
          | constructor1 | constructor2 | constructor3
          deriving ...
    """
    pattern = rf"inductive\s+{re.escape(type_name)}\s+where\s*\n(.*?)deriving"
    m = re.search(pattern, lean_text, re.DOTALL)
    if not m:
        return None
    raw = m.group(1)
    constructors = []
    # Split on | and extract constructor names
    for part in re.split(r"\|", raw):
        part = part.strip()
        if not part or part.startswith("--"):
            continue
        # First word is the constructor name; skip type annotations
        token = part.split()[0].split(":")[0].strip()
        # Strip Lean 4 guillemet escaping: «none» → none
        clean = token.strip("«»")
        if clean and clean.isidentifier() and not clean.startswith("--"):
            constructors.append(clean)
    return constructors if constructors else None
