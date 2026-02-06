"""
PROSE-YAML CONSISTENCY — the prose manifesto must not drift from the YAML.

The YAML is authoritative. The prose is a derived rendering. These tests
verify structural and content consistency between the two artifacts.
"""

import re
import pytest


class TestProseConsistency:
    """Verify prose/intent-manifesto.md is consistent with root intent YAML."""

    @pytest.mark.prose
    @pytest.mark.core
    def test_prose_version_matches_yaml(self, root_intent, prose_manifesto_text):
        """Prose mentions the same version as the YAML."""
        yaml_version = str(root_intent["version"])
        assert yaml_version in prose_manifesto_text, (
            f"Prose does not mention YAML version {yaml_version}"
        )

    @pytest.mark.prose
    @pytest.mark.core
    def test_prose_declares_matches_yaml(self, root_intent, prose_manifesto_text):
        """Key phrases from the YAML declares field appear in prose."""
        declares = root_intent.get("declares", "")
        # Extract key phrases that MUST appear in any faithful rendering
        key_phrases = [
            "first-class entity",
            "purpose governance model",
            "domain is a parameter",
        ]
        missing = [p for p in key_phrases if p.lower() not in prose_manifesto_text.lower()]
        assert not missing, (
            f"Prose missing key declares phrases: {missing}"
        )

    @pytest.mark.prose
    @pytest.mark.core
    def test_prose_provides_coverage(self, root_intent, prose_manifesto_text):
        """All 6 provides items are mentioned in prose."""
        provides = root_intent.get("provides", [])
        assert len(provides) >= 6, f"Expected >= 6 provides items, got {len(provides)}"

        missing = []
        for p in provides:
            pid = p.get("id", "")
            # Check for the provides ID (e.g., "provides-a") or a key phrase
            desc = p.get("description", "")
            # Extract first few significant words
            desc_words = desc.strip().split()[:5]
            desc_fragment = " ".join(desc_words)
            if pid not in prose_manifesto_text and desc_fragment not in prose_manifesto_text:
                missing.append(pid)

        assert not missing, (
            f"Prose missing provides items: {missing}"
        )

    @pytest.mark.prose
    @pytest.mark.core
    def test_prose_tensions_coverage(self, root_intent, prose_manifesto_text):
        """All tension IDs (T-01 through T-05) appear in prose."""
        tensions = root_intent.get("tensions", [])
        missing = []
        for t in tensions:
            tid = t.get("id", "")
            if tid and tid not in prose_manifesto_text:
                missing.append(tid)
        assert not missing, (
            f"Prose missing tension IDs: {missing}"
        )

    @pytest.mark.prose
    @pytest.mark.core
    def test_prose_falsifiable_claims_coverage(self, root_intent, prose_manifesto_text):
        """All FC IDs (FC-01 through FC-08) appear in prose."""
        claims = root_intent.get("falsifiable_claims", [])
        missing = []
        for fc in claims:
            fid = fc.get("id", "")
            if fid and fid not in prose_manifesto_text:
                missing.append(fid)
        assert not missing, (
            f"Prose missing falsifiable claim IDs: {missing}"
        )

    @pytest.mark.prose
    @pytest.mark.core
    def test_prose_failure_modes_coverage(self, root_intent, prose_manifesto_text):
        """All FM IDs (FM-01 through FM-06) appear in prose."""
        fms = root_intent.get("failure_modes", [])
        missing = []
        for fm in fms:
            fid = fm.get("id", "")
            if fid and fid not in prose_manifesto_text:
                missing.append(fid)
        assert not missing, (
            f"Prose missing failure mode IDs: {missing}"
        )

    @pytest.mark.prose
    @pytest.mark.core
    def test_prose_operational_cycle_phases(self, prose_manifesto_text):
        """Red/Green/Refactor phases are all described in prose."""
        phases = ["Red", "Green", "Refactor"]
        lower = prose_manifesto_text.lower()
        missing = [p for p in phases if p.lower() not in lower]
        assert not missing, (
            f"Prose missing operational cycle phases: {missing}"
        )

    @pytest.mark.prose
    @pytest.mark.core
    def test_prose_transition_log_coverage(self, root_intent, prose_manifesto_text):
        """All version transitions from the log are mentioned in prose."""
        log = root_intent.get("transition_log", [])
        missing = []
        for entry in log:
            from_v = str(entry.get("from_version") or entry.get("from", ""))
            to_v = str(entry.get("to_version") or entry.get("to", ""))
            # Check that the transition is mentioned (either as "X -> Y" or both versions)
            if to_v not in prose_manifesto_text:
                missing.append(f"{from_v} -> {to_v}")
        assert not missing, (
            f"Prose missing transitions: {missing}"
        )

    @pytest.mark.prose
    @pytest.mark.core
    def test_prose_has_derivation_markers(self, prose_manifesto_text):
        """Each major section has a <!-- source: ... --> derivation marker."""
        required_sources = [
            "intent.declares",
            "intent.provides",
            "intent.design_stance",
            "intent.operational_cycle",
            "intent.current_reality",
            "intent.tensions",
            "intent.falsifiable_claims",
            "intent.failure_modes",
            "intent.transition_log",
            "intent.ext",
        ]
        markers_found = re.findall(r"<!--\s*source:\s*([^>]+?)\s*-->", prose_manifesto_text)
        markers_text = " ".join(markers_found).lower()

        missing = []
        for src in required_sources:
            # Check the key part (after "intent.")
            key = src.split(".")[-1]
            if key not in markers_text:
                missing.append(src)

        assert not missing, (
            f"Prose missing derivation markers: {missing}\n"
            f"Found markers: {markers_found}"
        )

    @pytest.mark.prose
    @pytest.mark.core
    def test_prose_no_claims_beyond_yaml(self, root_intent, prose_manifesto_text):
        """No FC/FM/T IDs in prose that don't exist in YAML (anti-hallucination)."""
        # Collect all IDs from YAML
        yaml_fc_ids = {fc["id"] for fc in root_intent.get("falsifiable_claims", []) if "id" in fc}
        yaml_fm_ids = {fm["id"] for fm in root_intent.get("failure_modes", []) if "id" in fm}
        yaml_t_ids = {t["id"] for t in root_intent.get("tensions", []) if "id" in t}

        # Find all IDs in prose
        prose_fc_ids = set(re.findall(r"\bFC-\d+\b", prose_manifesto_text))
        prose_fm_ids = set(re.findall(r"\bFM-\d+\b", prose_manifesto_text))
        prose_t_ids = set(re.findall(r"\bT-\d+\b", prose_manifesto_text))

        extra_fc = prose_fc_ids - yaml_fc_ids
        extra_fm = prose_fm_ids - yaml_fm_ids
        extra_t = prose_t_ids - yaml_t_ids

        hallucinations = []
        if extra_fc:
            hallucinations.append(f"FC IDs in prose but not YAML: {extra_fc}")
        if extra_fm:
            hallucinations.append(f"FM IDs in prose but not YAML: {extra_fm}")
        if extra_t:
            hallucinations.append(f"T IDs in prose but not YAML: {extra_t}")

        assert not hallucinations, (
            f"Prose contains IDs not in YAML:\n  " + "\n  ".join(hallucinations)
        )
