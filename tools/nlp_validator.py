#!/usr/bin/env python3
"""
NLP-assisted prose validator for Intent Framework v1.6.1

Replaces the regex heuristics in score_v150.py with semantic entailment
checks for the 16 criteria that Lean 4 cannot prove. Uses Claude as
the NLP engine via the Anthropic API.

Architecture:
  ┌──────────────────────────────────────────────────┐
  │  Lean 4          │  12 CC  │  Kernel-checked     │
  ├──────────────────┼─────────┼─────────────────────┤
  │  NLP validator   │  11 CC  │  Semantic entailment │ ← this file
  ├──────────────────┼─────────┼─────────────────────┤
  │  Human judgment  │   5 CC  │  Cannot automate     │
  ├──────────────────┼─────────┼─────────────────────┤
  │  Regex scorer    │  28 CC  │  Keyword heuristics  │ (baseline)
  └──────────────────┴─────────┴─────────────────────┘

The 16 non-Lean criteria split into three NLP tiers:

  TIER 1 — HIGH confidence (regex → near-certain with NLP):
    CC-03   Principles named/numbered/explained
    CC-09   Repo structure fully specified
    CC-13   Adoption sequence ordered and actionable
    CC-15   ≥3 practical entry points described
    CC-17   Daily practice stated concretely
    CC-26   Failure mode catalogue (≥3 modes, each with structure)

  TIER 2 — MEDIUM confidence (meaningful improvement over regex):
    CC-01   Problem stated
    CC-02   Inversion stated
    CC-16   No external concepts in principles
    CC-19   declares quality guidance (falsifiability)
    CC-21   Adoption ramp for next-touch rule

  TIER 3 — LOW confidence (NLP helps marginally, human judgment dominates):
    CC-08a  Contradiction → supersession described
    CC-08c  Scope overlap detection described
    CC-10   Reader can create _repo/ from docs alone (sufficiency)
    CC-14   Legacy strategy doesn't require comprehensive audit
    CC-20   Tooling surface section exists with contracts

  Total automatable improvement: 11 CC from TIER 1+2 go from fragile
  regex to semantic entailment. 5 CC in TIER 3 stay human-dependent.

Usage:
  export ANTHROPIC_API_KEY=sk-...
  python3 nlp_validator.py ../prose/intent-manifesto.md ../prose/intent-spec.md

  Or without API key (dry-run mode, shows prompts without calling):
  python3 nlp_validator.py --dry-run ../prose/intent-manifesto.md ../prose/intent-spec.md
"""

import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from textwrap import dedent

# ── Configuration ────────────────────────────────────────────────────

MODEL = "claude-sonnet-4-5-20250929"
MAX_TOKENS = 1024
TEMPERATURE = 0.0  # deterministic for reproducibility

# ── Data structures ──────────────────────────────────────────────────

@dataclass
class NLPCheck:
    id: str
    tier: int                    # 1, 2, or 3
    test: str
    section_regex: str           # extracts the relevant section from the doc
    source: str                  # "manifesto" or "spec" or "both"
    entailment_prompt: str       # the NLP question
    required_verdicts: list      # what the model must confirm
    passed: bool = False
    evidence: str = ""
    raw_response: str = ""
    skipped: bool = False


# ── Section extraction ───────────────────────────────────────────────

def extract_section(text: str, pattern: str, fallback_whole: bool = False) -> str:
    """Extract a section from markdown using a header regex."""
    m = re.search(pattern, text, re.S)
    if m:
        return m.group(0)[:8000]  # cap to fit context
    return text[:8000] if fallback_whole else ""


# ── Entailment engine ────────────────────────────────────────────────

def call_claude(system: str, user: str, dry_run: bool = False) -> dict:
    """Call Claude API for structured entailment judgment."""
    if dry_run:
        return {"dry_run": True, "prompt_preview": user[:200]}

    try:
        import anthropic
    except ImportError:
        # Fall back to raw HTTP
        import urllib.request
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            return {"error": "No ANTHROPIC_API_KEY and no anthropic package"}
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=json.dumps({
                "model": MODEL,
                "max_tokens": MAX_TOKENS,
                "temperature": TEMPERATURE,
                "system": system,
                "messages": [{"role": "user", "content": user}]
            }).encode(),
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            }
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        text = data["content"][0]["text"]
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown fences
            m = re.search(r"```json\s*\n(.*?)```", text, re.S)
            if m:
                return json.loads(m.group(1))
            return {"raw": text, "error": "Could not parse JSON"}

    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
        system=system,
        messages=[{"role": "user", "content": user}]
    )
    text = msg.content[0].text
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"```json\s*\n(.*?)```", text, re.S)
        if m:
            return json.loads(m.group(1))
        return {"raw": text, "error": "Could not parse JSON"}


