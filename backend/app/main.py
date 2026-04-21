# Ezer Backend - main.py
# -------------------------------------------------------
# PURPOSE: This is the entry point of the entire Ezer backend.
# Think of this file as the front door of the Ezer kitchen.
# Every request from the user comes through here first.
# This file defines all the "endpoints" - the doors that
# accept different types of requests from the frontend.
# -------------------------------------------------------


# IMPORT STATEMENTS
# Bringing in all the tools we need before we start cooking.

from fastapi import FastAPI, File, UploadFile, HTTPException
# FastAPI - the main framework that runs our backend server
# File - tells FastAPI to expect a file in the request
# UploadFile - the specific type for uploaded files like PDFs
# HTTPException - used to send error messages back to the user

from dotenv import load_dotenv
# load_dotenv reads your .env file and loads the API key
# into memory so the rest of the code can access it

import os
# os is Python's built-in tool for interacting with your
# operating system - we use it to read environment variables
# and to handle file paths

import tempfile
# tempfile creates temporary files that are automatically
# deleted when we are done with them.
# This is how Ezer stays true to its "Process and Discard"
# privacy principle from the PRD - we never store uploads.

from backend.app.extractor import process_denial_letter
# Import PDF extraction function from extractor.py
# Reads denial letter PDF and pulls out key fields

from backend.app.letter_generator import generate_cgo_letter
# Import CGO letter generator from letter_generator.py
# Reads legal language from config files - no hardcoding

from backend.app.case_json import generate_case_json
# Import case JSON generator from case_json.py
# Creates the portable case record the user downloads

from backend.app.analyser import analyse_rejection
# This imports our analyse_rejection function from analyser.py
# It takes the extracted fields and returns legal analysis
# This connects our two core engines together

from backend.app.settlement_extractor import extract_settlement_document
# Import settlement letter extractor from settlement_extractor.py
# Reads settlement PDFs and pulls out financials, deductions, and flags

# -------------------------------------------------------
# ENVIRONMENT SETUP
# -------------------------------------------------------

load_dotenv("backend/.env")
# This reads your .env file and loads ANTHROPIC_API_KEY
# into memory. Must be called before anything tries to
# use the API key, so we do it right at the top.


# -------------------------------------------------------
# APPLICATION SETUP
# -------------------------------------------------------

app = FastAPI(
    title="Ezer API",
    # The name of our API - shows up in documentation

    description="AI-powered insurance escalation engine for policyholders. With you through denial.",
    # A description of what Ezer does

    version="1.0.0"
    # The version number of our API
)
# app is our FastAPI application object.
# Every endpoint we create is attached to this app.
# When uvicorn runs, it runs this app.


# -------------------------------------------------------
# ENDPOINT 1: Root
# The home page of the Ezer API
# -------------------------------------------------------

@app.get("/")
# @app.get("/") means: when someone visits the root URL
# (http://127.0.0.1:8000/) using a GET request, run this function.
# GET means "I want to read something" - no data being sent.

def read_root():
    # This function runs when someone visits the root URL.
    # It returns a simple message confirming Ezer is alive.
    
    return {
        "product": "Ezer",
        "tagline": "With you through denial.",
        "status": "alive",
        "version": "1.0.0"
    }
    # We return a dictionary which FastAPI automatically
    # converts to JSON format - the language of the web.


# -------------------------------------------------------
# ENDPOINT 2: Health Check
# Used to confirm the server is running correctly
# -------------------------------------------------------

@app.get("/health")
# When someone visits /health, run this function.
# This is a standard practice in all production systems.
# Deployment platforms like Railway ping this to check
# if the server is healthy.

def health_check():
    # Simply confirms the server is running.
    return {"status": "healthy"}


# -------------------------------------------------------
# ENDPOINT 3: Extract Denial Letter
# This is the core of Ezer's backend.
# It accepts a PDF upload and returns extracted fields.
# -------------------------------------------------------

@app.post("/extract")
# @app.post means this endpoint accepts POST requests.
# POST means "I am sending you something" - in this case a PDF file.
# The URL will be http://127.0.0.1:8000/extract

