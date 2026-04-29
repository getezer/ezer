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
| user_schedule_2805207149369401000_basanti.json | Basanti Satapathy | 2805207149369401000 | Optima Restore |

---

## What Gets Built Next — In Order

1. ~~Insight Engine~~ ✅ Done — classification, grouping, summary, action outputs, draft letters
2. ~~Schedule Integrity Checker~~ ✅ Done — flags surface in engine, correction letter generated
3. ~~PED Quality Checker~~ ✅ Done — ICD vagueness flags, clarification letter generated
4. Policy Evolution Layer (V3.1) — waiting period milestones, renewal guidance, coverage maturity
5. FastAPI endpoint — wraps the engine, single-policy mode
6. Correspondence Tracker — tracks open items, Ombudsman-aware
7. Claim navigation features — only after the above are solid

## Architecture Decision — V3.1 (Logged 2026-04-29)

- Policy is treated as an evolving system, not a static document
- V3.1 adds a lifecycle view: how coverage changes over time as waiting periods expire
- Renewal guidance layer: what to add at next renewal and why
- Coverage maturity indicator: time-resolving gaps vs action gaps vs renewal gaps
- This is the next layer after the insight engine — not claim navigation yet

---

*Last updated: 2026-04-29*
*Author: Badal Satapathy*
