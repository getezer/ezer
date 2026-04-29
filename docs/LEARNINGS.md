# Ezer - Engineering and Product Learnings
## Badal Satapathy | Started April 2026

This file documents what we learned from real documents,
real testing, and real mistakes while building Ezer.
Different from DECISIONS.md — this is what surprised us,
what we got wrong first, and what real data taught us.

---

## Learning 1 - Three distinct HDFC ERGO policy formats exist
**Date:** April 21, 2026
**Source:** Reading 5 real HDFC ERGO policies

Three formats confirmed within one insurer:
- my: Optima Secure newer format — Section B.1. references
- Optima Secure older format — B-1.1 references
- Optima Restore — B-1.a references

Waiting period fields appear in the Customer Information
Sheet in Optima Restore format — NOT in the main Policy
Schedule. Extractor must look in CIS section specifically.

**Impact on code:** Added format-specific note to
policy_extractor.py prompt instructing Claude to search
Customer Information Sheet for waiting periods.

---

## Learning 2 - Policyholder and insured person are different people
**Date:** April 21, 2026
**Source:** Gupta Prasad and Basanti Satapathy policies

Badal Satapathy is the policyholder. Gupta Prasad is the
insured person. They are father and son. The policy
covers the father but is owned by the son.

This matters for:
- CGO letters — must address the policyholder, not the patient
- Ombudsman jurisdiction — determined by policyholder address
- Claim eligibility — insured person's conditions, not policyholder's

**Impact on code:** Added policyholder_is_insured boolean
field to PolicyDocument schema.

---

## Learning 3 - Declared pre-existing conditions have tiered waiting periods
**Date:** April 21, 2026
**Source:** Basanti Satapathy policy — Hypertension with
three-tier waiting period structure

Same condition, three different waiting periods based on
which portion of the sum insured is being claimed:
- Rs 10,00,000 — all waiting periods waived
- Rs 5,00,000 — initial and specific waiting periods waived,
  pre-existing reduced to 1 year
- Rs 5,00,000 — initial waived, specific reduced to 1 year,
  pre-existing reduced to 2 years

Insurers frequently cite waiting periods without specifying
which tier applies. This is a contestable point.

**Impact on code:** DeclaredPreExistingCondition schema
has waiting_period_details field that captures full tiered
structure as text. Extractor prompt instructs Claude to
capture tiered amounts explicitly.

---

## Learning 4 - Sum insured enhancements trigger fresh waiting periods
**Date:** April 21, 2026
**Source:** Kajal Satapathy policy — sum insured enhanced
from Rs 10,00,000 to Rs 20,00,000 at renewal

Fresh waiting periods apply only on the enhanced portion.
The existing sum insured carries full continuity.

Insurers sometimes apply waiting periods to the entire
sum insured instead of just the enhancement. This is
a contestable point.

**Impact on code:** previous_year_sum_insured field added
to PolicyDocument schema. Extractor successfully detected
enhancement in Kajal's policy.

---

## Learning 5 - One hospitalisation can generate multiple settlement letters
**Date:** April 21, 2026
**Source:** GPS hospitalisation July 2025 — three settlements

Settlement 1: Rs 4,63,900 — main hospitalisation August 2025
Settlement 2: Rs 6,121 — post-discharge supplementary December 2025
Settlement 3: Rs 1,768 — post-discharge supplementary January 2026

The claim reference suffix pattern: RR-HS25-15050055,
RR-HS25-15050055-2, RR-HS25-15050055-3

Balance sum insured reduces with each settlement and is
trackable across the chain.

**Impact on code:** Settlement extractor handles all three
formats correctly. claim_reference field captures suffix.

---

## Learning 6 - Protector Rider balance of zero does not mean rider exists
**Date:** April 21, 2026
**Source:** GPS settlement letter — Protector Rider: 0

Balance of zero has two possible meanings:
1. Rider exists but was fully exhausted
2. Rider was never part of this policy

Must cross-reference with policy document to confirm.
GPS policy schedule shows Protector Rider as blank/dash
meaning it was never part of the policy.

**Impact on code:** has_protector_rider only set to True
if balance is greater than zero. Rider Validation Rule
from Settlement Auditor Supplement V3 implemented.

---

## Learning 7 - ZDR is an enterprise agreement, not an API header
**Date:** April 21, 2026
**Source:** Testing policy_extractor.py

Attempted to pass ZDR as anthropic-beta header.
API returned 400 error — header value not recognised.

ZDR requires a signed enterprise agreement with Anthropic.
Not available on standard API keys.
Anthropic's default API retention is 7 days since
September 2025. API data never used for training.

**Impact on code:** ZDR headers removed from all API calls.
Decision 23 recorded.

---

## Learning 8 - analyser.py had an indentation bug in git
**Date:** April 21, 2026
**Source:** uvicorn startup error

The prompt f-string closing triple quotes were followed
by code that had 8 spaces of indentation instead of 4.
Python read the code as being inside the string.

The bug was already committed to git — git checkout
restored the broken version.

Fixed by rewriting the entire function cleanly in VS Code.

**Impact on process:** Any file with complex f-strings
should be tested with a simple import check before
committing. Added to standing rules.

---

## Learning 9 - pdfplumber extracts tables as text, not structured data
**Date:** April 21, 2026
**Source:** Settlement letter table extraction

The settlement breakdown table on page 2 is extracted
as text by pdfplumber, not as a structured table.
Claude then parses this text into line item objects.

This works well for clean digital PDFs like HDFC ERGO
settlement letters. May not work for scanned documents
or poorly formatted PDFs.

This is why settlement_extraction_confidence exists —
LOW confidence means the table text was unclear and
no financial conclusions should be shown.

---

## Learning 10 - Customer Information Sheet is the most reliable anchor
**Date:** April 21, 2026
**Source:** Reading all five policies across three formats

Every HDFC ERGO policy format has a Customer Information
Sheet / Know Your Policy section. This section always
contains key fields in a consistent table format
regardless of which product format the policy uses.

When in doubt, extract from CIS first.
Main Policy Schedule is format-specific and less reliable.

---

## Learning 11 - CGO is internal. Ombudsman is where resolution happens.
**Date:** April 21, 2026
**Source:** Founder's direct experience — 3 CGO responses
from HDFC ERGO reviewed, all deflecting or moving goalposts.

The CGO letter is a procedural gate, not a resolution path.
IRDAI requires exhausting internal grievance process before
Ombudsman will accept a complaint. So the CGO step is
mandatory — but the expectation of resolution must be zero.

Ezer's real value is getting the user to the Ombudsman
with a complete, well-documented case. The Ombudsman is
free, binding, and has a 3-month award timeline.

This changes how Screen 6 and Screen 7 must be written.
CGO letter = complete this step so you can escalate.
Ombudsman = where your case will actually be heard.