async def extract_denial_letter(file: UploadFile = File(...)):
    # async means this function can handle multiple requests
    # at the same time without blocking - important for a web app.
    
    # file: UploadFile = File(...) means:
    # We expect a file to be uploaded with this request.
    # The ... means this field is mandatory - cannot be empty.
    
    # -------------------------------------------------------
    # STEP 1: Validate the uploaded file
    # Make sure the user actually uploaded a PDF
    # -------------------------------------------------------
    
    if not file.filename.endswith('.pdf'):
        # .endswith('.pdf') checks if the filename ends with .pdf
        # If someone uploads a .jpg or .docx we reject it here.
        
        raise HTTPException(
            status_code=400,
            # 400 means "Bad Request" - the user sent something wrong
            
            detail="Only PDF files are accepted. Please upload a PDF denial letter."
            # This message is sent back to the user explaining the problem.
        )
    
    # -------------------------------------------------------
    # STEP 2: Read the uploaded file into memory
    # -------------------------------------------------------
    
    contents = await file.read()
    # await means "wait for this to complete before moving on"
    # file.read() reads the entire PDF file into memory as bytes.
    # bytes are the raw binary data that makes up any file.
    
    # -------------------------------------------------------
    # STEP 3: Save to a temporary file
    # This is Ezer's "Process and Discard" privacy principle.
    # We create a temporary file, process it, then it is
    # automatically deleted. Nothing is stored permanently.
    # -------------------------------------------------------
    
    with tempfile.NamedTemporaryFile(delete=True, suffix='.pdf') as tmp_file:
        # tempfile.NamedTemporaryFile creates a temporary file
        # delete=True means it is automatically deleted when we are done
        # suffix='.pdf' makes sure the temp file has a .pdf extension
        # 'with' means: use this file within this block, then close it
        
        tmp_file.write(contents)
        # Write the uploaded PDF bytes into the temporary file
        
        tmp_file.flush()
        # flush() forces Python to write everything to disk immediately
        # Without this, the file might not be fully written when we read it
        
        # -------------------------------------------------------
        # STEP 4: Run the extraction
        # Send the temporary file to our extractor
        # -------------------------------------------------------
        
        try:
            # try means: attempt the following, catch any errors
            
            result = process_denial_letter(tmp_file.name)
            # tmp_file.name is the path to our temporary file
            # process_denial_letter is our function from extractor.py
            # result will be a dictionary with all extracted fields
            
        except Exception as e:
            # If anything goes wrong during extraction, we catch it here
            # and return a clean error message instead of crashing
            
            raise HTTPException(
                status_code=500,
                # 500 means "Internal Server Error" - something went wrong on our end
                
                detail=f"Extraction failed: {str(e)}"
                # We include the actual error message to help with debugging
            )
    
    # -------------------------------------------------------
    # STEP 5: Return the extracted fields to the user
    # -------------------------------------------------------
    
    return {
        "success": True,
        # Confirms the extraction worked
        
        "filename": file.filename,
        # Echo back the original filename so user knows which file was processed
        
        "extracted_fields": result
        # The dictionary of all fields Claude extracted from the denial letter
    }
    # -------------------------------------------------------
# ENDPOINT 4: Analyse Denial Letter
# This is Ezer's most powerful endpoint.
# It combines extraction AND analysis in one single step.
# The user uploads a PDF and gets back:
# - All extracted fields
# - Plain English explanation
# - Contestability assessment
# - Legal contestation language
# - Next steps
# This is the endpoint the frontend will use.
# -------------------------------------------------------

@app.post("/analyse")
# When someone sends a POST request to /analyse,
# run this function. This is the main Ezer endpoint.

