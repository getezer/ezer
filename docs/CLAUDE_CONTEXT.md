# CLAUDE CONTEXT - EZER BUILD PROJECT
# Read this fully before responding to anything.
# Updated after each session.
# Last updated: April 17, 2026 - End of Day 3

---

## WHO I AM

Badal Satapathy. Founder of Ezer.
Based in Bhubaneswar, India.
23 years in IT delivery, operations, program management.
Non-developer founder using AI-assisted coding.
Age 47. 12 month runway from May 2026.
Open to relocate: Bengaluru or Mumbai.

How to work with me:
- Treat me as a non-technical co-founder
- Explain every command before I run it
- Explain what each piece of code does
- Never assume I know something
- Always tell me where to save each file
- Remind me to commit to GitHub regularly
- Architecture discussion before any new component
- Push back if I go off track from the PRD
- End each day with a structured briefing
- Every line of code must have plain English comments

---

## WHAT EZER IS

AI-powered insurance escalation engine for policyholders.
Starting India. Health and life insurance V1.
Global vision.

Product name: Ezer (Hebrew: helper)
Tagline: With you through denial.
Domain: getezer.app (primary)
Backup: getezer.in
GitHub: github.com/getezer/ezer
Company: Ezer Technologies Private Limited (MCA pending)

---

## WHY EZER EXISTS - THE FOUNDER STORY

My father needed urological surgery in 2025.
Two stage procedure. Cystoscopy then Urolift.

July 17 2025: Cashless claim for cystoscopy rejected.
Reason: "Patient admitted primarily for investigation
and evaluation of the ailment only."
This was pattern H5 - Investigative Procedure Trap.
The cystoscopy was a mandatory prerequisite for Urolift.

July 21 2025: Cashless claim for Urolift rejected.
Reason: "Indication for hospitalisation cannot be established."
This was pattern H4 - changed rejection reason.
Bill exceeded Rs 5 lakhs. Paid from credit card.

Both letters from HDFC ERGO. Patient: Gupta Prasad Satapathy.
Hospital: Care Hospitals, Bhubaneswar.
Policy: ER2434224975-01F.
CCNs: RC-HS25-15028403 and RC-HS25-15034871.

Used AI to decode letters and draft structured escalation.
Discovered Insurance Ombudsman exists.
Claim settled in two days before case formally registered.
Insurer settled because a well-armed claimant is expensive.

Two active Ombudsman cases still pending April 2026:
1. HDFC ERGO - Unlimited Restore Benefit removed after
   written quotation and premium payment. Promissory estoppel.
2. ICICI Lombard - Coverage gap in Activate Booster policy.

---

## REAL DENIAL LETTERS AVAILABLE

Both HDFC ERGO letters are in:
backend/tests/sample_letters/

Letter 1: PreAuthDenialLe_RC-HS25-15028403_202_20250717164350184.pdf
Date: July 17 2025
Pattern: INVESTIGATIVE_PROCEDURE
Rejection: "Patient admitted primarily for investigation
and evaluation of the ailment only."

Letter 2: PreAuthDenialLe_RC-HS25-15034871_202_20250721154551508.pdf
Date: July 21 2025
Pattern: MEDICAL_NECESSITY
Rejection: "Indication for hospitalisation cannot be established."

Both tested successfully. Both return HIGH contestability.
Both generate legally grounded CGO letters.

---

## TECH STACK

Frontend: React (built with vibe coding - v0.dev or Bolt.new)
Backend: Python with FastAPI
AI Layer: Claude API (Anthropic) - claude-sonnet-4-6
Orchestration: LangChain (to be integrated)
RAG: LlamaIndex or LangChain RAG (to be integrated)
Vector DB: Chroma (dev) - Pinecone (prod)
Document: PyMuPDF + pdfplumber
OCR: Claude Vision API (V1.1 - deferred)
Database: Supabase (free tier)
Payments: Razorpay (Month 6)
Hosting: Vercel (frontend) Railway or Render (backend)
Container: Docker (basic)
Version: GitHub - github.com/getezer/ezer

---

## CURRENT BUILD STATUS - END OF DAY 3

All five backend prompts complete.

