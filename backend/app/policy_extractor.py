# Ezer Policy Extractor - policy_extractor.py
# -------------------------------------------------------
# PURPOSE: Extracts structured data from insurance policy
# documents using the Claude API.
#
# This is Ezer's policy reading engine. When a user
# uploads their policy document on Screen 2, this file
# reads it and returns all key fields in a structured
# format the rest of Ezer can work with.
#
# SUPPORTS THREE HDFC ERGO FORMATS:
# 1. my: Optima Secure - newer format (Section B.1. refs)
# 2. Optima Secure older format (B-1.1 refs)
# 3. Optima Restore (B-1.a refs)
# Designed to handle any insurer - not HDFC ERGO specific.
#
# PRIVACY: Zero Data Retention on every Claude API call.
# Documents are processed and discarded. Never stored.
# -------------------------------------------------------

import os
import json
import anthropic
import pdfplumber

from backend.app.schemas import (
    PolicyDocument,
    RiderAddon,
    DeclaredPreExistingCondition,
    DocumentType
)


# -------------------------------------------------------
# CORE FIELDS WE EXPECT TO FIND
# Used to calculate extraction_completeness score.
# -------------------------------------------------------

CORE_FIELDS = [
    "policyholder_name",
    "policy_number",
    "insurer_name",
    "product_name",
    "policy_start_date",
    "policy_end_date",
    "first_inception_date",
    "base_sum_insured",
    "room_rent_limit",
    "waiting_period_pre_existing",
    "policy_address",
]


# -------------------------------------------------------
# STEP 1: EXTRACT TEXT FROM PDF
# -------------------------------------------------------

def extract_text_from_pdf(pdf_path: str) -> tuple[str, bool]:
    """
    Reads a PDF and returns all text as a single string.

    Returns a tuple:
    - text: the extracted text content
    - password_required: True if PDF was locked

    We use pdfplumber because it handles multi-column
    layouts and tables better than basic PDF readers.
    This matters for policy documents which have complex
    table structures for benefits and exclusions.
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            pages = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
            full_text = "\n\n".join(pages)
            return full_text, False

    except Exception as e:
        error_message = str(e).lower()
        if "password" in error_message or "encrypted" in error_message:
            return "", True
        raise


# -------------------------------------------------------
# STEP 2: CALL CLAUDE API TO EXTRACT FIELDS
# -------------------------------------------------------

def call_claude_for_policy_extraction(policy_text: str) -> dict:
    """
    Sends policy document text to Claude API.
    Returns a dictionary of extracted fields.

    PROMPT DESIGN:
    The prompt is built around what we learned from
    reading real HDFC ERGO policies. It handles three
    distinct document formats and instructs Claude to
    always return structured JSON - never free text.

    ZERO DATA RETENTION:
    The anthropic-beta header ensures Anthropic does not
    use this document text for model training.
    This is Ezer's core privacy commitment.
    """

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    prompt = """You are a precise insurance policy document reader for Ezer, an AI-powered insurance escalation engine for Indian policyholders.

You will read an insurance policy document and extract specific fields into a structured JSON object.

CRITICAL RULES:
1. Extract only what is explicitly stated in the document. Never infer or assume.
2. For any field not found, use exactly: "Not found in document"
3. For boolean fields not found, use false.
4. For list fields not found, use empty array [].
5. Return ONLY valid JSON. No explanation text before or after. No markdown code blocks.
6. Never abbreviate insurer names. Use full legal name as printed.
7. Dates must be in format: DD Month YYYY. Example: 05 February 2026.
8. All money amounts must include Rs prefix and Indian comma formatting. Example: Rs 25,00,000.

DOCUMENT FORMAT NOTES:
This document may be one of three HDFC ERGO formats or any other Indian insurer format:
- Optima Secure newer format uses Section B.1. references
- Optima Secure older format uses B-1.1 references  
- Optima Restore format uses B-1.a references
The Customer Information Sheet / Know Your Policy section is the most reliable source for key fields across all formats.

EXTRACT THESE FIELDS:

Basic identification:
- policyholder_name: Full name of policy owner. May differ from insured person.
- policy_number: Unique policy number as printed.
- insurer_name: Full legal name of insurance company.
- product_name: Name of insurance product. Example: my: Optima Secure
- policy_type: INDIVIDUAL or FLOATER

