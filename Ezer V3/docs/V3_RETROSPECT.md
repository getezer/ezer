# Ezer V3 — Retrospective

## What Failed in V2
- LLM extraction hallucinated values not present in policy documents
- Flat schema could not represent conditional policy language
- Table structure in schedules was lost during extraction
- Waiting period blocks became unstructured text — unusable for logic
- Probabilistic output is incompatible with insurance domain requirements
- Attempt to build claim navigation before policy understanding was solid

## What Worked in V3
- Curated JSON library produces deterministic, zero-hallucination insights
- Separation of product rules (Tier 1) from user data (Tier 2) scales cleanly
- Real family policies (4 users, 2 products) validated engine against actual schedules
- Action outputs (draft letters) close the gap between insight and user action
- Classification layer (type + priority) enables structured, scannable output
- Summary block + grouped sections make output decision-oriented, not just informational
- Schedule integrity detection surfaced a live underwriting error (Basanti phantom block)
- PED quality flagging surfaced a live vagueness risk (Gupta Prasad cardiac PED)

## Key Design Decisions
- Human curation over LLM extraction — reliability non-negotiable in insurance
- One product library shared across all users of that product
- Confidence provenance tag on every insight (🟢 Verified / 🟡 Extracted / 🔴 Experimental)
- Problem → WARNING, Solution → ACTION — never mixed
- Priority based on risk impact, not actionability
- No frontend, no database, no API until engine was stable
- Policy is treated as an evolving system, not a static document (foundation for V3.1)

## Current State
- Engine stable and producing correct insights across 4 real users
- 2 product libraries curated (Optima Secure, Optima Restore)
- Classification, grouping, and Next Best Action working correctly
- Draft letters generated deterministically from JSON flags
- Ready for: FastAPI endpoint, single-policy mode, Tier 1 library expansion

## Known Limitations
- Next Best Action for WARNING insights is descriptive, not imperative — `suggested_action` field planned
- Curation velocity is the primary bottleneck for scaling Tier 1 coverage
- Tier 4 fallback (LLM extraction for unknown policies) not yet built

---
*Last updated: 2026-04-29*
