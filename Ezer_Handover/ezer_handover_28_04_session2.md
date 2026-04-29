# EZER — SESSION HANDOVER DOCUMENT
*Paste this entire document at the start of a new Claude conversation*

---

## WHO I AM

I am building **Ezer** — an insurance policy decoder that gives power back to buyers.
The name is mine. The vision is mine. I am a solo founder based in Bhubaneswar, Odisha.

---

## THE PRODUCT VISION

> "After a user uploads their policy, they should get critical non-obvious insights that influence their decisions — not just extracted text."

This is NOT a policy extraction tool. It is a **decision support tool** built on verified policy data.

---

## THE ARCHITECTURE — "The Ezer Way"

### Tiered Hybrid Architecture

**Tier 1 — The Verified Product Library**
One JSON file per product. Pure product rules — no user data. Shared across every user who uploads that product. Curated by humans, verified against policy wording.

**Tier 2 — User Schedule**
One JSON file per policy number. User-specific data only — SI, PEDs, waiting period status, addons active/inactive, premium. Linked to the product library via `product_library_ref`.

**Tier 3 — Derived Insights (Runtime Output)**
Computed by the Insight Engine at runtime by joining Tier 1 + Tier 2. Not stored permanently. Three insight types:
- "You have X and here's what it means" — active features
- "You don't have Y and here's what you're missing" — gap features
- "There's a problem with Z" — schedule integrity flags

**Tier 4 — Fallback (Experimental)**
If policy is not in the library, revert to LLM extraction with heavy "Experimental / Low Confidence" warning.

### Confidence Provenance Tags
- 🟢 Verified — from Tier 1 library
- 🟡 Extracted — from Tier 2 user schedule
- 🔴 Experimental — from Tier 4 fallback

---

## FILE NAMING CONVENTION

```
product_library_{insurer}_{product_name}.json
user_schedule_{policy_number}_{insured_name}.json
```

---

## CURRENT EZER LIBRARY — FILES BUILT

### Product Libraries (Tier 1)
| File | Product | Status |
|------|---------|--------|
| `product_library_hdfc_optima_secure.json` | HDFC ERGO my:Optima Secure UIN: HDFHLIP25041V062425 | ✅ Curated |
| `product_library_hdfc_optima_restore.json` | HDFC ERGO Optima Restore UIN: HDFHLIP26055V102526 | ✅ Curated |

### User Schedules (Tier 2)
| File | Insured | Policy No | Product | Status |
|------|---------|-----------|---------|--------|
| `user_schedule_2856205213169603000_badal.json` | Badal Satapathy (Self) | 2856205213169603000 | Optima Secure | ✅ Curated |
| `user_schedule_2805207151903301000_gupta_prasad.json` | Gupta Prasad Satapathy (Father) | 2805207151903301000 | Optima Restore | ✅ Curated |
| `user_schedule_2805207149369401000_basanti.json` | Basanti Satapathy (Mother) | 2805207149369401000 | Optima Restore | ✅ Curated |

### Not Yet Built
- Insight Engine (runtime, joins Tier 1 + Tier 2)
- Schedule Integrity Checker
- PED Quality Checker
- Correspondence Tracker
- FastAPI endpoint

---

## KEY POLICY FACTS — SATAPATHY FAMILY

### Badal Satapathy — Optima Secure
- Policy: 2856205213169603000 | Period: 05/02/2026 to 04/02/2027
- Base SI: ₹25L | Plus Benefit: ₹25L | Secure Benefit: ₹25L
- Unlimited Restore: ACTIVE | Protect Benefit: ACTIVE (default ON)
- No declared PEDs
- Three SI blocks with staggered waiting periods:
  - ₹10L block — all waiting periods waived
  - ₹5L block (a) — specific disease 12 months remaining, PED 24 months remaining
  - ₹5L block (b) — specific disease waived, PED 12 months remaining
- First inception: 02/02/2016 — moratorium crossed
- Two Ombudsman cases pending (see below)

