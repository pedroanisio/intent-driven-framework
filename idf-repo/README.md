# Intent Driven Framework — Repository

Initialized with IDF v1.7.0 / schema v0.1.0

## Structure

```
prose/                    # Philosophy and specification
  intent-manifesto.md     # CC-01, CC-02, CC-03
  intent-spec-core.md     # Core data model
criteria/                 # Completeness criteria
schemas/                  # YAML schemas (CC-04–CC-08)
  enums.yml               # Canonical enums (CC-05)
  intent-aspirational.yml # Aspirational intent schema
  intent-achieved.yml     # Achieved intent schema
intents/                  # Declared intents
  aspirational/           # Intents with gaps
  achieved/               # Fully met intents
tensions/                 # Declared tensions (CC-08a–CC-08c)
decisions/                # Decision records
transitions/              # Transition records
plugins/                  # Plugin manifests (CC-11, CC-12)
  examples/               # Worked examples
tools/                    # Tooling surface (CC-20)
  ci/                     # CI validation
  hooks/                  # Lifecycle hooks (CC-07)
lean/                     # Formal verification
tests/                    # Test suites
docs/                     # Guides and references
  adoption/               # Adoption guide (CC-13–CC-15, CC-21)
  failure-modes/          # Failure mode catalogue (CC-26)
```

## Quick Start

1. Read `docs/adoption/adoption-guide.md`
2. Copy `intents/aspirational/_template.yml` to declare your first intent
3. Run `python tools/ci/validate.py intents/` to validate
4. See `docs/daily-practice.md` for day-to-day workflow

## Validation

```bash
pip install pyyaml
python tools/ci/validate.py intents/
```
