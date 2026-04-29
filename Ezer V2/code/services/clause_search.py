# -----------------------------------------
# CLAUSE SEARCH ENGINE
# -----------------------------------------

def search_relevant_clauses(pages):
    """
    Filters only relevant parts of policy
    """

    keywords = {
        "ped_waiting": ["pre-existing", "ped"],
        "specific_waiting": ["cataract", "knee", "specific disease"],
        "pre_hospitalization": ["pre-hospitalization"],
        "post_hospitalization": ["post-hospitalization"],
        "exclusions": ["not covered", "excluded", "exclusion"]
    }

    results = {}

    for key, words in keywords.items():
        results[key] = []

        for page in pages:
            text = page["text"].lower()

            for word in words:
                if word in text:
                    results[key].append(page)
                    break

    return results