### Gupta Prasad Satapathy — Optima Restore (Father, 77 years)
- Policy: 2805207151903301000 | Period: 01/02/2026 to 31/01/2027
- Policyholder: Badal Satapathy
- Base SI: ₹10L | Multiplier: ₹10L | Total: ₹20L
- Unlimited Restore: NOT active | No Protector Rider
- First inception: 01/02/2016 — 10 years — ALL waiting periods fully served
- Declared PEDs (all fully covered, no restrictions):
  - Hypertension_1 (ICD I10) — declared at inception 2016
  - Type 2 Diabetes Mellitus_1 (ICD E11-E11.9) — declared at inception 2016
  - Other disorders of heart — added via mid-policy endorsement post-Urolift surgery July 2025. HDFC ERGO confirmed NO specific ICD code available. Vague catch-all acceptance.
- ICD codes appear in elaboration pages attached to schedule but NOT in the exclusion table itself — this is HDFC ERGO's standard practice
- Urolift surgery July 2025 — cashless rejected twice, reimbursed after Ombudsman escalation threat. ₹5.3L paid upfront.
- Premium: ₹78,975 (net ₹81,000 less ₹2,025 discount)

### Basanti Satapathy — Optima Restore (Mother, 66 years)
- Policy: 2805207149369401000 | Period: 02/02/2026 to 01/02/2027
- Policyholder: Gupta Prasad Satapathy
- Base SI: ₹15L (₹10L original + ₹5L enhanced in 25-26) | Multiplier: ₹15L | Total: ₹30L
- Unlimited Restore: NOT active | No Protector Rider
- First inception: 02/02/2016 — 10 years
- SI blocks:
  - ₹10L original block — all waiting periods waived ✅
  - ₹5L enhanced block (25-26) — C1(i) waived, C1(ii) ~12 months remaining (~Feb 2027), C1(iii) ~24 months remaining (~Feb 2028)
- Declared PEDs: Hypertension_1 only
  - Fully covered on ₹10L block
  - NOT covered on ₹5L enhanced block until ~Feb 2028
- **SCHEDULE INTEGRITY ERROR:** Exclusion table shows THREE SI blocks — two ₹5L rows and one ₹10L row. Only one ₹5L enhancement was done. Middle ₹5L block is an underwriting error (phantom block). Flagged as HIGH priority.
- Hysterectomy — disclosed verbally to agent at onboarding 2016, agent advised to omit. Disclosed again in fresh proposal submitted during last renewal when policyholder name change was requested. HDFC ERGO neither changed policyholder name nor endorsed the disclosure. This matter is with the Ombudsman.
- Premium: ₹64,900 (no discount, no loading)

---

## OMBUDSMAN CASES PENDING (as of 28 April 2026)

### Case 1 — URB Removal After Premium Payment (Badal's Optima Secure)
HDFC ERGO provided written quotation for Unlimited Restore Benefit, collected premium, then issued policy without URB. Matter pending with Ombudsman. Ombudsman may or may not allow URB restoration.

### Case 2 — Policyholder Name Change + Hysterectomy Endorsement (Basanti's Policy)
Fresh proposal submitted by Badal during last renewal requesting:
- Change of policyholder name from Gupta Prasad to Badal
- Endorsement of hysterectomy disclosure
HDFC ERGO actioned neither. Matter pending with Ombudsman. Ombudsman likely to allow name change even if URB case is not fully resolved.

**IMPORTANT:** Do NOT send parallel correspondence to HDFC ERGO on Case 2 matters while Ombudsman case is active. This could weaken the Ombudsman position.

---

## EMAILS SENT / PENDING (as of 28 April 2026)

### Email 1 — SENT ✅
**To:** care@hdfcergo.com | **CC:** grievance@hdfcergo.com
**Subject:** Policy No. 2805207149369401000 — Discrepancy in Exclusion Table Requiring Urgent Correction | Basanti Satapathy
**Issue:** Phantom SI block in exclusion table — underwriting error
**Deadline given:** Acknowledge 7 working days, correct 15 working days
**Escalation threat:** Ombudsman Bhubaneswar + IRDAI IGMS

