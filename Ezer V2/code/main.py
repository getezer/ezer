# -----------------------------------------
# IMPORTS
# -----------------------------------------

from fastapi import FastAPI, UploadFile, File

from services.pdf_reader import extract_text_with_pages
from services.policy_extractor import extract_policy_data
from services.explainer import explain_policy
from services.proof import build_proof


app = FastAPI()


@app.get("/")
def home():
    return {"message": "Ezer backend is running"}


# -----------------------------------------
# NEXT STEPS
# -----------------------------------------

def build_next_steps(summary):

    if not isinstance(summary, dict):
        return ["Review your policy document carefully."]

    risks = summary.get("key_risks") or []
    text = " ".join([str(r) for r in risks]).lower()

    steps = []

    if "pre-existing" in text:
        steps.append(
            "Check the total waiting period for pre-existing diseases (not just remaining)."
        )

    if "treatment" in text:
        steps.append(
            "Check waiting periods for specific treatments like cataract or surgeries."
        )

    if not steps:
        steps.append("Review your policy document for coverage details.")

    return steps


# -----------------------------------------
# COVERAGE STATUS (SAFE)
# -----------------------------------------

def build_coverage_status(summary):

    if not isinstance(summary, dict):
        return {
            "status": "UNKNOWN",
            "confidence": "LOW",
            "note": "Unable to determine coverage clearly."
        }

    risks = summary.get("key_risks", [])
    text = " ".join(risks).lower()

    if "wait" in text or "not be covered" in text:
        return {
            "status": "PARTIAL",
            "confidence": "MEDIUM",
            "note": "Some conditions may not be covered yet due to waiting periods."
        }

    return {
        "status": "LIKELY_COVERED",
        "confidence": "LOW",
        "note": "Coverage depends on the specific condition."
    }


# -----------------------------------------
# COVERAGE BREAKDOWN (FIXED)
# -----------------------------------------

def build_coverage_breakdown(summary):

    if not isinstance(summary, dict):
        return {}

    risks = summary.get("key_risks", [])
    text = " ".join(risks).lower()

    breakdown = {
        "pre_existing_conditions": "UNKNOWN",
        "new_illnesses": "LIKELY_COVERED",
        "accidents": "LIKELY_COVERED"
    }

    if "pre-existing" in text:
        breakdown["pre_existing_conditions"] = "NOT_COVERED_YET"

    return breakdown


# -----------------------------------------
# API
# -----------------------------------------

@app.post("/upload-policy")
async def upload_policy(file: UploadFile = File(...)):

    try:
        pages = extract_text_with_pages(file.file) or []
        data = extract_policy_data(pages) or {}

        if not isinstance(data, dict):
            data = {}

        summary = explain_policy(data) or {}
        proof = build_proof(data) or {}

        next_steps = build_next_steps(summary)
        coverage_status = build_coverage_status(summary)
        coverage_breakdown = build_coverage_breakdown(summary)

        return {
            "summary": summary,
            "proof": proof,
            "next_steps": next_steps,
            "coverage_status": coverage_status,
            "coverage_breakdown": coverage_breakdown
        }

    except Exception as e:
        return {"error": str(e)}