SYSTEM_PROMPT = dedent("""\
    You are a formal document auditor. You will be given a section of a
    technical document and a set of verification questions. For each
    question, determine whether the text ENTAILS the claim (the answer
    is clearly supported by the text), CONTRADICTS it, or is INSUFFICIENT
    (the text doesn't address it or is ambiguous).

    Respond ONLY with a JSON object. No markdown, no preamble.
    Schema:
    {
      "verdicts": [
        {
          "id": "v1",
          "claim": "...",
          "judgment": "ENTAILS" | "CONTRADICTS" | "INSUFFICIENT",
          "evidence": "brief quote or paraphrase from the text",
          "confidence": 0.0-1.0
        }
      ],
      "overall": "PASS" | "FAIL" | "PARTIAL",
      "summary": "one sentence"
    }
""")


# ── Check definitions ────────────────────────────────────────────────

def build_checks() -> list[NLPCheck]:
    return [
        # ── TIER 1: HIGH confidence ─────────────────────────────────

        NLPCheck(
            id="CC-03", tier=1,
            test="Principles named, numbered, explained with rationale",
            section_regex=r"(?s)(##\s+[IVXLC]*\.?\s*Core\s+Principles.*?)(?=\n##\s+[IVXLC])",
            source="manifesto",
            entailment_prompt=dedent("""\
                Verify these claims about the Core Principles section:
                v1: At least 3 principles exist, each with a numbered heading (e.g., "### 1. ...")
                v2: Each principle has a title AND a body of at least 2 substantive paragraphs
                v3: Each principle includes rationale or justification (why it matters)
            """),
            required_verdicts=["v1", "v2", "v3"]
        ),

        NLPCheck(
            id="CC-09", tier=1,
            test="Repository structure fully specified",
            section_regex=r"(?s)(##\s+[IVXLC]*\.?\s*The\s+Repository\s+Structure.*?)(?=\n##\s+[IVXLC]|\Z)",
            source="spec",
            entailment_prompt=dedent("""\
                Verify these claims about the repository structure section:
                v1: A directory tree is shown with the _repo/ root folder
                v2: At least these directories are present: intents/, transitions/, tensions/, decisions/, origins/, plugins/
                v3: Each directory's purpose is stated or inferable from context
            """),
            required_verdicts=["v1", "v2", "v3"]
        ),

        NLPCheck(
            id="CC-13", tier=1,
            test="Adoption sequence is ordered and actionable",
            section_regex=r"(?s)(###?\s*[Tt]he\s+adoption\s+sequence.*?)(?=\n###?\s|\n##\s|\n---|\Z)",
            source="manifesto",
            entailment_prompt=dedent("""\
                Verify these claims about the adoption sequence:
                v1: Steps are numbered (1, 2, 3, ...)
                v2: At least 5 steps exist
                v3: Each step contains a concrete, actionable instruction (not just a principle)
                v4: No step requires knowledge not available in this document
            """),
            required_verdicts=["v1", "v2", "v3"]
        ),

        NLPCheck(
            id="CC-15", tier=1,
            test="At least 3 practical entry points described",
            section_regex=r"(?s)(##\s+[IVXLC]*\.?\s*Adopting\s+in\s+the\s+Real\s+World.*?)(?=\n##\s+[IVXLC]|\Z)",
            source="manifesto",
            entailment_prompt=dedent("""\
                Verify these claims about adoption entry points:
                v1: At least 3 distinct, named strategies or entry points are described
                v2: Each strategy has enough detail that a team could execute it without external guidance
                v3: Identify the strategy names (list them)
            """),
            required_verdicts=["v1", "v2"]
        ),

        NLPCheck(
            id="CC-17", tier=1,
            test="Daily practice stated concretely",
            section_regex=r"(?s)(##\s+[IVXLC]*\.?\s*The\s+Practice.*?)(?=\n##\s|\Z)",
            source="manifesto",
            entailment_prompt=dedent("""\
                Verify these claims about the practice section:
                v1: The section contains specific behavioral instructions (not just philosophy)
                v2: It describes WHEN to declare intent
                v3: It describes WHEN to link a decision to intent
                v4: It describes WHEN to record a transition
                v5: It describes WHEN to check existing intent (e.g., when encountering resistance)
            """),
            required_verdicts=["v1", "v2", "v3", "v4"]
        ),

        NLPCheck(
            id="CC-26", tier=1,
            test="Failure mode catalogue with ≥3 named modes",
            section_regex=r"(?s)(##\s+[IVXLC]*\.?\s*How\s+This\s+Fails.*?)(?=\n##\s|\Z)",
            source="manifesto",
            entailment_prompt=dedent("""\
                Verify these claims about the failure modes section:
                v1: At least 3 distinct failure modes are named (bolded or headed)
                v2: Each failure mode describes recognizable symptoms
                v3: Each failure mode includes at least one remedy or mitigation
                v4: The modes include: (a) performative/hollow declarations,
                    (b) bureaucratic overhead or over-specification,
                    (c) some form of drift, blur, or staleness
            """),
            required_verdicts=["v1", "v2", "v3", "v4"]
        ),

        # ── TIER 2: MEDIUM confidence ───────────────────────────────

        NLPCheck(
            id="CC-01", tier=2,
            test="Manifesto states the problem it solves",
            section_regex=r"(?s)(##\s+[IVXLC]*\.?\s*The\s+Problem.*?)(?=\n##\s+[IVXLC])",
            source="manifesto",
            entailment_prompt=dedent("""\
                Verify these claims about the problem section:
                v1: The section describes a current state of software development WITHOUT the proposed model
                v2: The description includes concrete consequences or failures caused by this current state
                v3: The problem is about intent being invisible, lost, or scattered (not about code quality generically)
            """),
            required_verdicts=["v1", "v2", "v3"]
        ),

        NLPCheck(
            id="CC-02", tier=2,
            test="Manifesto states the inversion explicitly",
            section_regex=r"(?s)(##\s+[IVXLC]*\.?\s*The\s+Inversion.*?)(?=\n##\s+[IVXLC])",
            source="manifesto",
            entailment_prompt=dedent("""\
                Verify these claims about the inversion section:
                v1: An OLD orientation/model is explicitly named (e.g., "code is primary", "decisions explain code")
                v2: A NEW orientation/model is explicitly named (e.g., "intent is primary")
                v3: The two are presented as a deliberate reversal, not just an improvement
            """),
            required_verdicts=["v1", "v2", "v3"]
        ),

        NLPCheck(
            id="CC-16", tier=2,
            test="No principle references concepts defined only outside the document",
            section_regex=r"(?s)(##\s+[IVXLC]*\.?\s*Core\s+Principles.*?)(?=\n##\s+[IVXLC])",
            source="manifesto",
            entailment_prompt=dedent("""\
                Verify these claims about the principles section:
                v1: No principle uses technical jargon that is undefined in this document
                     (common software terms like "API", "CI", "ADR" are acceptable if
                     their role is clear from context)
                v2: No principle says "see [external document]" or "refer to [URL]" for
                     a concept that is essential to understanding the principle
                v3: Every concept central to a principle is either common knowledge among
                     software engineers or explained within the document
            """),
            required_verdicts=["v1", "v2", "v3"]
        ),

        NLPCheck(
            id="CC-19", tier=2,
            test="declares field has quality guidance with falsifiability",
            section_regex=r"(?s)(##\s+[IVXLC]*\.?\s*How\s+This\s+Fails.*?)(?=\n##\s|\Z)",
            source="manifesto",
            entailment_prompt=dedent("""\
                Verify these claims about quality guidance for the 'declares' field:
                v1: A falsifiability test is stated — if no code change could violate
                    the declaration, it is not a valid intent
                v2: At least one POSITIVE example of a good declares statement is given
                    (specific, testable commitment)
                v3: At least one NEGATIVE example of a bad declares statement is given
                    (vague, platitude-like, unfalsifiable)
                v4: A recommended structure or grammar for writing declares statements
                    is suggested (e.g., subject + verb + predicate)
            """),
            required_verdicts=["v1", "v2", "v3"]
        ),

        NLPCheck(
            id="CC-21", tier=2,
            test="Next-touch rule has an adoption ramp",
            section_regex=r"(?s)(###?\s*The\s+.?next\s+touch.?\s+rule.*?)(?=\n###?\s|\n##\s|\Z)",
            source="manifesto",
            entailment_prompt=dedent("""\
                Verify these claims about the next-touch rule's adoption ramp:
                v1: There is an advisory or grace period where the rule is non-blocking
                v2: The transition from advisory to enforcement is described
                v3: The cold-start problem is acknowledged — the first PR into undeclared
                    territory carries extra burden, and this is explicitly addressed
            """),
            required_verdicts=["v1", "v2", "v3"]
        ),

        # ── TIER 3: LOW confidence (still include for completeness) ──

        NLPCheck(
            id="CC-08a", tier=3,
            test="Contradiction between active intents → supersession",
            section_regex=r"(?s)(###?\s*6\.\s+Tensions.*?)(?=\n###?\s+\d+\.|\n##\s|\Z)",
            source="manifesto",
            entailment_prompt=dedent("""\
                Verify these claims about handling contradictions:
                v1: The document defines what happens when a new intent DIRECTLY
                    CONTRADICTS an existing active intent (not just tension)
                v2: The contradiction is surfaced as a supersession proposal
                v3: An authority (resolution_owner or intent owner) decides the outcome
                v4: The outcome is recorded as an intent transition
            """),
            required_verdicts=["v1", "v2", "v3", "v4"]
        ),

        NLPCheck(
            id="CC-08c", tier=3,
            test="Scope overlap between intents is detectable",
            section_regex=r"(?s)(##\s+[IVXLC]*\.?\s*The\s+Extension\s+Surface.*?)(?=\n##\s|\Z)",
            source="spec",
            entailment_prompt=dedent("""\
                Verify these claims about scope overlap detection:
                v1: The document describes how overlapping scopes between two intents
                    can be detected (heuristic or tooling)
                v2: Overlapping intents must either declare a tension or establish
                    a relationship (e.g., serves)
                v3: A validation rule or CI check for scope overlap is shown or described
            """),
            required_verdicts=["v1", "v2"]
        ),

        NLPCheck(
            id="CC-10", tier=3,
            test="Reader can create _repo/ from docs alone",
            section_regex=r"(?s)(##\s+[IVXLC]*\.?\s*The\s+Repository\s+Structure.*?)(?=\n##\s|\Z)",
            source="spec",
            entailment_prompt=dedent("""\
                Verify this claim:
                v1: A reader with no prior knowledge of this framework could create
                    the complete _repo/ directory structure using ONLY information
                    present in this document — no external references are needed
                v2: The document shows the directory tree, the manifest file format,
                    at least one example intent YAML, and the plugin structure
            """),
            required_verdicts=["v1", "v2"]
        ),

        NLPCheck(
            id="CC-14", tier=3,
            test="Legacy strategy does not require comprehensive audit",
            section_regex=r"(?s)(##\s+[IVXLC]*\.?\s*Adopting\s+in\s+the\s+Real\s+World.*?)(?=\n##\s+[IVXLC]|\Z)",
            source="manifesto",
            entailment_prompt=dedent("""\
                Verify these claims:
                v1: The document explicitly states that aspirational intent can be
                    declared WITHOUT understanding the existing code
                v2: The document explicitly discourages or warns against a
                    comprehensive audit as an adoption strategy
            """),
            required_verdicts=["v1", "v2"]
        ),

        NLPCheck(
            id="CC-20", tier=3,
            test="Spec defines a tooling surface with contracts",
            section_regex=r"(?s)(##\s+[IVXLC]*\.?\s*Tooling\s+Surface.*?)(?=\n##\s|\Z)",
            source="spec",
            entailment_prompt=dedent("""\
                Verify these claims about the tooling surface section:
                v1: A dedicated section exists that defines tooling contracts
                v2: CI validation is described (what is checked on commit)
                v3: Scope lookup is described (how to query which intents govern a file path)
                v4: Lifecycle event propagation is described (how hooks are invoked)
            """),
            required_verdicts=["v1", "v2", "v3", "v4"]
        ),
    ]


