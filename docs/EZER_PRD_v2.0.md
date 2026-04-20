    # EZER — PRODUCT REQUIREMENTS DOCUMENT

**Product Name:** Ezer
**Tagline:** Clarity for your next move.
**Version:** 2.0
**Date:** 20 April 2026
**Author:** Badal Satapathy
**Status:** FINAL PRE-BETA FREEZE — No further changes without founder approval.
**Classification:** Insurance Escalation Engine for Policyholders — Starting India. Global Vision.

---

## VERSION HISTORY

| Version | Changes |
|---|---|
| v0.1 | Initial draft (April 2026) |
| v1.0 | Complete PRD after BA review |
| v1.1 | External reviewer feedback — Document quality handling, Confidence indicator, Case type differentiation, AI fail-safe, Chief Grievance Officer directory disclaimer, Monetisation model revised, Phase 1 emergency disclaimer, Pre-build validation |
| v1.2 | Product Manager feedback — Jurisdictional logic fixed, Chief Grievance Officer and IRDAI emails user-editable, Document quality soft warning, IRDAI carbon copy added, Case Metadata JSON download, Business model paths documented, V2 Parking Lot added |
| v1.3 | Final editorial pass — Formatting standardised, Tone neutralised |
| v1.4 | Pre-Build Validation — Empathy layer, Plain language case type detection, Treatment status options, Multi-letter same-policy logic, Multi-stage treatment linking, Investigative procedure detection, Desk review language, Structural impact of denial, Case JSON as case thread |
| v1.5 | Strategic lifecycle update — Architecture principle, Scope expanded beyond health, Full product lifecycle, Milestone and timeline roadmap, Revenue targets, Internationalisation flag, Founder commercial intent |
| v1.6 | Life insurance added to V1 scope — Life denial patterns, Life-specific escalation language, Tech stack updated, LangChain, Vector DB, Docker added, GitHub and React confirmed |
| v1.7 | Identity and infrastructure confirmed — Product name finalised, Domains registered, GitHub live, All credentials documented, Project prompts added, Future versions and global vision added |
| v1.8 | Brand, UX, and product flow overhaul — New tagline, Primary user redefined, Brand voice locked, No abbreviations rule, No conflict language rule, Seven-screen flow, Know Your Policy screen added as mandatory Screen 3, Claim File replaces Case everywhere, Two letter generation moments defined, Ombudsman stage as print-ready submission package, Chief Grievance Officer response pattern documented, Language rules locked |
| v1.9 | FINAL FREEZE — Hybrid AI architecture adopted (Surgical Engine plus Digital Law Clerk), Password-protected PDF handling added, Document quality soft warning formalised, Confidence indicator rules locked, "Required by regulation" replaces "Must respond", "We have done the work" retained, Context-complete trust line added to Screen 3, Partial extraction path formalised with edit capability, Tech stack finalised, All reviewer amendments resolved |
| v2.0 | FINAL PRE-BETA FREEZE — Three targeted updates: (1) Anonymous observability metrics added to Data Privacy and Compliance section, (2) Consent text updated to include AI-assisted generation disclosure, (3) Anthropic Zero Data Retention added to Data Privacy and Compliance section. No structural changes. No screen changes. No flow changes. All other reviewer amendments handled in TDD v1.1. |

---

## 1. PRODUCT OVERVIEW

Ezer is an AI-powered web-based insurance escalation engine for policyholders globally. It reads policy documents and denial letters, explains both in plain English, and generates legally grounded escalation documents at each stage — from Chief Grievance Officer letter to Ombudsman submission package.

V1 launches with health and life insurance in India. The architecture is designed to expand across all insurance categories and geographies without rebuild.

Ezer's core value is not the AI. It is the structured escalation intelligence, legally grounded document generation, and timing and pressure orchestration that the AI enables.

**Strategic Positioning:** Ezer is the only tool globally built exclusively for the policyholder who just got denied. Not for insurers, brokers, or underwriters. Every funded InsurTech company builds for the insurer side. Ezer builds for the other side.

**Architecture Principle:** Ezer is category-agnostic at the core. Health insurance is the V1 implementation. Category-specific knowledge is modular. Adding a new category is configuration, not a rebuild.

**Job Readiness Principle:** Every technology choice serves dual purpose — build the best product AND build the most relevant portfolio for AI governance and systems roles in BFSI. The GitHub repository is a living portfolio that speaks louder than any certification.

**Founder Intent:** Noble purpose and commercial ambition pursued together without compromise. Help policyholders navigate denials. Build a scalable revenue-generating product. Both pursued without apology.

---

## 2. PRODUCT IDENTITY AND CREDENTIALS

**Product Name:** Ezer
**Meaning:** Hebrew — helper, one who helps. Persian via Azer — fire, light. The helper who lights the way.
**Tagline:** Clarity for your next move.
**Previous tagline retired:** "With you through denial." — replaced after brand voice session, Day 4.

