# Intent Framework — Organizational Governance Domain

## Status

**Version**: 0.0.0 (Not yet started)
**Structural Fit**: MEDIUM
**Type**: Proposed pilot

## Thesis

Cross-department tensions are the operating system of an organization. Sales wants customization; engineering wants standardization. Legal wants caution; product wants speed. Finance wants cost control; operations wants reliability.

These tensions are currently:
- **Invisible** — resolved ad hoc in meetings
- **Re-litigated** — the same fight happens quarterly when someone forgets the last resolution
- **Dependent on institutional memory** — when the person who last decided leaves, the decision evaporates

The Intent Framework can make organizational tensions explicit, versioned, and traceable. Each tension has a **resolution_owner** who can change the strategy when conditions change — but the history is preserved.

## Key Differences from Software

| Aspect | Software | Governance |
|--------|----------|-----------|
| **Authority** | Engineers | Executives, department heads |
| **Scope** | Code modules | Departments, functions, processes |
| **Verification** | Automated | Social/political execution |
| **Confidence** | High (code is visible) | Low (execution is opaque) |
| **Enforcement** | Technical (CI/CD gates) | Human (policy, incentives) |

## Example: Sales vs. Engineering Tension

```yaml
tension:
  id: org-customization-vs-standardization
  description: |
    Sales wins customers with bespoke features.
    Engineering needs standardization to maintain product.

    High customization → more revenue, higher cost.
    High standardization → lower cost, slower growth.

  resolution_owner: product-leadership

  strategy: |
    v1.0.0: Customize on request (Sales wins) — cost was acceptable
    v1.1.0: Ban custom features (Engineering wins) — caused revenue drop
    v1.2.0: Plugins + configuration, no code (both win) — found the tradeoff
    v1.3.0: Strategic customers get customization (Revenue + cost)

  transition_log:
    - from: v1.0.0
      to: v1.1.0
      date: 2023-Q1
      forcing_function: scalability-crisis

    - from: v1.1.0
      to: v1.2.0
      date: 2023-Q3
      forcing_function: revenue-drop
```

## The Political Challenge

This domain's core challenge is not technical — it's **political**.

- **Software domain**: The framework is credible because tooling enforces it (CI/CD gates, code review, tests)
- **Governance domain**: The framework is only as credible as the resolution_owner's willingness to enforce it

**Blocker**: Does the model add value when enforcement is social, not technical?

## What Needs to Happen

1. **Identify real organizational tensions** — what does your leadership debate every quarter?
2. **Declare them explicitly** — version 1.0.0
3. **Name the resolution_owner** — who actually decides?
4. **Log transitions** — when and why did the strategy change?
5. **Measure outcomes** — did explicit intent + versioning help?

## Candidate Organizations to Pilot

### Internal Department (Low risk)
- Engineering vs. Product
- Design vs. Engineering
- **Advantage**: Full control, safe to experiment
- **Challenge**: Low stakes, easy to abandon

### Startup (Medium risk)
- Cross-functional founders
- Early growth phase
- **Advantage**: Rapid iteration, all stakeholders visible
- **Challenge**: Chaos; hard to maintain formality

### Established Org (High risk, high value)
- Multiple departments, complex incentives
- **Advantage**: Real tensions, clear ROI if model helps
- **Challenge**: Skepticism, political resistance

## Getting Started

1. Create `prose/intent-spec-governance.md` — how governance specializes the model
2. Identify 3 real organizational tensions
3. Declare them as tension blocks (no resolution yet)
4. Choose a resolution_owner for each
5. Let them run for 3-6 months with versioned strategies
6. Measure: fewer re-litigations? Better decisions? Political acceptance?

## Open Questions

- Can explicit tension declaration reduce re-litigation?
- Does versioning a strategy make it easier to revisit and improve?
- Is transparency about tradeoffs (naming both sides of tension) politically viable?
- Does the framework help organizations onboard new leaders (institutional memory)?
- What happens when the resolution_owner refuses to update the strategy despite changed conditions?
