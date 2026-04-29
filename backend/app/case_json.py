# Ezer Case Metadata JSON Generator - case_json.py
# -------------------------------------------------------
# PURPOSE: Packages everything Ezer knows about a case
# into a single structured JSON that the user downloads
# and keeps as their portable case record.
#
# This file reads ALL content from config files.
# No text is hardcoded here.
# Non-developers can update all content without touching
# this file.
#
# The JSON serves two purposes:
# 1. Machine readable case thread for return visits
# 2. Source data for human readable card on frontend
#
# PRD Reference: Section 9 Step 8
# Decision Log: Decisions 9, 11, 12, 17, 18
# -------------------------------------------------------


# IMPORT STATEMENTS

import json
# json reads our config files and builds the output JSON

import uuid
# uuid generates unique case reference numbers

from datetime import datetime
# datetime gives us current timestamps


# -------------------------------------------------------
# CONFIG FILE PATHS
# -------------------------------------------------------

CONFIG_DIR = "backend/config"
# Folder where all config files live

OMBUDSMAN_FILE = f"{CONFIG_DIR}/ombudsman_directory.json"
# Contains all Ombudsman office details by state

ESCALATION_FILE = f"{CONFIG_DIR}/escalation_ladder.json"
# Contains all phase descriptions and next steps

APP_CONFIG_FILE = f"{CONFIG_DIR}/app_config.json"
# Contains version, disclaimer, labels, empathy messages


# -------------------------------------------------------
# FUNCTION 1: load_config
# -------------------------------------------------------

def load_config(filepath: str) -> dict:
    """
    WHAT THIS FUNCTION DOES:
    Reads a JSON config file and returns its contents
    as a Python dictionary.

    INPUT:
    filepath = path to the JSON config file

    OUTPUT:
    Returns dictionary with file contents
    Or empty dictionary if file cannot be read
    """

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
            # json.load converts JSON text to Python dictionary
    except Exception as e:
        print(f"Error loading config {filepath}: {e}")
        return {}
        # Return empty dict so code does not crash


# -------------------------------------------------------
# FUNCTION 2: generate_case_reference
# -------------------------------------------------------

def generate_case_reference(ccn: str) -> str:
    """
    WHAT THIS FUNCTION DOES:
    Generates a unique Ezer case reference number.
    Combines a short UUID with the CCN number.

    ANALOGY:
    Like a hospital patient ID that links all your
    visits into one continuous record.

    INPUT:
    ccn = claim reference number from denial letter

    OUTPUT:
    Unique case reference string
    Example: "EZER-RC-HS25-15028403-A3F2"
    """

    short_id = str(uuid.uuid4())[:4].upper()
    # uuid4() generates random unique ID
    # [:4] takes first 4 characters only
    # .upper() converts to uppercase
    # Result: "A3F2"

    return f"EZER-{ccn}-{short_id}"
    # Example: "EZER-RC-HS25-15028403-A3F2"


# -------------------------------------------------------
# FUNCTION 3: get_ombudsman_office
# -------------------------------------------------------

def get_ombudsman_office(policy_address: str) -> dict:
    """
    WHAT THIS FUNCTION DOES:
    Reads ombudsman_directory.json and maps the policy
    address to the correct Ombudsman office.

    Per PRD: Jurisdiction is determined by address in
    policy document. Not current location. Not Aadhaar.

    INPUT:
    policy_address = address from policy document

    OUTPUT:
    Dictionary with Ombudsman office details
    """

    directory = load_config(OMBUDSMAN_FILE)
    # Load Ombudsman directory from config file

    offices = directory.get("offices", {})
    # Get the offices section from config

    address_lower = policy_address.lower()
    # Convert address to lowercase for matching

    for state, office in offices.items():
        # Go through each state entry
        if state in address_lower:
            # If state name appears in policy address
            return office
            # Return matching office details

    return directory.get("default", {
        "city": "Unknown",
        "address": "Please visit cioins.co.in",
        "email": "Please check cioins.co.in",
        "jurisdiction": "Determined by policy address"
    })
    # Return default if no state match found


# -------------------------------------------------------
# FUNCTION 4: get_next_step
# -------------------------------------------------------

def get_next_step(phase_completed: str) -> dict:
    """
    WHAT THIS FUNCTION DOES:
    Reads escalation_ladder.json and returns the next
    step details for the given completed phase.

    INPUT:
    phase_completed = current phase that was just done
    Example: "CGO_LETTER_GENERATED"

    OUTPUT:
    Dictionary with next step details from config
    """

    ladder = load_config(ESCALATION_FILE)
    # Load escalation ladder from config file

    phases = ladder.get("phases", {})
    # Get the phases section

    current_phase = phases.get(phase_completed, {})
    # Get details for the completed phase

    if current_phase:
        return {
            "next_step": current_phase.get("next_step", ""),
            "next_step_label": current_phase.get("next_step_label", ""),
            "next_step_description": current_phase.get("next_step_description", ""),
            "timeline": current_phase.get("timeline", ""),
            "urgency": current_phase.get("urgency", "MEDIUM"),
            "urgency_reason": current_phase.get("urgency_reason", ""),
            "instructions": current_phase.get("instructions", [])
        }
        # Return structured next step from config

    return {
        "next_step": "CONSULT_ADVISOR",
        "next_step_description": "Please consult a qualified insurance advisor.",
        "urgency": "HIGH"
    }
    # Return default if phase not found


# -------------------------------------------------------
# FUNCTION 5: generate_case_json
# -------------------------------------------------------