**Primary Domain:** getezer.app — Registered April 2026. Renews April 2027 at Rs 2,616. Registrar: GoDaddy.
**India Backup:** getezer.in — Registered April 2026. Renews April 2027 at Rs 899. Auto-renewal: OFF.
**Renewal Reminder:** 1st March 2027 — Google Calendar set. GoDaddy login: badalsmailbox@gmail.com.

**GitHub:** github.com/getezer/ezer — Public. License: MIT. Created April 2026.
**Founder:** Badal Satapathy
**Founder Email:** badalsmailbox@gmail.com
**Founder Location:** Bhubaneswar. Open to relocate: Bengaluru or Mumbai.
**Company:** Ezer Technologies Private Limited (MCA registration pending)

---

## 3. BRAND VOICE AND LANGUAGE RULES

These rules are permanent and apply to every screen, every generated letter, every config file, and every user-facing piece of text in Ezer. No exceptions.

### Brand Voice
Calm. Capable. Warm. On your side.
Not aggressive. Not legal. Not activist. Not a charity. Not startup-flashy.
Like a knowledgeable friend who has been through this and knows the way out.

### What Ezer Is NOT
- Not a law firm or legal advisor
- Not an activist platform
- Not a claims settlement guarantee service
- Not a product that takes sides aggressively
- Not a product that promises outcomes

### The Airbnb Framing
Ezer's story is not "I went through pain so I built this." That is a sympathy play with a limited market.
Ezer's framing: "Insurers have a repeatable playbook for denying claims. Ezer has cracked the code."
The insight is systematic. The market is every policyholder in India — and eventually the world.

### STANDING LANGUAGE RULES — PERMANENT

**Rule 1 — No Abbreviations. Ever.**
Full form everywhere. Every time. No exceptions.
- NOT: CGO, IRDAI, TPA, CCN, Pre-Auth, PED
- YES: Chief Grievance Officer, Insurance Regulatory and Development Authority of India, Third Party Administrator, Claim Reference Number, Pre-Authorisation, Pre-Existing Disease
- If a term is too long for a line — rewrite the line. Never shorten the term.
- Applies to: all screens, all generated letters, all config files, all user-facing text

**Rule 2 — No Conflict Language.**
- NOT: fight back, battle, ammunition, arms, challenge aggressively, combat
- YES: review, address, process, submit, prepare, escalate formally, request a review

**Rule 3 — No Judgment Language.**
Ezer does not label denial patterns to the user. Ezer does not say "your insurer did something wrong." Ezer translates what happened and informs the user of their options. The user decides.

**Rule 4 — No Promises of Resolution.**
Ezer promises the best possible informed action. Never the outcome.
- NOT: "your claim will be settled" or "you will win this"
- YES: "Many claims like yours get resolved at this stage. We hope yours does too."

**Rule 5 — No Medical or Legal Terms Without Plain English Translation.**
Every technical term must be followed by or replaced with plain English.

**Rule 6 — User Autonomy at Every Step.**
Every screen must respect that the user decides. Ezer informs. Ezer never pressures.

**Rule 7 — Claim File Replaces Case Everywhere.**
- NOT: Case, Case File, Download Your Case File, case_json (user-facing)
- YES: Claim File, Your Claim File, Download Your Claim File
- Note: backend file case_json.py to be renamed carefully in a future session. Do not rename during active development.

**Rule 8 — Regulatory Obligations Use Precise Language.**
- NOT: "Must respond in 15 days" — implies certainty Ezer cannot guarantee
- NOT: "Are expected to respond in 15 days" — too weak, dilutes regulatory weight
- NOT: "Expected to respond within 15 days" — same problem as above — REJECTED
- YES: "Your insurer is required by regulation to respond within 15 days."
- Applies to: all screens, all generated letters, all user-facing text
- This rule is final and will not be revisited.

**Rule 9 — Ezer Never Discourages Escalation.**
No confidence rating, document quality warning, or analysis result should ever discourage the user from proceeding. Ezer always presents a path forward. Always.

**Rule 10 — AI Involvement Is Always Disclosed.**
Wherever Ezer generates content on behalf of the user — letters, analysis, summaries — the user must be informed that AI assistance was used. This disclosure appears in the consent gate and in the document footer. It is an ethical and regulatory requirement.

---

## 4. THE USER

### Primary User — V1
The exhausted, tensed person in a hospital corridor or at home after receiving a rejection or denial letter from their insurer.
- Limited time — possibly hours not days
- Limited cash — cashless denial may mean no financial buffer
- Needs calm guidance immediately
- Has never read their policy document in full — the complexity was deliberate
- Does not know the Chief Grievance Officer exists
- Does not know the Insurance Ombudsman exists
- May refer to denial as "rejected" or "denied" — both terms used interchangeably by insurers
- May have received the denial as an email, a portal download, or a physical letter

