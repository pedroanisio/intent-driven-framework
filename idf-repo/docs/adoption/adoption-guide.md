# Adoption Guide — Intent Driven Framework

This guide provides an ordered, actionable adoption sequence (CC-13)
that does not require a comprehensive legacy audit (CC-14).

## Adoption Sequence

1. **Install the IDF structure** — Run `python idf_init.py <your-repo>`.
   This creates the directory tree, schemas, and tooling stubs.

2. **Declare your first intent** — Copy
   `intents/aspirational/_template.yml` and fill in the `declares` field.
   Start with whatever pain point prompted you to look at IDF.

3. **Add CI validation** — Wire `tools/ci/validate.py` into your
   CI pipeline. Start in advisory mode (exit 0 on errors).

4. **Adopt the next-touch rule** — When touching a file, check if an
   intent governs it. If not, declare one. This is advisory at first
   (CC-21 adoption ramp).

5. **Transition to enforcement** — After a defined ramp period, switch
   CI validation to blocking (exit 1 on errors).

6. **Record tensions** — When two intents conflict, create a tension
   file in `tensions/`. Don't resolve prematurely.

7. **Iterate** — Review intents periodically. Promote aspirational
   intents to achieved when all commitments are met and verified.

## Three Entry Points (CC-15)

### Pain-First
Start with the intent that addresses your most pressing problem.
Don't try to be comprehensive — declare one intent for one pain point.

### Next-Touch
Every time you open a file, check if an intent governs it. If not,
declare one. Coverage grows organically with development activity.

### Amnesty
Declare aspirational intents for entire subsystems without auditing
existing code. The `current_reality` block captures the gap honestly.
No archaeology required (CC-14).

## Adoption Ramp (CC-21)

The next-touch rule starts as **advisory** (non-blocking) for a team-defined
period. This addresses the cold-start problem: on a legacy codebase with
zero declared intents, "every PR must reference an intent" would block
every PR until someone does the archaeology.

The transition from advisory to enforcement should be explicit and communicated.
