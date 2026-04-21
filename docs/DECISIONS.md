# Ezer - Architecture Decision Log
## Badal Satapathy | Started April 2026

This file documents every significant technical and product decision
made while building Ezer, and the reasoning behind each one.

Standard practice in professional engineering teams.
Visible on GitHub as evidence of structured thinking.

---

## Standing Rules - Apply to Every Session

**Rule 1: Architecture discussion before coding**
Design first. Code second. No file gets written without
discussing what it does, who interacts with it, what might
change over time, and what should be code vs configuration.
Established: April 17, 2026. Reason: jumped into
letter_generator.py without architecture discussion and
had to stop and redesign.

**Rule 2: Proper comments on all code**
Every file, every function, every non-obvious line gets
a plain English comment. Code you can explain is code you own.
Established: April 16, 2026.

**Rule 3: Config files for non-developer content**
Legal language, email templates, escalation text — all live
in JSON config files. Python code reads from these files.
Non-developers can update content without touching code.
Established: April 17, 2026.

---

## Decision 1 - Combined /analyse endpoint
**Date:** April 16, 2026
**Decision:** Built one /analyse endpoint that runs both
extraction and analysis, returning a single combined response.

**Why:** PRD principle — zero friction. A policyholder in
distress wants one answer, not two separate calls to manage.
Two API calls happen invisibly behind the scenes.

---

## Decision 2 - Temporary files for PDF processing
**Date:** April 16, 2026
**Decision:** Use Python tempfile module. Files auto-deleted
after processing.

**Why:** Implements Process and Discard privacy principle
from PRD Section 14. DPDP Act 2023 compliance.
Trust differentiator for B2B clients.

---

## Decision 3 - Claude Sonnet for extraction and analysis
**Date:** April 16, 2026
**Decision:** Use claude-sonnet-4-6 for all API calls.

**Why:** Fast, accurate, cost effective for development volume.
Opus gives marginally better analysis at 5x cost.
Revisit at scale.

---

## Decision 4 - Python virtual environment named venv
**Date:** April 15, 2026
**Decision:** Named venv following universal Python convention.

**Why:** Every professional Python developer recognises venv.
Ezer GitHub is a portfolio. Standard naming signals
professional practice.

---

## Decision 5 - FastAPI over Flask or Django
**Date:** April 15, 2026
**Decision:** FastAPI as Python backend framework.

**Why:** Appears in almost every AI engineering job description.
Auto-generates API documentation. Handles async natively.
Standard for AI backends in 2026.

---

## Decision 6 - Config files for legal language
**Date:** April 17, 2026
**Decision:** All legal language, CGO emails, and letter
templates live in JSON config files under backend/config/.
Python code reads from these files. No hardcoding.

**Files created:**
- legal_language.json — all legal paragraphs by denial pattern
- cgo_directory.json — CGO email addresses by insurer
- letter_templates.json — letter structure and boilerplate

**Why:** Lawyers and business users can update content without
touching Python code. Supports internationalisation.
Aligns with PRD principle — all text in separate language files.

---

## Decision 7 - CMS with approval workflow deferred to V2
**Date:** April 17, 2026
**Decision:** Full screen-based content management with
business approval workflow deferred to V2.

**Why:** Building a CMS takes 2 to 3 weeks. V1 has one user —
the founder. JSON files edited directly in V1. Admin screen
added in V2 when B2B clients need non-developer access.
PRD to be updated to reflect this.

---

## Decision 8 - Informed consent gate
**Date:** April 17, 2026
**Decision:** Mandatory three-sentence consent gate before
CGO letter generation. User must check a checkbox to proceed.

**Consent text:**
"Based on your denial letter, your claim appears contestable.
Ezer will now generate a formal complaint letter to your
insurer's Chief Grievance Officer. This is guidance only —
not legal advice. Outcomes depend on your specific case."

**Why:** Protects Ezer from allegations of encouraging
unnecessary litigation. Required for IRDAI regulatory
compliance. Keeps Ezer clearly positioned as guidance,
not legal advice. Proposed by founder during morning
reflection, April 17, 2026.

---

## Decision 9 - Consent record in Case Metadata JSON
**Date:** April 17, 2026
**Decision:** Consent record lives in user-owned Case
Metadata JSON. Nothing stored on Ezer servers.

**Fields recorded:**
- consent_given: true
- consent_text_version: v1.0
- consent_timestamp: ISO 8601 format
- consent_text_shown: exact text displayed
- case_reference, policy_number, ccn

**Why:** Maintains Process and Discard privacy principle.
User can produce JSON as proof of informed consent.
DPDP Act 2023 compliant. No server storage required.

---

## Decision 10 - PDF only for V1
**Date:** April 17, 2026
**Decision:** V1 accepts PDF denial letters only.
Image and screenshot support deferred to V1.1.

