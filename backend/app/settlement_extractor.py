# Ezer Settlement Extractor - settlement_extractor.py
# -------------------------------------------------------
# PURPOSE: Extracts structured data from insurance
# settlement letters and payment advice documents.
#
# When a user uploads a settlement letter on Screen 4,
# this file reads it and returns all key fields including
# financial summary, deductions, and flags.
#
# SAFETY GUARDRAILS (from Settlement Auditor Supplement V3):
# - No financial conclusions on LOW confidence
# - Consumables only flagged if Protector Rider confirmed
# - All amounts shown as approximate
# - No guaranteed recovery statements
#
# PRIVACY: API retention is 7 days by default.
# Data is never used for model training.
# -------------------------------------------------------

import os
import json
import anthropic
import pdfplumber

from backend.app.schemas import (
    SettlementExtraction,
    SettlementLineItem
)


# -------------------------------------------------------
# STEP 1: EXTRACT TEXT FROM PDF
# -------------------------------------------------------

def extract_text_from_settlement_pdf(pdf_path: str) -> tuple[str, bool]:
    """
    Reads a settlement letter PDF and returns all text.

    Settlement letters have two sections:
    - Page 1: Header with claim details in label-value format
    - Page 2: Breakdown table with line items
    - Page 3: Post-settlement balances

    We extract all pages as text. The table on page 2
    may not extract perfectly as structured data - this
    is why we have the confidence field.

    Returns:
    - text: full extracted text
    - password_required: True if PDF was locked
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

def call_claude_for_settlement_extraction(settlement_text: str) -> dict:
    """
    Sends settlement letter text to Claude API.
    Returns a dictionary of extracted fields.

    PROMPT DESIGN:
    Built around the real HDFC ERGO settlement letter format
    we have read. The letter has three distinct sections:
    1. Claim header with patient and hospital details
    2. Line item breakdown table
    3. Post-settlement balance summary

    Claude extracts all three sections into structured JSON.
    """

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    prompt = """You are a precise insurance document reader for Ezer, an AI-powered insurance escalation engine for Indian policyholders.

You will read an insurance settlement letter or payment advice document and extract specific fields into a structured JSON object.

CRITICAL RULES:
1. Extract only what is explicitly stated. Never infer or assume.
2. For any field not found, use exactly: "Not found in document"
3. For boolean fields not found, use false.
4. For numeric fields not found, use 0.0.
5. For list fields not found, use empty array [].
6. Return ONLY valid JSON. No explanation. No markdown.
7. All money amounts must be numbers only - no Rs prefix, no commas. Example: 463900.0
8. Dates in format: DD Month YYYY. Example: 12 August 2025.

DOCUMENT STRUCTURE:
Settlement letters typically have:
- Page 1: Claim reference, policy number, UTR number, settlement amount, patient details
- Page 2: Line item table with columns: Bill No, Service Type, Claimed Amount, Deduction Amount, Discount, Settled Amount, Remarks
- Page 3: Post-settlement balances including Balance Sum Insured, Cumulative Bonus, Protector Rider balance

WITHOUT PREJUDICE FLAG:
If the document title or header contains "Without Prejudice", set without_prejudice to true.
This means the insurer paid but did not admit liability. The policyholder retains the right to contest.

MOU CLAUSE FLAG:
If the document mentions "MOU" or "Memorandum of Understanding" in relation to tariff or discount rates, set mou_clause_present to true.

PROTECTOR RIDER:
Set has_protector_rider to true ONLY if the Protector Rider balance shown is greater than 0.
If Protector Rider balance is 0, set has_protector_rider to false.
Never assume the rider is active.

LINE ITEMS:
Extract every row from the breakdown table as a line item object.
Each line item has: bill_number, service_type, claimed_amount, deduction_amount, discount_amount, settled_amount, remarks.
All amounts as numbers. Example: 960.0 not "Rs 960".

EXTRACT THESE FIELDS:

{
  "claim_reference": "",
  "policy_number": "",
  "hdfc_ergo_id": "",
  "utr_number": "",
  "settlement_date": "",
  "transaction_date": "",
  "patient_name": "",
  "main_member_name": "",
  "relationship": "",
  "hospital_name": "",
  "ailment": "",
  "hospitalization_from": "",
  "hospitalization_to": "",
  "claim_type": "",
  "payee_name": "",
  "claimed_amount": 0.0,
  "deduction_amount": 0.0,
  "mou_discount": 0.0,
  "settled_amount": 0.0,
  "gst_amount": 0.0,
  "grand_total_paid": 0.0,
  "balance_sum_insured": 0.0,
  "balance_cumulative_bonus": 0.0,
  "protector_rider_balance": 0.0,
  "without_prejudice": false,
  "mou_clause_present": false,
  "has_protector_rider": false,
  "line_items": [],
  "settlement_extraction_confidence": "MEDIUM"
}

For each line item in line_items array:
{
  "bill_number": "",
  "service_type": "",
  "claimed_amount": 0.0,
  "deduction_amount": 0.0,
  "discount_amount": 0.0,
  "settled_amount": 0.0,
  "remarks": ""
}

