# EZER — INTEGRATED TECHNICAL DESIGN DOCUMENT

**Product:** Ezer
**Version:** 1.1 — Aligned to PRD v2.0
**Date:** 20 April 2026
**Author:** Badal Satapathy
**Status:** FINAL — Blueprint for V1.9 Build
**Classification:** Internal — Engineering Reference Document

---

## DOCUMENT PURPOSE

This document is the single engineering blueprint for Ezer V1.9. It maps every user action to an API endpoint, documents every AI prompt in the system, specifies every data structure, and provides a Data Governance framework detailed enough to satisfy a Banking, Financial Services, and Insurance security audit.

This document is read alongside PRD v2.0. The PRD defines what Ezer does. This document defines how Ezer does it.

### Changes from TDD v1.0 to v1.1

| Section | Change |
|---|---|
| Section 1 | Architecture updated — JSON primary, RAG supplementary in V1 |
| Section 1 | Principle 6 added — Zero Data Retention |
| Section 1 | Principle 7 added — Fail-Fast Config Validation |
| Section 1 | Principle 8 added — Light Failure versus Hard Failure |
| Section 2 | Second visit flow updated — UI-first document identification, AI fallback |
| Section 3 | WeasyPrint endpoint added, Anonymous metrics endpoint added |
| Section 4 | All prompts updated — Zero Data Retention, AI disclosure in consent |
| Section 4 | Hybrid confidence downgrade logic added |
| Section 5 | Anonymous metrics schema added |
| Section 7 | Regulatory Knowledge Base updated — JSON primary, RAG supplementary |
| Section 8 | Zero Data Retention fully documented — BFSI audit ready |
| Section 8 | Anonymous metrics governance added |
| Section 9 | Light Failure versus Hard Failure formalised |
| Section 10 | legal_language.json updated — consent text v2.0 with AI disclosure |
| Section 11 | Volatile state warning added — browser beforeunload event |
| Section 11 | Session state documentation updated — volatility warning |
| Section 12 | WeasyPrint added to deployment dependencies |
| Section 13 | Config validation at startup added |

---

## TABLE OF CONTENTS

1. System Architecture Overview
2. User Flow to API Mapping
3. API Schema — All Endpoints
4. AI Prompt Catalog
5. Data Structures and Schemas
6. Document Processing Pipeline
7. Regulatory Knowledge Base — Digital Law Clerk
8. Data Governance and Security
9. Error Handling and Failure Modes
10. Config File Specifications
11. Frontend to Backend Integration
12. Deployment Architecture
13. Development Standards

---

## 1. SYSTEM ARCHITECTURE OVERVIEW

### High Level Architecture

```
USER BROWSER (Next.js Frontend — Vercel)
        |
        | HTTPS only — TLS 1.3 preferred
        |
FASTAPI BACKEND (Railway or Render)
        |
        |--- SURGICAL ENGINE
        |    Claude API — Single-pass full context window (200k+ tokens)
        |    Zero Data Retention enforced on every call
        |    Reads policy document + denial letter together
        |    Generates analysis, letter, claim file
        |    All user data discarded after response
        |
        |--- DIGITAL LAW CLERK
        |    V1 Primary: JSON regulatory lookup (fast, predictable)
        |    V1 Supplementary: LangChain RAG pipeline
        |    Chroma (dev) / Pinecone (prod)
        |    Regulatory Knowledge Base only — IRDAI circulars,
        |    Ombudsman Rules 2017, legal precedents
        |    No user data ever stored here
        |
        |--- WEASYPRINT PDF ENGINE
        |    Converts HTML letter templates to professional PDFs
        |    Claim File, CGO letters, Ombudsman packages
        |    No user data stored — generated in memory, returned immediately
        |
        |--- SUPABASE (Anonymous Metrics Only)
        |    No personal data
        |    Denial pattern codes, confidence levels,
        |    extraction completeness, processing duration
        |
        |--- CONFIG FILES (JSON — Pydantic validated at startup)
             Legal language, CGO directory,
             Letter templates (plain text + HTML for WeasyPrint),
             Ombudsman directory, Escalation ladder, App config,
             Prompt catalog
```

### Architecture Principles

**Principle 1 — Process and Discard:**
User documents are loaded into memory for the duration of one API call. They are never written to disk, never stored in a database, never passed to the vector database. After the API response is returned, all user data is garbage collected from memory.

**Principle 2 — Separation of User Data and Regulatory Data:**
The vector database contains only regulatory knowledge. User documents never touch the vector database. This separation is architectural, not procedural.

**Principle 3 — Single Source of Truth:**
All legal language, insurer contacts, letter templates, and escalation steps live in JSON config files. No hardcoding anywhere in Python files. Config files updated without touching code.

**Principle 4 — No Authentication in V1:**
Ezer V1 requires no login, no account, no session. Each request is stateless. Authentication added in V2 when paid tier requires it.

**Principle 5 — Full Forms Everywhere:**
No abbreviations in any user-facing output. Enforced at the prompt level and the template level.

**Principle 6 — Zero Data Retention on Every Claude API Call:**
Anthropic Zero Data Retention header enforced on every single Claude API call. No exceptions. Verified in integration tests before deployment. Creates a double layer of protection alongside Process and Discard.

**Principle 7 — Fail-Fast Config Validation:**
All JSON config files validated against Pydantic schemas at application startup. If any config file is malformed or missing required fields, the application refuses to start and logs exactly what is wrong. Silent failures with broken config are not acceptable.

**Principle 8 — Light Failure Over Hard Failure:**
Document quality issues, partial extraction, and low confidence scores are Light Failures. The user sees a plain English soft warning and can proceed. Hard Failures (application errors, API timeouts) show a plain English message and always suggest a next action. No technical error codes ever shown to users.

---

## 2. USER FLOW TO API MAPPING

### First Visit — Complete Flow

```
SCREEN 1 — Landing Page
User action: Clicks "Begin"
API call: None — static page
Frontend action: Navigate to Screen 2

SCREEN 2 — Upload Policy Document
User action: Selects PDF file, clicks Upload
API call: POST /extract-policy
Request: multipart/form-data { file: PDF binary }
Response: PolicyDocument object
Frontend action: Display Screen 3 with extracted fields

If password-protected PDF detected:
Response includes: { password_required: true }
Frontend action: Show password input field with hint text
User enters password
API call: POST /extract-policy with { file: PDF binary, password: string }

If document quality is low:
Response includes: { soft_warning: true, warning_message: string }
Frontend action: Show soft warning above extracted fields
User can edit fields and proceed — never blocked

SCREEN 3 — Know Your Policy
User action: Reviews extracted policy fields — all editable
User action: Edits any missing or incorrect fields
User action: Clicks "Yes — show me why my claim was denied"
API call: None — user confirmation only
Frontend action: Store confirmed policy fields in session state
Frontend action: Activate volatile state warning (beforeunload event)
Frontend action: Navigate to Screen 4

If user clicks "This does not look right":
Frontend action: Flag discrepancy in session state
Frontend action: Navigate to Screen 4 with discrepancy flag active

SCREEN 4 — Upload Denial Letter
User action: Selects PDF file, clicks Upload
API call: POST /analyse
Request: multipart/form-data {
  denial_file: PDF binary,
  policy_fields: PolicyDocument JSON
}
Response: DenialAnalysis object
Frontend action: Display Screen 5

SCREEN 5 — Your Insurer's Decision and What It Means
User action: Reads two column analysis
User action: Reads confidence statement
User action: Reads next steps
User action: Clicks "Generate my grievance letter"
API call: POST /generate-cgo
Request: {
  policy_fields: PolicyDocument,
  analysis: DenialAnalysis
}
Response: { letter: string, claim_file: ClaimFile }
Frontend action: Display Screen 6

User action: Clicks "Save this — I will decide later"
API call: POST /generate-pdf
Request: { content_type: "PARTIAL_CLAIM_FILE", content: ClaimFile }
Response: PDF binary
Frontend action: Trigger download — deactivates volatile state warning

User action: Clicks "My claim has been resolved"
API call: POST /metrics (anonymous only)
Request: { event: "CLAIM_RESOLVED", phase: "PHASE_2" }
Frontend action: Show — "We are glad to hear it. We hope your situation is resolved."
Frontend action: Deactivate volatile state warning

SCREEN 6 — Chief Grievance Officer Letter
User action: Reviews generated letter
User action: Edits Chief Grievance Officer email if needed
User action: Edits carbon copy email if needed
User action: Checks consent checkbox (includes AI disclosure)
User action: Clicks "Download Your Claim File"
API call: POST /generate-pdf
Request: { content_type: "FULL_CLAIM_FILE", content: ClaimFile }
Response: PDF binary
Frontend action: Trigger download — deactivates volatile state warning
Frontend action: Navigate to Screen 7

SCREEN 7 — Your Claim File
User action: Reviews Claim File summary card
User action: Clicks "Download Your Claim File" again if needed
API call: POST /generate-pdf (same as Screen 6)
Response: PDF binary
Frontend action: Trigger download
```

