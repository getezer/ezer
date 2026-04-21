# Ezer Settlement Auditor Supplement V4
## Status: AS-BUILT RECORD — Day 6, April 21, 2026

This document records what was actually designed and built
for settlement analysis in V1, compared to what V3 proposed.
V3 was the requirement. V4 is the implementation record.

---

## What V3 Proposed vs What V4 Built

### Schema Fields
V3 proposed 5 fields. V4 built 20+ fields.

V3 proposed:
- claimed_amount
- settled_amount
- leakage_amount
- has_protector_rider
- settlement_extraction_confidence

V4 built all of the above plus:
- claim_reference, policy_number, hdfc_ergo_id, utr_number
- settlement_date, transaction_date
- patient_name, main_member_name, relationship
- hospital_name, ailment, hospitalization dates, claim_type
- deduction_amount, mou_discount, gst_amount, grand_total_paid
- balance_sum_insured, balance_cumulative_bonus, protector_rider_balance
- without_prejudice, mou_clause_present
- consumables_deducted, consumables_deducted_total
- line_items — full breakdown table, every row
- soft_warning

Note: leakage_amount from V3 is not a stored field in V4.
It is calculated on demand as claimed_amount minus
settled_amount minus mou_discount. Storing a derived
value would create inconsistency risk.

---

## New Document Type Added
SETTLEMENT_ADVICE added to DocumentType enum in schemas.py.
Enables document detection on second visit.

---

## New Endpoint Added
POST /extract-settlement — live and tested.
Accepts PDF upload, returns full SettlementExtraction JSON.

---

## Modular Router
V3 proposed escalator.py with a doc_type fork.
V4 deferred the router — not needed in V1 because
settlement and denial are handled by separate endpoints.
The user uploads to the correct endpoint directly.
Router to be added in V1.1 when document detection
on second visit is built.

---

## Safety Guardrails — All Implemented
From V3, all four guardrails are in place:

1. No financial conclusions on LOW confidence.
   settlement_extraction_confidence LOW triggers
   soft_warning and frontend shows verification message.

2. Probabilistic language only.
   consumables_deducted_total shown as approximate.
   No guaranteed recovery statements anywhere.

3. Rider Validation Rule implemented.
   has_protector_rider only True if protector_rider_balance
   greater than zero. Never assumed. Never inferred.

4. Consumables only flagged if rider confirmed.
   consumables_deducted list only populated when
   has_protector_rider is True.

---

## What Was Tested
Four real settlement letters tested:

| Letter | Claim | Amount | Result |
|---|---|---|---|
| SettlementLetter 1_GPS_HDFC | RR-HS25-15050055 | Rs 4,63,900 | Perfect |
| RR-FC25-14824548 | Kajal checkup | Rs 4,100 | Perfect |
| RR-HS25-15050055-2 | GPS supplementary | Rs 6,121 | Perfect |
| RR-HS25-15050055-3 | GPS supplementary | Rs 1,768 | Perfect |

Three claim types handled correctly:
- REIMBURSEMENT (main hospitalisation)
- REIMBURSEMENT (preventive checkup)
- SUPPLEMENTRY (post-discharge)

---

## What V3 Proposed for V1 vs What Is Deferred to V1.1

### V1 — Built and live:
- Full field extraction from settlement letters
- Line item breakdown table extraction
- Financial summary: claimed, deducted, MOU discount, settled, GST, total
- Post-settlement balance tracking
- without_prejudice flag detection
- mou_clause_present flag detection
- Protector Rider validation
- Consumables identification (when rider confirmed)
- Confidence scoring
- /extract-settlement endpoint

### V1.1 — Deferred:
- Full MOU recovery analysis
- Comparison of deductions against IRDAI non-payable list
- Automated leakage quantification with user-facing amount
- CGO letter generation specific to settlement disputes
- Multi-settlement chain analysis (linking -1, -2, -3 settlements)
- Document type auto-detection routing settlements to correct engine

---

## Key Insight From Real Documents
One hospitalisation can generate multiple settlement letters
with suffix pattern: CCN, CCN-2, CCN-3.

GPS hospitalisation July 2025 produced three settlements:
- August 2025: Rs 4,63,900 main claim
- December 2025: Rs 6,121 supplementary
- January 2026: Rs 1,768 supplementary
- Total received: Rs 4,71,789 of Rs 4,75,846 claimed

The balance sum insured reduces with each settlement
and is trackable across the chain.
V1.1 to build multi-settlement chain linking logic.

---

## Files Created or Modified
- backend/app/schemas.py — SettlementExtraction, SettlementLineItem
- backend/app/settlement_extractor.py — new file
- backend/app/main.py — /extract-settlement endpoint added
- docs/Settlement_Auditor_Supplement_V4.md — this file