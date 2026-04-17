# Ezer - Architecture Decision Log
## Badal Satapathy | Started April 2026

This file documents every significant technical and product decision
made while building Ezer, and the reasoning behind each one.

Standard practice in professional engineering teams.
Visible on GitHub as evidence of structured thinking.

---

## Decision 1 - Combined /analyse endpoint
**Date:** April 16, 2026
**Decision:** Built one /analyse endpoint that runs both extraction
and analysis, returning a single combined response.

**Alternatives considered:**
- Separate /extract and /analyse endpoints requiring two calls
- Streaming response delivering results progressively

**Why we chose this:**
PRD principle: Zero friction. A policyholder in distress wants
one answer, not two separate calls to manage. The two API calls
to Claude happen invisibly behind the scenes.

---

## Decision 2 - Temporary files for PDF processing
**Date:** April 16, 2026
**Decision:** Use Python's tempfile module to create temporary
files that are automatically deleted after processing.

**Why we chose this:**
Directly implements Ezer's "Process and Discard" privacy principle
from PRD Section 14. Nothing is stored on our server after
the response is sent. User owns their data via JSON download.
This is both DPDP Act 2023 compliance and a trust differentiator
for future B2B clients.

---

## Decision 3 - Claude Sonnet for both extraction and analysis
**Date:** April 16, 2026
**Decision:** Use claude-sonnet-4-6 for both the extraction
and analysis API calls.

**Why we chose this:**
Fast, accurate, and cost effective for our development volume.
Opus would give marginally better analysis but at 5x the cost.
For V1 with low volume, Sonnet is the right balance.
Revisit at scale.

---

## Decision 4 - Python virtual environment named venv
**Date:** April 15, 2026
**Decision:** Named the virtual environment folder "venv"
following universal Python convention.

**Why we chose this:**
Every professional Python developer recognises venv instantly.
Alternative names like ezer-env would work but look non-standard.
Ezer's GitHub is a portfolio. Standard naming signals
professional practice.

---

## Decision 5 - FastAPI over Flask or Django
**Date:** April 15, 2026
**Decision:** Use FastAPI as the Python backend framework.

**Why we chose this:**
FastAPI appears in almost every AI engineering job description.
It automatically generates API documentation at /docs.
It handles async operations natively - important for AI calls.
It is the standard for AI backends in 2026.
Flask is older and less suited for AI workloads.
Django is too heavy for what Ezer needs.

---

## Decision 6 - Commented code as standard
**Date:** April 16, 2026
**Decision:** Every file, every function, every non-obvious line
gets a plain English comment explaining what it does and why.

**Why we chose this:**
Founder's professional standard from TCS code review experience.
Code you can explain is code you own.
Recruiters reading the GitHub will see professional discipline.
Future contributors will understand the codebase without asking.
Ezer is a portfolio as much as it is a product.

---