### Email 2 — READY TO SEND ⏳
**To:** care@hdfcergo.com | **CC:** grievance@hdfcergo.com
**Subject:** Policy No. 2805207151903301000 — ICD-10 Code Confirmation Requested for All Declared PEDs | Gupta Prasad Satapathy
**Issue:** ICD codes appear in elaboration pages but not in schedule exclusion table. Requesting written confirmation of scope for all three PEDs — Hypertension_1, Type 2 Diabetes Mellitus_1, Other disorders of heart.
**Three specific confirmations requested:**
1. Hypertension_1 covers I10 and all related hypertensive conditions
2. Type 2 Diabetes covers E11 through E11.9 including all complications
3. Other disorders of heart covers any and all cardiac conditions regardless of specific ICD
**Deadline given:** Acknowledge 7 working days, confirm 15 working days
**Escalation threat:** Ombudsman Bhubaneswar + IRDAI IGMS
**Status:** Drafted, not yet sent. Send separately from Email 1 — different policy number, different thread.

### Email 3 — ON HOLD ⏸
Broader ICD codes on schedule clarification for all policies. Hold until Email 2 gets a response. Send after HDFC ERGO's response reveals their position on ICD specificity.

---

## CRITICAL PRODUCT DIFFERENCES — OPTIMA SECURE vs OPTIMA RESTORE

| Feature | Optima Secure | Optima Restore |
|---------|--------------|----------------|
| Consumables | Protect Benefit DEFAULT ON — Annexure B covered | Annexure I EXCLUDED — 68 items not covered |
| Additional SI Pool | Secure Benefit (100% of base SI) | Not available |
| Bonus name | Plus Benefit | Multiplier Benefit |
| Restore | Base once/year + Unlimited Restore addon | Base once/year + Unlimited Restore addon |
| Restore same disease | YES per Section 2.6(vi) | YES per schedule |

---

## PRD UPDATES PENDING (from this session)

### Architecture Decision
- product_library and user_schedule are separate files
- derived_insights are runtime outputs — not stored permanently
- One product_library per product shared across all users
- One user_schedule per policy number

### New Capabilities to Add to PRD

**1. Schedule Integrity Checker**
Reads issued schedule, cross-references against declared SI enhancement history, detects anomalies (phantom blocks, mismatched waiting period entries, underwriting errors). Output: Schedule Integrity Alert + draft correction request to insurer.
Data hook: `schedule_integrity_flags` array on `user_schedule.waiting_periods`

**2. PED Quality Checker**
Reads declared PEDs, checks ICD code specificity, scores contestation risk:
- Low risk — unambiguous condition name (Hypertension, Type 2 Diabetes)
- Medium risk — somewhat specific but overlapping categories
- High risk — catch-all or residual category (Other disorders of heart)
Output: PED quality flag + draft written confirmation request to insurer.
Data hook: `ezer_flags` array on individual PED entries in user_schedule

**3. Gap Insights**
Product library describes ALL features a product offers. User schedule records which are active/inactive. Insight Engine generates gap insights for inactive features — "you don't have X, here's what you're missing, here's what it would cost you."
Example: Gupta Prasad has no Unlimited Restore — gap insight explains the risk at 77 with multiple PEDs.

**4. Correspondence Tracker**
Tracks open action items with insurer. Generates follow-up demands when timelines are missed. Critically — must be Ombudsman-aware. If matter is already escalated, flag as "pending escalation — do not send parallel correspondence" rather than generating a demand letter.

---

## WHAT TO WORK ON NEXT

**Option A:** Update user_schedule_2805207151903301000_gupta_prasad.json — correct the declared_peds section to accurately represent that ICD codes are in elaboration pages, not in the schedule exclusion table itself

**Option B:** Build the Policy Library loader — code that reads JSON schema files and makes them queryable

**Option C:** Build the Insight Engine — rules that join product_library + user_schedule and produce insight objects

**Option D:** Build the Schedule Integrity Checker — reads schedule_integrity_flags and generates insurer correction requests

**Option E:** Update the PRD formally with all decisions from this session

---

## IMPORTANT CONTEXT ABOUT THE FOUNDER

- Solo builder, no team, no funding yet
- Based in Bhubaneswar, Odisha
- Strong domain knowledge of health insurance policies and claim denials
- Has attempted this product twice before — both failed at extraction
- Building in Python/FastAPI
- Product name is **Ezer**
- Father (Gupta Prasad, 77) and Mother (Basanti, 66) are real users whose policies were curated in this session
- Has two pending Ombudsman cases against HDFC ERGO
- ICD-10 classification = International Classification of Diseases 10th Revision — WHO standard alphanumeric codes for every known disease/condition. Bridge between what a doctor writes and what an insurer pays.

---

*End of handover. Attach the five JSON files separately if available.*
