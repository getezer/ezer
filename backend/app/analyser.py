# Ezer Rejection Analyser - analyser.py
# -------------------------------------------------------
# PURPOSE: This is Ezer's legal intelligence layer.
# Once the extractor has pulled out the rejection reason,
# this file analyses it and tells the policyholder:
# 1. What the insurer is actually claiming in plain English
# 2. Whether the claim is likely contestable
# 3. What specific legal grounds exist to challenge it
# 4. What pattern of denial this represents
#
# This is what transforms Ezer from a PDF reader into
# an escalation engine. The extractor reads. The analyser thinks.
# -------------------------------------------------------


# IMPORT STATEMENTS

import os
# os is Python's built-in tool for reading environment variables
# We use it to access the ANTHROPIC_API_KEY

from anthropic import Anthropic
# The official Anthropic Python library
# This is how we send messages to Claude and receive responses

from dotenv import load_dotenv
# load_dotenv reads our .env file and loads the API key into memory
# Must be called before we create the Anthropic client


# -------------------------------------------------------
# ENVIRONMENT SETUP
# -------------------------------------------------------

load_dotenv("backend/.env")
# Load the .env file so ANTHROPIC_API_KEY is available
# We do this here too because analyser.py may run independently


# -------------------------------------------------------
# CLIENT SETUP
# -------------------------------------------------------

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
# Create our connection to Claude AI
# os.getenv reads ANTHROPIC_API_KEY from memory
# This client is used every time we want to analyse a rejection reason


# -------------------------------------------------------
# DENIAL PATTERN DEFINITIONS
# These are the known patterns from the Ezer PRD
# Each pattern has a name and keywords to detect it
# -------------------------------------------------------

DENIAL_PATTERNS = {
    # Pattern H5 from PRD - Investigative Procedure Trap
    # Insurer claims the procedure was just an investigation
    # not actual treatment - even when it was a prerequisite
    "INVESTIGATIVE_PROCEDURE": [
        "investigation",
        "evaluation only",
        "investigative",
        "diagnostic only",
        "evaluation of the ailment"
    ],

    # Pattern H1/H2 - Medical Necessity Denial
    # Insurer claims the hospitalisation was not medically necessary
    # without any clinical basis for this claim
    "MEDICAL_NECESSITY": [
    "indication cannot be established",
    "not medically necessary",
    "indication for hospitalization cannot be established",
    "indication for the hospitalization cannot be established",
    "medical necessity not established",
    "medically necessary",
    "clinical necessity",
    "necessity not established",
    "cannot be established"
],

    # Pattern H4 - Changing Denial Reasons
    # Insurer gives different reasons across multiple rejections
    # This is a strong ground for escalation
    "CHANGING_REASONS": [
        "further documents required",
        "additional information",
        "pending documents"
    ],

    # Pattern H3 - Pre-existing Disease Exclusion
    # Insurer claims the condition existed before the policy started
    "PRE_EXISTING": [
        "pre-existing",
        "pre existing",
        "prior condition",
        "existing condition"
    ]
}


# -------------------------------------------------------
# FUNCTION 1: detect_denial_pattern
# -------------------------------------------------------

def detect_denial_pattern(rejection_reason: str) -> str:
    """
    WHAT THIS FUNCTION DOES:
    Looks at the rejection reason text and identifies which
    known denial pattern it matches from our PRD definitions above.

    ANALOGY:
    Think of this like a doctor looking at symptoms and saying
    "this looks like pattern X". We look at the rejection reason
    and match it to known insurer tactics.

    INPUT:
    rejection_reason = the exact rejection reason text from the denial letter
    Example: "patient is being admitted primarily for investigation and evaluation"

    OUTPUT:
    Returns the name of the pattern detected as a string
    Example: "INVESTIGATIVE_PROCEDURE"
    Or returns "GENERAL_DENIAL" if no specific pattern is matched
    """

    # Convert to lowercase for easier matching
    # "Investigation" and "investigation" should both match
    rejection_lower = rejection_reason.lower()
    # .lower() converts all letters to lowercase
    # This makes our keyword matching case-insensitive

    # Go through each pattern and its keywords
    for pattern_name, keywords in DENIAL_PATTERNS.items():
        # pattern_name = "INVESTIGATIVE_PROCEDURE" etc
        # keywords = the list of trigger words for that pattern
        # .items() gives us both the name and the list together

        for keyword in keywords:
            # Check each keyword one by one
            if keyword.lower() in rejection_lower:
                # If this keyword appears in the rejection reason
                # we have found our pattern
                return pattern_name
                # Return immediately with the pattern name

    # If no pattern matched, return a general category
    return "GENERAL_DENIAL"


# -------------------------------------------------------
# FUNCTION 2: analyse_rejection
# -------------------------------------------------------