DONE:
- Development environment fully configured
- FastAPI backend running on port 8000
- PDF extraction engine - extractor.py
- Rejection analysis engine - analyser.py
- CGO letter generator - letter_generator.py
- Case Metadata JSON - case_json.py
- Six API endpoints live and tested
- Six config files - all content separated from code
- Both HDFC ERGO letters tested successfully
- LEARNINGS.md and DECISIONS.md created and updated
- SSH connection to GitHub working
- All code on github.com/getezer/ezer

PENDING:
- requirements.txt - first task tomorrow
- Policy document extractor - extract_from_policy_document()
- React frontend - Prompt 6 - using vibe coding
- Deployment to getezer.app - Prompt 7
- Real letter testing with 5 letters - Prompt 8
- README.md - Prompt 9
- LinkedIn launch post - Prompt 10

---

## PROJECT FOLDER STRUCTURE

ezer/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          - all six endpoints
│   │   ├── extractor.py     - PDF extraction engine
│   │   ├── analyser.py      - rejection analysis engine
│   │   ├── letter_generator.py - CGO letter generator
│   │   └── case_json.py     - case metadata JSON
│   ├── config/
│   │   ├── legal_language.json
│   │   ├── cgo_directory.json
│   │   ├── letter_templates.json
│   │   ├── ombudsman_directory.json
│   │   ├── escalation_ladder.json
│   │   └── app_config.json
│   ├── tests/
│   │   └── sample_letters/  - real HDFC ERGO letters
│   └── .env                 - API key (never on GitHub)
├── frontend/                - React app (Prompt 6)
├── docs/
│   ├── LEARNINGS.md
│   ├── DECISIONS.md
│   └── CLAUDE_CONTEXT.md   - this file
├── .gitignore
├── README.md
└── requirements.txt         - to be created tomorrow

---

## SIX API ENDPOINTS

GET  /              - Ezer is alive check
GET  /health        - Health check for deployment
POST /extract       - Extract fields from denial letter PDF
POST /analyse       - Extract and analyse denial letter PDF
POST /generate-cgo  - Generate CGO complaint letter
POST /case-json     - Generate Case Metadata JSON

---

## KEY ARCHITECTURAL DECISIONS

1. Architecture discussion before every new component
2. Proper comments on all code - every line
3. Config files for all non-developer content
4. No hardcoding anywhere in Python files
5. Consent gate mandatory before CGO generation
6. Consent record in user-owned Case JSON only
7. Process and Discard - nothing stored on server
8. PDF only for V1 - images in V1.1
9. No hard blocks on missing fields
10. Five mandatory fields minimum
11. Two document extractors needed
12. Vibe coding for frontend
13. Case file shown as human readable card
14. Download button says "Download Your Case File"
15. .env file written via Python only - never echo

---

## STANDING RULES FOR EVERY SESSION

1. Start by activating venv:
   cd ~/Developer/ezer
   source venv/bin/activate

2. Start server:
   uvicorn backend.app.main:app --reload

3. Write .env via Python only:
   python3.11 -c "open('backend/.env', 'w').write('ANTHROPIC_API_KEY=YOUR-KEY')"

4. Kill server if needed:
   pkill -f uvicorn

5. Commit regularly:
   git add .
   git commit -m "description"
   git push origin main

6. End every session with:
   - Daily briefing
   - Update LEARNINGS.md
   - Update DECISIONS.md
   - Commit everything

---

## MILESTONE TARGET

30 days to working beta at getezer.app
Start: May 2026
Beta: July 2026
Public launch: August 2026
Paid tier: October 2026

Decision point: April 2027
Either Ezer earns money or job search activates.
Both outcomes planned for. No panic.

---

## RUNWAY AND JOB READINESS

12 months from May 2026.
Start job applications in parallel from Month 3
when beta is live and GitHub shows real product.
Target roles: AI Governance Lead, Responsible AI Advisor,
AI Risk Manager in Insurance or FinTech.
Target companies: Digit, Acko, Innovaccer, Fractal, EXL.
Ezer GitHub is the portfolio. Every commit counts.

---

## PEER REVIEWER

Action pending on founder.
Identify reviewer with legal or insurance domain knowledge.
Target: Before July 2026 beta launch.
Even one review session before beta is valuable.

---