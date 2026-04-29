# -----------------------------------------
# HUMAN EXPLANATION (FINAL TRUST-AWARE)
# -----------------------------------------

def is_noise(quote):
    if not quote:
        return True
    if len(quote.split()) <= 2:
        return True
    if sum(c.isdigit() for c in quote) > len(quote) * 0.5:
        return True
    return False


def explain_policy(data):

    if not isinstance(data, dict):
        data = {}

    result = {
        "key_risks": [],
        "needs_verification": []
    }

    def safe_get(obj, key):
        return obj.get(key) if isinstance(obj, dict) else None

    # -----------------------------------------
    # PED WAITING
    # -----------------------------------------

    ped = safe_get(data, "ped_waiting")

    if isinstance(ped, dict) and safe_get(ped, "value"):

        value = safe_get(ped, "value")
        quote = str(safe_get(ped, "quote") or "")

        if is_noise(quote):
            result["needs_verification"].append(
                "Pre-existing disease waiting clause is unclear. Verify from policy document."
            )
        else:
            result["key_risks"].append(
                f"If you had any illness before buying the policy, you may need to wait {value} before it is covered."
            )

    # -----------------------------------------
    # SPECIFIC WAITING
    # -----------------------------------------

    specific = safe_get(data, "specific_waiting")

    if isinstance(specific, dict) and safe_get(specific, "value"):

        value = safe_get(specific, "value")
        quote = str(safe_get(specific, "quote") or "")

        if is_noise(quote):
            result["needs_verification"].append(
                "Specific treatment waiting clause is unclear. Verify from policy document."
            )
        else:
            result["key_risks"].append(
                f"Some treatments may not be covered for {value}."
            )

    else:
        result["needs_verification"].append(
            "Waiting period for specific treatments is not clearly identified."
        )

    # -----------------------------------------
    # CLEAN OUTPUT
    # -----------------------------------------

    if not result["needs_verification"]:
        result.pop("needs_verification")

    return result