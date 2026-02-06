# Failure Modes — Intent Driven Framework

The IDF can be adopted badly. This document names the three primary failure
modes so teams have vocabulary to self-correct (CC-26).

---

## 1. Performative Intent

**Symptoms:** Intent files pass schema validation but contain vague,
unfalsifiable declarations like "maintain code quality" or "ensure reliability."

**Root cause:** Teams treat intent declarations as bureaucratic checkboxes
rather than meaningful commitments.

**Mitigation:** Apply the CC-19 falsifiability test: if no code change
could violate the declaration, it is not an intent. Use the declares
quality guidance (positive/negative examples, commitment verb + observable
predicate structure).

---

## 2. Over-Specification

**Symptoms:** Intent declarations are so granular that every function or
module has its own intent. The governance overhead exceeds the value.
Teams spend more time maintaining intent files than writing code.

**Root cause:** Misunderstanding of the appropriate granularity. Intents
should capture meaningful architectural or behavioral commitments, not
mirror the code structure 1:1.

**Mitigation:** Intents should be at the subsystem or capability level.
If an intent governs fewer than ~5 files, it's probably too granular.
Use the pain-first entry point to calibrate the right level.

---

## 3. Intent Drift

**Symptoms:** Declared intents no longer reflect actual system behavior.
The codebase has evolved but the intent files haven't been updated.
`current_reality` blocks are stale. `last_assessed` dates are months old.

**Root cause:** No enforcement mechanism for keeping intents current.
The next-touch rule isn't being followed, or it was never transitioned
from advisory to enforcement.

**Mitigation:** Use CI tooling (CC-20) to flag stale `last_assessed`
dates. Enforce the next-touch rule. Review intents during sprint
retrospectives. Transition drifted intents to `residual` status
rather than letting them silently rot.
