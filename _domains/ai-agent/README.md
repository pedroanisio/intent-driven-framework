# Intent Framework — AI Agent Guardrails Domain

## Status

**Version**: 0.0.0 (Not yet started)
**Structural Fit**: MEDIUM
**Type**: Proposed pilot

## Thesis

An AI agent operating within a scope governed by declared intents gains **semantic boundaries** it can reason about. Rather than "do what the user asks" (unbounded) or "refuse everything unexpected" (brittle), the agent can evaluate: "Does my proposed action violate any intent governing this scope?"

Intent declarations become the **semantic contract** between the system designer and the agent. The agent self-verifies against declared boundaries before acting.

## Key Differences from Software

| Aspect | Software | AI Agent |
|--------|----------|----------|
| **Authority** | Engineers | System designers + safety team |
| **Scope** | Code paths | Agent capabilities, decision domains |
| **Verification** | CI/CD time | Real-time (before action execution) |
| **Falsifiability** | Code inspection | LLM evaluation (probabilistic) |
| **Confidence** | Deterministic | Probabilistic (theme: "I'm 87% confident this violates intent") |

## Falsifiability in the Agent Context

The general spec requires **falsifiable** intent declarations:

```yaml
declares: "Agent never executes DELETE operations on user data"
```

In software, this is verified by code analysis.
In an agent, this must be evaluable by LLM:

```python
agent.evaluate_intent_compliance(
  intent="Agent never executes DELETE operations on user data",
  proposed_action="DELETE FROM users WHERE id=123",
  confidence_threshold=0.9  # must be 90%+ confident
)
# Returns: (compliant=False, confidence=0.98, reasoning="...")
```

## Example Intent for an Agent

```yaml
intent:
  id: agent-customer-support-scope
  version: 1.0.0
  declares: |
    Agent supports only: account lookup, password reset, refund requests.
    Agent refuses: product design feedback, sales negotiations, API key generation.

  scope:
    - agent-decision-boundary/customer-support/
    - authorized-actions: [account_lookup, password_reset, refund_request]

  tensions:
    - ref: agent-helpfulness-vs-safety
      description: "User asks agent to override scope; helpful would violate boundary"
      resolution_strategy: "Politely decline and offer in-scope alternatives"
```

## Challenge: The Gap

**Declared in principle**: "Agent never executes DELETE"
**Mechanically evaluable**: Hard. An LLM must reason: does this action logically amount to deletion?

The distance between "falsifiable intent" and "mechanically evaluable by an LLM" is nontrivial. This domain tests whether the Intent Framework can bridge it.

## What Needs to Happen

1. **Pick a real agent** — chatbot, code assistant, autonomous system
2. **Declare its operating boundaries** — what IS it authorized to do?
3. **Test the model** — does the agent respect declared intent?
4. **Measure false positives** — does it over-refuse?
5. **Measure false negatives** — does it under-catch violations?
6. **Evaluate utility** — is intent-based governance better than hardcoded rules?

## Candidate Agents to Pilot

### Internal Chatbot (Low risk)
- Customer support, employee Q&A
- **Advantage**: Safe scope, simple verification
- **Challenge**: Low stakes, may not reveal real issues

### Code Assistant (Medium risk)
- Code generation, debugging, refactoring
- **Advantage**: Clear logical boundaries
- **Challenge**: High false positive/negative rates likely

### Autonomous Tool (High risk, high value)
- Autonomous ticket resolution, workflow automation
- **Advantage**: Real cost/benefit measurable
- **Challenge**: Safety-critical

## Getting Started

1. Create `prose/intent-spec-ai-agent.md` — how guardrails specialize the model
2. Pick an agent (suggest: internal chatbot)
3. Declare 5-10 scope boundaries as intent blocks
4. Implement `evaluate_intent_compliance()` function (use Claude API)
5. Log all evaluations: what did it refuse? What did it allow?
6. Measure: accuracy, false positives, false negatives, user friction

## Open Questions

- Can LLM evaluation be reliable enough for safety-critical decisions?
- What confidence threshold is needed for different risk levels?
- Does intent-based guardrailing add value vs. simpler rule-based approaches?
- How much does over-refusing (false positives) hurt user experience?
- Can the agent explain its reasoning back to users in terms of declared intent?
