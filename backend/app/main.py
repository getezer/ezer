# Ezer Backend - main.py

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import tempfile

from backend.app.extractor import process_denial_letter
from backend.app.letter_generator import generate_cgo_letter
from backend.app.case_json import generate_case_json
from backend.app.analyser import analyse_rejection
from backend.app.settlement_extractor import extract_settlement_document
from backend.app.policy_extractor import extract_policy_document

load_dotenv("backend/.env")

app = FastAPI(
    title="Ezer API",
    description="AI-powered insurance escalation engine for policyholders. With you through denial.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------
# ENDPOINT 1: Root
# -------------------------------------------------------

@app.get("/")
def read_root():
    return {
        "product": "Ezer",
        "tagline": "With you through denial.",
        "status": "alive",
        "version": "1.0.0"
    }


# -------------------------------------------------------
# ENDPOINT 2: Health Check
# -------------------------------------------------------

@app.get("/health")
def health_check():
    return {"status": "healthy"}


# -------------------------------------------------------
# ENDPOINT 3: Extract Denial Letter (PDF upload)
# -------------------------------------------------------

@app.post("/extract")
async def extract_denial_letter(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted. Please upload a PDF denial letter."
        )

    contents = await file.read()

    with tempfile.NamedTemporaryFile(delete=True, suffix='.pdf') as tmp_file:
        tmp_file.write(contents)
        tmp_file.flush()

        try:
            result = process_denial_letter(tmp_file.name)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Extraction failed: {str(e)}"
            )

    return {
        "success": True,
        "filename": file.filename,
        "extracted_fields": result
    }


# -------------------------------------------------------
# ENDPOINT 4: Analyse Denial Letter (JSON input)
# Frontend sends extracted_fields as JSON
# -------------------------------------------------------

class AnalyseRequest(BaseModel):
    extracted_fields: dict


@app.post("/analyse")
async def analyse_denial_letter(request: AnalyseRequest):
    try:
        analysis = analyse_rejection(request.extracted_fields)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

    return {
        "success": True,
        "analysis": analysis
    }


# -------------------------------------------------------
# ENDPOINT 5: Generate CGO Letter
# -------------------------------------------------------

class CGOLetterRequest(BaseModel):
    extracted_fields: dict
    analysis: dict
    policyholder_name: str
    policy_address: str
    consent: bool
    consent_timestamp: str
    amount_disputed: str = "0"


@app.post("/generate-cgo")
async def generate_cgo_letter_endpoint(request: CGOLetterRequest):
    if not request.consent:
        raise HTTPException(
            status_code=400,
            detail="Consent required before generating letter."
        )

    try:
        result = generate_cgo_letter(
            extracted_fields=request.extracted_fields,
            analysis=request.analysis,
            policyholder_name=request.policyholder_name,
            policy_address=request.policy_address,
            consent=request.consent,
            consent_timestamp=request.consent_timestamp,
            amount_disputed=request.amount_disputed
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Letter generation failed: {str(e)}"
        )

    return {
        "success": True,
        "letter": result
    }


# -------------------------------------------------------
# ENDPOINT 6: Generate Case JSON
# -------------------------------------------------------

class CaseJSONRequest(BaseModel):
    policyholder_name: str
    policy_address: str
    phase_completed: str = "CGO_LETTER_GENERATED"
    extracted_fields: dict
    analysis: dict
    letter_result: dict


@app.post("/case-json")
async def generate_case_json_endpoint(request: CaseJSONRequest):
    try:
        case_data = generate_case_json(
            extracted_fields=request.extracted_fields,
            analysis=request.analysis,
            letter_result=request.letter_result,
            policyholder_name=request.policyholder_name,
            policy_address=request.policy_address,
            phase_completed=request.phase_completed
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Case JSON generation failed: {str(e)}"
        )

    return {
        "success": True,
        "file_label": "Your Ezer Case File",
        "download_button_label": "Download Your Case File",
        "case_data": case_data,
        "return_visit_instruction": "Save this file. If you return to Ezer to continue your case, upload this file when prompted.",
        "next_step": case_data.get("escalation", {}).get("next_step", {})
    }


# -------------------------------------------------------
# ENDPOINT 7: Extract Policy Document
# -------------------------------------------------------

@app.post("/extract-policy")
async def extract_policy_endpoint(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted. Please upload a PDF policy document."
        )

    contents = await file.read()

    with tempfile.NamedTemporaryFile(delete=True, suffix='.pdf') as tmp_file:
        tmp_file.write(contents)
        tmp_file.flush()

        try:
            result = extract_policy_document(tmp_file.name)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Policy extraction failed: {str(e)}"
            )

    return {
        "success": True,
        "filename": file.filename,
        "policy_data": result
    }


# -------------------------------------------------------
# ENDPOINT 8: Extract Settlement Letter
# -------------------------------------------------------

@app.post("/extract-settlement")
async def extract_settlement_endpoint(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted. Please upload a PDF settlement letter."
        )

    contents = await file.read()

    with tempfile.NamedTemporaryFile(delete=True, suffix='.pdf') as tmp_file:
        tmp_file.write(contents)
        tmp_file.flush()

        try:
            result = extract_settlement_document(tmp_file.name)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Settlement extraction failed: {str(e)}"
            )

    return {
        "success": True,
        "filename": file.filename,
        "settlement_data": result
    }
