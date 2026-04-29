# Ezer V3 — Current State
*As of 2026-04-29*
- Scope: Supports only curated products (2) — deterministic mode

## Fully Working

### Engine
- Deterministic insight engine running against 4 real user schedules
- 2 product libraries curated (HDFC ERGO Optima Secure, Optima Restore)
- Zero LLM dependency in runtime logic
- Correct output every run — no hallucination, no ambiguity

### Insight Generation
- Active feature insights (Unlimited Restore, Protect Benefit, Secure Benefit, Plus/Multiplier)
- Gap feature insights (missing riders, missing addons)
- Waiting period insights by SI block with expiry dates
- PED waiting period insights by block and condition
- PED quality flags (ICD vagueness, contestation risk)
- Schedule integrity error detection (phantom blocks, underwriting errors)
- Moratorium protection status
- Post-hospitalisation coverage awareness

### Classification
- Every insight carries: type (ACTION / WARNING / INFO) and priority (HIGH / MEDIUM / LOW)
- Classification is consistent — same insight type always gets same classification

### Output Layer
- Policy summary block: strength (WEAK / MODERATE / STRONG), counts, Next Best Action
- Three grouped sections: Immediate Actions → Risks & Warnings → Coverage & Benefits
- Within sections: sorted HIGH → MEDIUM → LOW
- Empty sections hidden
- Draft letters generated for schedule correction and PED clarification

---

## Partially Working

- Next Best Action for WARNING insights uses "Be aware:" prefix — descriptive, not imperative
- Waiting period insights for Badal and Kajal show three separate entries for two ₹5L blocks — technically correct but slightly repetitive
- `suggested_action` field on WARNING insights not yet implemented

---

## Known Limitations

- No policy evolution layer — cannot show how coverage changes over time
- No renewal guidance — no "what to do at next renewal" output
- No API endpoint — engine runs as a local Python script only
- No UI — terminal output only
- Tier 1 library covers 2 products only — any other policy falls to Tier 4 (not yet built)
- Tier 4 fallback (LLM extraction for unknown policies) not yet implemented

---

## Immediate Next Step

- Build Policy Evolution Timeline layer (V3.1)
  - Milestone view: which waiting periods expire when
  - Which PEDs become claimable on which blocks and when
  - Renewal guidance: what to add, what decisions to make before renewal date

---
*System is stable. Engine is production-ready for supported products.*