### Secondary User
The financially comfortable, time-rich, fighting-spirit user who wants to challenge the insurer on principle. Ezer serves them well. But all product decisions are made for the primary user first.

### Other Secondary Users
Hospital Third Party Administrator desk staff assisting policyholders. Family members acting as point of contact for the policyholder.

### Out of Scope — V1
Group and corporate insurance policyholders. Insurance agents acting independently. Legal professionals. Hindi-only users — V2.

---

## 5. THE PROBLEM

When an insurance claim is denied, the policyholder faces three simultaneous crises.

**Crisis 1 — Comprehension:** The denial letter is vague, jargon-heavy, and deliberately ambiguous. The user cannot decode what the rejection reason means or whether it is legally legitimate.

**Crisis 2 — Emotion:** Shock, panic, and anger. A family member needs treatment, a major financial loss must be absorbed, or a nominee is left without support. Clear thinking is impossible.

**Crisis 3 — Action:** No structured guidance exists on what to do first, who to contact, what rights apply, and what to say. Google returns scattered results. Customer care is unhelpful. Friends do not know.

**Result:** Most people either pay and give up — or escalate without structure, exhaust themselves, and lose.

**The Core Insight:** A denial letter is not a final decision. It is the opening move in a system designed to test whether the policyholder will push back. Most do not escalate. Insurers are aware of this. When a policyholder responds with a structured, legally grounded escalation — starting with a Chief Grievance Officer complaint and proceeding to the Insurance Ombudsman — the dynamics change completely.

**The Information Asymmetry:** The insurer has a playbook. Until Ezer, the policyholder did not. The user was not ignorant — the information was deliberately withheld. The policy language was deliberately complex. Ezer levels the playing field.

**The LinkedIn Problem:** Many policyholders pour their pain on LinkedIn to shame insurers into settling. This works occasionally for high-follower accounts. It is unpredictable, humiliating, not replicable, and not scalable. Ezer is what they should be using instead.

**Structural Impact of Initial Denial:** A cashless denial at the initial stage blocks the entire supplementary claim chain. For life insurance, denial leaves the nominee without financial support at the most vulnerable moment. Responding promptly protects rights across the entire treatment or claim episode.

---

## 6. AI ARCHITECTURE — HYBRID ENGINE

Ezer uses a two-brain hybrid architecture. Finalised in v1.9. Architecture principles unchanged in v2.0.

### Brain 1 — The Surgical Engine
Single-pass Claude API call with full context window (200,000 plus tokens).
Both the user's policy document and denial letter are passed together in one API call.
The AI reads the complete policy — every page, every clause, every exclusion — and the denial letter simultaneously.
After output is generated, all user data is discarded. Nothing stored. Process and Discard intact.
Anthropic Zero Data Retention configuration enforced on every API call — see Section 22.

### Brain 2 — The Digital Law Clerk
Vector database containing the Ezer Regulatory Knowledge Base.
Contents: Insurance Ombudsman Rules 2017, IRDAI Master Circulars, IRDAI guidelines and notifications, past Ombudsman awards and precedents, consumer court judgements relevant to insurance disputes.
V1 primary source: Hardcoded JSON regulatory lookup — fast, predictable, no latency.
V1 supplementary source: RAG pipeline queries knowledge base in parallel — better citations surfaced when available.
V2: RAG becomes primary as knowledge base scales.
No user data ever touches the vector database.

### Why This Architecture Wins
Privacy first. Regulatory depth. Surgical accuracy. Portfolio value.

---

## 7. REAL-WORLD CHIEF GRIEVANCE OFFICER PATTERN

Three real Chief Grievance Officer responses from HDFC ERGO reviewed and documented.

**Response 1 — Grievance Cell (July 22, 2025):** Copy paste rejection.
**Response 2 — Desk of Chief Grievance Officer (January 31, 2026):** Blame shift.
**Response 3 — Desk of Chief Grievance Officer (February 7, 2026):** Moving goalposts.

**Key Insight:** The Chief Grievance Officer is an employee of the insurer. Their role appears to be defending the denial with different reasons — not independently reviewing it. This is expected and must be communicated to users gently on Screen 7.

---

## 8. INSURANCE OMBUDSMAN — VERIFIED FACTS

All facts verified against IRDAI official documentation and Insurance Ombudsman Rules 2017. Nationally applicable.