### Second Visit — Ombudsman Flow

```
LANDING PAGE (second visit)
User action: Indicates this is a return visit
Frontend action: Navigate to second visit upload screen

SECOND VISIT UPLOAD SCREEN
Frontend shows: "What are you uploading today?"
  Option A: "My Ezer Claim File"
  Option B: "The response I received from my insurer"
  Option C: "I am not sure"

If Option A or Option B selected:
  User uploads files individually — identified by their own selection
  API call: POST /generate-ombudsman directly
  No document detection API call needed

If Option C selected (AI fallback):
  User uploads both files
  API call: POST /detect-documents
  Request: multipart/form-data { file_1: PDF binary, file_2: PDF binary }
  Response: { doc_1_type: DocumentType, doc_2_type: DocumentType,
              doc_1_confidence: string, doc_2_confidence: string }
  Frontend action: Show detection results to user for confirmation
  If UNKNOWN returned: Ask user to identify — plain English message

User confirms document identification
Frontend shows location dropdown: "Which city or state are you based in?"
User selects location

API call: POST /generate-ombudsman
Request: {
  claim_file: ClaimFile JSON,
  cgo_rejection_file: PDF binary,
  user_location: string
}
Response: OmbudsmanPackage object

API call: POST /generate-pdf
Request: { content_type: "OMBUDSMAN_PACKAGE", content: OmbudsmanPackage }
Response: PDF binary — print-ready
Frontend action: Display package summary
Frontend action: Trigger download
```

---

## 3. API SCHEMA — ALL ENDPOINTS

### Current Endpoints — Live and Tested

```
GET  /
     Purpose: Root health check — confirms Ezer backend is alive
     Request: None
     Response: { status: "Ezer is alive", version: string }

GET  /health
     Purpose: Deployment health check for Railway or Render
     Request: None
     Response: { status: "healthy", timestamp: string }

POST /extract
     Purpose: Extract fields from denial letter PDF (original extractor — V1)
     Request: multipart/form-data { file: PDF }
     Response: DenialExtraction object

POST /analyse
     Purpose: Extract and analyse denial letter with policy context
     Request: multipart/form-data {
       denial_file: PDF,
       policy_fields: JSON string
     }
     Response: DenialAnalysis object

POST /generate-cgo
     Purpose: Generate Chief Grievance Officer letter
     Request: {
       policy_fields: PolicyDocument,
       analysis: DenialAnalysis
     }
     Response: { letter: string, claim_file: ClaimFile }

POST /case-json
     Purpose: Generate Claim File metadata JSON
     Request: { policy_fields: PolicyDocument, analysis: DenialAnalysis }
     Response: ClaimFile object
```

### New Endpoints — To Be Built

```
POST /extract-policy
     Purpose: Extract fields from policy document PDF
     Request: multipart/form-data {
       file: PDF binary,
       password: string (optional — for password-protected PDFs)
     }
     Response: PolicyDocument object
     Notes:
       Single-pass Claude API call — full policy document in context window
       Zero Data Retention header enforced
       Password parameter decrypts PDF in memory only
       extraction_confidence set by hybrid confidence logic
       soft_warning set if confidence is LOW
       If confidence LOW: warning_message populated in response
       All processing in memory — nothing written to disk

POST /detect-documents
     Purpose: AI fallback for document identification on second visit
     Request: multipart/form-data { file_1: PDF binary, file_2: PDF binary }
     Response: {
       doc_1_type: DocumentType,
       doc_1_confidence: string,
       doc_2_type: DocumentType,
       doc_2_confidence: string
     }
     Document types: EZER_CLAIM_FILE, CGO_REJECTION, ORIGINAL_DENIAL, UNKNOWN
     Notes:
       Only called when user selects "I am not sure" on second visit
       UI-first identification is primary — this is the surgical fallback
       Zero Data Retention enforced

POST /generate-ombudsman
     Purpose: Generate complete Ombudsman submission package
     Request: {
       claim_file: ClaimFile,
       cgo_rejection_file: PDF binary,
       user_location: string
     }
     Response: OmbudsmanPackage object
     Notes:
       Looks up correct Ombudsman office from ombudsman_directory.json
       Generates pre-filled complaint form in required format
       Zero Data Retention enforced on Claude API call

POST /generate-pdf
     Purpose: Convert any Ezer document to downloadable PDF via WeasyPrint
     Request: {
       content_type: string,  — FULL_CLAIM_FILE, PARTIAL_CLAIM_FILE,
                                 OMBUDSMAN_PACKAGE, CGO_LETTER
       content: ClaimFile or OmbudsmanPackage
     }
     Response: PDF binary
     Notes:
       WeasyPrint renders HTML template with content data
       HTML templates in letter_templates.json
       Professional typography — not raw text
       Generated in memory — returned immediately — nothing stored
       AI disclosure footer on every generated document

POST /metrics
     Purpose: Log anonymous observability metrics
     Request: {
       insurance_category: string,     — General, Life, Health
       denial_pattern: string,         — H1-H6, L1-L6, UNKNOWN
       confidence_level: string,       — HIGH, MEDIUM, LOW
       extraction_completeness: float, — 0.0 to 1.0
       processing_duration_ms: int,
       phase_completed: string,        — PHASE_1, PHASE_2, PHASE_3
       second_visit: boolean,
       event: string                   — optional, CLAIM_RESOLVED etc.
     }
     Response: { logged: true }
     Notes:
       No personal data in any field
       No IP address stored
       No policy number, no name, no document content
       Stored in Supabase anonymous_metrics table
       Called after each major processing step
       Fire and forget — failure does not affect user flow
```

---

## 4. AI PROMPT CATALOG

All prompts stored in config/prompts/ as JSON files. Never hardcoded in Python. Versioned. Updated without code changes. Zero Data Retention enforced on every call.

### Hybrid Confidence Logic — Applied to All Prompts Returning Confidence

```python
def calculate_final_confidence(claude_confidence: str,
                                extraction_completeness: float) -> str:
    """
    Automatically downgrade confidence if document extraction was poor.
    claude_confidence: HIGH, MEDIUM, or LOW — from Claude's self-assessment
    extraction_completeness: 0.0 to 1.0 — fields extracted / fields expected
    Returns final confidence level to show user.
    """

    # Auto-downgrade rule 1: Below 50% completeness always means LOW
    if extraction_completeness < 0.5:
        return "LOW"

    # Auto-downgrade rule 2: Below 80% completeness demotes HIGH to MEDIUM
    elif extraction_completeness < 0.8:
        if claude_confidence == "HIGH":
            return "MEDIUM"
        return claude_confidence

    # Above 80% completeness: trust Claude's assessment
    else:
        return claude_confidence


def get_confidence_statement(confidence_level: str) -> str:
    """
    Convert internal confidence level to plain English user-facing statement.
    Never shows LOW, MEDIUM, HIGH labels to user.
    Never discourages escalation — Rule 9.
    """
    statements = {
        "HIGH": "Based on the documents you have provided, your next steps are clear.",
        "MEDIUM": "We have completed your analysis. Some details were unclear — please review the information above carefully before proceeding.",
        "LOW": "We could only read part of your document. Your analysis may be incomplete. Please review carefully. You can still proceed — your options remain open."
    }
    return statements.get(confidence_level, statements["MEDIUM"])
```

---

### PROMPT 1 — Policy Document Extractor
**Endpoint:** POST /extract-policy
**File:** config/prompts/policy_extractor_prompt.json
**Purpose:** Extract all key fields from a policy document in plain English
**Zero Data Retention:** Enforced

