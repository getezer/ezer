# -----------------------------------------
# PROOF LAYER (SAFE)
# -----------------------------------------

def build_proof(data):

    if not isinstance(data, dict):
        data = {}

    proof = {}

    def safe_get(obj, key):
        return obj.get(key) if isinstance(obj, dict) else None

    # PED
    ped = safe_get(data, "ped_waiting")

    if isinstance(ped, dict):
        value = str(safe_get(ped, "value") or "").lower()
        quote = str(safe_get(ped, "quote") or "").lower()

        proof["ped_waiting"] = {
            "value": safe_get(ped, "value"),
            "page": safe_get(ped, "page"),
            "quote": safe_get(ped, "quote"),
            "match": value in quote if value and quote else False
        }

    # Specific
    specific = safe_get(data, "specific_waiting")

    if isinstance(specific, dict):
        value = str(safe_get(specific, "value") or "").lower()
        quote = str(safe_get(specific, "quote") or "").lower()

        proof["specific_waiting"] = {
            "value": safe_get(specific, "value"),
            "page": safe_get(specific, "page"),
            "quote": safe_get(specific, "quote"),
            "match": value in quote if value and quote else False
        }

    return proof