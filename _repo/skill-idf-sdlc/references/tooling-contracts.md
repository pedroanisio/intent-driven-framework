# IDF SDLC v1.7.0 — Tooling Contracts

These are the interfaces any conforming tool must satisfy. Not implementations — contracts.

## CI Validation

Triggered on every commit modifying `_repo/`. Two tiers:

### Tier 1 — Structural
- Every intent file parses as valid YAML
- Conforms to core intent schema (and extension schema for ext: fields)
- No unresolved intent_ref pointers

### Tier 2 — Relational
- serves, tensions, supersedes references resolve to existing intents
- depends_on_intents references resolve to reachable repos and intent IDs
- No proposed intent duplicates the id of an active intent
- Plugin validation rules run alongside core checks

## Scope Lookup

Input: file path
Output: all intents whose scope glob matches, ordered by specificity

```
src/billing/calculations/tax.py
  → intent-billing-accuracy (scope: src/billing/calculations/**)
  → intent-billing-compliance (scope: src/billing/**)
```

More specific scope returned first. When no intent matches → report gap
(advisory signal for next-touch declarations).

## Lifecycle Event Propagation

When intent transitions between states, core emits a lifecycle event.

**Invocation contract**:
(a) Every plugin in registry.yaml with matching on_<event> handler is invoked
(b) Handlers invoked in registry order
(c) Handler failure does NOT prevent subsequent handlers from executing
(d) Aggregate result (pass/fail/advisory) reported to caller

**Event payload**:
- intent_id
- previous_state
- new_state
- transition_version (semver)
- author

## Tension Resolution Staleness (CC-23)

applies_to on a resolution binds it to specific intent versions. When either evolves:

### Pre-transition check
Before a version bump on intent A is accepted:
1. Scan all tensions where A appears in `between`
2. For each tension, check if current_resolution.applies_to references pre-bump version
3. If yes:
   - MAJOR bump → resolution is stale, transition BLOCKED until resolution updated
   - MINOR bump → review flag (advisory, does not block)
   - PATCH bump → no action

### Enforcement
Hook: on_tension_resolution_stale
Payload: tension_id, bumped_intent, bump_level, current applies_to versions

## Deprecation Ceremonies (CC-25)

When intent enters superseded or residual:

### Step 1: Identify dependents
Scan depends_on_intents, serves, tensions refs to the deprecated intent.
Within single repo: static scan of _repo/intents/.
Cross-repo: depends on CC-22 protocol.

### Step 2: Notify with migration path
Each dependent must: re-point to successor (from supersedes field on new intent),
drop the dependency, or explicitly acknowledge residual state.

### Step 3: Grace period
Calendar deadline or deferral to dependent team's next planning cycle.
Recorded on the transition that moved intent to superseded/residual.

### Step 4: Surface unresolved
After grace period, unresolved downstream refs → surfaced as tensions.
Active intent depending on deprecated intent = structural inconsistency.

## Schema Versioning

manifest.yaml.schema_version declares which core schema version the repo uses.
When core schema evolves (new required fields, changed semantics), schema_version bumps.
Migration tooling reads this field to determine transformations needed.
