# CLAUDE.md — Ezer Backend Context
# Read this first at the start of every session.
# Last updated: Day 7 frontend session.

---

## What Ezer Does

Ezer is an AI-powered insurance claim support engine for Indian policyholders.
It reads insurance documents and helps users understand their policy, understand
a denial or settlement, and prepare formal letters to the insurer's Chief
Grievance Officer (CGO) or the Insurance Ombudsman.

Tagline: "Clarity for your next move."
Brand voice: Calm. Capable. Warm. On your side.
Primary user: Exhausted person in a hospital corridor. Limited time. Limited cash.

---

## Product Stage

V1 — Internal only. Not public.
Stack: Python 3.11, FastAPI, Anthropic Claude API (claude-sonnet-4-6), pdfplumber, PyMuPDF
Deployment: Vercel (frontend), Railway (backend)
Repo: github.com/getezer/ezer

---

## Two User Journeys

### Journey 1 — First visit (denial letter received)
Screen 1: Landing
Screen 2: Upload policy
Screen 3: Loading — reading policy
Screen 4: Know your policy (4 swipe cards)
Screen 5: Upload denial letter
Screen 5B: Loading — reading denial letter
Screen 6: What your insurer decided
Screen 7: How this works
Consent: Bottom sheet slides up on Screen 7
Screen 8: Your CGO draft — ready to review and download
Screen 9: You are all set

### Journey 2 — Return visit (insurer has responded to CGO letter)
Screen J2-1: Welcome back — two path cards
Screen J2-2: Upload insurer response (primary) + optional denial letter + optional policy
Screen J2-3: Loading — reading documents
Screen J2-4: How your insurer responded
Screen J2-5: What you can do next (DYNAMIC — driven by scenario)
Screen J2-6: Consent — bottom sheet
Screen J2-7: Your summary (agreement breakdown + key issues)
Screen J2-8: Your Ombudsman draft — ready to review and download
Screen J2-9: You are all set (checklist, not timeline — Ezer cannot track status)

---

## Backend File Structure

```
backend/
  app/
    main.py               — FastAPI app, all 8 endpoints
    schemas.py            — All data structures (Pydantic models)
    extractor.py          — Reads denial letter PDF, extracts fields via Claude
    policy_extractor.py   — Reads policy PDF, extracts all policy fields via Claude
    settlement_extractor.py — Reads settlement letter PDF, extracts financials
    analyser.py           — Analyses denial pattern, determines contestability
    letter_generator.py   — Generates CGO letter via Claude
    case_json.py          — Packages everything into portable case JSON
  config/
    legal_language.json   — Legal paragraphs by denial pattern
    cgo_directory.json    — CGO email addresses for all major insurers
    letter_templates.json — Letter structure and boilerplate
    ombudsman_directory.json — Ombudsman office details by state
    escalation_ladder.json — Phase descriptions and next steps
    app_config.json       — Version, disclaimer, labels
```

---

## Current Endpoints (8 total)

| Endpoint | Method | What it does |
|---|---|---|
| / | GET | Root — confirms server is alive |
| /health | GET | Health check for Railway |
| /extract | POST | Reads denial letter PDF, returns extracted fields |
| /analyse | POST | Takes extracted fields, returns legal analysis |
| /generate-cgo | POST | Takes fields + analysis, generates CGO letter |
| /case-json | POST | Packages everything into case JSON |
| /extract-policy | POST | Reads policy PDF, returns all policy fields |
| /extract-settlement | POST | Reads settlement letter PDF, returns financials |

---

## Key Data Structures (schemas.py)

### PolicyDocument
Full policy data including: policyholder, policy number, insurer, dates,
sum insured, room rent limit, waiting periods, riders, pre-existing conditions,
exclusions, address, CGO email, confidence level.

### SettlementExtraction
Settlement data including: claim reference, patient, hospital, ailment,
financials (claimed, deducted, settled), line items, without_prejudice flag,
MOU clause flag, Protector Rider balance, consumables breakdown, confidence level.

### DocumentType (enum)
ORIGINAL_DENIAL, CGO_REJECTION, EZER_CLAIM_FILE, SETTLEMENT_ADVICE,
POLICY_DOCUMENT, UNKNOWN

---

## Key Design Decisions Already Made

1. Nothing is stored. Process and discard. Temp files deleted immediately.
2. Consent is mandatory before CGO letter generation. Consent record lives in user-owned JSON.
3. CGO letter is a procedural step. Ombudsman is where resolution happens.
4. Confidence levels are internal — LOW/MEDIUM/HIGH never shown to user.
5. "Start with what you have" — never block the user. Even one document produces output.
6. Adaptive output — language adjusts based on documents available.
7. Ezer NEVER says a claim is invalid. NEVER discourages escalation.
8. Use MAY not WILL when assessing outcomes.
9. Ombudsman jurisdiction determined by policy address, not current location.
10. Zero Data Retention headers on all Claude API calls.