def analyse_rejection(extracted_fields: dict) -> dict:
    """
    WHAT THIS FUNCTION DOES:
    Takes the extracted fields from the denial letter and
    sends them to Claude for deep analysis.
    Claude explains what the insurer is claiming, assesses
    contestability, and generates legally grounded language.

    ANALOGY:
    This is like handing your denial letter to a legal expert
    who reads it and tells you exactly what your rights are
    and how strong your case is.

    INPUT:
    extracted_fields = the dictionary returned by our extractor
    Contains: INSURER, CCN, REJECTION_REASON, DATE, HOSPITAL etc

    OUTPUT:
    Returns a dictionary with:
    - plain_english_explanation: what the insurer is actually saying
    - denial_pattern: which known tactic this is
    - contestability: HIGH, MEDIUM, LOW, or CANNOT ASSESS
    - contestation_language: the specific legal language to use
    - next_step: what the policyholder should do next
    """

    # First detect the pattern using our function above
    rejection_reason = extracted_fields.get("REJECTION_REASON", "")
    # .get() safely retrieves a value from a dictionary
    # If REJECTION_REASON does not exist, it returns empty string ""

    denial_pattern = detect_denial_pattern(rejection_reason)
    # Call Function 1 to identify which pattern this is

    # Build special context based on the pattern detected
    # This gives Claude extra guidance for specific patterns
    pattern_context = ""
    # We start with empty context and add to it based on pattern

    if denial_pattern == "INVESTIGATIVE_PROCEDURE":
        pattern_context = """
        IMPORTANT: This is the Investigative Procedure Trap.
        The insurer has labelled a mandatory clinical prerequisite
        as "investigation only". This is one of the most common
        and most contestable denial patterns in Indian health insurance.
        The key legal argument is: if the investigation was a mandatory
        prerequisite for the main treatment, it cannot be classified
        as investigation only. The treating doctor's clinical judgement
        must be given primacy over a desk review.
        """
        # This extra context helps Claude give more specific advice
        # for this particular denial pattern

    elif denial_pattern == "MEDICAL_NECESSITY":
        pattern_context = """
        IMPORTANT: This is a Medical Necessity denial.
        The insurer is claiming the hospitalisation was not necessary
        without any clinical staff having examined the patient.
        This is a desk review overriding a treating specialist's judgement.
        Under IRDAI guidelines, the treating doctor's assessment carries
        significant weight. A desk review cannot override clinical judgement
        without specific documented medical grounds.
        """

    # Build the main prompt for Claude
    prompt = f"""
You are Ezer, an AI-powered insurance escalation engine for policyholders in India.
Your role is to help policyholders understand their denial letters and fight back
with legally grounded escalation.

You are analysing a cashless health insurance denial letter with these details:

Insurer: {extracted_fields.get('INSURER', 'NOT FOUND')}
Policy Number: {extracted_fields.get('POLICY_NUMBER', 'NOT FOUND')}
CCN: {extracted_fields.get('CCN', 'NOT FOUND')}
Date of Denial: {extracted_fields.get('DATE', 'NOT FOUND')}
Hospital: {extracted_fields.get('HOSPITAL', 'NOT FOUND')}
Patient: {extracted_fields.get('PATIENT', 'NOT FOUND')}
Denial Type: {extracted_fields.get('DENIAL_TYPE', 'NOT FOUND')}
Rejection Reason: {rejection_reason}

{pattern_context}

Do not use markdown formatting, headers, or ** bold text. Use plain text only.
Please provide your analysis in this exact format:

PLAIN_ENGLISH: [Explain in 2-3 simple sentences what the insurer is actually 
claiming. Use language a non-lawyer can understand. No jargon.]

CONTESTABILITY: [Write exactly one of these: HIGH or MEDIUM or LOW or CANNOT ASSESS]

CONTESTABILITY_REASON: [In 2-3 sentences, explain why this claim is or is not 
contestable. Reference IRDAI guidelines or Insurance Ombudsman principles where relevant.]

CONTESTATION_LANGUAGE: [Write the specific legal language the policyholder should 
use in their CGO complaint letter. This should be firm, factual, and reference 
the policyholder's rights under IRDAI regulations.]

STRUCTURAL_IMPACT: [Explain if this denial affects any other claims or procedures. 
For cashless denials, mention that this may block supplementary claims.]

NEXT_STEP: [Tell the policyholder exactly what to do next. Be specific.]

IMPORTANT RULES:
- Ezer NEVER says a claim is invalid
- Ezer NEVER discourages escalation
- Ezer ALWAYS uses MAY not WILL when assessing outcomes
- Ezer speaks with empathy - the user is in distress
"""

        # Send to Claude for analysis
        message = client.messages.create(
            model="claude-sonnet-4-6",
            # Using Claude Sonnet - fast and accurate for this task
            max_tokens=1500,
            # We allow more tokens here because the analysis response
            # needs to be detailed and thorough
            messages=[
                {"role": "user", "content": prompt}
                # Send our prompt as a user message to Claude
            ],
            extra_headers={
                "anthropic-beta": "zero-data-retention-2025-02-19"
                # Zero Data Retention — Anthropic will not store this call
            }
        )
    # Get Claude's response text
    response_text = message.content[0].text
    # message.content[0].text extracts the actual text from Claude's response
# TEMPORARY DEBUG LINE
# This prints Claude's raw response to Terminal
# so we can see exactly what format it is returning
# We will remove this after we fix the parser

    # Parse Claude's structured response into a dictionary
    analysis = {}
    # Start with empty dictionary

    # Split response into lines and process each one
    current_key = None
    # We track which field we are currently reading
    current_value = []
    # We collect the value lines here

    for line in response_text.strip().split('\n'):
        # Go through each line of Claude's response

        if ': ' in line and line.split(': ')[0].isupper():
            # This detects lines like "PLAIN_ENGLISH: some text"
            # .isupper() checks if the key part is all uppercase
            # This helps us identify field names vs regular text

            if current_key:
                # Save the previous field before starting a new one
                analysis[current_key] = ' '.join(current_value).strip()

            # Start a new field
            parts = line.split(': ', 1)
            # Split at the first ': ' only
            current_key = parts[0]
            # The field name e.g. "PLAIN_ENGLISH"
            current_value = [parts[1]] if len(parts) > 1 else []
            # The value e.g. "The insurer is claiming..."

        elif current_key:
            # This is a continuation line of the current field
            current_value.append(line)
            # Add it to the current value

    # Save the last field
    if current_key:
        analysis[current_key] = ' '.join(current_value).strip()

    # Add the detected pattern to the analysis
    analysis["DENIAL_PATTERN"] = denial_pattern
    # This tells us which of our known patterns was detected

    return analysis
    # Return the complete analysis dictionary