- 17 Ombudsman offices: Ahmedabad, Bengaluru, Bhopal, Bhubaneswar, Chandigarh, Chennai, Delhi, Guwahati, Hyderabad, Jaipur, Kochi, Kolkata, Lucknow, Mumbai, Noida, Pune, Patna
- Advocates and agents on behalf of complainants are not permitted — national rule
- One year limitation period — from date of Chief Grievance Officer response, not original denial date
- Process is completely free — no charges to complainant
- Ombudsman award is binding on insurer — must comply within 30 days
- Award passed within 3 months of receiving all requirements
- Jurisdiction: complainant's residential address or insurer's branch address
- Physical submission is the ground reality — Ezer generates print-ready packages
- Claims up to Rs 50 lakhs handled

---

## 9. COMPLETE PRODUCT FLOW — V1

### First Visit — Seven Screens

Screen 1 — Landing Page. Screen 2 — Upload Policy Document. Screen 3 — Know Your Policy. Screen 4 — Upload Denial Letter. Screen 5 — Your Insurer's Decision and What It Means. Screen 6 — Chief Grievance Officer Letter. Screen 7 — Your Claim File.

### Second Visit — Ombudsman Stage

User returns with Claim File and Chief Grievance Officer rejection. UI asks user to identify documents first. AI detection as fallback for uncertain cases. Location captured. Ombudsman office identified. Print-ready submission package generated and downloaded.

---

## 10. SCREEN SPECIFICATIONS

### Screen 1 — Landing Page

**Headline:** "Clarity for your next move."
**Subheading:** "Upload your rejection letter. We decode it, identify your options, and show you exactly how to escalate — in minutes."
Clean, minimal, no images, no hospital photos, no distressed humans, no sermons. Mobile responsive. English only.

---

### Screen 2 — Upload Policy Document

**Instruction:** "Let us start with your policy document."
**Subtext:** "We will decode it in plain English before looking at your denial."
**Supporting line:** "PDF format only."
**Trust line:** "We read your entire policy — every page, every clause, every exclusion. Nothing is skimmed."

Password-protected PDF: Password field shown. Hint: "This is often your date of birth or policy number."
Document quality soft warning if extraction confidence is low. Never a hard block.
Upload is mandatory. No skip option.
Upload itself is implicit consent.

---

### Screen 3 — Know Your Policy

**Opening line:** "Here is what your policy actually covers — in plain English."
**Trust line:** "We have read your entire policy document — every page, every clause, every exclusion. Nothing has been skimmed."

Table displays: Policyholder name, Policy number, Coverage period, Sum insured, Waiting period, Pre-Existing Disease clause, Room rent limit, Key exclusions, Policy address.

Partial extraction: "Not found in your document" shown with editable field. Never blank. Never error. Five minimum fields required to proceed.

Confirmation gate: "Does this match what you understood about your policy?"
Option A: "Yes — show me why my claim was denied"
Option B: "This does not look right — I need help understanding my policy"

Option B flags discrepancy — factored into Chief Grievance Officer letter.

**Volatile state warning:** From Screen 3 onwards, if the user attempts to refresh or leave the browser, a standard browser warning fires: "Changes you made may not be saved." Warning deactivates after Claim File is downloaded.

---

### Screen 4 — Upload Denial Letter

**Instruction:** "Upload what your insurer sent you."
**Subtext:** "PDF format only."
Same password and quality handling as Screen 2. Nothing else on this screen.

---

### Screen 5 — Your Insurer's Decision and What It Means

Two column layout:

| Your insurer's decision | What this means for you |
|---|---|
| Exact words from the document | Plain English translation plus neutral statement of options |

Right column formula — universal and locked:
"Your insurer has declined this claim citing [plain English reason]. You may request a review of this decision by writing to the Chief Grievance Officer."

Confidence indicator — contextual statement, never a label:
- High: "Based on the documents you have provided, your next steps are clear."
- Medium: "We have completed your analysis. Some details were unclear — please review carefully before proceeding."
- Low: "We could only read part of your document. Your analysis may be incomplete. Please review carefully. You can still proceed — your options remain open."

Confidence automatically downgraded if extraction completeness is below threshold — see TDD v1.1 Section 4.

Next steps:
1. Write to the Chief Grievance Officer — every insurer has one. Your insurer is required by regulation to respond within 15 days.
2. If unresolved, approach the Insurance Ombudsman — free and independent. Advocates and agents not permitted. You have one year from the Chief Grievance Officer's response to file.

Decision gate:
- "Generate my grievance letter"
- "Save this — I will decide later"
- "My claim has been resolved"

---

### Screen 6 — Chief Grievance Officer Letter

Generated letter displayed in full. Chief Grievance Officer email pre-filled and user-editable. Carbon copy to complaints@irdai.gov.in pre-filled and user-editable.

**Consent gate — single checkbox — updated in v2.0:**
"I confirm this letter represents my grievance and I am submitting it of my own choice. I understand this letter was generated with AI assistance and that Ezer is not a legal advisor. This letter is guidance only."

Download button greyed out until checkbox is checked. Consent record in Claim File only. Nothing on server.

**Download button:** "Download Your Claim File"

