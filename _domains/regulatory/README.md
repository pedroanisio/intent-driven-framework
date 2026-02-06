# Intent Framework — Regulatory Compliance Domain

## Status

**Version**: 0.0.0 (Not yet started)
**Structural Fit**: HIGH
**Type**: Proposed pilot

## Thesis

Compliance requirements are intents imposed by external authorities. They have:
- **Versions** — regulatory amendments, notice periods, grace periods
- **Transitions** — drafting → enforcement → supersession (like the general lifecycle)
- **Tensions** — compliance cost vs. business agility; safety requirements vs. operational simplicity
- **Residual artifacts** — processes shaped by rules that were superseded years ago
- **Deprecation** — sunset provisions with grace periods

This domain is structurally high-fit for the Intent Framework because the core mechanic (declare → version → transition → tension → verify) maps directly to regulatory governance.

## Key Differences from Software

| Aspect | Software | Regulatory |
|--------|----------|-----------|
| **Authority** | Internal | External (law, regulator) |
| **Scope** | File globs, code modules | Clause references, section numbers |
| **Verification** | Automated (code analysis, CI) | Human audit, compliance report |
| **Version semantics** | Semver | Regulatory numbering (varies) |
| **Confidence** | Built from code inspection | Built from policy + audit trail |

## What Needs to Happen

1. **Identify a concrete target** — WCAG (accessibility), GDPR (data privacy), SOC 2 (security audit), PCI-DSS (payment), etc.
2. **Extract intent declarations** — for each requirement, write a falsifiable intent statement
3. **Build a criteria set** — adapt the 28 general criteria for regulatory context
4. **Create a manifest** — minimal viable intent repository for the target standard
5. **Verify the transfer** — does the five-layer stack work on compliance intents?

## Candidate Standards

### WCAG 2.1 (Accessibility)
- **Scope**: 50+ success criteria across 4 principles
- **Applicability**: Governs product requirement, design, QA, documentation
- **Example intent**: `id: wcag-2.1-1.4.3-contrast-minimum`, `declares: "All text has a contrast ratio of at least 4.5:1"`
- **Verification**: Automated tools exist (WAVE, Axe); human judgment required

### GDPR (Data Privacy)
- **Scope**: 7 chapters, 99 articles
- **Applicability**: Governs data collection, retention, processing, deletion
- **Example intent**: `id: gdpr-article-7-consent`, `declares: "User consent is explicit, revocable, and documented"`
- **Verification**: Policy + audit trail

### SOC 2 Type II (Trust Services)
- **Scope**: 5 trust principles (CC = Common Criteria)
- **Applicability**: Governs operations, security, availability, processing integrity, confidentiality, privacy
- **Example intent**: `id: soc2-cc-security-1`, `declares: "Organization operates in accordance with a defined risk management framework"`
- **Verification**: Human audit, evidence collection

## Getting Started

1. Create `prose/intent-spec-regulatory.md` explaining domain specialization
2. Choose one standard (suggest: **WCAG 2.1** — smallest, most automatable, concrete)
3. Extract 5-10 key requirements as intent blocks
4. Write minimal `intent-regulatory-v0.1.0.yml`
5. Test with general tools: validate, score, NLP check
6. Document what transferred vs. what broke

## Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/) — starting point for accessibility domain
- [GDPR Regulation](https://gdpr-info.eu/) — full text, well-structured
- [SOC 2 Trust Principles](https://us.aicpa.org/interestareas/informationsystems/auditabilitycenter/downloads/trust-services-criteria)