**Why:** Real HDFC ERGO letters are clean PDFs.
Most hospital TPA letters are PDFs. Covers 80% of use cases.
Claude Vision AP

---

## Decision 17 - Case file presented as human readable card
**Date:** April 17, 2026
**Decision:** Case Metadata JSON is displayed as a human
readable card on the frontend. User never sees raw JSON.
Download button says "Download Your Case File" not
"Download JSON."

**Why:** Most users have never heard of JSON. A distressed
policyholder will not know what to do with a .json file.
The card format makes the data accessible. The friendly
label removes confusion. The JSON is still JSON underneath
for machine readability on return visits.

**V1.1 addition:** PDF case summary for users who want
a printable human readable version.

---

## Decision 18 - Five config files for all non-code content
**Date:** April 17, 2026
**Decision:** Created five JSON config files that contain
all content that non-developers may need to update.

**Files:**
- backend/config/legal_language.json
- backend/config/cgo_directory.json
- backend/config/letter_templates.json
- backend/config/ombudsman_directory.json
- backend/config/escalation_ladder.json
- backend/config/app_config.json

**Why:** Lawyers update legal language. Business updates
CGO emails. Operations updates Ombudsman details.
None of these people should need a developer to make
these changes. Config files enable non-developer
maintenance from day one.

**V2 addition:** Admin screen with approval workflow
so non-developers edit through a UI not files directly.

---

## Decision 19 - Consent validated in backend AND frontend
**Date:** April 17, 2026
**Decision:** Consent is enforced at two levels.

Frontend level: Generate button stays greyed out until
user checks consent checkbox. API is never called
without consent.

Backend level: /generate-cgo endpoint checks consent
flag. Returns 400 error if consent is false or missing.
Letter is never generated without consent.

**Why:** Two layers of protection. Frontend protects
user experience. Backend protects against any direct
API calls that bypass the frontend. Both are needed
for complete protection.

**Testing note:** During backend testing we manually
set consent true in test payload. Real consent comes
from user checking checkbox on frontend in Prompt 6.

---

## Decision 20 - requirements.txt to be created tomorrow
**Date:** April 17, 2026
**Decision:** Create requirements.txt as first task
of next session before any other work.

**Why:** requirements.txt lists all Python libraries
Ezer needs. Essential for deployment. Without it
Railway or Render cannot install dependencies.
Currently missing from the repository.

**Command to generate:**
pip freeze > requirements.txt

---

## Decision 21 - Schemas in one central file
**Date:** April 21, 2026
**Decision:** All Pydantic data structures live in one file —
schemas.py. All extractors import from here.

**Why:** Single source of truth. Add a field once, available
everywhere. No duplication, no drift between files.

---

## Decision 22 - Explicit fields for critical riders, open list for everything else
**Date:** April 21, 2026
**Decision:** Six critical riders get explicit boolean fields
in PolicyDocument. All other riders go in riders_and_addons
list as RiderAddon objects.

**Critical explicit fields:**
- protector_rider_active
- unlimited_restore_active
- co_payment_percentage
- aggregate_deductible
- waiting_period_pre_existing
- room_rent_limit

**Why:** Ezer reasons about critical fields during denial
analysis. Open list catches all future riders automatically
without schema changes. New products from any insurer
never break the schema.

---

## Decision 23 - ZDR not implemented in V1
**Date:** April 21, 2026
**Decision:** Zero Data Retention headers removed from all
API calls. Not implemented in V1.

**Why:** ZDR requires a signed enterprise agreement with
Anthropic. Not available on standard API keys.
Anthropic's default API retention is 7 days as of
September 2025. Data is never used for model training.
This is sufficient privacy protection for V1.
ZDR to be negotiated when Ezer reaches enterprise scale.

---

## Decision 24 - Settlement analysis basic awareness in V1, full audit in V1.1
**Date:** April 21, 2026
**Decision:** V1 extracts settlement letter fields and flags
without_prejudice, mou_clause_present, and protector_rider_balance.
Full consumables audit and MOU recovery analysis deferred to V1.1.

**Why:** Settlement extractor is built and tested. The schema
is complete and future-proof. Basic awareness — what was paid,
what was deducted, rights preserved — is valuable for V1 users.
Full audit engine needs more settlement letter samples from
multiple insurers before building confidently.

---

## Decision 25 - without_prejudice is a passive flag in V1
**Date:** April 21, 2026
**Decision:** without_prejudice flag is captured but not
acted upon in V1. No logic uses this flag to generate
recommendations or next steps.

**Why:** "Without Prejudice" appears in HDFC ERGO settlements
but pattern needs verification across other insurers before
building logic around it. Capturing is safe. Acting without
PRD decision is not. Any flag must be mapped to a user-facing
action in PRD before Ezer does anything with it.