---

### Screen 7 — Your Claim File

**Opening lines:**
"We have done the work. Your Claim File is ready."
"Many claims like yours get resolved at this stage. We hope yours does too."

Human readable card showing: policy summary, insurer's decision, Chief Grievance Officer letter, escalation options, all dates.

**Download button:** "Download Your Claim File"

Save instruction: "Please save this Claim File. You will need it if you need to take this further."

Return instruction: "If the Chief Grievance Officer does not resolve your claim, come back to Ezer. Bring this Claim File and their response. We will help you prepare your Ombudsman submission."

Gentle reality check: "The Chief Grievance Officer works within the insurer. Their response may not resolve your claim. If that happens, the Insurance Ombudsman is your next step — and it is a powerful one."

---

### Second Visit — Ombudsman Submission Package

**Document identification — UI first, AI fallback:**
"What are you uploading today?"
- "My Ezer Claim File" — radio button
- "The response I received from my insurer" — radio button
- "I am not sure" — triggers AI document detection as fallback

Location capture: "Which city or state are you based in?" — dropdown, 17 options.

Ombudsman Submission Package: Filled complaint form, covering letter, chronology of events, document checklist, Ombudsman office details.

**Download button:** "Download Your Submission Package"

Instructions: Print, sign, visit or courier. Monday to Friday, 10 AM to 5:30 PM. Advocates and agents not permitted.

---

## 11. ESCALATION LADDER

**Step 1 — Chief Grievance Officer Letter (Day 0 to 1)**
Mandatory first step. Response window: 15 days as required by regulation. Email pre-filled and user-editable. Carbon copy to complaints@irdai.gov.in.

**Step 2 — IRDAI Bima Bharosa (Day 1 to 15)**
File if Chief Grievance Officer silent after 15 days, or in parallel as pressure. Ezer guides to platform. Does not file on behalf of user.

**Step 3 — Insurance Ombudsman**
Quasi-judicial. Free. Binding. One year from Chief Grievance Officer response date. Print-ready submission package generated by Ezer.

---

## 12. THREE PHASES EZER GUIDES

**Phase 1 — Survive (0 to 2 hours):** Prioritise treatment or understand immediate financial impact.
**Phase 2 — Document (Same day):** Policy decoded, denial decoded, Chief Grievance Officer letter generated.
**Phase 3 — Challenge (Post immediate emergency):** Within 1 month recommended. Maximum 1 year from Chief Grievance Officer response.

Ezer does not replace medical, legal, or financial decision-making. Ezer provides guidance only.

---

## 13. INSURANCE CATEGORY SCOPE

**V1 — Health Insurance:** Investigative procedure trap, Multi-stage treatment linking, Changing denial reasons, Supplementary claim chain blockage, Desk review versus treating doctor argument.

**V1 — Life Insurance:** Non-disclosure allegation, Nominee disputes, Suicide clause invocation, Accidental versus natural death dispute, Fraud allegation without evidence, Premium lapse dispute.

**V2 — Motor Insurance (Month 7)**
**V3 — Crop, Agriculture, Travel Insurance (Year 2)**

---

## 14. HEALTH INSURANCE DENIAL PATTERNS

H1 — Single cashless denial. H2 — Multiple Third Party Administrator resubmissions. H3 — Multi-stage treatment episode. H4 — Changing rejection reasons. H5 — Investigative procedure trap. H6 — Supplementary claim chain blockage.

---

## 15. LIFE INSURANCE DENIAL PATTERNS

L1 — Non-disclosure: Burden of proof on insurer.
L2 — Nominee dispute: Documentation and succession law.
L3 — Suicide clause: Evidence required, ambiguity resolved in nominee's favour.
L4 — Accidental versus natural death: Medical and forensic records required.
L5 — Fraud allegation: Specific documented evidence required — blanket allegation invalid.
L6 — Premium lapse: Payment proof and reconciliation request.

---

## 16. KNOW YOUR POLICY — TECHNICAL REQUIREMENTS

Extractor: `extract_from_policy_document()` — pending build.
Fields: Policyholder name, Policy number, Insurer name, Start and end dates, Sum insured, Waiting periods, Pre-Existing Disease clause, Room rent limit, Key exclusions, Policy address, Branch details.
Approach: Single-pass Claude API call with full policy in context.
Missing fields: "Not found in your document" with editable input — never blank, never error.

---

## 17. CLAIM FILE SPECIFICATION

Reference format: EZR-YYYYMMDD-XXXX
Contains: Policy summary, denial extraction, denial analysis, confidence statement, Chief Grievance Officer letter, escalation ladder, consent record, all dates, phase completed, disclaimer.
Display: Human readable card — user never sees raw JSON.
Download: Single PDF via WeasyPrint — professional typography.
Ownership: "Your Claim File lives with you. Not with us."

