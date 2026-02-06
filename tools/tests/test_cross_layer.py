"""
CROSS-LAYER — verify YAML, Zod, and Lean agree on enums and versions.

These checks overlap with drift_check.py (Stage 0) but expressed as
pytest assertions for integration into the Stage 3 pipeline.
"""

import re
import pytest
from .helpers import parse_zod_enum_from_js, parse_lean_inductive


# Enum pairs: (label, zod_name, lean_name, alias_map)
# alias_map: {zod_value: lean_constructor} for known naming differences
ENUM_CROSS_REFS = [
    ("Status", "Status", "IntentStatus", {}),
    ("IntentType", "IntentType", "IntentType", {}),
    ("Priority", "Priority", "Priority", {}),
    ("Confidence", "Confidence", "Confidence", {}),
    ("AchievedCoverage", "AchievedCoverage", "AchievedCoverage", {}),
    ("OriginType", "OriginType", "OriginType", {}),
    ("OriginRelationship", "OriginRelationship", "OriginRelationship", {}),
    ("Tier", "Tier", "Tier", {}),
    ("FalsifiableClaimStatus", "FalsifiableClaimStatus", "FalsifiableClaimStatus", {}),
    ("TddIsomorphismStatus", "TddIsomorphismStatus", "TddIsomorphismStatus", {}),
    ("TensionStatus", "TensionStatus", "TensionStatus", {}),
    ("BoundaryType", "BoundaryType", "BoundaryType", {}),
]


class TestCrossLayer:
    """Enums and versions must agree across Zod and Lean."""

    @pytest.mark.cross_layer
    @pytest.mark.core
    @pytest.mark.parametrize(
        "label,zod_name,lean_name,aliases",
        [(e[0], e[1], e[2], e[3]) for e in ENUM_CROSS_REFS],
        ids=[e[0] for e in ENUM_CROSS_REFS],
    )
    def test_enum_consistency(self, schema_js_text, lean_text,
                               label, zod_name, lean_name, aliases):
        """CC-05: Enums match across Zod and Lean."""
        zod_vals = parse_zod_enum_from_js(schema_js_text, zod_name)
        lean_vals = parse_lean_inductive(lean_text, lean_name)

        if zod_vals is None:
            pytest.skip(f"Enum {zod_name} not found in schema.js")
        if lean_vals is None:
            pytest.skip(f"Inductive {lean_name} not found in Lean")

        # Normalize: apply aliases then lowercase comparison
        def normalize(vals, alias_map):
            return sorted(alias_map.get(v, v).lower().replace("_", "") for v in vals)

        zod_norm = normalize(zod_vals, aliases)
        lean_norm = normalize(lean_vals, {})

        assert zod_norm == lean_norm, (
            f"Enum drift for {label}:\n"
            f"  Zod  = {sorted(zod_vals)}\n"
            f"  Lean = {sorted(lean_vals)}"
        )

    @pytest.mark.cross_layer
    @pytest.mark.core
    def test_version_sync(self, root_intent, lean_text):
        """Root intent version matches Lean formalization."""
        m = re.search(
            r"def\s+root_meta_intent.*?version\s*:=\s*\.v\s+(\d+)\s+(\d+)\s+(\d+)",
            lean_text, re.DOTALL,
        )
        if not m:
            pytest.skip("root_meta_intent version not found in Lean")

        lean_ver = f"{m.group(1)}.{m.group(2)}.{m.group(3)}"
        yaml_ver = str(root_intent["version"])
        assert yaml_ver == lean_ver, (
            f"Version drift: YAML={yaml_ver}, Lean={lean_ver}"
        )

    @pytest.mark.cross_layer
    @pytest.mark.core
    def test_schema_version_sync(self, root_intent, lean_text):
        """Root intent schema_version matches Lean formalization."""
        m = re.search(
            r"def\s+root_meta_intent.*?schema_version\s*:=\s*some\s+\(\.v\s+(\d+)\s+(\d+)\s+(\d+)\)",
            lean_text, re.DOTALL,
        )
        if not m:
            pytest.skip("root_meta_intent schema_version not found in Lean")

        lean_sv = f"{m.group(1)}.{m.group(2)}.{m.group(3)}"
        yaml_sv = str(root_intent.get("schema_version", ""))
        assert yaml_sv == lean_sv, (
            f"Schema version drift: YAML={yaml_sv}, Lean={lean_sv}"
        )
