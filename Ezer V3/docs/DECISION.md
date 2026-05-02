# Ezer — Architecture Decision Record

## Why This Document Exists

Ezer failed twice before V3. This document captures what failed, why, and what decisions were made to prevent the same failures again. Every architectural decision in V3 flows from these lessons.

---

## Attempt 1 — Ezer V1

**What was built:** A claim settlement and denial navigation tool. FastAPI backend, frontend screens, argument engine.

**What failed:** The product tried to do too much too fast. Settlement and denial handling was attempted before a reliable policy understanding layer existed. The backend could not support what the frontend was trying to show. The requirements were not clear enough — Ezer was trying to solve too many problems at once.

**Root cause:** Wrong sequence. Claim navigation cannot be built on top of an unreliable policy understanding layer.

**Lesson:** Policy understanding must precede claim navigation. This sequence is non-negotiable.

---

## Attempt 2 — Ezer V2

**What was built:** An LLM-based policy extraction engine. Upload a PDF, extract structured data using Claude, feed into a decision engine.

**What failed:** LLM extraction proved fundamentally unreliable for insurance documents:
- Hallucinated values that were not in the document
- Flattened conditional language — converted "covered unless X" into "covered"
- Lost table structure — waiting period tables became flat text
- Generated garbage citations — cited clauses that did not exist
- Produced probabilistic output for a domain that requires determinism

**Root cause:** Wrong approach. Insurance policy schedules are legal documents. Every word matters. A probabilistic extraction engine cannot serve as the foundation for a tool that influences financial decisions.

**Lesson:** LLM-based broad extraction is not viable for insurance. Structured, surgical, human-verified approaches are necessary.

---

## V3 Architecture — The Ezer Way

### Core Principle
**Determinism over flexibility.** A confident wrong answer is worse than an honest low-confidence signal. The architecture must reflect this at every layer.

### Tiered Hybrid Architecture

**Tier 1 — Verified Product Library**
- One JSON file per insurance product
- Pure product rules — no user data
- Curated by humans, verified against actual policy wording
- Shared across every user who uploads that product
- Confidence tag: 🟢 Verified

**Tier 2 — User Schedule**
- One JSON file per policy number
- User-specific data only — SI, PEDs, waiting periods, active addons, premium
- Linked to Tier 1 via `product_library_ref`
- Curated by humans from the issued policy schedule
- Confidence tag: 🟡 Extracted

**Tier 3 — Derived Insights (Runtime)**
- Computed at runtime by joining Tier 1 + Tier 2
- Not stored permanently
- Three insight types:
  - Active features — "You have X and here is what it means"
  - Gap features — "You don't have Y and here is what you are missing"
  - Schedule integrity flags — "There is a problem with Z"

**Tier 4 — Fallback (Experimental)**
- For unrecognized policies not in the library
- Broader LLM extraction with heavy "Experimental / Low Confidence" warning
- Confidence tag: 🔴 Experimental

### Confidence Provenance
Every insight carries a confidence tag indicating which tier produced it. Users always know how reliable an insight is. Silent failures are not acceptable.

### File Naming Convention
```
product_library_{insurer}_{product_name}.json
user_schedule_{policy_number}_{insured_name}.json
```

---

## What V3 Does NOT Do (Yet)

- No claim settlement analysis at launch
- No denial navigation at launch
- No LLM extraction from raw PDFs at launch
- No frontend at launch
- No database at launch

These will be added after the policy understanding layer is solid. The sequence lesson from V1 applies.

---

## Current Library — As of April 2026

### Tier 1 — Product Libraries
| File | Product | Status |
|------|---------|--------|
| product_library_hdfc_optima_secure.json | HDFC ERGO my:Optima Secure UIN: HDFHLIP25041V062425 | ✅ Curated |
| product_library_hdfc_optima_restore.json | HDFC ERGO Optima Restore UIN: HDFHLIP26055V102526 | ✅ Curated |

### Tier 2 — User Schedules
| File | Insured | Policy No | Product |
|------|---------|-----------|---------|
| user_schedule_2856205213169603000_badal.json | Badal Satapathy | 2856205213169603000 | Optima Secure |
| user_schedule_2856205213224703000_kajal.json | Kajal Satapathy | 2856205213224703000 | Optima Secure |
| user_schedule_2805207151903301000_gupta_prasad.json | Gupta Prasad Satapathy | 2805207151903301000 | Optima Restore |
| user_schedule_2805207149369401001_basanti.json | Basanti Satapathy | 2805207149369401001 | Optima Restore — corrected schedule |

---

## What Gets Built Next — In Order