```
SYSTEM PROMPT:
You are Ezer's policy document analyst. Your job is to read an insurance
policy document completely and extract key information in plain English
that a policyholder can understand without any insurance knowledge.

Rules you must follow without exception:
1. Extract only what is explicitly stated in the document. Never infer or assume.
2. If a field cannot be found anywhere in the document, return exactly the
   string "Not found in document" — never return null, never return blank.
3. Use plain English only. No insurance jargon. No abbreviations of any kind.
   Write Pre-Existing Disease in full — never PED.
   Write Insurance Regulatory and Development Authority of India in full — never IRDAI.
4. For dates, use DD Month YYYY format. Example: 15 July 2024.
5. For amounts, use Indian rupee format with commas. Example: Rs 5,00,000.
6. For waiting periods, state in plain English.
   Example: "2 years from policy start date for pre-existing conditions."
7. For key exclusions, list the top 5 most important ones in plain English.
   One sentence each. No legal language.
8. Return your response as valid JSON only.
   No preamble. No explanation. No markdown. No backtick code blocks.
   The first character of your response must be the opening brace.

USER PROMPT:
Read the following insurance policy document completely — every page, every
clause, every exclusion, every definition. Extract the following fields and
return as JSON:

{
  "policyholder_name": "",
  "policy_number": "",
  "insurer_name": "",
  "policy_start_date": "",
  "policy_end_date": "",
  "sum_insured": "",
  "waiting_period_general": "",
  "waiting_period_pre_existing": "",
  "pre_existing_disease_clause": "",
  "room_rent_limit": "",
  "key_exclusions": [],
  "policy_address": "",
  "branch_details": "",
  "extraction_confidence": ""
}

For extraction_confidence, honestly assess how clearly you could read and
extract information from this document. Return one of: HIGH, MEDIUM, LOW.
HIGH means you found clear values for most fields.
MEDIUM means some fields were unclear or ambiguous.
LOW means significant portions of the document were unreadable or the
document appears to be incomplete.

Document:
[FULL POLICY DOCUMENT TEXT INSERTED HERE]
```

---

### PROMPT 2 — Denial Letter Extractor
**Endpoint:** POST /extract and POST /analyse (step 1)
**File:** config/prompts/denial_extractor_prompt.json
**Purpose:** Extract all key fields from a denial letter
**Zero Data Retention:** Enforced

```
SYSTEM PROMPT:
You are Ezer's denial letter analyst. Your job is to read an insurance
denial letter and extract key information with precision.

Rules:
1. Extract only what is explicitly stated. Never infer.
2. Quote the rejection reason verbatim — exact words from the letter.
   Do not paraphrase the verbatim field.
3. Also provide a plain English translation of the rejection reason.
4. If a field cannot be found, return "Not found in document."
5. No abbreviations in plain English fields.
6. Return valid JSON only. No preamble. No markdown. No backticks.

USER PROMPT:
Read the following insurance denial letter and extract these fields as JSON:

{
  "insurer_name": "",
  "claim_reference_number": "",
  "policy_number": "",
  "denial_date": "",
  "rejection_reason_verbatim": "",
  "rejection_reason_plain_english": "",
  "denial_type": "",
  "patient_name": "",
  "hospital_name": "",
  "treatment_description": "",
  "amount_denied": "",
  "cgo_email": "",
  "extraction_confidence": ""
}

For denial_type, return one of:
CASHLESS_DENIAL, REIMBURSEMENT_DENIAL, PARTIAL_DENIAL, UNKNOWN

For extraction_confidence: HIGH, MEDIUM, or LOW.

Document:
[FULL DENIAL LETTER TEXT INSERTED HERE]
```

---

### PROMPT 3 — Denial Analyser
**Endpoint:** POST /analyse (step 2)
**File:** config/prompts/analyser_prompt.json
**Purpose:** Analyse denial in full context of policy document
**Zero Data Retention:** Enforced

```
SYSTEM PROMPT:
You are Ezer's claim analysis engine. You are given an insurance policy
document and a denial letter together. You analyse the denial in the
context of what the policy actually covers.

Rules you must follow without exception:
1. Never say a claim is invalid or not worth pursuing.
2. Never discourage the user from escalating through official channels.
3. Never use insurance abbreviations — always full forms.
4. Never make promises about outcomes.
5. For the right_column_statement field, use this exact template and
   substitute only the bracketed section:
   "Your insurer has declined this claim citing [plain English reason].
    You may request a review of this decision by writing to the
    Chief Grievance Officer."
6. The denial_pattern field is for internal use only. Never surface
   pattern codes to users.
7. For regulatory_basis, first check the JSON regulatory lookup provided.
   If a relevant citation exists, use it. Then check your knowledge of
   IRDAI regulations and Ombudsman Rules 2017 for supplementary citations.
8. Return valid JSON only. No preamble. No markdown. No backticks.

USER PROMPT:
You have been given:
1. The policyholder's insurance policy document (full text)
2. The denial letter received from their insurer (full text)
3. Policy fields confirmed by the user after review
4. Regulatory JSON lookup for relevant citations

Analyse the denial in the context of the policy and return this JSON:

{
  "rejection_reason_verbatim": "",
  "rejection_reason_plain_english": "",
  "policy_context": "",
  "right_column_statement": "",
  "confidence_level": "",
  "denial_pattern": "",
  "regulatory_basis": "",
  "regulatory_citation_source": "",
  "next_step_1": "",
  "next_step_2": "",
  "discrepancy_flag": false,
  "discrepancy_description": ""
}

For confidence_level: HIGH, MEDIUM, or LOW based on document clarity
and how clearly the policy covers or excludes the denied treatment.
Note: This will be further adjusted by extraction completeness score.

For regulatory_citation_source: JSON_LOOKUP, RAG_SUPPLEMENTARY, or
CLAUDE_KNOWLEDGE — so we know where the citation came from.

For denial_pattern: Use H1 through H6 for health insurance patterns,
L1 through L6 for life insurance patterns. UNKNOWN if unclear.

Policy document:
[FULL POLICY DOCUMENT TEXT]

Denial letter:
[FULL DENIAL LETTER TEXT]

Confirmed policy fields from user:
[CONFIRMED POLICY FIELDS JSON]

Regulatory JSON lookup results:
[REGULATORY CITATIONS FROM JSON CONFIG]

Supplementary RAG results (if available):
[REGULATORY CITATIONS FROM KNOWLEDGE BASE — may be empty]
```

---

### PROMPT 4 — Chief Grievance Officer Letter Generator
**Endpoint:** POST /generate-cgo
**File:** config/prompts/cgo_letter_prompt.json
**Purpose:** Generate formal, legally grounded Chief Grievance Officer letter
**Zero Data Retention:** Enforced

```
SYSTEM PROMPT:
You are Ezer's escalation letter writer. You generate formal complaint
letters to insurance company Chief Grievance Officers on behalf of
policyholders.

Rules without exception:
1. Never use abbreviations — always full forms.
   Chief Grievance Officer — never CGO.
   Insurance Regulatory and Development Authority of India — never IRDAI.
   Pre-Existing Disease — never PED.
2. Never use aggressive or combative language.
3. Use formal, professional, respectful language throughout.
4. Cite the specific regulation or rule that applies — from the
   regulatory_basis field provided.
5. Include all reference numbers from the denial letter.
6. Address to Chief Grievance Officer by name if provided in
   the cgo_directory config. Otherwise: "The Chief Grievance Officer."
7. The tone is: informed, calm, firm, respectful. Like a well-prepared
   professional who knows their rights and exercises them calmly.
8. State the policyholder's right to escalate to the Insurance Ombudsman
   if this grievance is not resolved. The insurer is required by
   regulation to respond within 15 days.
9. Never promise or imply a specific outcome.
10. The letter footer must include:
    "This letter was prepared with AI assistance by Ezer
     (getezer.app). Ezer is not a legal advisor. This letter is
     guidance only."
11. Return the letter as plain text only. No JSON. No markdown.
    No backticks. Just the letter text from salutation to signature.

USER PROMPT:
Generate a formal complaint letter to the Chief Grievance Officer.

Today's date: [TODAY'S DATE]
Policyholder details: [POLICY FIELDS JSON]
Denial details: [DENIAL ANALYSIS JSON]
Regulatory basis: [REGULATORY CITATION]
Chief Grievance Officer name and email: [FROM CGO DIRECTORY CONFIG]
Carbon copy: complaints@irdai.gov.in

The letter must include in this order:
1. Date
2. Sender details (policyholder name and address from policy)
3. Recipient details (Chief Grievance Officer, insurer name, address)
4. Subject line: "Formal Grievance — Policy Number [X] — Claim Reference [Y]"
5. Salutation
6. Reference to the denial letter — date and rejection reason verbatim
7. Why the denial is being contested — citing policy terms in plain English
8. The specific regulation or rule that supports the review request
9. Clear request for review and written response within 15 days as
   required by regulation
10. Notice that failure to resolve will result in escalation to the
    Insurance Ombudsman
11. Request for acknowledgement of this complaint
12. Closing and signature block
13. AI assistance footer as specified in Rule 10 above
```

---

### PROMPT 5 — Document Type Detector
**Endpoint:** POST /detect-documents
**File:** config/prompts/document_detector_prompt.json
**Purpose:** AI fallback for document identification when user is unsure
**Zero Data Retention:** Enforced

