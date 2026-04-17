# Ezer CGO Letter Generator - letter_generator.py
# -------------------------------------------------------
# PURPOSE: Generates the CGO complaint letter that the
# policyholder sends to the insurer's Chief Grievance Officer.
#
# This file reads ALL legal language, email addresses, and
# letter templates from JSON config files in backend/config/.
# No legal text is hardcoded here.
# Non-developers can update legal language without touching
# this file.
#
# FLOW:
# 1. Load config files
# 2. Validate consent flag - refuse if not given
# 3. Look up CGO email from directory
# 4. Load appropriate legal language for denial pattern
# 5. Build prompt for Claude
# 6. Generate letter
# 7. Return letter with metadata
#
# PRD Reference: Section 9 Step 7
# Decision Log: Decisions 6, 8, 9, 11, 12
# -------------------------------------------------------


# IMPORT STATEMENTS

import os
# os is Python's built-in tool for reading environment
# variables and file paths

import json
# json is Python's built-in tool for reading JSON files
# We use it to load our config files

from anthropic import Anthropic
# Official Anthropic Python library
# Used to send prompts to Claude and receive responses

from dotenv import load_dotenv
# load_dotenv reads our .env file and loads API key into memory

from datetime import datetime
# datetime gives us the current date for the letter header


# -------------------------------------------------------
# ENVIRONMENT SETUP
# -------------------------------------------------------

load_dotenv("backend/.env")
# Load API key from .env file
# Must be called before creating the Anthropic client


# -------------------------------------------------------
# CLIENT SETUP
# -------------------------------------------------------

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
# Create our connection to Claude AI
# Used to generate the CGO letter text


# -------------------------------------------------------
# CONFIG FILE PATHS
# These point to our JSON config files
# All legal language and templates live in these files
# -------------------------------------------------------

CONFIG_DIR = "backend/config"
# The folder where all config files live

LEGAL_LANGUAGE_FILE = f"{CONFIG_DIR}/legal_language.json"
# Contains all legal paragraphs by denial pattern

CGO_DIRECTORY_FILE = f"{CONFIG_DIR}/cgo_directory.json"
# Contains CGO email addresses for all major insurers

LETTER_TEMPLATES_FILE = f"{CONFIG_DIR}/letter_templates.json"
# Contains letter structure and boilerplate text


# -------------------------------------------------------
# FUNCTION 1: load_config
# -------------------------------------------------------

def load_config(filepath: str) -> dict:
    """
    WHAT THIS FUNCTION DOES:
    Reads a JSON config file and returns its contents
    as a Python dictionary.

    ANALOGY:
    Like opening a filing cabinet drawer and reading
    the document inside. The filing cabinet is our
    config folder. The document is the JSON file.

    INPUT:
    filepath = path to the JSON file
    Example: "backend/config/legal_language.json"

    OUTPUT:
    Returns the JSON contents as a Python dictionary
    Or returns empty dictionary if file cannot be read
    """

    try:
        # try means: attempt this, catch errors gracefully
        with open(filepath, 'r', encoding='utf-8') as f:
            # open() opens the file for reading
            # 'r' means read mode
            # encoding='utf-8' handles special characters
            return json.load(f)
            # json.load() converts JSON text into Python dictionary
    except Exception as e:
        # If anything goes wrong reading the file
        print(f"Error loading config {filepath}: {e}")
        return {}
        # Return empty dictionary so code does not crash


# -------------------------------------------------------
# FUNCTION 2: get_cgo_email
# -------------------------------------------------------

def get_cgo_email(insurer_name: str) -> dict:
    """
    WHAT THIS FUNCTION DOES:
    Looks up the CGO email address for a given insurer
    by searching the cgo_directory.json config file.

    ANALOGY:
    Like looking up a contact in your phone by searching
    for their name. We search by partial name match.

    INPUT:
    insurer_name = full insurer name from denial letter
    Example: "HDFC ERGO General Insurance Company Limited"

    OUTPUT:
    Returns dictionary with cgo_email, grievance_email,
    website, and verified status
    Or returns default entry if insurer not found
    """

    directory = load_config(CGO_DIRECTORY_FILE)
    # Load the CGO directory from JSON file

    insurer_lower = insurer_name.lower()
    # Convert to lowercase for case-insensitive matching
    # "HDFC ERGO" and "hdfc ergo" should both match

    for key, details in directory.get("directory", {}).items():
        # Go through each insurer entry in the directory
        # key = insurer name fragment e.g. "hdfc ergo"
        # details = dictionary with email, website etc

        if key in insurer_lower:
            # If the key appears anywhere in the insurer name
            return details
            # Return the full details dictionary

    # If no match found return the default entry
    return directory.get("default", {
        "cgo_email": "cgo@[insurer-website].com",
        "verified": False
    })