1. ~~Insight Engine~~ ✅ Done — classification, grouping, summary, action outputs, draft letters
2. ~~Schedule Integrity Checker~~ ✅ Done — flags surface in engine, correction letter generated
3. ~~PED Quality Checker~~ ✅ Done — ICD vagueness flags, clarification letter generated
4. ~~Policy Evolution Timeline~~ ✅ Done — V3.1 Sprint A
5. ~~Renewal Guidance Layer~~ ✅ Done — V3.1 Sprint A
6. ~~Coverage Maturity Score~~ ✅ Done — V3.1 Sprint B
7. FastAPI endpoint — wraps the engine, single-policy mode
8. Correspondence Tracker — tracks open items, Ombudsman-aware
9. Claim navigation features — only after the above are solid

## Architecture Decision — V3.1 Sprint A (Logged 2026-04-29)

- Policy is treated as an evolving system, not a static document
- Policy Evolution Timeline: waiting period milestones sorted chronologically using datetime objects
- Renewal Guidance: gap-based recommendations for inactive features, qualitative framing only
- `suggested_action` field added to all WARNING insights for imperative NBA derivation
- RESOLVED flags suppressed from engine output — preserved in JSON as institutional memory

## Architecture Decision — V3.1 Sprint B (Logged 2026-04-30)

**The Fortress Philosophy:**
- Structural Maturity (DEVELOPING / MATURING / MATURE) and Functional Strength (WEAK / MODERATE / STRONG) are separate dimensions. They must never be conflated.
- Maturity = how evolved the contract is (waiting period clocks)
- Strength = how much clean SI is available today (Clean SI ratio)

**The 75% Clean SI Rule:**
- If ≥75% of total SI is clean (no running waiting periods, fully accrued bonuses), the policy is rated STRONG or MODERATE in Strength
- A ₹5L enhancement cooking does not weaken a ₹60L fortress
- Action override is absolute: any open ACTION → WEAK regardless of Clean SI ratio

**The Accrual Gate:**
- Bonus SI (Plus Benefit, Multiplier Benefit) counts toward Clean SI only when `status == "fully_accrued"`
- Partially accrued bonuses are potential assets, not clean assets

**The Senior Exception:**
- Insurers informally decline certain riders (e.g. URB) for elderly policyholders without written grounds
- This is captured as `rider_ineligible_due_to_age` in Tier 2 (user schedule) — a human-curated field
- The engine reads this flag and skips the MATURE penalty for that rider
- No hardcoded age logic in the engine — the curator decides case by case

**Fortress Detection:**
- The largest SI block is the fortress (base block)
- Smaller blocks are treated as enhancements
- Detection hierarchy: explicit `si_enhanced` flag → "enhanced" in block_id → smaller than largest block

## Architecture Decision — V3.2 Settlement Advocate (Logged 2026-05-02)

**The Two-Layer Audit:**
- Layer 1 (Invisible Loss): hospital billing irregularities paid by insurer without audit
- Layer 2 (Visible Loss): insurer deductions the patient receives but cannot interpret
- Total Asymmetry Payload = Layer 1 + Layer 2
- These two layers are always computed and displayed separately — never merged

**Curated JSON over PDF Extraction:**
- Settlement data is human-curated into JSON — same approach as policy schedules
- No LLM extraction — reliability non-negotiable in insurance adjudication
- Every line item verified against settlement letter before entry

**The Decision Gate — Three Routes:**
- Route is determined entirely from Tier 2 user schedule — no user input ever required
- Route A: rider active → grievance letter (insurer wrongly deducted)
- Route B: rider inactive + age flag → gap awareness (honest, no false promise)
- Route C: rider inactive + no age flag → renewal action (financial case for rider)

**Route B over Route A for Age-Ineligible Users (Deliberate Choice):**
- When `rider_ineligible_due_to_age` flag is present, engine does not suppress the recovery amount
- Shows ₹7,017 lost AND explains why rider may not be available at renewal
- Honest gap awareness over false promise of recovery
- This was Option B in a design discussion — chosen over Option A (suppress simulation) deliberately
- Reason: even if rider is unavailable, the financial proof of its absence has negotiation value

**PII Guardrail:**
- Patient name and account number are read for internal processing only
- Never written to any output file or terminal
- Claim reference and hospital name are institutional identifiers — included in memos

**Pydantic Full Contract Validation:**
- All enums validated on load — hard gates on EzerClassification, InsurerAction, FlagType, ContestTarget
- Engine refuses to run on invalid data — no silent failures acceptable in insurance context

**Ezer Closes Information Asymmetry — Does Not Chase Claims:**
- Ezer informs. User acts.
- Engine generates letters and memos. User decides whether to send.
- No automatic filing, no claim tracking, no Ombudsman automation

---

*Last updated: 2026-05-02*
*Author: Badal Satapathy*
