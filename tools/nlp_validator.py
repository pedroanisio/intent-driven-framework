#!/usr/bin/env python3
"""
NLP-assisted prose validator for Intent Framework v1.6.1+
Schema version: 0.3.0 | Framework version: 1.2.0

Replaces the regex heuristics in score_v150.py with semantic entailment
checks for the prose-level criteria that Lean 4 cannot prove. Uses Claude
as the NLP engine via the Anthropic API.

Architecture:
  ┌──────────────────────────────────────────────────────┐
  │  Lean 4          │  12 CC  │  Kernel-checked         │
  ├──────────────────┼─────────┼─────────────────────────┤
  │  NLP validator   │  13 CC  │  Semantic entailment    │ ← this file
  ├──────────────────┼─────────┼─────────────────────────┤
  │  Human judgment  │   5 CC  │  Cannot automate        │
  ├──────────────────┼─────────┼─────────────────────────┤
  │  Regex scorer    │  28 CC  │  Keyword heuristics     │ (baseline)
  └──────────────────┴─────────┴─────────────────────────┘

The non-Lean criteria split into three NLP tiers:

  TIER 1 — HIGH confidence (regex → near-certain with NLP):
    CC-03   Principles named/numbered/explained
    CC-09   Repo structure fully specified
    CC-13   Adoption sequence ordered and actionable
    CC-15   ≥3 practical entry points described
    CC-17   Daily practice stated concretely
    CC-26   Failure mode catalogue (≥3 modes, each with structure)
    CC-28   Operational cycle defined with phases and constraints   [NEW in 1.2.0]

  TIER 2 — MEDIUM confidence (meaningful improvement over regex):
    CC-01   Problem stated
    CC-02   Inversion stated
    CC-16   No external concepts in principles
    CC-19   declares quality guidance (falsifiability)
    CC-21   Adoption ramp for next-touch rule
    CC-29   TDD isomorphism is structural, not analogical          [NEW in 1.2.0]

  TIER 3 — LOW confidence (NLP helps marginally, human judgment dominates):
    CC-08a  Contradiction → supersession described
    CC-08c  Scope overlap detection described
    CC-10   Reader can create _repo/ from docs alone (sufficiency)
    CC-14   Legacy strategy doesn't require comprehensive audit
    CC-20   Tooling surface section exists with contracts

  Total automatable improvement: 13 CC from TIER 1+2 go from fragile
  regex to semantic entailment. 5 CC in TIER 3 stay human-dependent.

  NOTE: CC-28 and CC-29 are provisional IDs for the operational cycle
  criteria introduced with framework 1.2.0. If the official criteria
  numbering differs, update the IDs here and in LEAN_IDS.

Usage:
  export ANTHROPIC_API_KEY=sk-...
  python3 nlp_validator.py ../prose/intent-manifesto.md ../prose/intent-spec.md

  Options:
    --dry-run      Show prompts without calling the API
    --verbose      Print raw API responses for each check
    --min-conf N   Minimum confidence threshold (0.0-1.0, default 0.7)
    --out FILE     Output path for detailed results JSON (default: nlp-results.json)
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
DEFAULT_MIN_CONFIDENCE = 0.7  # verdicts below this are treated as INSUFFICIENT

# ── Lean-proven criteria ─────────────────────────────────────────────
# These 12 CC are verified by the Lean 4 kernel and are NOT checked
# by this validator. They are listed here for combined coverage reporting.
#
# IMPORTANT: If you add or remove Lean proofs, update this set AND
# the LEAN_PROVEN count. The validator will warn if they disagree.

LEAN_IDS = {
    "CC-04",   # Intent identity is independent of artifacts
    "CC-05",   # Intent → Decision → Artifact chain is defined
    "CC-06",   # Semantic versioning rules for intent
    "CC-07",   # Lifecycle states and valid transitions
    "CC-08",   # Tension model structure
    "CC-08b",  # Tension resolution strategies typed
    "CC-11",   # Manifest schema is defined
    "CC-12",   # Transition log schema is defined
    "CC-18",   # Scope is structurally declared on intents
    "CC-23",   # SemVer backward-compatibility rules
    "CC-25",   # Intent retirement conditions are typed
    "CC-27",   # Decision schema carries serves_intent ref
}
LEAN_PROVEN = 12

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
    verdict_details: list = field(default_factory=list)  # per-verdict confidence


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
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read())
        except Exception as e:
            return {"error": f"HTTP request failed: {e}"}

        text = data.get("content", [{}])[0].get("text", "")
        return _parse_json_response(text)

    client = anthropic.Anthropic()
    try:
        msg = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            system=system,
            messages=[{"role": "user", "content": user}]
        )
    except Exception as e:
        return {"error": f"Anthropic API call failed: {e}"}

    text = msg.content[0].text
    return _parse_json_response(text)


def _parse_json_response(text: str) -> dict:
    """Parse JSON from model response, handling markdown fences."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"```(?:json)?\s*\n(.*?)```", text, re.S)
        if m:
            try:
                return json.loads(m.group(1))
            except json.JSONDecodeError:
                pass
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
                v5: Green-washing is addressed — the failure mode where teams
                    claim satisfaction without updating evidence (achieved_coverage
                    or current_reality unchanged while intent is evolved)
            """),
            required_verdicts=["v1", "v2", "v3", "v4", "v5"]
        ),

        NLPCheck(
            id="CC-28", tier=1,
            test="Operational cycle defined with phases and constraints",
            section_regex=r"(?s)(##\s+[IVXLC]*\.?\s*(?:The\s+)?(?:Operational\s+Cycle|Red\s*/\s*Green\s*/\s*Refactor|The\s+Practice\s+Cycle).*?)(?=\n##\s|\Z)",
            source="both",
            entailment_prompt=dedent("""\
                Verify these claims about the operational cycle:
                v1: Three phases are defined: Red (Declare), Green (Satisfy),
                    Refactor (Evolve) — or semantically equivalent names
                v2: Each phase has a rule that constrains what work is permitted
                v3: The Red phase requires an unsatisfied intent before any work
                    is justified — work without a red intent is drift
                v4: The Green phase requires evidence — achieved_coverage or
                    current_reality must update for green to be claimed
                v5: The Refactor phase requires a prior green state — no evolution
                    without demonstrated satisfaction
                v6: At least 2 named constraints or violations are defined
                    (e.g., OC-01, OC-02 or equivalent)
            """),
            required_verdicts=["v1", "v2", "v3", "v4", "v5", "v6"]
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

        NLPCheck(
            id="CC-29", tier=2,
            test="TDD isomorphism is structural, not analogical",
            section_regex=r"(?s)(##\s+[IVXLC]*\.?\s*(?:The\s+)?(?:Operational\s+Cycle|Red\s*/\s*Green\s*/\s*Refactor|TDD\s+Isomorphism).*?)(?=\n##\s|\Z)",
            source="both",
            entailment_prompt=dedent("""\
                Verify these claims about the TDD isomorphism:
                v1: The document explicitly claims a structural (not merely analogical
                    or pedagogical) relationship between Intent-Driven Red/Green/Refactor
                    and Test-Driven Development
                v2: At least 2 specific structural parallels are drawn (e.g., failing
                    test ↔ unsatisfied intent, minimum code ↔ minimum decisions)
                v3: At least 2 divergences from TDD are acknowledged (e.g., binary
                    vs. graduated satisfaction, speed of cycle, scope of constraint)
                v4: The isomorphism is presented as falsifiable — conditions under
                    which it would be downgraded to a metaphor are stated or referenced
            """),
            required_verdicts=["v1", "v2", "v3", "v4"]
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

def run_check(
    check: NLPCheck,
    manifesto: str,
    spec: str,
    dry_run: bool,
    min_confidence: float = DEFAULT_MIN_CONFIDENCE
) -> NLPCheck:
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
    low_conf_ids = []
    check.verdict_details = []

    for req_id in check.required_verdicts:
        v = verdict_map.get(req_id)
        if v:
            conf = v.get("confidence", 0.0)
            check.verdict_details.append({
                "id": req_id,
                "judgment": v.get("judgment", "MISSING"),
                "confidence": conf,
                "evidence": v.get("evidence", "")
            })
            if v.get("judgment") == "ENTAILS" and conf >= min_confidence:
                passed_ids.append(req_id)
            elif v.get("judgment") == "ENTAILS" and conf < min_confidence:
                low_conf_ids.append(f"{req_id}@{conf:.2f}")
                failed_ids.append(req_id)
            else:
                failed_ids.append(req_id)
        else:
            failed_ids.append(req_id)
            check.verdict_details.append({
                "id": req_id,
                "judgment": "MISSING",
                "confidence": 0.0,
                "evidence": "Verdict not returned by model"
            })

    check.passed = len(failed_ids) == 0
    summary = result.get("summary", "")

    ev_parts = []
    if passed_ids:
        ev_parts.append(f"ENTAILS: {', '.join(passed_ids)}")
    if low_conf_ids:
        ev_parts.append(f"LOW_CONF: {', '.join(low_conf_ids)}")
    if failed_ids:
        missing_only = [fid for fid in failed_ids if fid not in [lc.split("@")[0] for lc in low_conf_ids]]
        if missing_only:
            ev_parts.append(f"MISSING: {', '.join(missing_only)}")
    if summary:
        ev_parts.append(summary)
    check.evidence = " | ".join(ev_parts)

    return check


def parse_args(argv: list[str]) -> dict:
    """Parse command-line arguments."""
    opts = {
        "dry_run": False,
        "verbose": False,
        "min_confidence": DEFAULT_MIN_CONFIDENCE,
        "out": "nlp-results.json",
        "files": []
    }

    i = 1
    while i < len(argv):
        arg = argv[i]
        if arg == "--dry-run":
            opts["dry_run"] = True
        elif arg == "--verbose":
            opts["verbose"] = True
        elif arg == "--min-conf" and i + 1 < len(argv):
            i += 1
            opts["min_confidence"] = float(argv[i])
        elif arg == "--out" and i + 1 < len(argv):
            i += 1
            opts["out"] = argv[i]
        elif not arg.startswith("--"):
            opts["files"].append(arg)
        i += 1

    return opts


def main():
    opts = parse_args(sys.argv)
    dry_run = opts["dry_run"]
    verbose = opts["verbose"]
    min_conf = opts["min_confidence"]

    files = opts["files"]
    if len(files) >= 2:
        mp, sp = files[0], files[1]
    else:
        mp = "../prose/intent-manifesto.md"
        sp = "../prose/intent-spec.md"

    manifesto = Path(mp).read_text(encoding="utf-8")
    spec = Path(sp).read_text(encoding="utf-8")

    # ── Validate Lean ID consistency ──────────────────────────────
    if len(LEAN_IDS) != LEAN_PROVEN:
        print(f"  ⚠  LEAN_IDS has {len(LEAN_IDS)} entries but LEAN_PROVEN = {LEAN_PROVEN}")
        print(f"     Fix LEAN_IDS or LEAN_PROVEN before trusting combined coverage.\n")

    checks = build_checks()
    w = 76
    print("=" * w)
    print("  NLP VALIDATOR — Semantic Entailment")
    print(f"  Framework: 1.2.0 | Schema: 0.3.0 | Model: {MODEL}")
    if dry_run:
        print("  MODE: DRY RUN (no API calls)")
    if min_conf != DEFAULT_MIN_CONFIDENCE:
        print(f"  Confidence threshold: {min_conf}")
    print("=" * w)

    # ── Check for NLP/Lean overlap ────────────────────────────────
    nlp_check_ids = {c.id for c in checks}
    overlap_with_lean = nlp_check_ids & LEAN_IDS
    if overlap_with_lean:
        print(f"\n  ⚠  NLP checks overlap with Lean: {', '.join(sorted(overlap_with_lean))}")
        print(f"     These are double-verified, not double-counted.\n")

    for tier_num in [1, 2, 3]:
        tier_checks = [c for c in checks if c.tier == tier_num]
        tier_label = {1: "HIGH", 2: "MEDIUM", 3: "LOW"}[tier_num]

        p = f = sk = 0
        print(f"\n  ── TIER {tier_num}: {tier_label} confidence ──\n")
        for check in tier_checks:
            run_check(check, manifesto, spec, dry_run, min_conf)
            if check.skipped:
                mark = "○"; sk += 1
            elif check.passed:
                mark = "✓"; p += 1
            else:
                mark = "✗"; f += 1
            print(f"    {mark} {check.id}: {check.test}")
            print(f"        {check.evidence}")
            if verbose and check.raw_response:
                print(f"        ── raw ──")
                for line in check.raw_response.split("\n"):
                    print(f"        {line}")
                print(f"        ── end ──")

        print(f"\n    Tier {tier_num}: {p}/{p+f} passed, {sk} skipped")

    # ── Summary ───────────────────────────────────────────────────
    total_p = sum(1 for c in checks if c.passed)
    total_f = sum(1 for c in checks if not c.passed and not c.skipped)
    total_sk = sum(1 for c in checks if c.skipped)

    print(f"\n{'─' * w}")
    print(f"  NLP TOTAL: {total_p}/{total_p+total_f} passed  ({total_f} failed, {total_sk} skipped)")

    # ── Combined coverage ─────────────────────────────────────────
    nlp_passed_ids = {c.id for c in checks if c.passed}
    overlap = nlp_passed_ids & LEAN_IDS
    unique_nlp = nlp_passed_ids - LEAN_IDS
    combined = LEAN_IDS | nlp_passed_ids

    # Total CC count — base 28 plus any new criteria
    all_known_ids = LEAN_IDS | nlp_check_ids
    total_cc = max(28, len(all_known_ids))

    print(f"\n  Combined coverage:")
    print(f"    Lean 4 (kernel-checked):    {len(LEAN_IDS)} CC")
    print(f"    NLP (semantic entailment):   {total_p} CC")
    print(f"    Overlap (double-verified):   {len(overlap)} CC")
    print(f"    Unique NLP contribution:     {len(unique_nlp)} CC")
    print(f"    Combined unique verified:    {len(combined)}/{total_cc} CC")

    # ── Unverified CC ─────────────────────────────────────────────
    nlp_failed_ids = {c.id for c in checks if not c.passed and not c.skipped}
    nlp_skipped_ids = {c.id for c in checks if c.skipped}
    human_only = nlp_failed_ids | nlp_skipped_ids
    if human_only:
        print(f"    Human review needed:         {', '.join(sorted(human_only))}")

    print("=" * w)

    # ── Write detailed results ────────────────────────────────────
    if not dry_run:
        out = Path(opts["out"])
        results = {
            "meta": {
                "framework_version": "1.2.0",
                "schema_version": "0.3.0",
                "model": MODEL,
                "min_confidence": min_conf,
                "lean_proven": list(sorted(LEAN_IDS)),
                "total_cc": total_cc,
                "combined_verified": len(combined),
            },
            "checks": []
        }
        for c in checks:
            results["checks"].append({
                "id": c.id,
                "tier": c.tier,
                "test": c.test,
                "passed": c.passed,
                "skipped": c.skipped,
                "evidence": c.evidence,
                "verdict_details": c.verdict_details,
                "raw_response": json.loads(c.raw_response) if c.raw_response else None
            })
        out.write_text(json.dumps(results, indent=2))
        print(f"\n  Detailed results written to {out}")

    sys.exit(0 if total_f == 0 else 1)


if __name__ == "__main__":
    main()