# -----------------------------------------
# POLICY EXTRACTOR (FINAL STABLE VERSION)
# -----------------------------------------

import json
import os
from dotenv import load_dotenv
from openai import OpenAI


# -----------------------------------------
# LOAD ENV VARIABLES
# -----------------------------------------

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")


# -----------------------------------------
# SAFE CLIENT INIT
# -----------------------------------------

client = None

if API_KEY:
    client = OpenAI(api_key=API_KEY)
else:
    print("⚠️ WARNING: OPENAI_API_KEY not found. Running in fallback mode.")


# -----------------------------------------
# LLM CALL
# -----------------------------------------

def call_llm(text):

    if client is None:
        # graceful fallback (no crash)
        return None

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
You are an insurance policy analyzer.

Extract ONLY the following fields in STRICT JSON:

{
  "ped_waiting": { "value": "", "page": 0, "quote": "" },
  "specific_waiting": { "value": "", "page": 0, "quote": "" },
  "pre_hospitalization": { "value": "", "page": 0, "quote": "" },
  "post_hospitalization": { "value": "", "page": 0, "quote": "" },
  "exclusions": [
    { "item": "", "page": 0, "quote": "" }
  ]
}

Rules:
- Output ONLY JSON (no explanation, no markdown)
- If not found → return null values
- Keep quotes EXACT from document
"""
                },
                {
                    "role": "user",
                    "content": text[:15000]
                }
            ],
            temperature=0
        )

        return response

    except Exception as e:
        print("LLM CALL ERROR:", str(e))
        return None


# -----------------------------------------
# MAIN EXTRACTION FUNCTION
# -----------------------------------------

def extract_policy_data(pages):

    try:
        # -----------------------------------------
        # VALIDATE INPUT
        # -----------------------------------------

        if not isinstance(pages, list):
            return {}

        full_text = "\n".join(
            [p.get("text", "") for p in pages if isinstance(p, dict)]
        )

        if not full_text.strip():
            return {}

        # -----------------------------------------
        # CALL MODEL
        # -----------------------------------------

        response = call_llm(full_text)

        if response is None:
            return {}

        # -----------------------------------------
        # SAFE PARSE RESPONSE
        # -----------------------------------------

        try:
            content = response.choices[0].message.content
        except Exception:
            return {}

        if not isinstance(content, str):
            return {}

        content = content.strip()

        # -----------------------------------------
        # CLEAN MARKDOWN
        # -----------------------------------------

        if content.startswith("```"):
            content = content.replace("```json", "").replace("```", "").strip()

        # -----------------------------------------
        # PARSE JSON
        # -----------------------------------------

        try:
            data = json.loads(content)
        except Exception:
            print("JSON PARSE ERROR:", content)
            return {}

        if not isinstance(data, dict):
            return {}

        # -----------------------------------------
        # STRUCTURE SAFETY
        # -----------------------------------------

        safe_data = {
            "ped_waiting": data.get("ped_waiting") or {},
            "specific_waiting": data.get("specific_waiting") or {},
            "pre_hospitalization": data.get("pre_hospitalization") or {},
            "post_hospitalization": data.get("post_hospitalization") or {},
            "exclusions": data.get("exclusions") or []
        }

        return safe_data

    except Exception as e:
        print("EXTRACTOR ERROR:", str(e))
        return {}