# Intent Specification — Core Data Model

This document defines the universal data model for the Intent Driven Framework.

## First-Class Entities (CC-04)

The model defines five first-class entities:
- **Intent** — a declared architectural or behavioral commitment
- **Transition** — a versioned change to an intent
- **Decision** — a recorded choice that affects intents
- **Tension** — a known conflict between intents
- **Manifest** — the repository-level index of all intents

See `schemas/` for complete YAML schemas of each entity.

## Lifecycle States (CC-07)

| State       | Entry Condition          | Exit Condition                    |
|-------------|--------------------------|-----------------------------------|
| proposed    | Intent declared          | Accepted → active; or → retracted |
| active      | Accepted by owner        | → evolving, superseded, residual  |
| evolving    | Undergoing change        | → active, superseded, residual    |
| superseded  | Replaced by successor    | → residual                        |
| residual    | No longer maintained     | Terminal                          |
| retracted   | Withdrawn before active  | Terminal                          |

## Tooling Surface (CC-20)

See `tools/ci/validate.py` for the reference implementation of:
- (a) Schema validation in CI
- (b) Scope lookup by file path
- (c) Lifecycle hook invocation
