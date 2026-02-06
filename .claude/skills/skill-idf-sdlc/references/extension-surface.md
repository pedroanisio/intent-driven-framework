# IDF SDLC v1.7.0 — Extension Surface

## Plugin Registry

`_repo/plugins/registry.yaml` — declares active plugins and enforcement level:

```yaml
plugins:
  - name: compliance
    version: 1.2.0
    required: true       # CI fails if this plugin's validations fail

  - name: observability
    version: 1.0.0
    required: false      # advisory only
```

## Plugin Manifest

Each plugin declares what it extends and what it registers:

```yaml
plugin:
  name: compliance
  version: 1.2.0
  description: "Adds regulatory compliance tracking to intents"

  extends:
    intent:                    # adds fields under ext.compliance
      frameworks: string[]
      audit_required: boolean
      last_audit: datetime
    transition:                # plugins can extend any core entity
      compliance_review: boolean
      reviewer: string

  registers:
    validators: validators.yaml
    hooks: hooks.yaml
    relations: relations.yaml
```

## Extension Fields in Practice

An intent with multiple active plugins:

```yaml
intent:
  id: intent-payment-idempotency
  version: 2.0.0
  declares: "Payment processing must be idempotent across retries"
  scope: [src/payments/processing/**]
  status: active

  ext:
    compliance:
      frameworks: [PCI-DSS, SOX]
      audit_required: true
      last_audit: 2025-01-15
    observability:
      sli: "duplicate_payment_rate < 0.001%"
      dashboard: "https://grafana.internal/payments/idempotency"
      alert_threshold: "0.0005%"
    org-acme:
      business_unit: payments-core
      cost_center: CC-4200
      executive_sponsor: jane.doe
```

Core schema knows nothing about these namespaces. Each is owned, validated,
and ignored-by-default per CC-12.

## Validation Plugins

Plugin-contributed rules run alongside core CI validation:

```yaml
validators:
  - rule: >
      intents with ext.compliance.frameworks containing 'PCI-DSS'
      must have priority: critical
  - rule: >
      intents with scope crossing domain boundaries must declare
      at least one tension
  - rule: >
      active intents with ext.compliance.audit_required: true
      must have ext.compliance.last_audit within 365 days
```

## Relation Type Plugins

Core relations: serves, tensions, supersedes. Plugins can register new edge types:

```yaml
relations:
  - type: constrains_training
    from: intent
    to: intent
    description: >
      This intent places constraints on how models trained in this scope can be used
  - type: data_lineage
    from: intent
    to: intent
    description: >
      Data shaped by this intent feeds into the scope of another intent
```

Tools that understand the edge type traverse it. Others see a simpler graph.

## Lifecycle Hooks

Core emits events. Plugins subscribe in hooks.yaml:

```yaml
hooks:
  on_intent_proposed:
    - action: check_regulatory_impact
  on_intent_major_bump:
    - action: scan_downstream_repos
  on_intent_superseded:
    - action: flag_residual_dashboards
  on_intent_stale:                    # last_affirmed exceeds threshold
    - action: schedule_compliance_review
  on_tension_resolution_stale:        # staleness contract trigger
    - action: notify_resolution_owner
```

The lifecycle is an event bus. Core emits. Plugins react. Core never inspects responses.