---

## BACKEND GAP ANALYSIS
## What needs to be built for both journeys

---

### GAP 1 — Document classifier (NEW — needed for Journey 2)

**What it does:**
When user uploads documents in Journey 2, the backend needs to identify
what type each document is before processing.

**Why needed:**
Journey 2 accepts up to 3 documents — CGO response (primary), original
denial letter (optional), policy (optional). Each needs different processing.
The existing DocumentType enum in schemas.py already has the right values.

**What to build:**
New function in extractor.py or a new file document_classifier.py:

```python
def classify_document(pdf_text: str) -> DocumentType:
    # Sends text to Claude, returns DocumentType enum value
    # ORIGINAL_DENIAL, CGO_REJECTION, POLICY_DOCUMENT, SETTLEMENT_ADVICE
```

**Where it sits:** Called before any extraction in Journey 2.

---

### GAP 2 — CGO response extractor (NEW — needed for Journey 2)

**What it does:**
Reads the insurer's response to the CGO letter and extracts:
- What they agreed to
- What they did not agree to
- Key reasons given
- Whether the response is final or provisional
- Whether they paid anything

**Why needed:**
Current extractor.py is built for original denial letters only.
CGO responses have a different structure — they reference the complaint,
give a formal decision, and may include partial settlement.

**What to build:**
New function in extractor.py or new file cgo_response_extractor.py:

```python
def extract_cgo_response(pdf_text: str, denial_fields: dict = None, policy_data: dict = None) -> dict:
    # Returns:
    # agreed_items: list
    # rejected_items: list
    # key_reasons: list
    # response_type: FINAL | PROVISIONAL | PARTIAL_SETTLEMENT
    # confidence: HIGH | MEDIUM | LOW (based on docs available)
    # confidence_statement: str (shown to user if limited docs)
```

**Adaptive logic:**
- CGO response only → limited analysis, generic guidance, lower confidence
- CGO response + denial letter → better context, pattern comparison
- CGO response + denial + policy → full intelligence, clause validation

---

### GAP 3 — Scenario detector (NEW — needed for Journey 2 Screen J2-5)

**What it does:**
After reading the CGO response, determines which scenario applies
and returns the appropriate next steps for the frontend to display.

**Why needed:**
Screen J2-5 "What you can do next" must be dynamic.
Static options are wrong — a full rejection needs different guidance
than a partial acceptance or a request for more documents.

**What to build:**
New function in analyser.py:

```python
def detect_cgo_scenario(cgo_response_fields: dict) -> dict:
    # Returns:
    # scenario: FULL_REJECTION | PARTIAL_ACCEPTANCE | REQUEST_FOR_DOCS | ACCEPTED_WRONG_AMOUNT
    # recommended_actions: list of dicts with title and description
    # primary_recommendation: str
    # ombudsman_ready: bool
```

**Scenario definitions:**
- FULL_REJECTION → insurer rejected everything → recommend Ombudsman
- PARTIAL_ACCEPTANCE → some accepted, some rejected → share more docs or Ombudsman for rejected parts
- REQUEST_FOR_DOCS → insurer wants more information → guide user on what to submit
- ACCEPTED_WRONG_AMOUNT → agreed but underpaid → Ombudsman for the difference

---

### GAP 4 — Ombudsman letter generator (NEW — needed for Journey 2 Screen J2-8)

**What it does:**
Generates the formal submission letter to the Insurance Ombudsman.
Different from the CGO letter in format, addressee, and legal language.

**Why needed:**
Current generate-cgo endpoint and letter_generator.py only generate CGO letters.
Ombudsman submissions have a different structure:
- Addressed to the Insurance Ombudsman office (jurisdiction-based)
- Must include proof that CGO process was exhausted
- References the CGO response as exhibit
- Different legal language — appeals to IRDAI Ombudsman Rules 2017

**What to build:**
New function in letter_generator.py:

```python
def generate_ombudsman_letter(
    cgo_response_fields: dict,
    denial_fields: dict = None,
    policy_data: dict = None,
    policyholder_name: str,
    policy_address: str,
    scenario: str,
    consent: bool,
    consent_timestamp: str
) -> dict:
    # Returns same structure as generate_cgo_letter
    # but with Ombudsman-specific content
```

**New endpoint needed in main.py:**