async def analyse_denial_letter(file: UploadFile = File(...)):
    """
    WHAT THIS ENDPOINT DOES:
    Accepts a PDF denial letter upload.
    Runs it through extraction then analysis.
    Returns the complete Ezer response in one call.
    
    INPUT: A PDF file uploaded by the user
    OUTPUT: Extracted fields + full legal analysis
    """
    
    # -------------------------------------------------------
    # STEP 1: Validate the file is a PDF
    # -------------------------------------------------------
    
    if not file.filename.endswith('.pdf'):
        # Reject anything that is not a PDF
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted. Please upload a PDF denial letter."
        )
    
    # -------------------------------------------------------
    # STEP 2: Read the uploaded file
    # -------------------------------------------------------
    
    contents = await file.read()
    # Read the entire PDF into memory as bytes
    # await means wait for this to complete before moving on
    
    # -------------------------------------------------------
    # STEP 3: Process and Discard - Ezer's privacy principle
    # Create a temporary file, use it, then delete it
    # Nothing is stored permanently on our servers
    # -------------------------------------------------------
    
    with tempfile.NamedTemporaryFile(delete=True, suffix='.pdf') as tmp_file:
        # Create a temporary PDF file
        # delete=True means it is automatically deleted when done
        
        tmp_file.write(contents)
        # Write the uploaded PDF into the temporary file
        
        tmp_file.flush()
        # Force Python to write everything to disk immediately
        
        # -------------------------------------------------------
        # STEP 4: Extract fields from the PDF
        # -------------------------------------------------------
        
        try:
            extracted_fields = process_denial_letter(tmp_file.name)
            # Call our extractor to read the PDF
            # extracted_fields now contains insurer, CCN, rejection reason etc
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Extraction failed: {str(e)}"
            )
        
        # -------------------------------------------------------
        # STEP 5: Analyse the extracted fields
        # -------------------------------------------------------
        
        try:
            analysis = analyse_rejection(extracted_fields)
            # Call our analyser to assess the rejection
            # analysis now contains plain English explanation,
            # contestability, legal language, and next steps
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Analysis failed: {str(e)}"
            )
    
    # -------------------------------------------------------
    # STEP 6: Return the complete Ezer response
    # -------------------------------------------------------
    
    return {
        "success": True,
        # Confirms everything worked
        
        "filename": file.filename,
        # The original filename so user knows which letter was processed
        
        "extracted_fields": extracted_fields,
        # All the fields extracted from the PDF
        # insurer, CCN, rejection reason, date, hospital, patient
        
        "analysis": analysis
        # The complete legal analysis from Claude
        # plain English explanation, contestability, legal language
    }


from pydantic import BaseModel
# BaseModel is used to define the exact structure of incoming
# request data - like a form with specific required fields


class CGORequest(BaseModel):
    """
    WHAT THIS CLASS DOES:
    Defines the exact structure of data the frontend must send
    when requesting a CGO letter generation.
    Think of it as a form that must be filled before proceeding.
    """

    policyholder_name: str
    # Name of the person sending the complaint letter

    policy_address: str
    # Address on the policy document
    # Needed for Ombudsman jurisdiction mapping

    consent: bool
    # True if user checked the consent checkbox
    # False means letter will not be generated

    consent_timestamp: str
    # When user gave consent in ISO 8601 format
    # Example: "2026-04-17T14:30:00"

    extracted_fields: dict
    # Fields extracted from the denial letter
    # Passed from the /analyse endpoint response

    analysis: dict
    # Analysis from the /analyse endpoint response
    # Contains denial pattern and contestation language

    amount_disputed: str = "As per policy terms"
    # Optional - defaults to "As per policy terms"


@app.post("/generate-cgo")
# When frontend sends POST to /generate-cgo run this function

async def generate_cgo_endpoint(request: CGORequest):
    """
    WHAT THIS ENDPOINT DOES:
    Receives all case information from the frontend.
    Validates consent first.
    Generates complete CGO complaint letter.
    Returns letter with all metadata including consent record.
    """

    # -------------------------------------------------------
    # STEP 1: Validate consent - mandatory per Decision 8
    # -------------------------------------------------------

    if not request.consent:
        # If user did not check the consent checkbox
        raise HTTPException(
            status_code=400,
            detail="Informed consent is required before generating a CGO letter. Please confirm you understand this is guidance only and not legal advice."
        )

    # -------------------------------------------------------
    # STEP 2: Generate the CGO letter
    # -------------------------------------------------------

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

    # -------------------------------------------------------
    # STEP 3: Return the complete response
    # -------------------------------------------------------

    return {
        "success": True,
        "letter": result,
        "next_steps": {
            "step1": "Review the letter carefully before sending.",
            "step2": "Verify the CGO email address on the insurer website.",
            "step3": "Send the letter by email. Keep a copy.",
            "step4": "Note the date sent. Insurer has 15 days to respond.",
            "step5": "Download your Case JSON file to track this case."
        }
    }
    from backend.app.case_json import generate_case_json