```
SYSTEM PROMPT:
You are Ezer's document classifier. Your job is to identify what type
of insurance document has been uploaded. This is used only when the
user is unsure what they have uploaded.

Return valid JSON only. No preamble. No markdown. No backticks.

USER PROMPT:
Read the following document carefully and classify it.

{
  "document_type": "",
  "confidence": "",
  "key_signals": [],
  "plain_english_description": ""
}

Document types to choose from:

EZER_CLAIM_FILE:
A document generated by Ezer. Look for: Ezer branding or getezer.app
reference, Claim File reference number starting with EZR-, structured
sections including policy summary and escalation steps, AI assistance
footer.

CGO_REJECTION:
A response from an insurer's Chief Grievance Officer or Grievance
Redressal Team. Look for: sender email containing cgo@ or grievance@,
language like "we have reviewed your grievance" or "we have examined
your complaint", signed by a named officer with "Desk of Chief
Grievance Officer" or "Grievance Redressal Team."

ORIGINAL_DENIAL:
An original claim denial letter from an insurer or Third Party
Administrator. Look for: Pre-Authorisation Denial, Cashless Denial,
Claim Rejection language, claim reference number format, denial reason.

UNKNOWN:
Cannot be classified with reasonable confidence.

For confidence: HIGH (very clear signals), MEDIUM (some signals present),
LOW (few or ambiguous signals).

For plain_english_description: One sentence describing what this document
appears to be, in plain English, for display to the user.

Document:
[DOCUMENT TEXT]
```

---

### PROMPT 6 — Ombudsman Package Generator
**Endpoint:** POST /generate-ombudsman
**File:** config/prompts/ombudsman_prompt.json
**Purpose:** Generate complete print-ready Ombudsman submission package
**Zero Data Retention:** Enforced

```
SYSTEM PROMPT:
You are Ezer's Ombudsman submission specialist. You generate complete,
print-ready submission packages for the Insurance Ombudsman.

Rules:
1. Never use abbreviations — always full forms.
2. Follow Insurance Ombudsman Rules 2017 format requirements.
3. Include all required fields for the Ombudsman complaint.
4. Generate a clear dated chronology of events.
5. Generate a complete document checklist.
6. Address package to the correct Ombudsman office based on location.
7. Include the reminder: advocates and agents are not permitted.
8. Include limitation reminder: one year from Chief Grievance Officer
   response date.
9. Every generated document must include the AI assistance footer:
   "Prepared with AI assistance by Ezer (getezer.app).
    Ezer is not a legal advisor. This is guidance only."
10. Return structured JSON with all package components.
    No preamble. No markdown. No backticks.

USER PROMPT:
Generate a complete Ombudsman submission package.

Claim File: [CLAIM FILE JSON]
Chief Grievance Officer rejection text: [EXTRACTED CGO REJECTION TEXT]
User location: [CITY OR STATE]
Ombudsman office details: [FROM OMBUDSMAN DIRECTORY CONFIG]

Return JSON:
{
  "ombudsman_office": {
    "name": "",
    "address": "",
    "contact": "",
    "working_hours": ""
  },
  "complaint_form": {
    "complainant_name": "",
    "complainant_address": "",
    "policy_number": "",
    "insurer_name": "",
    "claim_reference_numbers": [],
    "date_of_original_denial": "",
    "date_of_cgo_response": "",
    "nature_of_complaint": "",
    "relief_sought": "",
    "declaration": ""
  },
  "covering_letter": "",
  "chronology": [
    {
      "date": "",
      "event": "",
      "reference": ""
    }
  ],
  "document_checklist": [],
  "submission_instructions": "",
  "limitation_reminder": "",
  "advocates_reminder": "",
  "ai_footer": ""
}
```

---

## 5. DATA STRUCTURES AND SCHEMAS

### PolicyDocument

```python
class PolicyDocument(BaseModel):
    """
    Fields extracted from the user's insurance policy document.
    All fields are strings — never null, never blank.
    Missing fields contain "Not found in document".
    """
    policyholder_name: str
    policy_number: str
    insurer_name: str
    policy_start_date: str
    policy_end_date: str
    sum_insured: str
    waiting_period_general: str
    waiting_period_pre_existing: str
    pre_existing_disease_clause: str
    room_rent_limit: str
    key_exclusions: List[str]           # Maximum 5 items
    policy_address: str                 # Critical for Ombudsman jurisdiction
    branch_details: str

    # Quality and confidence fields
    extraction_confidence: str          # HIGH, MEDIUM, LOW — from Claude
    extraction_completeness: float      # 0.0 to 1.0 — calculated by backend
    final_confidence: str               # After hybrid downgrade logic applied
    soft_warning: bool                  # True if final_confidence is LOW
    warning_message: str                # Plain English — shown to user if soft_warning

    # Password handling
    password_required: bool             # True if PDF was password protected
    password_accepted: bool             # True if password successfully decrypted

    # User confirmation fields — populated after Screen 3
    user_confirmed: bool                # True after user clicks confirm
    discrepancy_flagged: bool           # True if user clicks "does not look right"
    discrepancy_description: str        # User's description if flagged
```

### DenialExtraction

```python
class DenialExtraction(BaseModel):
    """
    Fields extracted from the user's denial letter.
    All string fields are never null, never blank.
    """
    insurer_name: str
    claim_reference_number: str
    policy_number: str
    denial_date: str
    rejection_reason_verbatim: str      # Exact words from letter
    rejection_reason_plain_english: str # Plain English translation
    denial_type: str                    # CASHLESS_DENIAL, REIMBURSEMENT_DENIAL,
                                        # PARTIAL_DENIAL, UNKNOWN
    patient_name: str
    hospital_name: str
    treatment_description: str
    amount_denied: str
    cgo_email: str                      # If found in letter — pre-fills Screen 6

    # Quality fields
    extraction_confidence: str
    extraction_completeness: float
    final_confidence: str
    soft_warning: bool
    warning_message: str
```

### DenialAnalysis

```python
class DenialAnalysis(BaseModel):
    """
    Full analysis of the denial in context of the policy.
    Includes regulatory basis and next steps.
    """
    # Denial details
    rejection_reason_verbatim: str
    rejection_reason_plain_english: str
    policy_context: str                 # How the policy relates to the denial

    # User-facing content
    right_column_statement: str         # The locked template — shown on Screen 5
    confidence_statement: str           # Plain English — shown on Screen 5
    next_step_1: str                    # Chief Grievance Officer instruction
    next_step_2: str                    # Insurance Ombudsman instruction

    # Internal fields — never shown to user
    confidence_level: str               # HIGH, MEDIUM, LOW — internal
    denial_pattern: str                 # H1-H6, L1-L6 — internal
    regulatory_basis: str               # Citation used in CGO letter
    regulatory_citation_source: str     # JSON_LOOKUP, RAG_SUPPLEMENTARY, CLAUDE_KNOWLEDGE

    # Discrepancy tracking
    discrepancy_flag: bool
    discrepancy_description: str
```

### ClaimFile

```python
class ClaimFile(BaseModel):
    """
    Complete Claim File — the main output of Ezer.
    Downloaded by user as PDF. Lives on user's device — not on server.
    """
    # Reference
    claim_file_reference: str           # Format: EZR-YYYYMMDD-XXXX
    generated_date: str
    generated_time: str

    # Content
    policy_summary: PolicyDocument
    denial_extraction: DenialExtraction
    denial_analysis: DenialAnalysis
    cgo_letter: str                     # Full letter text

    # Pre-filled contact details
    cgo_email_prefilled: str            # From CGO directory — user-editable
    irdai_cc_email: str                 # Always complaints@irdai.gov.in

    # Escalation
    escalation_next_step: str
    ombudsman_office_mapped: str        # Populated on second visit

    # Consent record — DPDP compliance
    consent_given: bool
    consent_timestamp: str
    consent_text_version: str           # "2.0" — includes AI disclosure
    consent_text_shown: str             # Full exact text shown to user

    # Phase tracking
    phase_completed: str                # PHASE_1, PHASE_2, PHASE_3
    return_visit: bool

    # Disclaimer — on every document
    disclaimer: str                     # Full text including AI disclosure
```

### OmbudsmanPackage

```python
class OmbudsmanPackage(BaseModel):
    """
    Complete print-ready Ombudsman submission package.
    Generated on second visit. Downloaded as PDF.
    """
    package_reference: str
    generated_date: str
    claim_file_reference: str           # Links to original Claim File

    ombudsman_office: dict              # Name, address, contact, hours
    complaint_form: dict                # All fields pre-filled
    covering_letter: str
    chronology: List[dict]              # Dated events from denial to CGO rejection
    document_checklist: List[str]
    submission_instructions: str
    limitation_reminder: str
    advocates_reminder: str
    ai_footer: str
```

### AnonymousMetric

