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


import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv("backend/.env")

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


DENIAL_PATTERNS = {
    "INVESTIGATIVE_PROCEDURE": [
        "investigation",
        "evaluation only",
        "investigative",
        "diagnostic only",
        "evaluation of the ailment"
    ],
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
    "CHANGING_REASONS": [
        "further documents required",
        "additional information",
        "pending documents"
    ],
    "PRE_EXISTING": [
        "pre-existing",
        "pre existing",
        "prior condition",
        "existing condition"
    ]
}


def detect_denial_pattern(rejection_reason: str) -> str:
    rejection_lower = rejection_reason.lower()
    for pattern_name, keywords in DENIAL_PATTERNS.items():
        for keyword in keywords:
            if keyword.lower() in rejection_lower:
                return pattern_name
    return "GENERAL_DENIAL"


def analyse_rejection(extracted_fields: dict) -> dict:
    rejection_reason = extracted_fields.get("REJECTION_REASON", "")
    denial_pattern = detect_denial_pattern(rejection_reason)

    pattern_context = ""

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
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[
            {"role": "user", "content": prompt}
        ],
        extra_headers={
        }
    )
    response_text = message.content[0].text

    analysis = {}
    current_key = None
    current_value = []

    for line in response_text.strip().split('\n'):
        if ': ' in line and line.split(': ')[0].isupper():
            if current_key:
                analysis[current_key] = ' '.join(current_value).strip()
            parts = line.split(': ', 1)
            current_key = parts[0]
            current_value = [parts[1]] if len(parts) > 1 else []
        elif current_key:
            current_value.append(line)

    if current_key:
        analysis[current_key] = ' '.join(current_value).strip()

    analysis["DENIAL_PATTERN"] = denial_pattern

    return analysis