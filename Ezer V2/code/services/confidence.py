def compute_confidence(field):
    """
    Simple rule-based confidence scoring
    """

    if not field or not field.get("value"):
        return 0.0

    score = 0.5  # base

    # Strong quote increases confidence
    quote = field.get("quote", "")
    if len(quote.split()) >= 8:
        score += 0.2

    # Page reference exists
    if field.get("page"):
        score += 0.1

    # Penalize vague values
    value = field.get("value", "").lower()
    if "about" in value or "approx" in value:
        score -= 0.2

    # Penalize known bad pattern (like your 2-year issue)
    if "2 year" in value:
        score -= 0.2

    return max(0.0, min(score, 1.0))


def add_confidence(data):
    """
    Adds confidence score to each field
    """

    for key, field in data.items():

        if isinstance(field, dict):
            field["confidence"] = compute_confidence(field)

    return data


def summarize_confidence(data):

    scores = []
    low_fields = []

    for key, field in data.items():
        if isinstance(field, dict) and "confidence" in field:
            scores.append(field["confidence"])

            if field["confidence"] < 0.6:
                low_fields.append(key)

    overall = sum(scores) / len(scores) if scores else 0

    return {
        "overall": round(overall, 2),
        "low_confidence_fields": low_fields
    }