# -------------------------------------------------------
# FUNCTION 3: get_legal_language
# -------------------------------------------------------

def get_legal_language(denial_pattern: str) -> dict:
    """
    WHAT THIS FUNCTION DOES:
    Loads the appropriate legal language for the detected
    denial pattern from legal_language.json config file.

    ANALOGY:
    Like a lawyer pulling the right precedent folder from
    their filing cabinet based on the type of case.

    INPUT:
    denial_pattern = the pattern detected by analyser.py
    Example: "INVESTIGATIVE_PROCEDURE" or "MEDICAL_NECESSITY"

    OUTPUT:
    Returns dictionary with all legal paragraphs for
    that specific denial pattern
    """

    legal = load_config(LEGAL_LANGUAGE_FILE)
    # Load the legal language config file

    patterns = legal.get("patterns", {})
    # Get the patterns section from the config
    # This contains legal language for each denial pattern

    if denial_pattern in patterns:
        # If we have specific language for this pattern
        return patterns[denial_pattern]
        # Return the pattern-specific legal language

    # If pattern not found return general denial language
    return patterns.get("GENERAL_DENIAL", {})


# -------------------------------------------------------
# FUNCTION 4: validate_mandatory_fields
# -------------------------------------------------------

def validate_mandatory_fields(extracted_fields: dict) -> dict:
    """
    WHAT THIS FUNCTION DOES:
    Checks which mandatory fields are present and which
    are missing. Returns a report of what is found and
    what the user needs to provide.

    The five mandatory fields per Decision 12:
    1. Insurer name
    2. Insured person name
    3. Policy number
    4. Denial date
    5. Rejection reason

    IMPORTANT: Per Decision 11, nothing blocks generation.
    Missing mandatory fields are flagged for user input.
    User can proceed with placeholders if needed.

    INPUT:
    extracted_fields = dictionary from extractor.py

    OUTPUT:
    Returns dictionary with:
    - present: fields that were found
    - missing: fields that need user input
    - can_proceed: always True per Decision 11
    """

    mandatory_fields = {
        "INSURER": "Insurer name",
        "PATIENT": "Insured person name",
        "POLICY_NUMBER": "Policy number",
        "DATE": "Denial date",
        "REJECTION_REASON": "Rejection reason"
    }
    # Dictionary mapping field keys to human-readable names

    present = {}
    # Fields that were successfully extracted

    missing = {}
    # Fields that need user input

    for field_key, field_label in mandatory_fields.items():
        # Go through each mandatory field

        value = extracted_fields.get(field_key, "")
        # Get the value from extracted fields
        # Returns empty string if not found

        if value and value != "NOT FOUND":
            # If field has a real value
            present[field_key] = value
        else:
            # If field is missing or NOT FOUND
            missing[field_key] = field_label
            # Add to missing list with human readable label

    return {
        "present": present,
        # Fields that were found and have values

        "missing": missing,
        # Fields that need user input
        # Key = field code, Value = human readable label

        "can_proceed": True,
        # Always True per Decision 11
        # Nothing blocks generation

        "missing_count": len(missing)
        # How many fields are missing
        # Used to decide whether to show enrichment form
    }


# -------------------------------------------------------
# FUNCTION 5: generate_cgo_letter
# -------------------------------------------------------