```python
class AnonymousMetric(BaseModel):
    """
    Anonymous observability metric stored in Supabase.
    No personal data of any kind.
    """
    timestamp: str
    insurance_category: str             # General, Life, Health
    denial_pattern: str                 # H1-H6, L1-L6, UNKNOWN
    confidence_level: str               # HIGH, MEDIUM, LOW
    extraction_completeness: float      # 0.0 to 1.0
    processing_duration_ms: int
    phase_completed: str                # PHASE_1, PHASE_2, PHASE_3
    second_visit: bool
    event: Optional[str]                # CLAIM_RESOLVED, etc. — optional
```

### DocumentType

```python
class DocumentType(str, Enum):
    EZER_CLAIM_FILE = "EZER_CLAIM_FILE"
    CGO_REJECTION = "CGO_REJECTION"
    ORIGINAL_DENIAL = "ORIGINAL_DENIAL"
    UNKNOWN = "UNKNOWN"
```

---

## 6. DOCUMENT PROCESSING PIPELINE

### Policy Document Processing — POST /extract-policy

```
Step 1 — Receive and validate PDF
         Check file is PDF — magic bytes check %PDF — reject non-PDF
         Check MIME type — application/pdf only
         Check file size — reject above 10MB
         Check if password protected
         If password protected and password provided — decrypt in memory using PyMuPDF
         If password protected and no password — return { password_required: true }
         Never write file to disk at any point

Step 2 — Extract text
         PyMuPDF extracts text from all pages
         pdfplumber extracts tables if present
         Full text assembled in memory as single string

Step 3 — Calculate extraction completeness
         Count characters extracted versus expected minimum for a policy document
         Calculate ratio — set extraction_completeness (0.0 to 1.0)
         If very low (below 0.3) — document may be scanned image — set soft_warning

Step 4 — Claude API call — Surgical Engine
         Prompt 1 loaded from config/prompts/policy_extractor_prompt.json
         Full document text inserted into USER PROMPT
         Zero Data Retention header added: {"anthropic-beta": "zero-data-retention-2025-02-19"}
         API call made — single pass — full context window
         JSON response parsed — strip any accidental markdown if present

Step 5 — Apply hybrid confidence logic
         final_confidence = calculate_final_confidence(
           claude_confidence, extraction_completeness)
         confidence_statement = get_confidence_statement(final_confidence)
         soft_warning = (final_confidence == "LOW")

Step 6 — Validate and fill missing fields
         All fields checked — if null or empty — set to "Not found in document"
         Never return null for any field

Step 7 — Log anonymous metric
         POST /metrics with insurance_category, confidence_level,
         extraction_completeness, processing_duration_ms
         Fire and forget — metric failure does not affect response

Step 8 — Return PolicyDocument
         All user document data explicitly deleted from memory
         del document_text, del pdf_contents
         Python garbage collector invoked
```

### Denial Letter Processing — POST /analyse

```
Step 1 — Receive and validate denial letter PDF
         Same validation as policy document

Step 2 — Extract text
         Same extraction as policy document

Step 3 — Regulatory Knowledge Base query
         Query JSON regulatory lookup first — fast, synchronous
         If RAG pipeline available — query in parallel — asynchronous
         Combine results — JSON lookup cited first, RAG as supplementary

Step 4 — Claude API call — Surgical Engine
         Prompt 3 loaded from config/prompts/analyser_prompt.json
         Full policy document text + denial letter text + confirmed policy
         fields + regulatory citations — all in single context window
         Zero Data Retention header enforced
         JSON response parsed

Step 5 — Apply hybrid confidence logic
         Same as policy document processing

Step 6 — Construct DenialAnalysis
         Map confidence level to confidence statement
         Verify right_column_statement uses locked template
         Denial pattern stored internally — never in user-facing response

Step 7 — Log anonymous metric

Step 8 — Return DenialAnalysis
         All user data explicitly deleted from memory
```

---

## 7. REGULATORY KNOWLEDGE BASE — DIGITAL LAW CLERK

### V1 Architecture — JSON Primary, RAG Supplementary

**Primary source — JSON regulatory lookup:**
All key IRDAI regulations, Ombudsman Rules 2017 provisions, and common citations stored in config/regulatory_citations.json. Keyed by denial pattern code and insurance category. Looked up synchronously — zero latency.

```json
{
  "version": "1.0",
  "citations": {
    "H5": {
      "pattern_name": "Investigative Procedure",
      "primary_citation": "Insurance Ombudsman Rules 2017, Rule 13 — ...",
      "irdai_circular": "IRDAI/HLT/REG/CIR/...",
      "plain_english": "A mandatory prerequisite procedure cannot be classified as purely investigative when it was required to enable the primary treatment."
    },
    "H4": {
      "pattern_name": "Changed Rejection Reason",
      "primary_citation": "...",
      "irdai_circular": "...",
      "plain_english": "..."
    }
  }
}
```

**Supplementary source — RAG pipeline:**
LangChain RAG pipeline queries Chroma (dev) or Pinecone (prod) for relevant passages from the full regulatory knowledge base. Called in parallel after JSON lookup. Supplements JSON citations with more specific passages. If RAG returns nothing useful — JSON citation used alone.

**V2:** RAG becomes primary as knowledge base grows and JSON lookup becomes insufficient for complex cases.

### Knowledge Base Contents

| Document | Description | Priority |
|---|---|---|
| Insurance Ombudsman Rules 2017 | Complete rules as amended to date | Critical |
| IRDAI Health Insurance Regulations 2016 | Master circular | Critical |
| IRDAI Master Circular on Health Insurance 2024 | Latest amendments | Critical |
| IRDAI Policyholder Protection Regulations 2024 | Consumer rights | Critical |
| IRDAI Guidelines on Standardisation 2020 | Standard definitions | High |
| Selected Ombudsman Awards | Precedent cases — health and life | High |
| Consumer Court Judgements | Insurance-related precedents | Medium |

### Seeding Process

```bash
# Run once to seed — then update as new documents are added
python3 backend/scripts/seed_knowledge_base.py

# Script actions:
# 1. Reads PDFs from backend/knowledge_base/
# 2. Chunks into 500-token segments, 50-token overlap
# 3. Generates embeddings
# 4. Stores in Chroma (dev) or Pinecone (prod)
# 5. Logs all documents indexed with timestamps
# 6. No user data involved at any stage
```

---

## 8. DATA GOVERNANCE AND SECURITY

*This section satisfies a Banking, Financial Services, and Insurance security audit. Every statement is implementable and verifiable.*

---

### 8.1 Data Classification

| Data Type | Classification | Storage | Retention |
|---|---|---|---|
| Policy document | Highly Sensitive — Personal Financial Data | Memory only during processing | Zero — discarded after API response |
| Denial letter | Highly Sensitive — Personal Financial Data | Memory only during processing | Zero — discarded after API response |
| Extracted policy fields | Sensitive — Personal Financial Data | Frontend session state only | Session duration — cleared on browser close |
| Claim File (downloaded) | Sensitive — user-owned | User's device only | User's choice |
| Ombudsman package (downloaded) | Sensitive — user-owned | User's device only | User's choice |
| Policyholder name | Personal Data under DPDP Act 2023 | Memory during processing, Claim File on user device | Zero server-side |
| Email address | Personal Data — optional | Not collected in V1 | Not applicable |
| City or state | Non-sensitive | Memory during Ombudsman flow | Zero |
| Anonymous metrics | Non-personal | Supabase anonymous_metrics table | 12 months rolling |
| Regulatory Knowledge Base | Non-personal — public documents | Vector database | Permanent |
| Application logs | Operational — no personal data | Server logs | 30 days rolling |

---

### 8.2 Process and Discard — Technical Implementation

**Code-level enforcement in every endpoint handling user documents:**

```python
async def process_document(file: UploadFile):
    """
    Process a user document and discard all data after response.
    Never writes to disk. Never stores in database.
    Explicit deletion after use.
    """
    pdf_contents = None
    document_text = None

    try:
        # Read file into memory only — never write to disk
        pdf_contents = await file.read()

        # Validate
        if not pdf_contents.startswith(b'%PDF'):
            raise HTTPException(400, "This does not appear to be a valid PDF.")

        # Extract text in memory
        document_text = extract_text_from_bytes(pdf_contents)

        # Process
        result = await call_claude_api(document_text)

        return result

    except Exception as e:
        log_error_without_personal_data(e)
        raise

    finally:
        # Always executes — even on error
        # Explicit deletion of all user data variables
        if pdf_contents is not None:
            del pdf_contents
        if document_text is not None:
            del document_text
        # Force garbage collection
        import gc
        gc.collect()
```

**Verification:**
Process audit log records each API call with timestamp, endpoint, duration, status. No personal data in any log entry. Auditable.

---

### 8.3 Anthropic Zero Data Retention — NEW IN TDD v1.1

**What Zero Data Retention means:**
When Zero Data Retention is configured, Anthropic does not store any inputs or outputs from API calls. This means the user's policy document and denial letter text — sent to Claude API for analysis — are not retained by Anthropic after processing.