**Consent record fields — DPDP compliant:**
consent_given, consent_timestamp, consent_text_version, consent_text_shown (full text including AI disclosure), case_reference, policy_number.

---

## 18. DOCUMENT HANDLING RULES

PDF only — V1. Image support deferred to V1.1.
Password-protected PDFs: Handled in UI with hint text.
Document quality: Soft warning only — Light Failure path — never hard block.
Multiple letters same policy: All addressed together — multiple rejections noted.
Wrong document type: Soft warning — user can confirm and proceed.

---

## 19. WHAT EZER DOES NOT DO IN V1

Provide legal advice. Guarantee claim approval. Contact insurers on behalf of users. File on IRDAI or Ombudsman platforms. Handle motor insurance. Handle group or corporate insurance. Store uploaded documents. Support Hindi or regional languages. Provide chat or human support. Provide case tracking dashboard.

---

## 20. MONETISATION MODEL

**Free Tier:** Policy decode, Know Your Policy, Denial analysis, Plain English explanation, Confidence indicator, Chief Grievance Officer letter, Claim File download.

**Paid Tier (Month 6 — October 2026):** Ombudsman submission package, Advanced escalation, Priority processing. Target: Rs 5,000 to 10,000 monthly recurring revenue.

**B2B (Month 9 — January 2027):** Corporate HR white-label, Hospital Third Party Administrator integration. Target: Rs 25,000 to 50,000 first contract.

**Year 2:** Legal lead marketplace (opt-in only), Success fee model (1 to 2 percent), Fintech integration.

---

## 21. DATA GOVERNANCE AND COMPLIANCE — UPDATED IN V2.0

### Process and Discard
Documents processed in memory only. Nothing stored after output generated. User owns Claim File via download. Trust differentiator and B2B selling point. Never compromise this architecture.

### Data Collected
Policyholder name. Claimant name if different. City or state for Ombudsman mapping. Email — optional, reminders only. No document storage. No Aadhaar or sensitive ID storage.

### Consent
Upload is implicit consent given clearly stated purpose. Explicit checkbox consent before Chief Grievance Officer letter download. Consent text includes AI-assisted generation disclosure — Rule 10. Consent record in Claim File only — nothing on server.

### Anonymous Observability Metrics — NEW IN V2.0
Ezer collects anonymous, non-personal metrics for product quality improvement.

**What is collected:**
- Timestamp
- Insurance category (General, Life, Health) — not insurer name in V1
- Denial pattern code (H1 through H6, L1 through L6) — internal codes only
- Confidence level (High, Medium, Low)
- Extraction completeness score (0.0 to 1.0)
- Processing duration in milliseconds
- Phase completed (Phase 1, Phase 2, Phase 3)
- Second visit flag (true or false)

**What is never collected:**
- Policyholder name
- Policy number
- Claim reference number
- Document content of any kind
- IP address
- Device identifier
- Any personal data whatsoever

**Storage:** Supabase — already in tech stack. Anonymous metrics table only.
**Purpose:** Product quality improvement. Identifying extraction failures. Understanding denial pattern distribution.
**Disclosed in privacy policy:** Yes — before beta launch.
**Never shared externally:** Never sold, never shared, never used for advertising.
**Insurer name:** Not stored in V1 — stored as category only to avoid legal sensitivity. Revisit in V2 after legal review.

### Anthropic Zero Data Retention — NEW IN V2.0
Ezer enforces Anthropic's Zero Data Retention configuration on every Claude API call.

**What this means:** Anthropic does not retain any data from Ezer's API calls. User documents are not stored by Anthropic after processing. This is in addition to Ezer's own Process and Discard architecture — creating a double layer of data protection.

**Implementation:** Zero Data Retention header applied to every single Claude API call in the codebase. Verified before deployment. See TDD v1.1 Section 8 for technical implementation.

**Disclosed to users:** Privacy policy states: "We use Anthropic's Zero Data Retention configuration. Your documents are not retained by Anthropic after analysis."

**Marketing asset:** Very few products using the Claude API implement Zero Data Retention. Ezer does. This is a significant trust differentiator for both consumer and B2B users.

### DPDP Act 2023 Compliance

| Requirement | Ezer Implementation | Status |
|---|---|---|
| Consent before processing | Upload is implicit consent — purpose clearly stated | V1 compliant |
| Explicit consent for sensitive operations | Checkbox with AI disclosure before letter generation | V1 compliant — updated v2.0 |
| Data minimisation | Only fields necessary for escalation extracted | V1 compliant |
| Purpose limitation | Data used only for generating escalation documents | V1 compliant |
| Storage limitation | Process and Discard plus Zero Data Retention | V1 compliant |
| Right to erasure | Not applicable — nothing stored on server | V1 compliant |
| Privacy notice | Plain English privacy policy on website | Before beta |
| Cross-border transfer | Claude API (Anthropic USA) — disclosed in privacy policy | Before beta |
| AI involvement disclosure | Rule 10 — in consent gate and document footer | V1 compliant — added v2.0 |