# Import case JSON generator from case_json.py
# This creates the portable case record the user downloads
from backend.app.policy_extractor import extract_policy_document
# Import policy document extractor from policy_extractor.py
# Reads policy PDF and pulls out all key fields including
# sum insured, waiting periods, riders, pre-existing conditions


class CaseJSONRequest(BaseModel):
    """
    WHAT THIS CLASS DOES:
    Defines the exact structure of data the frontend
    must send when requesting a Case Metadata JSON.
    All fields from the previous steps are passed here.
    """

    policyholder_name: str
    # Name of the person who owns this case

    policy_address: str
    # Address from the policy document
    # Determines Ombudsman jurisdiction

    phase_completed: str = "CGO_LETTER_GENERATED"
    # Which stage has been completed
    # Defaults to CGO_LETTER_GENERATED

    extracted_fields: dict
    # Fields extracted from denial letter

    analysis: dict
    # Analysis from analyser.py

    letter_result: dict
    # Result from letter_generator.py
    # Contains CGO email, consent record etc


@app.post("/case-json")
# When frontend sends POST to /case-json run this function

async def generate_case_json_endpoint(request: CaseJSONRequest):
    """
    WHAT THIS ENDPOINT DOES:
    Takes all case information and generates the
    complete Case Metadata JSON for the user to download.

    This is the last step in the Ezer core flow.
    After this the user has everything they need:
    - CGO letter to send
    - Case JSON to track their case and return to Ezer

    INPUT: CaseJSONRequest with all case details
    OUTPUT: Complete case metadata JSON
    """

    try:
        case_data = generate_case_json(
            extracted_fields=request.extracted_fields,
            # Fields from denial letter extraction

            analysis=request.analysis,
            # Legal analysis results

            letter_result=request.letter_result,
            # CGO letter generation results

            policyholder_name=request.policyholder_name,
            # Person's name

            policy_address=request.policy_address,
            # Policy document address

            phase_completed=request.phase_completed
            # Current escalation stage
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Case JSON generation failed: {str(e)}"
        )

    return {
        "success": True,
        # Confirms generation worked

        "file_label": "Your Ezer Case File",
        # Human friendly label for the download button

        "download_button_label": "Download Your Case File",
        # Text for the download button on frontend

        "case_data": case_data,
        # The complete case metadata
        # Frontend displays this as a readable card
        # User downloads this as their case file

        "return_visit_instruction": "Save this file. If you return to Ezer to continue your case, upload this file when prompted.",
        # Clear instruction so user knows what to do with the file

        "next_step": case_data.get("escalation", {}).get("next_step", {})
        # The recommended next action from escalation ladder
    }
    from backend.app.policy_extractor import extract_policy_document


# -------------------------------------------------------
# ENDPOINT 7: Extract Policy Document
# Accepts a policy PDF upload and returns all key fields.
# This powers Screen 2 and Screen 3 of the Ezer flow.
# -------------------------------------------------------

@app.post("/extract-policy")
async def extract_policy_endpoint(file: UploadFile = File(...)):
    """
    INPUT:  A policy PDF uploaded by the user.
    OUTPUT: All extracted policy fields as structured JSON.

    Called on Screen 2 when user uploads their policy.
    Result displayed on Screen 3 - Know Your Policy.
    """

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
# Accepts a settlement letter PDF and returns all fields.
# Powers the settlement audit flow from Supplement V3.
# -------------------------------------------------------

@app.post("/extract-settlement")
async def extract_settlement_endpoint(file: UploadFile = File(...)):
    """
    INPUT:  A settlement letter PDF uploaded by the user.
    OUTPUT: All extracted settlement fields as structured JSON.

    Includes financial summary, line items, deductions,
    without_prejudice flag, and consumables analysis
    if Protector Rider is confirmed active.
    """

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