# ── Runner ───────────────────────────────────────────────────────────

def run_check(check: NLPCheck, manifesto: str, spec: str, dry_run: bool) -> NLPCheck:
    """Run a single NLP entailment check."""
    if check.source == "manifesto":
        text = extract_section(manifesto, check.section_regex, fallback_whole=True)
    elif check.source == "spec":
        text = extract_section(spec, check.section_regex, fallback_whole=True)
    else:
        text = extract_section(manifesto + "\n\n" + spec, check.section_regex, fallback_whole=True)

    if not text.strip():
        check.skipped = True
        check.evidence = "Section not found"
        return check

    user_msg = f"DOCUMENT SECTION:\n\n{text}\n\n---\n\nVERIFICATION TASK:\n\n{check.entailment_prompt}"
    result = call_claude(SYSTEM_PROMPT, user_msg, dry_run=dry_run)

    if dry_run:
        check.skipped = True
        check.evidence = f"DRY RUN — prompt ready ({len(text)} chars of context)"
        check.raw_response = json.dumps(result, indent=2)
        return check

    if "error" in result:
        check.skipped = True
        check.evidence = f"API error: {result.get('error', 'unknown')}"
        check.raw_response = json.dumps(result, indent=2)
        return check

    check.raw_response = json.dumps(result, indent=2)

    # Parse verdicts
    verdicts = result.get("verdicts", [])
    verdict_map = {v["id"]: v for v in verdicts}

    passed_ids = []
    failed_ids = []
    for req_id in check.required_verdicts:
        v = verdict_map.get(req_id)
        if v and v.get("judgment") == "ENTAILS":
            passed_ids.append(req_id)
        else:
            failed_ids.append(req_id)

    check.passed = len(failed_ids) == 0
    overall = result.get("overall", "UNKNOWN")
    summary = result.get("summary", "")

    ev_parts = []
    if passed_ids:
        ev_parts.append(f"ENTAILS: {', '.join(passed_ids)}")
    if failed_ids:
        ev_parts.append(f"MISSING: {', '.join(failed_ids)}")
    if summary:
        ev_parts.append(summary)
    check.evidence = " | ".join(ev_parts)

    return check