Dates:
- policy_start_date: Coverage start date.
- policy_end_date: Coverage end date.
- first_inception_date: Date first policy in this continuous chain began. Critical for waiting period calculation.
- policy_issuance_date: Date this document was issued.

Sum insured and premium:
- base_sum_insured: Core coverage amount.
- total_sum_insured: Total coverage including bonuses.
- previous_year_sum_insured: If this is a renewal and previous year SI is mentioned.
- gross_premium: Total premium paid.

Coverage:
- room_rent_limit: Daily room rent limit. Use "At Actuals" if no cap.
- pre_hospitalisation_days: Days covered before admission.
- post_hospitalisation_days: Days covered after discharge.

Waiting periods (CRITICAL - affects claim eligibility):
- waiting_period_initial: Initial waiting period for all illnesses.
- waiting_period_specific_diseases: Waiting period for listed diseases.
- waiting_period_pre_existing: Waiting period for declared pre-existing conditions. Note if tiered.
- moratorium_period: Period after which policy cannot be contested except for fraud.

Critical rider flags (boolean - true only if explicitly confirmed active):
- protector_rider_active: True only if Protector Rider is active with a sum insured value. False if blank, dash, or zero.
- unlimited_restore_active: True if Unlimited Restore Benefit is active.
- co_payment_percentage: Percentage as string. Use "0" if no co-payment.
- aggregate_deductible: Amount as string. Use "0" if no deductible.

People:
- policyholder_is_insured: true if policyholder is also the insured person.
- insured_persons: Array of objects. Each object has: name, member_id, date_of_birth, age, relationship, base_sum_insured, total_sum_insured.

Declared pre-existing conditions (CRITICAL - directly affects claims):
- declared_pre_existing_conditions: Array of objects. Each object has:
  - member_name: Name of insured person
  - condition_name: Condition as printed in exclusions table
  - icd_code: ICD code if listed
  - waiting_period_details: Waiting period for this condition. Note tiered amounts if present.
  - portability_renewal_benefit: Continuity benefit details if present.

Riders and add-ons (flexible - capture everything found):
- riders_and_addons: Array of objects for ALL riders found. Each object has:
  - name: Full rider name as printed
  - sum_insured: Coverage amount or description
  - active: true if active, false if blank or zero
  - uin_number: IRDAI UIN if printed
  - notes: Any additional details

Exclusions (plain English - maximum 5):
- key_exclusions: Array of strings. Plain English only. No legal language.

Endorsements:
- endorsements: Array of objects. Each has: endorsement_number, description, effective_date.

Contact and address:
- policy_address: Address as printed on policy. Determines Ombudsman jurisdiction.
- grievance_email: Grievance email address.
- cgo_email: Chief Grievance Officer email.
- customer_service_number: Customer service number.

Renewal:
- previous_policy_number: Previous policy number if renewal.
- is_renewal: true if this is a renewal.

Confidence:
- extraction_confidence: Your assessment. HIGH if most fields found clearly. MEDIUM if some ambiguity. LOW if document poorly readable.

Return ONLY this JSON structure with no other text:
{
  "policyholder_name": "",
  "policy_number": "",
  "insurer_name": "",
  "product_name": "",
  "policy_type": "",
  "policy_start_date": "",
  "policy_end_date": "",
  "first_inception_date": "",
  "policy_issuance_date": "",
  "base_sum_insured": "",
  "total_sum_insured": "",
  "previous_year_sum_insured": "",
  "gross_premium": "",
  "room_rent_limit": "",
  "pre_hospitalisation_days": "",
  "post_hospitalisation_days": "",
  "waiting_period_initial": "",
  "waiting_period_specific_diseases": "",
  "waiting_period_pre_existing": "",
  "moratorium_period": "",
  "protector_rider_active": false,
  "unlimited_restore_active": false,
  "co_payment_percentage": "0",
  "aggregate_deductible": "0",
  "policyholder_is_insured": true,
  "insured_persons": [],
  "declared_pre_existing_conditions": [],
  "riders_and_addons": [],
  "key_exclusions": [],
  "endorsements": [],
  "policy_address": "",
  "grievance_email": "",
  "cgo_email": "",
  "customer_service_number": "",
  "previous_policy_number": "",
  "is_renewal": false,
  "extraction_confidence": "MEDIUM"
}

