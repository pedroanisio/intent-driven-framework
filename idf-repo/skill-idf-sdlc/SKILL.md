---
name: idf-sdlc
description: >
  Intent Driven Framework SDLC v1.7.0 implementation skill. Use when the user
  wants to: (1) scaffold or maintain an IDF _repo/ directory structure,
  (2) write or validate intent/transition/decision/tension/origin YAML against
  the v1.7.0 schemas, (3) configure the plugin registry or write extension
  plugins (fields, validators, relations, lifecycle hooks), (4) implement or
  debug CI validation (structural tier + relational tier), (5) perform scope
  lookups to find which intents govern a file path, (6) manage lifecycle state
  transitions and propagate lifecycle events, (7) check tension resolution
  staleness after version bumps (MAJOR=block, MINOR=review, PATCH=noop),
  (8) execute deprecation ceremonies when intents enter superseded/residual,
  (9) configure cross-repo intent dependencies via depends_on_intents, or
  (10) manage schema_version migration across repos. Triggers on: "_repo/",
  "manifest.yaml", "intent YAML", "scope lookup", "lifecycle hook",
  "tension staleness", "deprecation ceremony", "plugin registry",
  "ext: namespace", "cross-repo dependencies", "CI validation contract".
---

# IDF SDLC v1.7.0

Implementation specification for Intent Driven Framework repositories.

## Repository Structure

Every IDF-governed repository contains a `_repo/` directory at the root:

```
_repo/
├── manifest.yaml              # repo identity + cross-repo deps + plugin list
├── intents/
│   ├── active/                # status: active | evolving
│   ├── superseded/            # status: superseded
│   └── proposed/              # status: proposed
├── transitions/               # version change records per intent
├── tensions/                  # declared conflicts between intents
├── decisions/
│   ├── active/                # status: accepted
│   └── superseded/            # status: superseded | deprecated
├── origins/
│   ├── product/               # origin.type grouping directories
│   ├── engineering/
│   ├── incident/ (and devops, ux, data, sre, security, compliance)
└── plugins/
    ├── registry.yaml          # active plugins + required/advisory flag
    └── <plugin-name>/
        ├── plugin.yaml        # manifest: name, version, extends, registers
        ├── schema.yaml        # extension field definitions
        └── validators.yaml    # plugin validation rules
```

The `_repo/` prefix signals meta — the system's knowledge about itself.

## Minimal Valid Intent

Four fields make a valid intent:

```yaml
intent:
  id: intent-checkout-reversibility
  version: 1.0.0
  declares: "Users can reverse any checkout action within 24 hours"
  scope: [src/checkout/**]
```

Start here. Add fields as they earn their place.

## CI Validation Contract

Two tiers, both run on every commit touching `_repo/`:

**Tier 1 — Structural**: YAML parses, conforms to schema, no unresolved `intent_ref` pointers.

**Tier 2 — Relational**: `serves`/`tensions`/`supersedes` refs resolve to existing intents.
`depends_on_intents` refs resolve to reachable repos. No `proposed` intent duplicates an
`active` intent's ID. Plugins contribute additional rules.

See `references/schemas.md` for full field definitions and enum values.

## Lifecycle State Machine

```
proposed → active | retracted
active   → evolving | superseded | residual
evolving → active | superseded | residual
superseded → residual
residual   (terminal)
retracted  (terminal)
```

**Event propagation contract** (4 guarantees):
(a) every plugin with matching `on_<event>` handler is invoked
(b) handlers invoked in registry order
(c) handler failure does not prevent subsequent handlers
(d) aggregate result (pass/fail/advisory) reported to caller

Events carry: intent_id, previous_state, new_state, transition_version, author.

## Tension Resolution Staleness

When a version bump lands on an intent referenced by a tension resolution:

| Bump  | Action       | Blocks transition? |
|-------|--------------|--------------------|
| MAJOR | Invalidate   | Yes — re-evaluate before merge |
| MINOR | Review flag  | No — advisory in CI output |
| PATCH | No action    | No |

Enforcement: `on_tension_resolution_stale` lifecycle hook fires with tension_id,
bumped_intent, bump_level, current applies_to versions.

## Deprecation Ceremonies

When status → `superseded` or `residual`:

1. **Identify** — scan `depends_on_intents`, `serves`, `tensions` refs to the deprecated intent
2. **Notify** — migration path per dependent: re-point to successor, drop, or acknowledge residual
3. **Grace period** — calendar deadline or deferral, recorded on the transition
4. **Surface** — after grace period, unresolved refs become tensions

## Extension Surface

Plugins extend the model in four ways. See `references/extension-surface.md` for
plugin.yaml schema, validator rule syntax, relation type registration, and hook events.

**Rules** (CC-12):
- Extensions live under `ext.<plugin_id>.*` — never shadow core fields
- Core tooling ignores unrecognized `ext:` keys gracefully
- Plugin validators run alongside core validation in CI

## Scope Lookup

Given a file path, return all intents whose `scope` glob matches it, ordered by
specificity (most specific first). When no intent matches, report the coverage gap.
This is the fundamental operation connecting code changes to declared purpose.

## Cross-Repo Dependencies

`depends_on_intents` in manifest.yaml declares purpose contracts (not API contracts):

```yaml
depends_on_intents:
  - repo: payments-service
    intent: intent-idempotent-processing
    minimum_version: 2.0.0
```

On upstream MAJOR bump → downstream repos receive signal (issue/notification/PR).
Downstream team evaluates, updates `minimum_version`, or transitions own intents.

## Reference Files

- `references/schemas.md` — full YAML schemas for all 6 entities + enum tables
- `references/extension-surface.md` — plugin manifest, validators, relations, hooks
- `references/tooling-contracts.md` — CI tiers, scope lookup, staleness, deprecation