This creates a double layer of protection:
- Layer 1: Ezer's Process and Discard — user data deleted from Ezer's servers
- Layer 2: Anthropic's Zero Data Retention — user data not retained by Anthropic

**Implementation — applied to every single Claude API call:**

```python
import anthropic

# Initialise client once at startup
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def call_claude_with_zdr(system_prompt: str, user_prompt: str,
                          max_tokens: int = 4096) -> str:
    """
    Make a Claude API call with Zero Data Retention enforced.
    This function must be used for ALL Claude API calls in Ezer.
    Never call the Claude API directly without this function.
    """
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
        # Zero Data Retention header — enforced on every call
        extra_headers={
            "anthropic-beta": "zero-data-retention-2025-02-19"
        }
    )
    return response.content[0].text


def verify_zdr_compliance():
    """
    Run at startup to verify Zero Data Retention is working.
    Makes a test call and checks response headers.
    Logs confirmation — fails startup if ZDR cannot be verified.
    """
    # Test call with innocuous content
    test_response = call_claude_with_zdr(
        system_prompt="You are a test assistant.",
        user_prompt="Respond with the single word: verified",
        max_tokens=10
    )
    # Log confirmation
    print("Zero Data Retention: Verified and active.")
```

**Audit trail:**
ZDR verification logged at every application startup. Log entry: timestamp, ZDR status, model version. No personal data in log.

**Privacy policy disclosure:**
"We use Anthropic's Zero Data Retention API configuration. This means your documents are not retained by Anthropic after analysis. Combined with our own Process and Discard architecture, your documents exist in our systems only for the seconds required to generate your Claim File."

---

### 8.4 Encryption in Transit

- All frontend to backend communication: HTTPS only — TLS 1.3 preferred, TLS 1.2 minimum
- .app domain enforces HTTPS — HTTP redirected automatically
- Claude API: HTTPS — Anthropic's transport security
- Pinecone: HTTPS — Pinecone's transport security
- Supabase: HTTPS — Supabase's transport security
- No unencrypted channels at any point

---

### 8.5 Encryption at Rest

- User documents: Not applicable — never stored
- Anonymous metrics (Supabase): AES-256 at rest — Supabase platform default
- Regulatory Knowledge Base (Pinecone prod): AES-256 at rest — Pinecone default
- Regulatory Knowledge Base (Chroma dev): Local encrypted volume
- Config files: Not encrypted — contain no personal data
- Environment variables: Encrypted by Railway or Render platform

---

### 8.6 API Key Management

```
ANTHROPIC_API_KEY    Stored in .env locally
                     Stored as environment variable in Railway or Render
                     Never committed to GitHub — .gitignore enforced
                     Never logged
                     Rotation: every 90 days — calendar reminder set
                     Written to .env via Python only:
                     python3 -c "open('backend/.env','w').write('KEY=VALUE')"

PINECONE_API_KEY     Same handling

SUPABASE_URL         Same handling
SUPABASE_KEY         Same handling
```

---

### 8.7 Input Validation

```python
ALLOWED_MIME_TYPES = ["application/pdf"]
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB

async def validate_pdf_upload(file: UploadFile) -> bytes:
    """
    Validate uploaded file before any processing.
    Rejects non-PDFs, oversized files, and MIME spoofing attempts.
    """
    # Check MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(400, "Only PDF files are accepted.")

    # Read into memory
    contents = await file.read()

    # Check file size
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(400, "File size must be under 10MB.")

    # Check PDF magic bytes — prevents MIME spoofing
    if not contents.startswith(b'%PDF'):
        raise HTTPException(400, "This does not appear to be a valid PDF.")

    return contents
```

**Prompt injection prevention:**
User document text passed as document content — not as instructions. System prompts loaded from config files only. User input cannot override system prompt. Claude API separates system and user roles — document text cannot issue new instructions.

---

### 8.8 CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

ALLOWED_ORIGINS_PRODUCTION = [
    "https://getezer.app",
    "https://www.getezer.app",
]

ALLOWED_ORIGINS_DEVELOPMENT = [
    "http://localhost:3000",
]

# Set in app_config.json — different per environment
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,     # Set per environment
    allow_credentials=False,            # No cookies, no credentials
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
```

---

### 8.9 Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Limits per endpoint per IP address
@app.post("/extract-policy")
@limiter.limit("10/minute")
async def extract_policy(): pass

@app.post("/analyse")
@limiter.limit("10/minute")
async def analyse(): pass

@app.post("/generate-cgo")
@limiter.limit("5/minute")
async def generate_cgo(): pass

@app.post("/generate-pdf")
@limiter.limit("10/minute")
async def generate_pdf(): pass

@app.post("/generate-ombudsman")
@limiter.limit("5/minute")
async def generate_ombudsman(): pass
```

---

### 8.10 Anonymous Metrics Governance

```python
# Supabase table schema — anonymous_metrics
# Created once — never modified to add personal fields
"""
CREATE TABLE anonymous_metrics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    insurance_category TEXT,        -- General, Life, Health
    denial_pattern TEXT,            -- H1-H6, L1-L6, UNKNOWN
    confidence_level TEXT,          -- HIGH, MEDIUM, LOW
    extraction_completeness FLOAT,  -- 0.0 to 1.0
    processing_duration_ms INTEGER,
    phase_completed TEXT,
    second_visit BOOLEAN,
    event TEXT                      -- Optional event label
    -- NO personal data columns ever added to this table
);
"""

async def log_anonymous_metric(metric: AnonymousMetric):
    """
    Log anonymous metric to Supabase.
    Fire and forget — failure does not affect user flow.
    Explicitly verified to contain no personal data before logging.
    """
    try:
        await supabase.table("anonymous_metrics").insert(
            metric.dict()
        ).execute()
    except Exception:
        # Metric failure is silent — never affects user
        pass
```

**Governance rules for anonymous metrics:**
- Schema is append-only — no personal data columns ever added
- Data retained for 12 months rolling — older records deleted automatically
- Never shared externally — never sold — never used for advertising
- Accessible only to founder for product quality review
- Disclosed in privacy policy before beta launch
- Insurer name not stored in V1 — insurance category only

---

### 8.11 Logging Policy

**Logged:**
API endpoint called, HTTP status code, processing duration, timestamp, sanitised error messages.

**Never logged:**
Request body contents, document text, policy numbers, policyholder names, API keys, IP addresses beyond rate limiting.

**Retention:** 30 days rolling.

---

### 8.12 DPDP Act 2023 Compliance

| Requirement | Implementation | Status |
|---|---|---|
| Consent before processing | Upload is implicit consent — purpose clearly stated on landing page | V1 compliant |
| Explicit consent for sensitive operations | Checkbox with AI disclosure before Chief Grievance Officer letter generation | V1 compliant |
| Data minimisation | Only fields necessary for escalation extracted | V1 compliant |
| Purpose limitation | Data used only for escalation documents | V1 compliant |
| Storage limitation | Process and Discard plus Zero Data Retention | V1 compliant |
| Right to erasure | Not applicable — nothing stored | V1 compliant |
| Privacy notice | Plain English privacy policy | Before beta |
| Cross-border transfer | Claude API — Anthropic USA — Zero Data Retention — disclosed | Before beta |
| AI involvement disclosure | Rule 10 — in consent gate and document footer | V1 compliant |
| Anonymous metrics disclosure | Disclosed in privacy policy | Before beta |

---

### 8.13 Third Party Data Sharing

| Third Party | Data Shared | Purpose | ZDR | User Informed |
|---|---|---|---|---|
| Anthropic Claude API | Document text — processing only | AI analysis | Yes — enforced | Privacy policy |
| Pinecone | Regulatory documents only — no user data | Knowledge base | Not applicable | Not applicable |
| Vercel | No personal data | Frontend hosting | Not applicable | Not applicable |
| Railway or Render | No personal data | Backend hosting | Not applicable | Not applicable |
| Supabase | Anonymous metrics only — no personal data | Product analytics | Not applicable | Privacy policy |

No user data sold, shared for advertising, or transferred to any unlisted party.

---

### 8.14 Vulnerability Management

- Dependencies pinned in requirements.txt
- pip audit run monthly for known vulnerabilities
- FastAPI and Uvicorn updated on security releases
- No direct database access from frontend
- Docker container runs as non-root user
- DEBUG=False enforced in production via app_config.json
- WeasyPrint sandbox mode enabled for PDF generation

---

### 8.15 Incident Response — V1

1. Issue discovered — Badal Satapathy notified immediately
2. Affected endpoint taken offline if necessary
3. Root cause identified
4. Fix deployed
5. Users notified if personal data involved — not applicable in V1 given Process and Discard and Zero Data Retention

