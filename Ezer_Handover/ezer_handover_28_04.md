# EZER — SESSION HANDOVER DOCUMENT
*Paste this entire document at the start of a new Claude conversation*

---

## WHO I AM

I am building **Ezer** — an insurance policy decoder that gives power back to buyers.
The name is mine. The vision is mine. I am a solo founder based in Bhubaneswar, Odisha.

---

## THE PRODUCT VISION

> "After a user uploads their policy, they should get critical non-obvious insights that influence their decisions — not just extracted text."

Examples of what I mean by "critical insights":
- "You can claim for cardiac issues only after 3 years"
- "You have Unlimited Restore — same disease, same year is covered"
- "Your policy covers consumables by default — most don't"
- "Your NCB grows whether or not you claimed"

This is NOT a policy extraction tool. It is a **decision support tool** built on verified policy data.

---

## THE ARCHITECTURE WE DECIDED ON — "The Ezer Way"

### Tiered Hybrid Architecture

**Tier 1 — The Verified Library**
When a user uploads a known policy (e.g. HDFC Optima Secure), Ezer identifies the Product ID and pulls 100% verified rules from a hand-curated JSON library. No LLM involved for product facts.

**Tier 2 — Surgical Schedule Extraction**
The LLM is used ONLY to extract user-specific schedule fields: Name, Sum Insured, PED declarations, Riders active, Waiting periods remaining, Premium. These are on page 1-2 of any policy in table format. Scope is narrow and tractable.

**Tier 3 — Fallback (Experimental)**
If the policy is NOT in the library, revert to LLM extraction with a heavy "Experimental / Low Confidence" warning to the user.

### Why This Architecture
- Tier 1 is deterministic and defensible (regulatory safety)
- Tier 2 avoids the hardest extraction problems (policy wording parsing)
- Tier 3 is honest about its limitations
- Scales by adding JSON files to the library, not by rewriting extraction logic

### Confidence Provenance Tags (on every insight)
- 🟢 Verified — from Tier 1 library
- 🟡 Extracted — from Tier 2 user schedule
- 🔴 Experimental — from Tier 3 fallback

---

## WHAT WE BUILT THIS SESSION

### 1. Full verified schema for HDFC Optima Secure
**File: `ezer_schema_hdfc_optima_secure.json`** — the user will attach this.

This schema has three blocks:
- `product_library` — verified product-level facts (Tier 1)
- `user_schedule` — user-specific extracted fields (Tier 2), populated for Badal Satapathy's actual policy
- `derived_insights` — 9 deterministic insights computed from the above two blocks

Every field has a clause reference. Every insight is traceable. No hallucination possible because LLM only phrases the output, not generates the facts.

### 2. The specified disease list (Code Excl02) — fully extracted
From the policy wording, these conditions have a 24-month waiting period even if NOT pre-existing:

**Illnesses:** Non-infective Arthritis, Pilonidal sinus, Gallbladder diseases, Kidney/Bladder stones, Benign tumors/cysts/polyps, Pancreatitis, Stomach ulcers, PCOS, Cirrhosis, GERD, Sinusitis/Rhinitis, Perineal/Perianal Abscesses, Skin tumors, Cataract, Fissure/Fistula/Haemorrhoids, Tonsillitis, Osteoarthritis/Osteoporosis, Fibroids, Benign Hyperplasia of Prostate

**Surgical Procedures:** Tonsillectomy/Adenoidectomy, Tympanoplasty, Hernia, D&C, Nasal concha resection, Prolapsed disc surgery, Myomectomy, Genito-urinary surgery (non-malignancy), Varicose vein surgery, Prostate surgery, Cholecystectomy (gallbladder removal), Surgery for Perianal Abscesses, Hydrocele/Rectocele, Joint replacement, Nasal septum surgery, Ligament/Tendon/Meniscal repair, Hysterectomy, Fissurectomy/Haemorrhoidectomy/Fistulectomy/ENT surgeries, Endometriosis, Prolapsed Uterus, Rectal Prolapse, Varicocele, Retinal detachment, Glaucoma, Nasal polypectomy

### 3. Key verified insights about Optima Secure (Badal's policy)

| # | Insight | Status |
|---|---------|--------|
| 1 | Unlimited Restore active — same disease, same year, unlimited times | ✅ Verified |
| 2 | No room rent cap — at actuals, no proportionate deduction risk | ✅ Verified |
| 3 | PED waiting still running on ₹10L (two ₹5L blocks with 24mo and 12mo remaining) | ✅ Verified |
| 4 | Plus Benefit grows SI by 50% at renewal regardless of claims | ✅ Verified |
| 5 | Effective coverage ceiling is ₹75L (25L base + 25L Secure + unlimited restore) | ✅ Derived |
| 6 | ₹5,000 health checkup — claimable only AFTER next renewal, not during current year | ✅ Verified |
| 7 | Consumables covered in TWO layers — base hospitalization (IV fluids, surgical appliances) AND Protect Benefit (default ON for Optima Secure per Annexure C) | ✅ Verified |
| 8 | 180 days post-discharge coverage — most policies cover 60-90 days only | ✅ Verified |
| 9 | Moratorium — 10+ years active, insurer cannot deny on non-disclosure grounds (but CAN still deny on medical necessity, procedural grounds, reasonable & customary) | ✅ Verified |

