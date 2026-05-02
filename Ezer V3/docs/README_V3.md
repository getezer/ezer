# Ezer V3

> "After a user uploads their policy, they should get critical non-obvious insights that influence their decisions — not just extracted text."

Ezer is an insurance policy decoder that gives power back to buyers. This is V3 — built after two failed attempts. Read `docs/DECISION.md` to understand why V3 is architected the way it is.

---

## What Ezer V3 Is

A **deterministic, rule-based insight engine** that joins verified product rules with user-specific schedule data to produce plain-language insights about a health insurance policy.

This is NOT a policy extraction tool. It is a decision support tool built on verified policy data.

---

## Architecture — The Ezer Way

### Tier 1 — Verified Product Library
One JSON file per product. Pure product rules. Curated by humans against actual policy wording. Shared across every user of that product.

### Tier 2 — User Schedule
One JSON file per policy number. User-specific data — SI, PEDs, waiting periods, active addons, premium. Linked to Tier 1 via `product_library_ref`.

### Tier 3 — Derived Insights (Runtime)
Computed by the Insight Engine at runtime by joining Tier 1 + Tier 2. Not stored permanently.

### Tier 4 — Fallback (Experimental)
For unrecognized policies. LLM extraction with heavy low-confidence warning.

### Confidence Tags
- 🟢 Verified — from Tier 1 library
- 🟡 Extracted — from Tier 2 user schedule
- 🔴 Experimental — from Tier 4 fallback

---

## Folder Structure

```
Ezer V3/
├── data/
│   ├── product_library/     ← Tier 1 JSON files
│   ├── user_schedules/      ← Tier 2 JSON files
│   └── settlements/         ← Settlement data (V3.2)
├── engine/
│   ├── insight_engine.py    ← V3.1 Insight Engine
│   ├── audit_engine.py      ← V3.2 Audit Engine
│   └── symmetry_report.py   ← V3.2 Report Generator
├── tests/
│   └── test_routing.py      ← V3.2 Unit Tests
├── reports/                 ← Generated report output
│   └── GPS_RR_HS25_15050055/
│       ├── hospital_memo.txt
│       ├── settlement_comparison.txt
│       └── rider_output.txt
├── api/                     ← FastAPI endpoints (not yet built)
└── docs/
    ├── DECISION.md
    ├── README_V3.md
    ├── PRD_V3.1.md
    ├── PRD_V3.2.md
    ├── TDD_V3.1.md
    ├── CURRENT_STATE.md
    ├── V3_RETROSPECT.md
    ├── FIRST_OUTCOME.md
    ├── V3.1_Product_Logic_Manifest.md
    ├── V3.1_Technical_Architecture_Guide.md
    ├── V3.1_Maintenance_Guide.md
    └── V3.2_Settlement_Advocate_Brief.md
```

---

## Current Library

### Product Libraries (Tier 1)
| Product | UIN | Status |
|---------|-----|--------|
| HDFC ERGO my:Optima Secure | HDFHLIP25041V062425 | ✅ Curated |
| HDFC ERGO Optima Restore | HDFHLIP26055V102526 | ✅ Curated |

### User Schedules (Tier 2)
| Insured | Policy No | Product | Status |
|---------|-----------|---------|--------|
| Badal Satapathy | 2856205213169603000 | Optima Secure | ✅ Curated |
| Kajal Satapathy | 2856205213224703000 | Optima Secure | ✅ Curated |
| Gupta Prasad Satapathy | 2805207151903301000 | Optima Restore | ✅ Curated |
| Basanti Satapathy | 2805207149369401001 | Optima Restore | ✅ Curated — corrected schedule |

---

## Build Status

| Component | Status |
|-----------|--------|
| Tier 1 — Product Libraries | ✅ Done |
| Tier 2 — User Schedules | ✅ Done |
| Insight Engine | ✅ Done |
| Schedule Integrity Checker | ✅ Done |
| PED Quality Checker | ✅ Done |
| Action Output — Draft Letters | ✅ Done |
| Policy Evolution Timeline | ✅ Done — V3.1 |
| Renewal Guidance Layer | ✅ Done — V3.1 |
| Coverage Maturity Score | ✅ Done — V3.1 |
| Settlement Data Layer | ✅ Done — V3.2 |
| Audit Engine | ✅ Done — V3.2 |
| Symmetry Report Generator | ✅ Done — V3.2 |
| Unit Tests — Routing | ✅ Done — V3.2 |
| FastAPI Endpoint | ⏳ Next |
| React Frontend | ⏳ Pending |
| Correspondence Tracker | ⏳ Pending |

---

## Tech Stack

- Python 3.9
- FastAPI
- Pydantic
- Anthropic SDK (for Tier 4 fallback only)

---

## Running the Insight Engine

```bash
cd "Ezer V3"
python engine/insight_engine.py
```

---

*Last updated: 2026-05-02*
*Author: Badal Satapathy*
*Product: Ezer — getezer.app*