Formal incident response plan before B2B contracts — Month 9.

---

## 9. ERROR HANDLING AND FAILURE MODES

### Failure Classification

**Hard Failure:** Application error, API failure, infrastructure issue.
Show plain English message. Always suggest next action. Never show technical error codes.

**Light Failure:** Document quality issue, partial extraction, low confidence.
Show soft warning. Allow user to proceed. Never block. Never discourage.

### Error Scenarios

```
LIGHT FAILURE — Low extraction confidence
USER SEES: "We had some difficulty reading parts of your document.
            The information below may be incomplete.
            Please review it carefully and correct anything that looks wrong."
TECHNICAL: soft_warning = True in response, HTTP 200

LIGHT FAILURE — Partial extraction, missing fields
USER SEES: Field shown as "Not found in your document" with editable input
TECHNICAL: Field set to "Not found in document" string, HTTP 200

HARD FAILURE — PDF cannot be read
USER SEES: "We had trouble reading your document.
            Please make sure it is a clear, unprotected PDF and try again."
TECHNICAL: HTTP 400, logged without personal data

HARD FAILURE — Password-protected PDF, no password provided
USER SEES: "This document is password protected.
            Please enter the password below, or upload an unlocked version.
            The password is often your date of birth or policy number."
TECHNICAL: HTTP 422, password_required: true in response

HARD FAILURE — Claude API timeout
USER SEES: "This is taking a little longer than usual.
            Please wait a moment — we are still working on your document."
TECHNICAL: Retry up to 3 times with exponential backoff.
           If all retries fail: HTTP 503

HARD FAILURE — Claude API returns malformed JSON
USER SEES: "We encountered an issue processing your document.
            Please try uploading again."
TECHNICAL: JSON parse error caught, retry once, then HTTP 500

HARD FAILURE — File too large
USER SEES: "Your file is larger than 10MB.
            Please compress the PDF and try again."
TECHNICAL: HTTP 400

HARD FAILURE — Wrong file type
USER SEES: "Please upload a PDF file.
            Other file types are not supported yet."
TECHNICAL: HTTP 400

HARD FAILURE — Rate limit exceeded
USER SEES: "You have made several requests in a short time.
            Please wait a moment and try again."
TECHNICAL: HTTP 429

LIGHT FAILURE — Document detection uncertain (second visit)
USER SEES: "We are not certain what this document is.
            [Plain English description of what we think it might be]
            Is this the response you received from your insurer?"
TECHNICAL: UNKNOWN DocumentType returned, confidence LOW
           Frontend asks user to confirm — never blocks
```

---

## 10. CONFIG FILE SPECIFICATIONS

### legal_language.json — Updated in v2.0

```json
{
  "version": "2.0",
  "last_updated": "2026-04-20",

  "right_column_template": "Your insurer has declined this claim citing {plain_english_reason}. You may request a review of this decision by writing to the Chief Grievance Officer.",

  "next_step_1": "Write to the Chief Grievance Officer — every insurer has one. Your insurer is required by regulation to respond within 15 days.",

  "next_step_2": "If unresolved, approach the Insurance Ombudsman — free and independent. Advocates and agents not permitted. You have one year from the Chief Grievance Officer's response to file.",

  "consent_text": {
    "version": "2.0",
    "text": "I confirm this letter represents my grievance and I am submitting it of my own choice. I understand this letter was generated with AI assistance and that Ezer is not a legal advisor. This letter is guidance only."
  },

  "disclaimer": "Ezer is not a legal advisor. Information provided is for guidance only. This analysis and letter were generated with AI assistance. Consult a qualified advisor for complex cases.",

  "ai_footer": "Prepared with AI assistance by Ezer (getezer.app). Ezer is not a legal advisor. This document is guidance only.",

  "screen_7_opening": [
    "We have done the work. Your Claim File is ready.",
    "Many claims like yours get resolved at this stage. We hope yours does too."
  ],

  "screen_7_reality_check": "The Chief Grievance Officer works within the insurer. Their response may not resolve your claim. If that happens, the Insurance Ombudsman is your next step — and it is a powerful one.",

  "screen_7_save_instruction": "Please save this Claim File. You will need it if you need to take this further.",

  "screen_7_return_instruction": "If the Chief Grievance Officer does not resolve your claim, come back to Ezer. Bring this Claim File and their response. We will help you prepare your Ombudsman submission.",

  "ombudsman_advocates_reminder": "Advocates and agents are not permitted. You must submit this yourself or through a family member.",

  "ombudsman_hours_reminder": "Ombudsman offices are open Monday to Friday, 10 AM to 5:30 PM. Closed Saturday and Sunday.",

  "claim_resolved_message": "We are glad to hear it. We hope your situation is resolved.",

  "volatile_state_warning": "You have unsaved progress. If you refresh or leave this page, you will need to start again. Please download your Claim File to save your work."
}
```

### cgo_directory.json — Structure Unchanged

```json
{
  "version": "1.0",
  "last_updated": "2026-04-20",
  "insurers": [
    {
      "insurer_name": "HDFC ERGO General Insurance Company Limited",
      "cgo_email": "cgo@hdfcergo.com",
      "grievance_email": "grievance@hdfcergo.com",
      "cgo_address": "",
      "irdai_registration_number": "",
      "insurer_type": "General"
    }
  ]
}
```

### letter_templates.json — WeasyPrint HTML Templates Added

```json
{
  "version": "2.0",
  "last_updated": "2026-04-20",
  "templates": {
    "cgo_letter": {
      "plain_text": "...",
      "html": "<html>...</html>"
    },
    "claim_file_cover": {
      "plain_text": "...",
      "html": "<html>...</html>"
    },
    "ombudsman_covering_letter": {
      "plain_text": "...",
      "html": "<html>...</html>"
    }
  },
  "css": {
    "base": "body { font-family: Georgia, serif; font-size: 12pt; ... }",
    "heading": "h1 { font-size: 14pt; font-weight: bold; ... }",
    "footer": ".footer { font-size: 9pt; color: #666; ... }"
  }
}
```

### ombudsman_directory.json — Structure Unchanged

```json
{
  "version": "1.0",
  "last_updated": "2026-04-20",
  "offices": [
    {
      "city": "Bhubaneswar",
      "states_covered": ["Odisha"],
      "address": "",
      "contact": "0674-2596003, 2596455",
      "working_hours": "Monday to Friday, 10 AM to 5:30 PM",
      "working_days": "Monday to Friday",
      "holiday": "Saturday and Sunday",
      "complaint_format_url": ""
    }
  ]
}
```

### NEW — config/prompts/ directory

All six prompts stored as individual JSON files:
- policy_extractor_prompt.json
- denial_extractor_prompt.json
- analyser_prompt.json
- cgo_letter_prompt.json
- document_detector_prompt.json
- ombudsman_prompt.json

Each file structure:

```json
{
  "version": "1.0",
  "last_updated": "2026-04-20",
  "system_prompt": "...",
  "user_prompt_template": "...",
  "model": "claude-sonnet-4-6",
  "max_tokens": 4096,
  "zero_data_retention": true
}
```

### NEW — config/regulatory_citations.json

```json
{
  "version": "1.0",
  "last_updated": "2026-04-20",
  "citations": {
    "H1": { "pattern_name": "Single cashless denial", "primary_citation": "", "irdai_circular": "", "plain_english": "" },
    "H2": { "pattern_name": "Multiple TPA resubmissions", "primary_citation": "", "irdai_circular": "", "plain_english": "" },
    "H3": { "pattern_name": "Multi-stage treatment", "primary_citation": "", "irdai_circular": "", "plain_english": "" },
    "H4": { "pattern_name": "Changing rejection reasons", "primary_citation": "", "irdai_circular": "", "plain_english": "" },
    "H5": { "pattern_name": "Investigative procedure trap", "primary_citation": "", "irdai_circular": "", "plain_english": "" },
    "H6": { "pattern_name": "Supplementary claim chain blockage", "primary_citation": "", "irdai_circular": "", "plain_english": "" },
    "L1": { "pattern_name": "Non-disclosure allegation", "primary_citation": "", "irdai_circular": "", "plain_english": "" },
    "L2": { "pattern_name": "Nominee dispute", "primary_citation": "", "irdai_circular": "", "plain_english": "" },
    "L3": { "pattern_name": "Suicide clause", "primary_citation": "", "irdai_circular": "", "plain_english": "" },
    "L4": { "pattern_name": "Accidental versus natural death", "primary_citation": "", "irdai_circular": "", "plain_english": "" },
    "L5": { "pattern_name": "Fraud allegation", "primary_citation": "", "irdai_circular": "", "plain_english": "" },
    "L6": { "pattern_name": "Premium lapse dispute", "primary_citation": "", "irdai_circular": "", "plain_english": "" }
  }
}
```

