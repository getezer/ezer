# Ezer V3 — Current State
*As of 2026-05-02*
- Scope: Supports only curated products (2) — deterministic mode

## Fully Working

### Insight Engine (V3.1)
- Deterministic insight engine running against 4 real user schedules
- 2 product libraries curated (HDFC ERGO Optima Secure, Optima Restore)
- Zero LLM dependency in runtime logic
- Active feature insights, gap insights, waiting period insights, PED quality flags
- Schedule integrity error detection (phantom blocks, underwriting errors)
- Moratorium protection, post-hospitalisation coverage awareness
- Policy Evolution Timeline — chronological milestones per user
- Renewal Guidance Layer — gap-based recommendations
- Coverage Maturity Score — DEVELOPING / MATURING / MATURE
- Strength via Clean SI Ratio — WEAK / MODERATE / STRONG
- Draft letters for schedule correction and PED clarification
- NBA using `suggested_action` field — imperative, not descriptive
- RESOLVED flags suppressed from output

### Audit Engine (V3.2)
- Pydantic full contract validation — hard enum gates on all classifications
- Integrity check: ±₹0.01 tolerance + GST rounding warning (ternary state)
- Asymmetry Payload: Layer 1 (hospital flags) + Layer 2 (insurer deductions)
- Rider simulation: recalculates settlement with rider active
- Talking memo data prep: plain English + evidence required per flag
- PII guardrail: patient name and account number never written to output

### Symmetry Report Generator (V3.2)
- Three-route Decision Gate: A (Grievance) / B (Gap Awareness) / C (Renewal Action)
- Route determined from Tier 2 user schedule — no user input required
- Document 1: Hospital Irregularity Memo — always generated
- Document 2: Settlement Comparison — actual vs Ezer view
- Document 3: Rider Output — route-dependent
- Reports saved to `reports/{claim_id}/`

### Real-World Outcomes
- Outcome 1: Basanti phantom SI block → HDFC ERGO corrected same day
- Outcome 2: Gupta Prasad ICD vagueness → written protective response obtained
- Outcome 3: Gupta Prasad Urolift — ₹1,04,908.81 asymmetry payload computed

### Unit Tests
- `tests/test_routing.py` — 3/3 routing scenarios verified deterministic

---

## Known Limitations

- No API endpoint — engines run as local Python scripts only
- No UI — terminal output and text files only
- Tier 1 library covers 2 products only
- Settlement data is human-curated — no PDF extraction
- Route A not yet tested against a real active-rider claim

---

## Immediate Next Steps

1. FastAPI endpoint — wrap insight engine and audit engine
2. React frontend — Settlement Advocate UI
3. Real Route A test — active-rider claim needed
4. Cystoscopy settlement JSON — second GPS claim

---
*Insight Engine: production-ready for supported products.*
*Audit Engine: production-ready for curated settlement data.*
