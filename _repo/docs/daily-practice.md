# Daily Practice — Intent Driven Framework

Concrete behavioral instructions for day-to-day development (CC-17).

## When to Declare
- Before starting a new feature or subsystem
- When you discover an implicit architectural commitment
- When a post-mortem reveals an unspoken assumption

## When to Link
- Every PR should reference at least one intent (after ramp period)
- When adding a dependency between subsystems, link the relevant intents
- When a test failure reveals an intent violation

## When to Record
- Record a tension when two intents conflict
- Record a decision when resolving a tension or making a trade-off
- Record a transition when an intent's version or status changes

## When to Check
- During code review: does this change align with governing intents?
- During CI: does the intent YAML validate against the schema?
- During retrospectives: are intents still current? Any drift?
- After a major bump: are tension resolutions still valid? (CC-23)