Full DPDP compliance deadline: May 2027.

### Third Party Data Sharing

| Third Party | Data Shared | Purpose | User Informed |
|---|---|---|---|
| Anthropic Claude API | Document text during processing only — Zero Data Retention enforced | AI analysis | Yes — privacy policy |
| Pinecone | No user data — regulatory documents only | Knowledge base | Not applicable |
| Vercel | No personal data | Frontend hosting | Not applicable |
| Railway or Render | No personal data | Backend hosting | Not applicable |
| Supabase | Anonymous metrics only — no personal data | Product analytics | Yes — privacy policy |

No user data is sold, shared for advertising, or transferred to any party not listed above.

### Disclaimer
"Ezer is not a legal advisor. Information provided is for guidance only. This analysis and letter were generated with AI assistance. Consult a qualified advisor for complex cases."

---

## 22. TECHNICAL STACK — FINALISED

| Layer | Technology | Notes | Hiring Risk |
|---|---|---|---|
| Backend language | Python | Free | Low |
| Backend framework | FastAPI | Free | Low |
| AI engine — Surgical | Anthropic Claude API (claude-sonnet-4-6) | Single-pass, full context, Zero Data Retention enforced | Not applicable |
| AI engine — Law Clerk | Anthropic Claude API (claude-sonnet-4-6) | Queries regulatory knowledge base, Zero Data Retention enforced | Not applicable |
| Orchestration | LangChain | Coordinates both AI engines | Low |
| RAG engine | LangChain RAG | Regulatory knowledge base — supplementary in V1, primary in V2 | Low |
| Vector database — dev | Chroma | Regulatory knowledge base | Low |
| Vector database — prod | Pinecone | Regulatory knowledge base | Low |
| Document parsing | PyMuPDF + pdfplumber | PDF text extraction | Not applicable |
| PDF generation | WeasyPrint | Professional HTML to PDF for Claim File and letters | Not applicable |
| OCR | Claude Vision API | V1.1 — deferred | Not applicable |
| Database | Supabase | Anonymous metrics only — free tier | Low |
| Payments | Razorpay | Month 6 — commission only | Not applicable |
| Frontend framework | Next.js | v0.dev generates Next.js natively | Low |
| Vibe coding tool | v0.dev | Frontend build | Not applicable |
| Hosting frontend | Vercel | Native Next.js host | Not applicable |
| Hosting backend | Railway or Render | Free tier | Not applicable |
| Container | Docker | Non-root user in production | Low |
| Version control | GitHub | Public portfolio | Not applicable |
| IDE | Visual Studio Code | Free | Not applicable |

**Architecture note:** RAG and Vector DB used exclusively for Regulatory Knowledge Base. User documents never stored in vector database. Process and Discard fully intact.

**Portfolio value:** Claude API, LangChain, Hybrid RAG architecture, Vector DB, Python FastAPI, Next.js, Docker, GitHub public, DPDP design, Zero Data Retention implementation, Insurance AI.

---

## 23. PRODUCT LIFECYCLE AND MILESTONES

**Runway:** 12 months from May 2026. Decision Point: April 2027.

**Milestone 1 — Build (Month 1 to 2: May to June 2026)**
All backend complete including `extract_from_policy_document()`. Regulatory Knowledge Base seeded. WeasyPrint PDF generation live. Next.js frontend live locally. 5 real denial letters and policy documents processed end to end.

**Milestone 2 — Private Beta (Month 3: July 2026)**
getezer.app live. 10 beta users from personal network. Privacy policy live with AI disclosure and Zero Data Retention statement. Anonymous metrics active. Peer reviewer engaged.

**Milestone 3 — Public Launch (Month 4: August 2026)**
LinkedIn posts published. GitHub public with strong README. 50 letters processed. Health and life both live.

**Milestone 4 — Paid Tier (Month 6: October 2026)**
Ombudsman submission package live. Razorpay integrated. First paying user. Target: Rs 5,000 to 10,000 monthly recurring revenue.

**Milestone 5 — Motor Insurance (Month 7: November 2026)**

**Milestone 6 — First B2B (Month 9: January 2027)**
Target: Rs 25,000 to 50,000.

**Milestone 7 — Decision Point (Month 12: April 2027)**
Scenario A — Founder path. Scenario B — Employment path (Digit, Acko, Innovaccer, Fractal, EXL). Scenario C — Partnership path.

---

## 24. PENDING DEVELOPMENT TASKS — IN ORDER