SETTLEMENT DOCUMENT TEXT:
""" + settlement_text

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    response_text = message.content[0].text.strip()

    if response_text.startswith("```"):
        lines = response_text.split("\n")
        lines = [l for l in lines if not l.startswith("```")]
        response_text = "\n".join(lines)

    return json.loads(response_text)


# -------------------------------------------------------
# STEP 3: IDENTIFY CONSUMABLE DEDUCTIONS
# Only called when has_protector_rider is True
# -------------------------------------------------------

CONSUMABLE_KEYWORDS = [
    "gloves", "cotton", "gauze", "drape", "sheet",
    "blade", "clipper", "syringe", "needle", "pad",
    "under pad", "urine bag", "urine pot", "bandage",
    "cannula", "catheter", "mask", "cap", "shoe cover",
    "apron", "gown", "examination gloves", "surgical",
    "ward material", "consumable"
]


def identify_consumables(line_items: list) -> tuple[list, float]:
    """
    From the full list of line items, finds items that
    appear to be consumables that may be covered under
    the Protector Rider.

    Only called when has_protector_rider is True.

    Returns:
    - consumable_items: list of SettlementLineItem
    - total: sum of deducted consumable amounts
    """
    consumables = []
    total = 0.0

    for item in line_items:
        remarks = item.get("remarks", "").lower()
        service_type = item.get("service_type", "").lower()
        deduction = item.get("deduction_amount", 0.0)

        if deduction > 0:
            for keyword in CONSUMABLE_KEYWORDS:
                if keyword in remarks or keyword in service_type:
                    consumables.append(item)
                    total += deduction
                    break

    return consumables, round(total, 2)


# -------------------------------------------------------
# STEP 4: BUILD FINAL SettlementExtraction OBJECT
# -------------------------------------------------------

def build_settlement_extraction(extracted: dict) -> SettlementExtraction:
    """
    Takes the raw dictionary from Claude and builds a
    validated SettlementExtraction object.

    Applies safety guardrails:
    - Consumables only populated if has_protector_rider True
    - soft_warning True if confidence is LOW or MEDIUM
    """

    # Build line items list
    line_items_list = []
    for item in extracted.get("line_items", []):
        try:
            line_items_list.append(SettlementLineItem(**item))
        except Exception:
            pass

    # Only identify consumables if Protector Rider confirmed
    has_rider = extracted.get("has_protector_rider", False)
    consumables_list = []
    consumables_total = 0.0

    if has_rider:
        raw_consumables, consumables_total = identify_consumables(
            extracted.get("line_items", [])
        )
        for item in raw_consumables:
            try:
                consumables_list.append(SettlementLineItem(**item))
            except Exception:
                pass

    # Determine soft warning
    confidence = extracted.get("settlement_extraction_confidence", "MEDIUM").upper()
    soft_warning = confidence in ["LOW", "MEDIUM"]

    return SettlementExtraction(
        claim_reference=extracted.get("claim_reference", "Not found in document"),
        policy_number=extracted.get("policy_number", "Not found in document"),
        hdfc_ergo_id=extracted.get("hdfc_ergo_id", "Not found in document"),
        utr_number=extracted.get("utr_number", "Not found in document"),
        settlement_date=extracted.get("settlement_date", "Not found in document"),
        transaction_date=extracted.get("transaction_date", "Not found in document"),
        patient_name=extracted.get("patient_name", "Not found in document"),
        main_member_name=extracted.get("main_member_name", "Not found in document"),
        relationship=extracted.get("relationship", "Not found in document"),
        hospital_name=extracted.get("hospital_name", "Not found in document"),
        ailment=extracted.get("ailment", "Not found in document"),
        hospitalization_from=extracted.get("hospitalization_from", "Not found in document"),
        hospitalization_to=extracted.get("hospitalization_to", "Not found in document"),
        claim_type=extracted.get("claim_type", "Not found in document"),
        payee_name=extracted.get("payee_name", "Not found in document"),
        claimed_amount=float(extracted.get("claimed_amount", 0.0)),
        deduction_amount=float(extracted.get("deduction_amount", 0.0)),
        mou_discount=float(extracted.get("mou_discount", 0.0)),
        settled_amount=float(extracted.get("settled_amount", 0.0)),
        gst_amount=float(extracted.get("gst_amount", 0.0)),
        grand_total_paid=float(extracted.get("grand_total_paid", 0.0)),
        balance_sum_insured=float(extracted.get("balance_sum_insured", 0.0)),
        balance_cumulative_bonus=float(extracted.get("balance_cumulative_bonus", 0.0)),
        protector_rider_balance=float(extracted.get("protector_rider_balance", 0.0)),
        without_prejudice=extracted.get("without_prejudice", False),
        mou_clause_present=extracted.get("mou_clause_present", False),
        has_protector_rider=has_rider,
        consumables_deducted=consumables_list,
        consumables_deducted_total=consumables_total,
        line_items=line_items_list,
        settlement_extraction_confidence=confidence,
        soft_warning=soft_warning,
    )


# -------------------------------------------------------
# MAIN FUNCTION - called by /extract-settlement endpoint
# -------------------------------------------------------

def extract_settlement_document(pdf_path: str) -> dict:
    """
    WHAT THIS FUNCTION DOES:
    Takes a path to a settlement letter PDF.
    Reads it, sends to Claude, builds structured output.
    Returns a dictionary ready to send back to frontend.

    This is the only function main.py needs to call.

    INPUT:  Path to a temporary PDF file
    OUTPUT: Dictionary with all extracted settlement fields
    """

    # Step 1: Extract text
    settlement_text, password_required = extract_text_from_settlement_pdf(pdf_path)

    if password_required:
        doc = SettlementExtraction(
            settlement_extraction_confidence="LOW",
            soft_warning=True
        )
        return doc.model_dump()

    if not settlement_text or len(settlement_text.strip()) < 50:
        doc = SettlementExtraction(
            settlement_extraction_confidence="LOW",
            soft_warning=True
        )
        return doc.model_dump()

    # Step 2: Call Claude
    extracted = call_claude_for_settlement_extraction(settlement_text)

    # Step 3: Build validated object
    settlement = build_settlement_extraction(extracted)

    return settlement.model_dump()