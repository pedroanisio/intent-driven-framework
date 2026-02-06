# Intent Framework — Product Strategy Domain

## Status

**Version**: 0.0.0 (Not yet started)
**Structural Fit**: HIGH
**Type**: Proposed pilot

## Thesis

Product teams already maintain intent-like artifacts — OKRs, north stars, principles — but these are disconnected from the decisions they govern. The Intent Framework can make product intent explicit, versioned, and traceable.

A product strategy intent declares what the product is committed to becoming:
- `declares: "Checkout conversion above 4%"` (measurable goal)
- `declares: "Users never wait > 1 second for payment response"` (performance commitment)
- `declares: "Product will never support fraud"` (principle)

These live in tension with each other. When they conflict, the **resolution_owner** decides. That decision is logged as a transition.

## Key Differences from Software

| Aspect | Software | Product |
|--------|----------|---------|
| **Authority** | Engineering | Product Manager, exec leadership |
| **Scope** | Code paths | User journeys, features, areas |
| **Verification** | Automated | Metric-based (analytics) |
| **Confidence** | High (code is visible) | Medium (market data is noisy) |
| **Tension example** | Performance vs. Correctness | Growth vs. Risk, Speed vs. Quality |

## What Needs to Happen

1. **Pick a product** — internal or external, early-stage or mature
2. **Identify current north stars** — what does the team actually care about?
3. **Declare them as intent blocks** — version 1.0.0
4. **Capture tensions** — where do goals compete?
5. **Document transitions** — when did strategy shift and why?
6. **Verify with metrics** — does intent match actual behavior?

## Example Intent

```yaml
intent:
  id: product-checkout-conversion
  version: 1.0.0
  declares: "Checkout conversion will reach 4% by Q3 2024"
  intent_type: aspirational
  current_reality:
    description: "Currently at 2.1% across all channels"
    gaps: ["Mobile conversion is 1.5%, needs UX redesign"]
  achieved_coverage: minimal

  scope:
    - checkout/ (all checkout flows)
    - payment-processing/
    - fraud-detection/ (tension: growth vs. fraud prevention)

  tensions:
    - ref: product-fraud-protection
      description: "Aggressive fraud rules hurt conversion; lenient rules hurt risk"
      resolution_strategy: "Accept 0.01% fraud loss to hit 4% conversion"
```

## Candidate Products to Pilot

### Internal Product (Low risk, high control)
- Team's own project or internal tool
- **Advantage**: Full control, can create retrofit intents
- **Challenge**: Limited external verification

### Public Early-Stage Product (Medium risk)
- Open-source project, startup MVP, beta feature
- **Advantage**: Real market signal, motivated team
- **Challenge**: Rapid change outpaces version cycles

### Mature Product (High risk, high value)
- Established SaaS, mobile app, platform
- **Advantage**: Clear constraints, historical data
- **Challenge**: Retroactively declaring intent is hard

## Getting Started

1. Create `prose/intent-spec-product.md` — how product specializes the model
2. Pick one product (suggest: internal tool or open-source project)
3. Document 3-5 north stars as intent blocks
4. Run 3-6 months of normal product work
5. Track what was declared vs. what happened
6. Write lessons learned: did intent tracking help?

## Questions to Answer

- Does versioning product intent help teams make better decisions?
- Does tension declaration prevent repeated fights over the same tradeoff?
- Does `achieved_coverage` tracking motivate teams?
- Does the framework slow down rapid iteration?
- Can product teams maintain this without engineering tooling?