### 4. Critical corrections made during session
- **Base restore (without add-on):** CAN be used for same disease same year (Section 2.6(vi)) — once per year limit only
- **Protect Benefit:** DEFAULT ON for Optima Secure per Annexure C — user must explicitly opt OUT
- **Moratorium:** Only closes the non-disclosure door, NOT all denial grounds
- **Consumables:** Two-layer structure — base hospitalization covers IV fluids/surgical appliances; Protect Benefit covers Annexure B items (68 items including gloves, masks, syringes)

---

## WHAT WE LEARNED ABOUT LLM EXTRACTION (from Ver 2 failures)

The previous code (Ver 2) had these structural problems:

1. **PDF parser destroys table structure** — `pdfplumber.extract_text()` flattens tables, losing column headers. "Waiting Period Remaining: 2 Years" becomes "500000 2 Years". Fix: use `pdfplumber.extract_tables()` for schedule pages, text extraction only for wording pages.

2. **Schema too flat** — `{ "ped_waiting": { "value": "", "quote": "" } }` cannot represent modifiers (waived, reduced, base vs remaining). Fix: nested schema with `base_period_months`, `waiver` object, `remaining_months`, `is_remaining` boolean.

3. **Single giant LLM call** — one prompt asking for everything from 15K characters of text. Fix: multi-pass extraction, one field group per call, against clause-filtered pages only.

4. **Garbage quote selection** — LLM latches onto nearest numeric tokens not semantic sentences. Fix: decouple value extraction from quote retrieval; verify quote is a complete sentence from source document.

5. **Confidence scoring using brittle heuristics** — penalizing "2 year" values (a bug workaround that breaks correct extractions). Fix: use structural signals (is the quote a complete sentence? does it contain field keywords?).

6. **Coverage status derived from keyword matching on generated prose** — not from structured data. Fix: compute status directly from structured fields.

---

## THE EXISTING VER 2 CODE STRUCTURE

Files: `pdf_reader.py`, `policy_extractor.py`, `extraction_schema.py`, `clause_search.py`, `proof.py`, `confidence.py`, `explainer.py`, `main.py`

What's good about Ver 2:
- Defensive coding throughout (isinstance checks, safe defaults)
- Proof layer concept is right
- Two-bucket output (key_risks vs needs_verification) is right UX
- `clause_search.py` exists but is NOT wired into the extraction flow

What needs fixing:
- `pdf_reader.py` — needs table-aware parsing for schedule pages
- `extraction_schema.py` — needs nested schema with modifiers
- `policy_extractor.py` — needs multi-pass per field, not one giant call
- `main.py` — coverage status must derive from structured data not text keywords
- `proof.py` — quote validation too lenient (substring match passes garbage quotes)

---

## THE 5-DAY PATCH PLAN (where we were headed)

- **Day 1-2:** Rewrite `pdf_reader.py` — table-aware parsing for schedules, text for wordings
- **Day 3:** Update schema to nested structure with modifiers
- **Day 4-5:** Refactor extractor to multi-pass, wire up `clause_search.py`
- **Day 6:** Tighten proof and confidence layers
- **Day 7:** Run end-to-end on 3 real policies that failed in Ver 2
- **Day 8-12:** Fix what the test reveals

But given the Tiered Architecture decision, the actual next steps are:

**Immediate next steps:**
1. Build the Policy Library loader — code that reads the JSON schema file and makes it queryable
2. Build the Insight Engine — rules that run against the structured data and produce insight objects
3. Build the LLM Translator — takes a verified insight object and phrases it in plain language
4. Build the Schedule Extractor — Tier 2 extraction for user-specific schedule fields only (narrow scope)
5. Build the Product Identifier — takes uploaded policy, identifies product name/insurer
6. Wire everything into the FastAPI endpoint

---

## WHAT TO WORK ON NEXT (your call)

Option A: **Start building the Policy Library + Insight Engine** (pure backend, no LLM yet, fully deterministic)

Option B: **Curate the next policy** into the library schema (Star Comprehensive or Niva Bupa ReAssure — the next most common)

Option C: **Build the Schedule Extractor** (Tier 2 — narrow LLM extraction for user-specific fields only)

Option D: **Design the user-facing output** — what does a user actually see when they upload their policy?

---

## IMPORTANT CONTEXT ABOUT THE FOUNDER

- Solo builder, no team, no funding yet
- Based in Bhubaneswar, Odisha
- Has strong domain knowledge of health insurance policies and claim denials
- Has attempted this product twice before — both attempts failed at extraction
- Is building in Python/FastAPI
- The product name is **Ezer**
- The policy used for first library entry belongs to Badal Satapathy (HDFC Optima Secure, Policy No. 2856205213169603000, period Feb 2026 - Feb 2027, ₹25L SI Individual)

---

*End of handover. The JSON schema file will be attached separately.*
