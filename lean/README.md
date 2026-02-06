# Intent Framework — Lean 4 Formalization

Machine-checked proofs of the 12 structurally provable completeness
criteria. Run `lake build` — if exit 0, all theorems are kernel-checked.

## Provability Map

| CC | What's proved | Lean section |
|---|---|---|
| CC-04 | 5 entity types as structures, `EntityKind` inductive | §4 |
| CC-05 | 10 enum types closed (exhaustive match) | §2 |
| CC-06 | Relationship inverse is involution | §10 |
| CC-07 | Lifecycle: no dead states, terminals terminal, all reachable | §3 |
| CC-08 | `wellFormed` predicate: aspirational ⇒ current_reality | §5 |
| CC-08b | Pre-transition resolution staleness blocks on MAJOR | §9 |
| CC-18 | Meta-intent well-formed, scope covers both docs | §11 |
| CC-23 | MAJOR→invalidate, MINOR→review, PATCH→pass | §8 |
| CC-25 | Deprecation migration function total | §12 |
| CC-27 | Transition log 1.0.0→1.6.1: contiguous 9-step chain | §7 |

## What's NOT provable

16 criteria require prose judgment (philosophy, adoption, failure modes)
and are verified by the pytest suite, regex scorer, and NLP semantic
evaluator instead. See [VERIFICATION.md](../VERIFICATION.md) for the
five-layer coverage map.

## Requirements

- Lean 4 toolchain v4.16.0 (see `lean-toolchain`)
- No external dependencies (Lean stdlib only)

```
lake build   # exit 0 = all proofs check
```