POLICY DOCUMENT TEXT:
""" + policy_text
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    response_text = message.content[0].text.strip()

    # Clean response if Claude added markdown despite instructions
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        lines = [l for l in lines if not l.startswith("```")]
        response_text = "\n".join(lines)

    return json.loads(response_text)


# -------------------------------------------------------
# STEP 3: CALCULATE EXTRACTION COMPLETENESS
# -------------------------------------------------------

def calculate_completeness(extracted: dict) -> float:
    """
    Checks how many core fields were successfully found.
    Returns a score between 0.0 and 1.0.

    A field counts as found if it is not:
    - "Not found in document"
    - Empty string
    - None
    """
    found = 0
    for field in CORE_FIELDS:
        value = extracted.get(field, "")
        if value and value != "Not found in document":
            found += 1
    return round(found / len(CORE_FIELDS), 2)


# -------------------------------------------------------
# STEP 4: APPLY HYBRID CONFIDENCE LOGIC
# -------------------------------------------------------

def apply_confidence_logic(extracted: dict, completeness: float) -> tuple[str, str, bool]:
    """
    Combines Claude's self-reported confidence with the
    completeness score to produce a final confidence level.

    Returns:
    - final_confidence: HIGH, MEDIUM, or LOW
    - confidence_statement: Plain English for the user
    - soft_warning: True if LOW confidence

    DOWNGRADE RULES:
    - Claude says HIGH but completeness below 0.7 -> MEDIUM
    - Claude says HIGH but completeness below 0.5 -> LOW
    - Claude says MEDIUM but completeness below 0.4 -> LOW
    - If password_required -> LOW always
    """
    claude_confidence = extracted.get("extraction_confidence", "MEDIUM").upper()

    if completeness >= 0.8 and claude_confidence == "HIGH":
        final = "HIGH"
        statement = "We were able to read your policy clearly. Please review the details below and confirm they look correct."
        warning = False

    elif completeness >= 0.6:
        final = "MEDIUM"
        statement = "We found most of the key details in your policy. A few fields may need your confirmation."
        warning = False

    elif completeness >= 0.4:
        final = "MEDIUM"
        statement = "We found some details in your policy. Please review carefully and correct anything that looks wrong."
        warning = False

    else:
        final = "LOW"
        statement = "We had difficulty reading parts of your policy clearly. Please review all fields carefully before continuing."
        warning = True

    return final, statement, warning


# -------------------------------------------------------
# STEP 5: BUILD FINAL PolicyDocument OBJECT
# -------------------------------------------------------

def build_policy_document(extracted: dict, completeness: float) -> PolicyDocument:
    """
    Takes the raw dictionary from Claude and builds a
    validated PolicyDocument object.

    Pydantic validation happens automatically here.
    Any field with wrong type is caught and defaulted.

    Also applies hybrid confidence logic and builds
    nested objects for pre-existing conditions,
    riders, and insured persons.
    """
    final_confidence, confidence_statement, soft_warning = apply_confidence_logic(
        extracted, completeness
    )

    # Build declared pre-existing conditions list
    ped_list = []
    for ped in extracted.get("declared_pre_existing_conditions", []):
        try:
            ped_list.append(DeclaredPreExistingCondition(**ped))
        except Exception:
            pass

    # Build riders and add-ons list
    riders_list = []
    for rider in extracted.get("riders_and_addons", []):
        try:
            riders_list.append(RiderAddon(**rider))
        except Exception:
            pass

    return PolicyDocument(
        # Identity
        policyholder_name=extracted.get("policyholder_name", "Not found in document"),
        policy_number=extracted.get("policy_number", "Not found in document"),
        insurer_name=extracted.get("insurer_name", "Not found in document"),
        product_name=extracted.get("product_name", "Not found in document"),
        policy_type=extracted.get("policy_type", "Not found in document"),

        # Dates
        policy_start_date=extracted.get("policy_start_date", "Not found in document"),
        policy_end_date=extracted.get("policy_end_date", "Not found in document"),
        first_inception_date=extracted.get("first_inception_date", "Not found in document"),
        policy_issuance_date=extracted.get("policy_issuance_date", "Not found in document"),

        # Sum insured
        base_sum_insured=extracted.get("base_sum_insured", "Not found in document"),
        total_sum_insured=extracted.get("total_sum_insured", "Not found in document"),
        previous_year_sum_insured=extracted.get("previous_year_sum_insured", "Not found in document"),
        gross_premium=extracted.get("gross_premium", "Not found in document"),

        # Coverage
        room_rent_limit=extracted.get("room_rent_limit", "Not found in document"),
        pre_hospitalisation_days=extracted.get("pre_hospitalisation_days", "Not found in document"),
        post_hospitalisation_days=extracted.get("post_hospitalisation_days", "Not found in document"),

        # Waiting periods
        waiting_period_initial=extracted.get("waiting_period_initial", "Not found in document"),
        waiting_period_specific_diseases=extracted.get("waiting_period_specific_diseases", "Not found in document"),
        waiting_period_pre_existing=extracted.get("waiting_period_pre_existing", "Not found in document"),
        moratorium_period=extracted.get("moratorium_period", "Not found in document"),

        # Critical riders
        protector_rider_active=extracted.get("protector_rider_active", False),
        unlimited_restore_active=extracted.get("unlimited_restore_active", False),
        co_payment_percentage=str(extracted.get("co_payment_percentage", "0")),
        aggregate_deductible=str(extracted.get("aggregate_deductible", "0")),

        # People
        insured_persons=extracted.get("insured_persons", []),
        policyholder_is_insured=extracted.get("policyholder_is_insured", True),

        # Pre-existing conditions and riders
        declared_pre_existing_conditions=ped_list,
        riders_and_addons=riders_list,

        # Exclusions and endorsements
        key_exclusions=extracted.get("key_exclusions", []),
        endorsements=extracted.get("endorsements", []),

        # Address and contacts
        policy_address=extracted.get("policy_address", "Not found in document"),
        grievance_email=extracted.get("grievance_email", "Not found in document"),
        cgo_email=extracted.get("cgo_email", "Not found in document"),
        customer_service_number=extracted.get("customer_service_number", "Not found in document"),

        # Renewal
        previous_policy_number=extracted.get("previous_policy_number", "Not found in document"),
        is_renewal=extracted.get("is_renewal", False),

        # Confidence
        extraction_confidence=extracted.get("extraction_confidence", "MEDIUM"),
        extraction_completeness=completeness,
        final_confidence=final_confidence,
        confidence_statement=confidence_statement,
        soft_warning=soft_warning,
    )


# -------------------------------------------------------
# MAIN FUNCTION - called by the /extract-policy endpoint
# -------------------------------------------------------

def extract_policy_document(pdf_path: str) -> dict:
    """
    WHAT THIS FUNCTION DOES:
    Takes a path to a policy PDF.
    Reads it, sends to Claude, builds structured output.
    Returns a dictionary ready to send back to frontend.

    This is the only function main.py needs to call.
    Everything else in this file supports this function.

    INPUT:  Path to a temporary PDF file
    OUTPUT: Dictionary with all extracted policy fields
    """

    # Step 1: Extract text from PDF
    policy_text, password_required = extract_text_from_pdf(pdf_path)

    if password_required:
        doc = PolicyDocument(
            password_required=True,
            final_confidence="LOW",
            confidence_statement="Your policy document appears to be password protected. Please remove the password and upload again.",
            soft_warning=True
        )
        return doc.model_dump()

    if not policy_text or len(policy_text.strip()) < 100:
        doc = PolicyDocument(
            final_confidence="LOW",
            confidence_statement="We were unable to read text from this document. Please ensure you have uploaded a valid policy PDF.",
            soft_warning=True
        )
        return doc.model_dump()

    # Step 2: Call Claude API
    extracted = call_claude_for_policy_extraction(policy_text)

    # Step 3: Calculate completeness
    completeness = calculate_completeness(extracted)

    # Step 4 and 5: Build validated PolicyDocument
    policy_doc = build_policy_document(extracted, completeness)

    return policy_doc.model_dump()