def generate_case_json(
    extracted_fields: dict,
    analysis: dict,
    letter_result: dict,
    policyholder_name: str,
    policy_address: str,
    phase_completed: str = "CGO_LETTER_GENERATED"
) -> dict:
    """
    WHAT THIS FUNCTION DOES:
    The main function. Packages everything into the
    Case Metadata JSON that the user downloads.

    Reads all content from config files.
    No hardcoded text anywhere in this function.

    INPUT:
    extracted_fields = from extractor.py
    analysis = from analyser.py
    letter_result = from letter_generator.py
    policyholder_name = person's name
    policy_address = address from policy document
    phase_completed = current stage completed

    OUTPUT:
    Complete case metadata dictionary
    """

    # Load all config files
    app_config = load_config(APP_CONFIG_FILE)
    # App version, disclaimer, labels, empathy messages

    # Generate unique identifiers
    ccn = extracted_fields.get("CCN", "UNKNOWN")
    case_reference = generate_case_reference(ccn)
    # Example: "EZER-RC-HS25-15028403-A3F2"

    now = datetime.now().isoformat()
    # Current timestamp in ISO 8601 format

    # Get next step from escalation ladder config
    next_step = get_next_step(phase_completed)

    # Get Ombudsman office from directory config
    ombudsman_office = get_ombudsman_office(policy_address)

    # Build the complete case metadata
    case_metadata = {

        # -------------------------------------------
        # SECTION 1: Case Identity
        # -------------------------------------------
        "ezer_case": {
            "case_reference": case_reference,
            # Unique Ezer ID for this case

            "created_at": now,
            # When case was created

            "last_updated": now,
            # When case was last updated

            "ezer_version": app_config.get("version", "1.0.0"),
            # From app_config.json - no hardcoding

            "phase_completed": phase_completed,
            # Current stage

            "phase_label": app_config.get(
                "phase_labels", {}
            ).get(phase_completed, phase_completed),
            # Human readable phase label from config

            "insurance_category": "Health",
            # Will be dynamic when life insurance added
        },

        # -------------------------------------------
        # SECTION 2: Policyholder
        # -------------------------------------------
        "policyholder": {
            "name": policyholder_name,
            "policy_address": policy_address,
            "patient_name": extracted_fields.get(
                "PATIENT", policyholder_name
            ),
        },

        # -------------------------------------------
        # SECTION 3: Insurance Details
        # -------------------------------------------
        "insurance": {
            "insurer_name": extracted_fields.get("INSURER", ""),
            "policy_number": extracted_fields.get("POLICY_NUMBER", ""),
            "ccn": extracted_fields.get("CCN", ""),
            "denial_type": extracted_fields.get("DENIAL_TYPE", "Cashless"),
            "denial_date": extracted_fields.get("DATE", ""),
            "hospital_name": extracted_fields.get("HOSPITAL", ""),
        },

        # -------------------------------------------
        # SECTION 4: Denial Details
        # -------------------------------------------
        "denial": {
            "rejection_reason_verbatim": extracted_fields.get(
                "REJECTION_REASON", ""
            ),
            # Exact words from denial letter

            "denial_pattern": analysis.get("DENIAL_PATTERN", ""),
            "contestability": analysis.get("CONTESTABILITY", ""),
            "plain_english_explanation": analysis.get("PLAIN_ENGLISH", ""),
            "contestability_reason": analysis.get(
                "CONTESTABILITY_REASON", ""
            ),
        },

        # -------------------------------------------
        # SECTION 5: Escalation Status
        # -------------------------------------------
        "escalation": {
            "phase_completed": phase_completed,

            "cgo_letter_generated": phase_completed in [
                "CGO_LETTER_GENERATED",
                "CGO_SENT",
                "BIMA_BHAROSA_FILED",
                "OMBUDSMAN_FILED"
            ],
            # True if CGO letter has been generated

            "cgo_email": letter_result.get("cgo_email", ""),
            "cgo_email_verified": letter_result.get(
                "cgo_email_verified", False
            ),
            "irdai_cc_email": app_config.get(
                "irdai_cc_email", "complaints@irdai.gov.in"
            ),
            # From app_config - not hardcoded

            "cgo_sent_date": "",
            # Empty - user fills this when they send the letter

            "ombudsman_office": ombudsman_office,
            # From ombudsman_directory.json config

            "next_step": next_step,
            # From escalation_ladder.json config

            "contact_links": app_config.get("contact_links", {}),
            # Bima Bharosa, Ombudsman portal links from config
        },

        # -------------------------------------------
        # SECTION 6: Consent Record
        # Per Decision 9 - lives in user-owned JSON
        # -------------------------------------------
        "consent": letter_result.get("consent_record", {}),

        # -------------------------------------------
        # SECTION 7: Documents
        # -------------------------------------------
        "documents": {
            "denial_letter_processed": True,
            "policy_document_uploaded": False,
            # Will be True when policy document uploaded
            "cgo_letter_generated": True,
            "email_subject": letter_result.get("email_subject", ""),
        },

        # -------------------------------------------
        # SECTION 8: Ezer Metadata
        # All text from app_config.json - no hardcoding
        # -------------------------------------------
        "ezer_metadata": {
            "disclaimer": app_config.get("disclaimer", ""),
            # From app_config.json

            "data_principle": app_config.get("data_principle", ""),
            # From app_config.json

            "return_visit_instruction": app_config.get(
                "return_visit_instruction", ""
            ),
            # From app_config.json

            "file_label": app_config.get(
                "case_file_label", "Your Ezer Case File"
            ),
            # From app_config.json

            "download_button_label": app_config.get(
                "download_button_label", "Download Your Case File"
            ),
            # From app_config.json

            "generated_by": f"Ezer v{app_config.get('version', '1.0.0')}",
            "generated_at": now
        }
    }

    return case_metadata
    # Return complete case metadata
    # FastAPI converts this to JSON automatically