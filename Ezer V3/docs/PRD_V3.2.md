# Ezer — PRD V3.2 Settlement Advocate

## Problem
- Policyholders receive settlement letters they cannot read or audit
- Insurers deduct amounts without clear itemised explanation
- Hospitals bill for services never rendered, quantities never consumed
- The patient is exhausted at discharge — no energy to question a 15-page bill
- Information asymmetry benefits both hospital and insurer at the patient's expense

## Target User
- Insured policyholders who have received a settlement letter
- Users who have paid a hospital bill and suspect overcharging
- Users who want to understand why their claim was partially settled

## The Two-Layer Problem Ezer V3.2 Solves

**Layer 1 — Hospital Bill Irregularities (Invisible Loss)**
Charges the hospital billed that are clinically suspicious, duplicated, or illegitimate. The insurer pays these without auditing. The patient never knows.

**Layer 2 — Insurer Settlement Errors (Visible Loss)**
Deductions the insurer made that are rider-dependent — correctly deducted given the policy, but recoverable if the right rider were active.

## Core Value — What V3.2 Delivers

- Reads settlement JSON (human-curated from settlement letter)
- Classifies every line item: SETTLED / RIDER_DEPENDENT / NON_PAYABLE / HOSPITAL_FLAG
- Computes Total Asymmetry Payload = Layer 1 + Layer 2
- Routes output based on rider status read from Tier 2 user schedule
- Generates three targeted documents — no user input required

## The Decision Gate — Three Routes

**Route A — Grievance Mode**
Rider is active. Insurer wrongly deducted. Generate formal grievance letter to HDFC ERGO with exact amounts and policy basis.

**Route B — Gap Awareness Mode**
Rider inactive. Age-based ineligibility flag present. Generate honest gap statement — what was lost, why the rider is unavailable, what to do next.

**Route C — Renewal Action Mode**
Rider inactive. No age flag. Rider is available. Generate renewal checklist with financial case for adding the rider.

## Three Output Documents

**Document 1 — Hospital Irregularity Memo**
Always generated. Independent of rider status. For billing desk use. Six flag types: DUPLICATE_CHARGE, QUANTITY_ANOMALY, DEFINITION_REQUIRED, GHOST_CONSULTATION, HOSPITAL_FLAG.

**Document 2 — Settlement Comparison**
Always generated. Actual settlement vs Ezer view. Numbers only. No opinion.

**Document 3 — Rider Output**
Route-dependent. Grievance letter / Gap awareness / Renewal checklist.

## What V3.2 Does NOT Do

- Does not extract data from PDFs — all settlement data is human-curated JSON
- Does not file grievances automatically — user decides whether to act
- Does not provide legal advice — provides factual audit with evidence requests
- Does not require any input from the user — reads policy and routes automatically

## Success Criteria

- User can answer: "What did the hospital charge that it shouldn't have?"
- User can answer: "What did the insurer deduct that was wrong or avoidable?"
- User can answer: "What should I do about it?"
- Engine routes correctly based on policy data — user never asked what their policy contains

## Proof of Concept — Gupta Prasad Satapathy, Urolift Claim

- Total claimed: ₹4,75,846
- Insurer deductions: ₹9,347 (₹7,017 rider-dependent + ₹2,330 non-payable)
- Hospital flags paid without audit: ₹95,561.81
- Total Asymmetry Payload: ₹1,04,908.81
- Route taken: B (Gap Awareness — age-based rider ineligibility)

---
*Version: 3.2*
*Last updated: 2026-05-02*