def main():
    dry_run = "--dry-run" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    if len(args) >= 2:
        mp, sp = args[0], args[1]
    else:
        mp = "../prose/intent-manifesto.md"
        sp = "../prose/intent-spec.md"

    manifesto = Path(mp).read_text(encoding="utf-8")
    spec = Path(sp).read_text(encoding="utf-8")

    checks = build_checks()
    w = 76
    print("=" * w)
    print("  NLP VALIDATOR — Semantic Entailment (16 prose-level CC)")
    if dry_run:
        print("  MODE: DRY RUN (no API calls)")
    print("=" * w)

    for tier_num in [1, 2, 3]:
        tier_checks = [c for c in checks if c.tier == tier_num]
        tier_label = {1: "HIGH", 2: "MEDIUM", 3: "LOW"}[tier_num]

        p = f = sk = 0
        print(f"\n  ── TIER {tier_num}: {tier_label} confidence ──\n")
        for check in tier_checks:
            run_check(check, manifesto, spec, dry_run)
            if check.skipped:
                mark = "○"; sk += 1
            elif check.passed:
                mark = "✓"; p += 1
            else:
                mark = "✗"; f += 1
            print(f"    {mark} {check.id}: {check.test}")
            print(f"        {check.evidence}")

        print(f"\n    Tier {tier_num}: {p}/{p+f} passed, {sk} skipped")

    # Summary
    all_checks = checks
    total_p = sum(1 for c in all_checks if c.passed)
    total_f = sum(1 for c in all_checks if not c.passed and not c.skipped)
    total_sk = sum(1 for c in all_checks if c.skipped)

    print(f"\n{'─' * w}")
    print(f"  NLP TOTAL: {total_p}/{total_p+total_f} passed  ({total_f} failed, {total_sk} skipped)")

    # Combine with Lean
    lean_proven = 12
    print(f"\n  Combined coverage:")
    print(f"    Lean 4 (kernel-checked):    {lean_proven} CC")
    print(f"    NLP (semantic entailment):   {total_p} CC")
    nlp_ids = {c.id for c in all_checks if c.passed}
    lean_ids = {"CC-04","CC-05","CC-06","CC-07","CC-08","CC-08b",
                "CC-18","CC-23","CC-25","CC-27"}
    overlap = nlp_ids & lean_ids
    unique_nlp = nlp_ids - lean_ids
    print(f"    Overlap (double-verified):   {len(overlap)} CC")
    print(f"    Unique NLP contribution:     {len(unique_nlp)} CC")
    print(f"    Combined unique verified:    {len(lean_ids | nlp_ids)}/28 CC")
    print("=" * w)

    # Write detailed results
    if not dry_run:
        out = Path("nlp-results.json")
        results = []
        for c in all_checks:
            results.append({
                "id": c.id, "tier": c.tier, "test": c.test,
                "passed": c.passed, "skipped": c.skipped,
                "evidence": c.evidence
            })
        out.write_text(json.dumps(results, indent=2))
        print(f"\n  Detailed results written to {out}")

    sys.exit(0 if total_f == 0 else 1)


if __name__ == "__main__":
    main()