```python
@app.post("/generate-ombudsman")
async def generate_ombudsman_endpoint(request: OmbudsmanLetterRequest):
    # Similar to /generate-cgo but calls generate_ombudsman_letter
```

**New config files needed:**
- ombudsman_legal_language.json — legal paragraphs specific to Ombudsman submissions
- ombudsman_templates.json — letter structure for Ombudsman format

---

### GAP 5 — New endpoint for Journey 2 full flow (NEW)

**What it does:**
A single endpoint that accepts all Journey 2 documents and returns
the full analysis — scenario, summary, and Ombudsman draft.

**Why needed:**
Journey 2 has up to 3 documents and multiple processing steps.
A single orchestrating endpoint is cleaner than the frontend
calling 4 separate endpoints in sequence.

**What to build:**

```python
@app.post("/analyse-cgo-response")
async def analyse_cgo_response(
    cgo_response: UploadFile = File(...),
    denial_letter: UploadFile = File(None),  # optional
    policy: UploadFile = File(None)           # optional
):
    # Step 1: Classify and extract all uploaded documents
    # Step 2: Detect scenario
    # Step 3: Return analysis + scenario + confidence statement
```

---

### GAP 6 — Confidence-aware output (EXTENSION to existing files)

**What it does:**
Adjusts the language of analysis and letter generation based on
which documents are available.

**Why needed:**
"Start with what you have" is Ezer's core differentiator.
The backend must handle graceful degradation cleanly.

**What to extend:**
In analyser.py and letter_generator.py, add a confidence_context parameter:

```python
def build_confidence_context(docs_available: dict) -> dict:
    # docs_available = {response: True, denial: False, policy: True}
    # Returns:
    # level: HIGH | MEDIUM | LOW
    # preamble: str (shown at top of analysis — e.g. "Based on the response you uploaded...")
    # letter_tone: STRONG | MODERATE | CAUTIOUS
```

**What user sees (never LOW/MEDIUM/HIGH directly):**
- Full docs: "Based on your policy, your denial letter, and the insurer's response..."
- Response + denial: "Based on the documents you shared..."
- Response only: "Based on the response you uploaded. Adding earlier documents can strengthen this."

---

### GAP 7 — File type validation update (EXTENSION to main.py)

**What it does:**
Journey 2 Screen J2-2 accepts PDF, JPG, and PNG.
Current validation in main.py only accepts PDF.

**What to extend:**
In main.py, update all upload endpoints to accept:

```python
ALLOWED_TYPES = ['.pdf', '.jpg', '.jpeg', '.png']

def validate_file_type(filename: str):
    if not any(filename.lower().endswith(t) for t in ALLOWED_TYPES):
        raise HTTPException(status_code=400, detail="Please upload a PDF, JPG, or PNG file.")
```

**Also needed:**
Image-to-text extraction for JPG and PNG uploads.
PyMuPDF handles this — fitz can open images too.
Or use Claude's vision capability directly for images.

---

### GAP 8 — Policy data integration into denial analysis (EXTENSION)

**What it does:**
When a policy is uploaded in Journey 1, the policy data should
inform the denial analysis — not just sit separately.

**Why needed:**
Currently extractor.py extracts denial fields and policy_extractor.py
extracts policy fields but analyser.py only receives denial fields.
The real power is cross-referencing — "your policy covers this, but
the insurer denied it for this reason."

**What to extend:**
Update analyse_rejection in analyser.py:

```python
def analyse_rejection(extracted_fields: dict, policy_data: dict = None) -> dict:
    # If policy_data present, include policy context in prompt
    # Cross-reference waiting periods, exclusions, sum insured
    # Flag if denial reason conflicts with policy terms
```

---

## Summary — What to Build

| Item | Type | Priority | Journey |
|---|---|---|---|
| Document classifier | NEW file | High | J2 |
| CGO response extractor | NEW function | High | J2 |
| Scenario detector | NEW function | High | J2 Screen J2-5 |
| Ombudsman letter generator | NEW function | High | J2 Screen J2-8 |
| /generate-ombudsman endpoint | NEW endpoint | High | J2 |
| /analyse-cgo-response endpoint | NEW endpoint | High | J2 |
| Confidence-aware output | EXTENSION | High | J2 |
| File type validation (JPG/PNG) | EXTENSION | Medium | J2 |
| Policy data in denial analysis | EXTENSION | Medium | J1 + J2 |

---

## How to Start Each Session

Paste this in your first message:
"Read this first: [paste raw GitHub URL of this CLAUDE.md file]
Today we are working on: [what you want to build]"

If working on a specific file, also paste that file's contents.