1. Policy document extractor — `extract_from_policy_document()` — backend — **highest priority**
2. WeasyPrint PDF generation — `/generate-pdf` endpoint — backend
3. Anonymous metrics table — Supabase — backend
4. Pydantic config validation at startup — backend
5. Zero Data Retention header — all Claude API calls — backend
6. Seed Regulatory Knowledge Base — IRDAI circulars and Ombudsman Rules 2017 — backend
7. Add Ombudsman complaint format to ombudsman_directory.json config
8. Add Ombudsman contact numbers to ombudsman_directory.json config
9. Next.js frontend — all seven screens — v0.dev — **next major frontend task**
10. Volatile state warning — browser beforeunload event — frontend
11. Deployment to getezer.app — Prompt 7
12. Real letter and policy testing with 5 sets — Prompt 8
13. README.md — Prompt 9
14. LinkedIn launch post — Prompt 10
15. Rename case_json.py carefully — do not rename during active development

---

## 25. CONFIG FILES — CURRENT STATUS

| File | Contents | Status |
|---|---|---|
| legal_language.json | Legal language including updated consent text with AI disclosure | Updated — consent text v2.0 |
| cgo_directory.json | Chief Grievance Officer contacts by insurer | Complete |
| letter_templates.json | Letter templates — HTML versions for WeasyPrint to be added | Needs WeasyPrint HTML templates |
| ombudsman_directory.json | 17 office addresses and jurisdictions | Complete — contact numbers and complaint format to be added |
| escalation_ladder.json | Escalation steps and timing | Complete |
| app_config.json | Application configuration | Complete |

---

## 26. INTERNATIONALISATION

V1: English, India. V2: Hindi, India. V3: Regional Indian languages. V4: International English.
Target markets: Bangladesh, Nigeria, Kenya, Indonesia, Egypt.
All text in separate language files. Date and currency formats localised. Regulatory modules per country.

---

## 27. SUCCESS METRICS

**V1 Primary:** Policy documents and denial letters uploaded and processed. Each upload equals one person helped in crisis.

**V1 Secondary:** Chief Grievance Officer letters downloaded. Claim Files downloaded. Ombudsman packages generated. Second visit return rate. Confidence level distribution from anonymous metrics. User-reported outcomes — voluntary.

**Business (Month 6 onwards):** Monthly Recurring Revenue. Paying users. B2B pipeline value. Cost per acquisition.

---

## 28. FUTURE VERSIONS AND GLOBAL VISION

**Ezer V1 (2026):** Health and life. India. English. Seven screens. Hybrid AI. Zero Data Retention. WeasyPrint PDFs. getezer.app live.

**Ezer V2 (2027):** Motor. Hindi. Paid Ombudsman tier. B2B white-label. Dashboard. RAG primary. 50,000 letters milestone.

**Ezer V3 (2027 to 2028):** Regional languages. Crop and travel. Legal lead marketplace. Success fee. Outcome prediction.

**Ezer V4 (2028 to 2029):** International. Southeast Asia, Africa, Middle East. Local regulatory modules.

**Ezer V5 (2029+):** Global policyholder rights platform. Every policyholder. Every denial. Every country.

**The Long Vision:** Insurance exists to protect people. When it fails to do so, people need Ezer. Until every insurer honours every valid claim without a fight, Ezer has work to do.

---

## 29. PRE-BUILD VALIDATION LOG

Scenarios tested: 2 of 5. Real letters used: 2 (HDFC ERGO health). Real Chief Grievance Officer responses reviewed: 3 (HDFC ERGO). Findings logged: 17 plus. PRD versions: 20. Core domain validation complete. Remaining scenarios tested during development.

---

## 30. V2 PARKING LOT

Case tracking dashboard, Ayushman card eligibility check, Hindi and regional language support, Partial denial handling, Automated IRDAI Bima Bharosa filing, Pre-Existing Disease module, Room rent capping module, Non-medical exclusion module, Minor nominee guardianship module, Policy assignment and loan module, Policy health check, Plain English policy summary at renewal, Annual renewal reminder email, Tagline A/B testing, B2B corporate HR white-label, Legal lead marketplace, Success fee escrow model, Bridge lending fintech integration, Embedded insurance platform partnerships, Motor garage network integration, Life insurance nominee support services, Motor insurance module, Crop and agriculture insurance, Travel insurance, Insurer behaviour data layer, Outcome prediction engine, Global regulatory knowledge base expansion, International regulatory modules, Dynamic UI differentiation for Cashless versus Reimbursement denial flows, RAG as primary citation source, Insurer name in anonymous metrics (after legal review).

---

*End of Document*
*Ezer PRD v2.0 — 20 April 2026*
*FINAL PRE-BETA FREEZE — No further changes without founder approval.*
*Hybrid AI. Zero Data Retention. WeasyPrint. Seven Screens. Anonymous Metrics. AI Disclosure.*
*12 Month Runway. Decision Point April 2027.*
*The monk with a Ferrari is building.*