def generate_cgo_letter(
    extracted_fields: dict,
    analysis: dict,
    policyholder_name: str,
    policy_address: str,
    consent: bool,
    consent_timestamp: str,
    amount_disputed: str = "As per policy terms"
) -> dict:
    """
    WHAT THIS FUNCTION DOES:
    The main function. Takes all case information and
    generates a complete CGO complaint letter using Claude.

    Reads legal language from config files.
    Validates consent before proceeding.
    Returns letter text plus all metadata needed by frontend.

    INPUT:
    extracted_fields = dictionary from extractor.py
    analysis = dictionary from analyser.py
    policyholder_name = name of person sending letter
    policy_address = address on the policy document
    consent = True if user checked consent checkbox
    consent_timestamp = when user gave consent (ISO format)
    amount_disputed = claim amount (optional)

    OUTPUT:
    Returns dictionary with:
    - letter_text: complete CGO letter ready to send
    - cgo_email: pre-filled CGO email (user should verify)
    - irdai_cc_email: complaints@irdai.gov.in
    - date: today's date
    - reference_numbers: policy number and CCN
    - consent_record: for Case Metadata JSON
    - disclaimer: mandatory legal disclaimer
    - field_validation: which fields were present/missing
    """

    # -------------------------------------------------------
    # STEP 1: Validate consent
    # Per Decision 8 - consent is mandatory
    # -------------------------------------------------------

    if not consent:
        # If consent flag is False or not provided
        return {
            "error": "Consent required",
            "message": "User must provide informed consent before CGO letter can be generated.",
            "consent_required": True
        }
        # Return error - do not generate letter without consent

    # -------------------------------------------------------
    # STEP 2: Load all config files
    # -------------------------------------------------------

    legal = load_config(LEGAL_LANGUAGE_FILE)
    # Load legal language config

    templates = load_config(LETTER_TEMPLATES_FILE)
    # Load letter templates config

    # -------------------------------------------------------
    # STEP 3: Validate mandatory fields
    # -------------------------------------------------------

    field_validation = validate_mandatory_fields(extracted_fields)
    # Check which mandatory fields are present and missing

    # -------------------------------------------------------
    # STEP 4: Extract fields for letter
    # Use extracted values or smart defaults
    # -------------------------------------------------------

    insurer_name = extracted_fields.get("INSURER", "The Insurer")
    policy_number = extracted_fields.get("POLICY_NUMBER", "[Policy number not available]")
    ccn = extracted_fields.get("CCN", "[Claim reference not available]")
    rejection_reason = extracted_fields.get("REJECTION_REASON", "[Rejection reason not provided by insurer]")
    denial_date = extracted_fields.get("DATE", "[Date not available]")
    hospital_name = extracted_fields.get("HOSPITAL", "[Hospital name not available]")
    patient_name = extracted_fields.get("PATIENT", policyholder_name)
    denial_type = extracted_fields.get("DENIAL_TYPE", "Cashless")

    # Get today's date for the letter header
    today = datetime.now().strftime("%d %B %Y")
    # Formats as "17 April 2026"

    # -------------------------------------------------------
    # STEP 5: Look up CGO email from directory
    # -------------------------------------------------------

    cgo_details = get_cgo_email(insurer_name)
    cgo_email = cgo_details.get("cgo_email", "cgo@[insurer-website].com")
    cgo_verified = cgo_details.get("verified", False)

    # Get IRDAI CC email from legal language config
    irdai_cc = load_config(CGO_DIRECTORY_FILE).get("irdai_cc", "complaints@irdai.gov.in")

    # -------------------------------------------------------
    # STEP 6: Load pattern-specific legal language
    # -------------------------------------------------------

    denial_pattern = analysis.get("DENIAL_PATTERN", "GENERAL_DENIAL")
    pattern_language = get_legal_language(denial_pattern)
    # Loads the right legal paragraphs for this denial type

    contestation_language = analysis.get("CONTESTATION_LANGUAGE", "")
    # Get the contestation language from analyser output

    structural_impact = analysis.get("STRUCTURAL_IMPACT", "")
    # Get the structural impact assessment

    # Get letter closing language from templates
    letter_closings = templates.get("cgo_letter", {}).get("closing", {})
    response_demand = letter_closings.get("response_demand", "")
    escalation_warning = letter_closings.get("escalation_warning", "")
    acknowledgement_request = letter_closings.get("acknowledgement_request", "")

    # Get disclaimer from legal language config
    disclaimer = legal.get("disclaimer", "Ezer is not a legal advisor.")

    # -------------------------------------------------------
    # STEP 7: Build Claude prompt for letter generation
    # -------------------------------------------------------

    prompt = f"""
You are Ezer, helping an Indian policyholder write a formal CGO
complaint letter. Generate a complete, professional letter.

STRICT RULES:
- Plain text only. No markdown. No bullet points. No asterisks.
- Formal Indian business letter format.
- Firm but professional tone.
- Never say the claim is invalid.
- Never discourage escalation.
- Use MAY not WILL for outcomes.
- Include all reference numbers in every relevant paragraph.

LETTER DETAILS:
Date: {today}
From: {policyholder_name}
Address: {policy_address}
To: The Chief Grievance Officer, {insurer_name}
Subject: Formal Complaint - Denial of {denial_type} Claim
Policy Number: {policy_number}
CCN: {ccn}
Patient: {patient_name}
Hospital: {hospital_name}
Date of Denial: {denial_date}
Amount Disputed: {amount_disputed}

REJECTION REASON (quote this verbatim in the letter):
"{rejection_reason}"

CONTESTATION LANGUAGE TO INCLUDE:
{contestation_language}

PATTERN SPECIFIC LEGAL LANGUAGE:
{pattern_language.get('legal_grounding', '')}
{pattern_language.get('desk_review_challenge', '')}
{pattern_language.get('prerequisite_language', '')}
{pattern_language.get('vague_denial_language', '')}
{pattern_language.get('burden_of_proof', '')}

STRUCTURAL IMPACT TO MENTION:
{structural_impact}

CLOSING REQUIREMENTS:
{response_demand}
{escalation_warning}
{acknowledgement_request}

CC: {irdai_cc} (IRDAI - always include this)

ENCLOSURES TO LIST:
Copy of denial letter dated {denial_date}
Copy of policy document if available
Any supporting medical documents

FOOTER DISCLAIMER TO INCLUDE AT END:
{disclaimer}

Generate the complete letter now.
"""

    # -------------------------------------------------------
    # STEP 8: Call Claude to generate the letter
    # -------------------------------------------------------

    message = client.messages.create(
        model="claude-sonnet-4-6",
        # Claude Sonnet for letter generation

        max_tokens=2000,
        # Letters can be long - 2000 tokens allows ~1500 words

        messages=[
            {"role": "user", "content": prompt}
            # Send our complete prompt to Claude
        ]
    )

    letter_text = message.content[0].text
    # Extract the generated letter from Claude's response

    # -------------------------------------------------------
    # STEP 9: Build consent record for Case Metadata JSON
    # Per Decision 9 - consent lives in user-owned JSON
    # -------------------------------------------------------

    consent_gate_config = legal.get("consent_gate", {})

    consent_record = {
        "consent_given": True,
        # User explicitly consented

        "consent_text_version": consent_gate_config.get("version", "v1.0"),
        # Version of consent text shown - for traceability

        "consent_timestamp": consent_timestamp,
        # When user gave consent - ISO 8601 format

        "consent_text_shown": consent_gate_config.get("body", ""),
        # Exact text that was displayed to user

        "case_reference": f"EZER-{ccn}",
        # Ezer generated case reference

        "policy_number": policy_number,
        "ccn": ccn
        # Reference numbers for this consent record
    }

    # -------------------------------------------------------
    # STEP 10: Return complete response
    # -------------------------------------------------------

    return {
        "success": True,
        # Confirms letter was generated successfully

        "letter_text": letter_text,
        # The complete CGO letter - ready to send

        "cgo_email": cgo_email,
        # Pre-filled CGO email from our directory
        # User should verify on insurer website before sending

        "cgo_email_verified": cgo_verified,
        # Whether we have verified this email is current

        "irdai_cc_email": irdai_cc,
        # Always CC IRDAI as per PRD

        "date": today,
        # Today's date used in the letter

        "reference_numbers": {
            "policy_number": policy_number,
            "ccn": ccn
        },
        # All reference numbers for easy access

        "consent_record": consent_record,
        # For inclusion in Case Metadata JSON
        # Per Decision 9 - user owns this record

        "field_validation": field_validation,
        # Which fields were present and which were missing
        # Frontend uses this to show what user should verify

        "disclaimer": disclaimer,
        # Mandatory legal disclaimer per PRD

        "email_subject": f"Formal CGO Complaint - Policy {policy_number} - CCN {ccn} - {denial_date}",
        # Pre-filled email subject line for convenience

        "cgo_email_note": "Please verify this email address on the insurer's official website before sending." if not cgo_verified else "Email address verified against insurer directory."
        # Guidance on whether to verify the email
    }