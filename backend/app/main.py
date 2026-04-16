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
# This imports our process_denial_letter function from
# the extractor.py file we just wrote.
# Think of it as bringing the chef from the kitchen
# into the main dining room so they can receive orders.


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