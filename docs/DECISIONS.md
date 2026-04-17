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