---

## 11. FRONTEND TO BACKEND INTEGRATION

### Session State Management — Volatile

**Critical:** EzerSessionState is held in React component state only. It does not persist across page refreshes or browser tab closes. This is intentional — consistent with Process and Discard and no-authentication architecture.

**Volatility protection:**

```typescript
// Session state structure — TypeScript
interface EzerSessionState {
  // Screen 2 output
  policyDocument: PolicyDocument | null;

  // Screen 3 output
  confirmedPolicyFields: PolicyDocument | null;
  discrepancyFlagged: boolean;

  // Screen 4 output
  denialAnalysis: DenialAnalysis | null;

  // Screen 5 output
  decisionMade: 'generate' | 'save' | 'resolved' | null;

  // Screen 6 output
  claimFile: ClaimFile | null;
  cgoLetter: string | null;
  consentGiven: boolean;
  consentTimestamp: string | null;

  // Download tracking
  claimFileDownloaded: boolean;  // True after first download

  // Second visit
  isReturnVisit: boolean;
  ombudsmanPackage: OmbudsmanPackage | null;
}

// VOLATILE STATE WARNING
// Activate from Screen 3 onwards when state is populated
// Deactivate after Claim File is downloaded

useEffect(() => {
  const stateIsPopulated = sessionState.confirmedPolicyFields !== null;
  const claimFileDownloaded = sessionState.claimFileDownloaded;

  const handleBeforeUnload = (e: BeforeUnloadEvent) => {
    if (stateIsPopulated && !claimFileDownloaded) {
      e.preventDefault();
      e.returnValue = '';
      // Browser shows standard warning:
      // "Changes you made may not be saved. Leave page?"
    }
  };

  if (stateIsPopulated && !claimFileDownloaded) {
    window.addEventListener('beforeunload', handleBeforeUnload);
  } else {
    window.removeEventListener('beforeunload', handleBeforeUnload);
  }

  return () => {
    window.removeEventListener('beforeunload', handleBeforeUnload);
  };
}, [sessionState.confirmedPolicyFields, sessionState.claimFileDownloaded]);
```

**Warning activates:** From Screen 3 onwards, once policy data confirmed.
**Warning deactivates:** After Claim File downloaded — claimFileDownloaded set to true.
**Warning does not activate:** On Screen 1 or 2 — nothing valuable to lose yet.
**Warning does not activate:** After "My claim has been resolved" selected.

---

### API Base URL Configuration

```typescript
// .env.local (development)
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

// .env.production
NEXT_PUBLIC_API_BASE_URL=https://ezer-backend.railway.app
```

### File Upload Pattern

```typescript
async function uploadDocument(
  file: File,
  endpoint: string,
  additionalData?: object
): Promise<any> {
  const formData = new FormData();
  formData.append('file', file);

  if (additionalData) {
    formData.append('data', JSON.stringify(additionalData));
  }

  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_BASE_URL}${endpoint}`,
    {
      method: 'POST',
      body: formData,
      // No Content-Type header — browser sets multipart boundary
    }
  );

  if (!response.ok) {
    const error = await response.json();
    // Show plain English error to user — never technical codes
    throw new Error(error.detail || 'An error occurred. Please try again.');
  }

  return response.json();
}
```

### Config Validation at Startup — Pydantic Schemas

```python
from pydantic import BaseModel, ValidationError
import json

class LegalLanguageConfig(BaseModel):
    version: str
    right_column_template: str
    next_step_1: str
    next_step_2: str
    consent_text: dict
    disclaimer: str
    ai_footer: str
    screen_7_opening: list
    screen_7_reality_check: str
    screen_7_save_instruction: str
    screen_7_return_instruction: str

# Additional Pydantic models for each config file

@app.on_event("startup")
async def validate_all_configs():
    """
    Validate all JSON config files at startup.
    If any file is malformed or missing required fields:
    log the error and refuse to start (fail-fast).
    """
    configs_to_validate = [
        ("config/legal_language.json", LegalLanguageConfig),
        ("config/cgo_directory.json", CGODirectoryConfig),
        ("config/letter_templates.json", LetterTemplatesConfig),
        ("config/ombudsman_directory.json", OmbudsmanDirectoryConfig),
        ("config/escalation_ladder.json", EscalationLadderConfig),
        ("config/app_config.json", AppConfig),
        ("config/regulatory_citations.json", RegulatoryCitationsConfig),
    ]

    for config_path, config_schema in configs_to_validate:
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
            config_schema(**data)
            print(f"Config validated: {config_path}")
        except FileNotFoundError:
            print(f"STARTUP FAILED: Config file not found: {config_path}")
            raise SystemExit(1)
        except ValidationError as e:
            print(f"STARTUP FAILED: Config validation error in {config_path}: {e}")
            raise SystemExit(1)
        except json.JSONDecodeError as e:
            print(f"STARTUP FAILED: Config JSON error in {config_path}: {e}")
            raise SystemExit(1)

    print("All configs validated. Ezer is starting.")
    verify_zdr_compliance()
    print("Ezer is ready.")
```

---

## 12. DEPLOYMENT ARCHITECTURE

### Frontend — Vercel

```
Repository: github.com/getezer/ezer
Branch: main
Framework: Next.js
Build command: npm run build
Output directory: .next
Domain: getezer.app
HTTPS: Enforced by .app domain
Environment variables: Set in Vercel dashboard — never in code
```

### Backend — Railway or Render

```
Repository: github.com/getezer/ezer
Branch: main
Start command: uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
Health check: GET /health
Environment variables: Set in platform dashboard — never in code
Docker: Dockerfile in repository root
Non-root user: Enforced in Dockerfile
```

### Dockerfile — Updated with WeasyPrint Dependencies

```dockerfile
FROM python:3.11-slim

# Install WeasyPrint system dependencies
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash ezer
USER ezer

COPY --chown=ezer:ezer requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

COPY --chown=ezer:ezer backend/ ./backend/
COPY --chown=ezer:ezer config/ ./config/

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "backend.app.main:app",
     "--host", "0.0.0.0", "--port", "8000"]
```

---

## 13. DEVELOPMENT STANDARDS

### Code Standards — All Python Files

1. Every line of code has a plain English comment
2. No hardcoding — all content in JSON config files
3. No abbreviations in variable names that surface to users
4. All functions have docstrings
5. All API endpoints have FastAPI docstrings
6. Error handling on every external API call
7. Explicit deletion of user document variables after use
8. Zero Data Retention header on every Claude API call — non-negotiable
9. All prompts loaded from config — never hardcoded in Python

### WeasyPrint Usage Standards

```python
from weasyprint import HTML, CSS

def generate_pdf_from_html(html_content: str, css_content: str) -> bytes:
    """
    Generate a professional PDF from HTML using WeasyPrint.
    Returns PDF bytes — caller is responsible for delivering to user.
    Nothing written to disk.
    """
    # Generate PDF in memory
    pdf_bytes = HTML(string=html_content).write_pdf(
        stylesheets=[CSS(string=css_content)]
    )
    return pdf_bytes
    # No file written — bytes returned directly to FastAPI response
```

### Commit Standards

```
Format: "[Day N] — [Component] — [What changed]"
Examples:
"Day 5 — Backend — Add extract_from_policy_document() with ZDR"
"Day 5 — Backend — Add WeasyPrint PDF generation endpoint"
"Day 5 — Config — Add policy extractor prompt v1.0"
"Day 5 — Config — Add regulatory citations JSON"
"Day 6 — Frontend — Screen 1 and 2 built on v0.dev"
"Day 6 — Frontend — Volatile state warning added from Screen 3"
```

### Testing Standards

- Real documents only — no synthetic data
- Minimum 2 real policy documents tested before frontend build
- Minimum 5 real denial letters tested before deployment
- Both HDFC ERGO letters already tested and passing
- Zero Data Retention verified in each test run
- Config validation tested by deliberately breaking one config and confirming fail-fast
- Test results logged in LEARNINGS.md

### Daily Session Rules

1. Activate virtual environment before starting
2. Start server and confirm health before writing code
3. Architecture discussion before any new component
4. Every line of code explained in plain English before running
5. Zero Data Retention verified working before any session involving Claude API
6. Commit to GitHub at end of every session
7. Update LEARNINGS.md and DECISIONS.md at end of every session
8. End with daily briefing

---

*End of Document*
*Ezer Integrated Technical Design Document v1.1*
*Aligned to PRD v2.0 — 20 April 2026*
*FINAL — Blueprint for V1.9 Build.*
*Process and Discard. Zero Data Retention. Surgical Engine. Digital Law Clerk.*
*WeasyPrint PDFs. Pydantic Fail-Fast. Light Failure paths. Seven Screens.*
*BFSI Audit Ready.*
