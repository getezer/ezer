"""
Ezer V3 — Insight Engine
Joins Tier 1 (Product Library) + Tier 2 (User Schedule)
Produces plain-language insights with confidence provenance tags.

Usage:
    python engine/insight_engine.py
"""

import json
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ── Confidence Tags ────────────────────────────────────────────────────────────
VERIFIED     = "🟢 VERIFIED"
EXTRACTED    = "🟡 EXTRACTED"
EXPERIMENTAL = "🔴 EXPERIMENTAL"

# ── Paths ──────────────────────────────────────────────────────────────────────
_SCRIPT_DIR  = Path(__file__).resolve().parent
# Support both: run from engine/ subfolder (production) or root (testing)
BASE_DIR     = _SCRIPT_DIR.parent if _SCRIPT_DIR.name == "engine" else _SCRIPT_DIR
LIBRARY_DIR  = BASE_DIR / "data" / "product_library"
SCHEDULE_DIR = BASE_DIR / "data" / "user_schedules"


# ── Loaders ───────────────────────────────────────────────────────────────────
def load_json(path: Path) -> dict:
    with open(path, "r") as f:
        return json.load(f)

def load_product_library(product_id: str) -> dict:
    for f in LIBRARY_DIR.glob("*.json"):
        data = load_json(f)
        if data.get("_schema_meta", {}).get("product_id") == product_id:
            return data
    raise FileNotFoundError(f"No product library found for product_id: {product_id}")

def load_user_schedule(policy_number: str) -> dict:
    for f in SCHEDULE_DIR.glob("*.json"):
        data = load_json(f)
        if data.get("_schema_meta", {}).get("policy_number") == policy_number:
            return data
    raise FileNotFoundError(f"No user schedule found for policy_number: {policy_number}")


# ── Insight Object ─────────────────────────────────────────────────────────────
def insight(category: str, confidence: str, title: str, body: str,
            type: str = "INFO", priority: str = "LOW",
            suggested_action: str = "",
            draft_letter: str = None) -> dict:
    obj = {
        "category":         category,
        "confidence":       confidence,
        "type":             type,
        "priority":         priority,
        "title":            title,
        "body":             body,
        "suggested_action": suggested_action
    }
    if draft_letter:
        obj["draft_letter"] = draft_letter
    return obj


# ── Insight Generators ─────────────────────────────────────────────────────────

def check_unlimited_restore(lib: dict, sch: dict) -> list:
    insights = []
    active = sch.get("addons", {}).get("unlimited_restore_active") or \
             sch.get("addons_active", {}).get("unlimited_restore", False)

    if active:
        insights.append(insight(
            "ACTIVE_FEATURE", VERIFIED,
            "Unlimited Restore is ACTIVE",
            "Your sum insured is restored 100% unlimited times in a policy year whenever "
            "it is partially or fully exhausted. This is the most valuable feature on this "
            "policy — most buyers don't know they have it.",
            type="INFO", priority="LOW"
        ))
    else:
        addon_info = lib.get("restore_benefit", {}).get("unlimited_restore_addon", {})
        insights.append(insight(
            "GAP_FEATURE", VERIFIED,
            "Unlimited Restore is NOT active",
            "Your policy only restores your SI once per year. If you exhaust it twice in "
            "the same year, you are on your own for the second claim. Unlimited Restore "
            "can be added at next renewal — ask your agent for the premium.",
            type="WARNING", priority="MEDIUM",
            suggested_action="Add Unlimited Restore at next renewal to protect against multiple claims in the same year."
        ))
    return insights


def check_protect_benefit(lib: dict, sch: dict) -> list:
    insights = []
    # Optima Secure only
    product_id = sch.get("_schema_meta", {}).get("product_id", "")
    if "OPTIMA_SECURE" not in product_id:
        return []

    active = sch.get("addons", {}).get("protect_benefit_active", True)
    if active:
        insights.append(insight(
            "ACTIVE_FEATURE", VERIFIED,
            "Protect Benefit is ACTIVE — consumables covered",
            "Non-medical consumables — gloves, masks, syringes, PPE, attendant charges, "
            "diapers and 60+ other Annexure B items — are covered by default on your policy. "
            "Most policies deduct these from every settlement. Yours does not.",
            type="INFO", priority="LOW"
        ))
    else:
        insights.append(insight(
            "GAP_FEATURE", VERIFIED,
            "Protect Benefit has been removed",
            "Annexure B consumables are NOT covered on your policy. You will face deductions "
            "of ₹10,000–30,000 per hospitalisation for gloves, masks, syringes and similar items.",
            type="WARNING", priority="MEDIUM",
            suggested_action="Reinstate Protect Benefit at next renewal to cover consumable deductions."
        ))
    return insights


def check_consumables_optima_restore(lib: dict, sch: dict) -> list:
    insights = []
    product_id = sch.get("_schema_meta", {}).get("product_id", "")
    if "OPTIMA_RESTORE" not in product_id:
        return []

    protector = sch.get("addons_active", {}).get("protector_rider", False)
    if not protector:
        insights.append(insight(
            "GAP_FEATURE", VERIFIED,
            "Consumables NOT covered — Protector Rider absent",
            "Optima Restore excludes 68 non-medical items (Annexure I) — gloves, masks, "
            "syringes, PPE, attendant charges and more. Without the Protector Rider, expect "
            "₹10,000–30,000 in deductions per hospitalisation. The Protector Rider covers "
            "these — ask your agent to add it at next renewal.",
            type="WARNING", priority="MEDIUM",
            suggested_action="Add Protector Rider at renewal to cover consumables. Check premium impact with your insurer."
        ))
    else:
        insights.append(insight(
            "ACTIVE_FEATURE", VERIFIED,
            "Protector Rider ACTIVE — consumables covered",
            "Annexure I non-medical items are covered via your Protector Rider. "
            "You will not face consumable deductions at settlement.",
            type="INFO", priority="LOW"
        ))
    return insights


def check_waiting_periods(lib: dict, sch: dict) -> list:
    insights = []
    blocks = sch.get("waiting_periods", {}).get("si_blocks", [])

    for block in blocks:
        si = block.get("si_inr", 0)
        si_label = f"₹{si // 100000}L"
        block_id = block.get("block_id", "")

        # Specific disease waiting
        spec = block.get("specific_disease_24_month_waiting", {})
        if spec.get("status") == "running":
            remaining = spec.get("remaining_months") or spec.get("remaining_months_approximate", "?")
            expiry = spec.get("approximate_expiry", "unknown date")
            insights.append(insight(
                "WAITING_PERIOD", VERIFIED,
                f"Specific Disease Waiting Running — {si_label} block",
                f"For the {si_label} SI block, a 24-month specific disease waiting period "
                f"is still running. Approximately {remaining} months remaining — expires "
                f"around {expiry}. Conditions like cataract, hernia, gallbladder, kidney "
                f"stones, joint replacement are NOT claimable on this block until then.",
                type="WARNING", priority="HIGH",
                suggested_action=f"Avoid elective procedures covered under specific disease waiting on this block until {expiry}."
            ))

        # PED waiting
        ped = block.get("ped_36_month_waiting", {})
        if ped.get("status") == "running":
            remaining = ped.get("remaining_months") or ped.get("remaining_months_approximate", "?")
            expiry = ped.get("approximate_expiry", "unknown date")
            insights.append(insight(
                "WAITING_PERIOD", VERIFIED,
                f"PED Waiting Running — {si_label} block",
                f"Pre-existing disease waiting period is still running on the {si_label} "
                f"block. Approximately {remaining} months remaining — expires around "
                f"{expiry}. Any declared PED claim on this block will be denied until then.",
                type="WARNING", priority="HIGH",
                suggested_action=f"Do not file PED-related claims on this block until {expiry}."
            ))

    return insights


def check_schedule_integrity(lib: dict, sch: dict) -> list:
    insights = []
    flags = sch.get("waiting_periods", {}).get("schedule_integrity_flags", [])

    for flag in flags:
        priority = flag.get("priority", "MEDIUM")
        desc = flag.get("description", "")
        correct = flag.get("correct_structure", "")
        action = flag.get("recommended_action", "")
        status = flag.get("status", "OPEN")
        if status == "RESOLVED":
            continue
        insights.append(insight(
            "SCHEDULE_INTEGRITY_ERROR", VERIFIED,
            f"⚠️  Schedule Error Detected [{priority} PRIORITY]",
            f"{desc}\n\n"
            f"Correct structure: {correct}\n\n"
            f"Action required: {action}",
            type="WARNING", priority="HIGH",
            suggested_action="Send schedule correction request to HDFC ERGO grievance team."
        ))
    return insights


def check_ped_quality(lib: dict, sch: dict) -> list:
    insights = []
    peds = sch.get("declared_peds", [])

    for ped in peds:
        flags = ped.get("ezer_flags", [])
        for flag in flags:
            if flag.get("status") == "RESOLVED":
                continue
            insights.append(insight(
                "PED_QUALITY_FLAG", EXTRACTED,
                f"⚠️  PED Risk Flag — {ped.get('condition_name', 'Unknown')}",
                flag.get("description", ""),
                type="WARNING", priority="HIGH",
                suggested_action="Obtain written confirmation of PED scope from insurer before any claim arises."
            ))

        # Check coverage status per block
        wp_by_block = ped.get("waiting_period_by_block", {})
        for block_id, block_info in wp_by_block.items():
            if not block_info.get("currently_covered", True):
                remaining = block_info.get("remaining_months_approximate", "?")
                expiry = block_info.get("approximate_expiry", "unknown")
                insights.append(insight(
                    "PED_WAITING", VERIFIED,
                    f"PED Not Yet Covered — {ped.get('condition_name')} on {block_id}",
                    f"{ped.get('condition_name')} is NOT claimable on the {block_id} "
                    f"SI block for approximately {remaining} more months "
                    f"(until ~{expiry}). Claims on this block related to "
                    f"{ped.get('condition_name')} will be denied until then.",
                    type="WARNING", priority="HIGH"
                ))

    return insights


def check_moratorium(lib: dict, sch: dict) -> list:
    insights = []
    months = sch.get("policy_meta", {}).get("months_continuous_coverage", 0)
    moratorium_months = lib.get("moratorium_period", {}).get("months", 60)

    if months >= moratorium_months:
        insights.append(insight(
            "LEGAL_PROTECTION", VERIFIED,
            "Moratorium Protection ACTIVE",
            f"You have {months} months of continuous coverage. The moratorium period "
            f"({moratorium_months} months) has been crossed. HDFC ERGO cannot contest "
            f"your policy or deny any claim on grounds of non-disclosure or "
            f"misrepresentation — except in cases of proven fraud.",
            type="INFO", priority="LOW"
        ))
    return insights


def check_plus_benefit(lib: dict, sch: dict) -> list:
    insights = []
    product_id = sch.get("_schema_meta", {}).get("product_id", "")

    if "OPTIMA_SECURE" in product_id:
        plus = sch.get("sum_insured", {})
        status = plus.get("plus_benefit_status", "")
        plus_si = plus.get("plus_benefit_si_inr", 0)
        if status == "fully_accrued":
            insights.append(insight(
                "ACTIVE_FEATURE", VERIFIED,
                "Plus Benefit Fully Accrued",
                f"Your Plus Benefit of ₹{plus_si // 100000}L is fully accrued and locked in. "
                f"This grows your SI by 100% at no extra premium. It accrues irrespective "
                f"of claims — this is NOT a no-claim bonus.",
                type="INFO", priority="LOW"
            ))

    if "OPTIMA_RESTORE" in product_id:
        multiplier = sch.get("sum_insured", {})
        status = multiplier.get("multiplier_benefit_status", "")
        m_si = multiplier.get("multiplier_benefit_si_inr", 0)
        if status == "fully_accrued":
            insights.append(insight(
                "ACTIVE_FEATURE", VERIFIED,
                "Multiplier Benefit Fully Accrued",
                f"Your Multiplier Benefit of ₹{m_si // 100000}L is fully accrued. "
                f"This effectively doubles your base SI at no extra premium.",
                type="INFO", priority="LOW"
            ))
    return insights


def check_post_hospitalisation(lib: dict, sch: dict) -> list:
    days = sch.get("schedule_of_benefits", {}).get("post_hospitalisation_days", 0)
    if days >= 180:
        return [insight(
            "ACTIVE_FEATURE", VERIFIED,
            "180-Day Post-Hospitalisation Coverage",
            "Post-discharge expenses — follow-up visits, medicines, physiotherapy — "
            "are covered for 180 days from discharge. Industry standard is 60-90 days. "
            "Keep all post-discharge receipts and file one consolidated claim before "
            "the 180-day window closes.",
            type="INFO", priority="LOW"
        )]
    return []


def check_secure_benefit(lib: dict, sch: dict) -> list:
    product_id = sch.get("_schema_meta", {}).get("product_id", "")
    if "OPTIMA_SECURE" not in product_id:
        return []
    secure_si = sch.get("sum_insured", {}).get("secure_benefit_si_inr", 0)
    if not secure_si:
        return []
    base_si = sch.get("sum_insured", {}).get("base_si_inr", 0)
    plus_si = sch.get("sum_insured", {}).get("plus_benefit_si_inr", 0)
    total = base_si + plus_si + secure_si
    return [insight(
        "ACTIVE_FEATURE", VERIFIED,
        f"Secure Benefit — Additional ₹{secure_si // 100000}L SI Pool ACTIVE",
        f"On top of your Base SI (₹{base_si // 100000}L) and Plus Benefit "
        f"(₹{plus_si // 100000}L), you have an additional Secure Benefit pool of "
        f"₹{secure_si // 100000}L. Your real coverage ceiling before Restore even "
        f"triggers is ₹{total // 100000}L. This is unique to Optima Secure — "
        f"Optima Restore does not have an equivalent. Most buyers and even some agents "
        f"are unaware of this benefit.",
        type="INFO", priority="LOW"
    )]


def draft_schedule_correction_letter(sch: dict, flag: dict) -> str:
    name = sch.get("policy_meta", {}).get("insured_name", "Insured")
    policy = sch.get("_schema_meta", {}).get("policy_number", "")
    desc = flag.get("description", "")
    correct = flag.get("correct_structure", "")
    return (
        f"To,\n"
        f"The Grievance Officer\n"
        f"HDFC ERGO General Insurance Company Limited\n"
        f"Customer Happiness Center, D-301, 3rd Floor,\n"
        f"Eastern Business District, LBS Marg,\n"
        f"Bhandup (West), Mumbai - 400 078\n\n"
        f"Email: grievance@hdfcergo.com | care@hdfcergo.com\n\n"
        f"Subject: Policy No. {policy} — Discrepancy in Exclusion/Waiting Period "
        f"Table Requiring Urgent Correction | {name}\n\n"
        f"Dear Team,\n\n"
        f"I write with reference to the above policy issued in favour of {name}.\n\n"
        f"On careful review of the issued policy schedule, I have identified a "
        f"discrepancy in the exclusion/waiting period table that requires immediate "
        f"correction:\n\n"
        f"ISSUE IDENTIFIED:\n"
        f"{desc}\n\n"
        f"CORRECT STRUCTURE SHOULD BE:\n"
        f"{correct}\n\n"
        f"I request you to:\n"
        f"1. Acknowledge this communication within 7 working days\n"
        f"2. Issue a corrected policy schedule within 15 working days\n"
        f"3. Confirm in writing that the corrected schedule accurately reflects "
        f"the actual SI enhancement history\n\n"
        f"Please note that failure to correct this error may result in disputes "
        f"at claim time, which I wish to avoid by resolving this proactively.\n\n"
        f"If this matter is not resolved within the timelines above, I reserve the "
        f"right to escalate to the Insurance Ombudsman, Bhubaneswar and file a "
        f"complaint on IRDAI IGMS portal.\n\n"
        f"Yours faithfully,\n"
        f"[Policyholder Name]\n"
        f"Policy No: {policy}\n"
        f"Contact: [Phone] | [Email]"
    )


def draft_ped_clarification_letter(sch: dict, ped: dict) -> str:
    name = sch.get("policy_meta", {}).get("insured_name", "Insured")
    policy = sch.get("_schema_meta", {}).get("policy_number", "")
    condition = ped.get("condition_name", "")
    icd = ped.get("icd_code") or ped.get("icd_codes", [{}])[0].get("code", "unspecified")
    return (
        f"To,\n"
        f"The Grievance Officer\n"
        f"HDFC ERGO General Insurance Company Limited\n"
        f"Customer Happiness Center, D-301, 3rd Floor,\n"
        f"Eastern Business District, LBS Marg,\n"
        f"Bhandup (West), Mumbai - 400 078\n\n"
        f"Email: grievance@hdfcergo.com | care@hdfcergo.com\n\n"
        f"Subject: Policy No. {policy} — Written Confirmation Requested for "
        f"Declared PED Scope | {name}\n\n"
        f"Dear Team,\n\n"
        f"I write with reference to the above policy issued in favour of {name}, "
        f"wherein '{condition}' has been declared and accepted as a Pre-Existing Disease.\n\n"
        f"I have noted that the ICD-10 code assigned to this condition is listed as "
        f"'{icd}', which is a broad/catch-all category. In order to ensure clarity "
        f"at the time of any future claim, I request your written confirmation of "
        f"the following:\n\n"
        f"1. The exact scope of conditions covered under the declared PED "
        f"'{condition}'\n"
        f"2. Whether all conditions medically arising from or related to "
        f"'{condition}' will be treated as covered under the declared PED\n"
        f"3. The specific ICD-10 codes, if any, that have been recorded against "
        f"this PED in your underwriting system\n\n"
        f"This confirmation is sought proactively to avoid any disputes at claim "
        f"time regarding the scope of coverage.\n\n"
        f"I request you to:\n"
        f"1. Acknowledge this communication within 7 working days\n"
        f"2. Provide written confirmation within 15 working days\n\n"
        f"If this matter is not resolved within the timelines above, I reserve the "
        f"right to escalate to the Insurance Ombudsman, Bhubaneswar and file a "
        f"complaint on IRDAI IGMS portal.\n\n"
        f"Yours faithfully,\n"
        f"[Policyholder Name]\n"
        f"Policy No: {policy}\n"
        f"Contact: [Phone] | [Email]"
    )


def check_action_outputs(lib: dict, sch: dict) -> list:
    insights = []

    # Schedule integrity action letters
    flags = sch.get("waiting_periods", {}).get("schedule_integrity_flags", [])
    for flag in flags:
        if flag.get("status") == "RESOLVED":
            continue
        if flag.get("priority") in ("HIGH", "MEDIUM"):
            letter = draft_schedule_correction_letter(sch, flag)
            insights.append(insight(
                "ACTION_REQUIRED", VERIFIED,
                "Action Required — Send Schedule Correction Request to HDFC ERGO",
                "A schedule error has been detected that requires a formal written "
                "correction request to HDFC ERGO. A draft letter is provided below — "
                "review, fill in your contact details, and send to care@hdfcergo.com "
                "and grievance@hdfcergo.com. Keep a copy and note the date sent.",
                type="ACTION", priority="HIGH",
                draft_letter=letter
            ))

    # PED ICD vagueness action letters
    peds = sch.get("declared_peds", [])
    for ped in peds:
        for flag in ped.get("ezer_flags", []):
            if flag.get("flag_type") == "PED_ICD_VAGUENESS" and flag.get("status") != "RESOLVED":
                letter = draft_ped_clarification_letter(sch, ped)
                insights.append(insight(
                    "ACTION_REQUIRED", EXTRACTED,
                    f"Action Required — Request Written PED Scope Confirmation for "
                    f"'{ped.get('condition_name', '')}'",
                    "The ICD code for this declared PED is vague or a catch-all category. "
                    "At claim time, HDFC ERGO may attempt to argue the specific condition "
                    "is outside the declared PED scope. Obtain written confirmation now, "
                    "before any claim arises. A draft letter is provided below.",
                    type="ACTION", priority="HIGH",
                    draft_letter=letter
                ))

    return insights


# ── Policy Evolution Timeline ──────────────────────────────────────────────────

# Tier 1 plain-English names for specific disease conditions
SPECIFIC_DISEASE_PLAIN = (
    "Cataract, Hernia, Gallbladder stones, Kidney stones, "
    "Joint replacement, Piles surgery, Prostate surgery, Sinusitis, "
    "Tonsillitis, Varicose veins and other listed conditions"
)

def _parse_expiry(expiry_str: str):
    """Parse approximate_expiry string to datetime. Returns None if unparseable."""
    if not expiry_str or expiry_str in ("unknown date", "unknown"):
        return None
    for fmt in ("%B %Y", "%b %Y", "%Y-%m-%d", "%Y-%m"):
        try:
            return datetime.strptime(expiry_str.strip(), fmt)
        except ValueError:
            continue
    return None


def generate_evolution_timeline(schedule: dict) -> list:
    """
    Scan all waiting period blocks for future expiry dates.
    Group by date. Sort chronologically using datetime objects.
    Returns list of milestone dicts. Empty list if no future milestones.
    """
    milestones = defaultdict(list)
    blocks = schedule.get("waiting_periods", {}).get("si_blocks", [])
    peds = schedule.get("declared_peds", [])
    now = datetime.now()

    for block in blocks:
        si = block.get("si_inr", 0)
        si_label = f"₹{si // 100000}L"
        block_id = block.get("block_id", "")

        # Specific disease expiry
        spec = block.get("specific_disease_24_month_waiting", {})
        if spec.get("status") == "running":
            expiry_str = spec.get("approximate_expiry", "")
            dt = _parse_expiry(expiry_str)
            if dt and dt > now:
                milestones[dt].append(
                    f"{si_label} block ({block_id}) — Specific disease waiting expires. "
                    f"{SPECIFIC_DISEASE_PLAIN} become claimable on this block."
                )

        # PED expiry — cross-reference with declared PEDs
        ped_wp = block.get("ped_36_month_waiting", {})
        if ped_wp.get("status") == "running":
            expiry_str = ped_wp.get("approximate_expiry", "")
            dt = _parse_expiry(expiry_str)
            if dt and dt > now:
                # Find which PEDs are affected
                affected_peds = []
                for ped in peds:
                    wp_by_block = ped.get("waiting_period_by_block", {})
                    for bid, binfo in wp_by_block.items():
                        if not binfo.get("currently_covered", True):
                            affected_peds.append(ped.get("condition_name", "Declared PED"))
                ped_names = ", ".join(affected_peds) if affected_peds else "Declared PED(s)"
                milestones[dt].append(
                    f"{si_label} block ({block_id}) — PED waiting expires. "
                    f"{ped_names} become(s) fully claimable on this block."
                )

    # Sort by datetime, return as list
    sorted_milestones = []
    for dt in sorted(milestones.keys()):
        sorted_milestones.append({
            "date": dt.strftime("%B %Y"),
            "events": milestones[dt]
        })

    return sorted_milestones


# ── Renewal Guidance ───────────────────────────────────────────────────────────

def generate_renewal_guidance(lib: dict, sch: dict) -> list:
    """
    Compare Tier 1 optional addons against Tier 2 active addons.
    Generate qualitative renewal recommendations for inactive features.
    """
    guidance = []
    product_id = sch.get("_schema_meta", {}).get("product_id", "")
    addons = sch.get("addons", sch.get("addons_active", {}))

    # Unlimited Restore — available on both products, check if inactive
    ur_active = addons.get("unlimited_restore_active") or addons.get("unlimited_restore", False)
    if not ur_active:
        guidance.append(
            "Consider adding Unlimited Restore at renewal to protect against multiple "
            "hospitalisations in the same year. Without it, once your SI and base restore "
            "are exhausted, no further claims are payable. Check premium impact with your insurer."
        )

    # Protector Rider — Optima Restore only
    if "OPTIMA_RESTORE" in product_id:
        protector = addons.get("protector_rider", False)
        if not protector:
            guidance.append(
                "Consider adding the Protector Rider at renewal to cover consumables "
                "(gloves, masks, syringes, PPE, attendant charges and 60+ Annexure I items). "
                "Without it, expect ₹10,000–30,000 in deductions per hospitalisation. "
                "Check premium impact with your insurer."
            )

    return guidance


# ── Master Engine ──────────────────────────────────────────────────────────────

def generate_insights(schedule: dict) -> list:
    product_id = schedule.get("_schema_meta", {}).get("product_library_ref", "")
    # Derive product_id from ref filename
    pid = schedule.get("_schema_meta", {}).get("product_id", "")
    library = load_product_library(pid)

    all_insights = []
    all_insights += check_unlimited_restore(library, schedule)
    all_insights += check_protect_benefit(library, schedule)
    all_insights += check_consumables_optima_restore(library, schedule)
    all_insights += check_secure_benefit(library, schedule)
    all_insights += check_plus_benefit(library, schedule)
    all_insights += check_post_hospitalisation(library, schedule)
    all_insights += check_moratorium(library, schedule)
    all_insights += check_waiting_periods(library, schedule)
    all_insights += check_ped_quality(library, schedule)
    all_insights += check_schedule_integrity(library, schedule)
    all_insights += check_action_outputs(library, schedule)

    return all_insights


# ── Presentation Helpers ──────────────────────────────────────────────────────

PRIORITY_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}

def derive_action_instruction(title: str, priority: str) -> str:
    """Convert insight title into a short imperative instruction."""
    # Strip ACTION prefix
    instruction = title.replace("Action Required — ", "").strip()
    # For WARNING insights that aren't actions, prefix with advisory verb
    if not instruction[0].isupper() or instruction == title:
        instruction = "Review: " + instruction
    # Add 'today' for HIGH priority actions
    if priority == "HIGH" and not instruction.startswith("Review"):
        if not instruction.endswith("today"):
            instruction += " today"
    return instruction


def compute_summary(insights: list) -> dict:
    actions   = [i for i in insights if i["type"] == "ACTION"]
    warnings  = [i for i in insights if i["type"] == "WARNING"]
    high_warn = [i for i in warnings if i["priority"] == "HIGH"]
    info      = [i for i in insights if i["type"] == "INFO"]

    # Strength
    if len(actions) >= 1:
        strength = "WEAK"
    elif len(high_warn) >= 1:
        strength = "MODERATE"
    else:
        strength = "STRONG"

    # Next Best Action
    next_action = None
    if actions:
        top = sorted(actions, key=lambda x: PRIORITY_ORDER.get(x["priority"], 9))[0]
        next_action = derive_action_instruction(top["title"], top["priority"])
    elif warnings:
        high_warnings = [w for w in warnings if w["priority"] == "HIGH"]
        if high_warnings:
            top = sorted(high_warnings, key=lambda x: PRIORITY_ORDER.get(x["priority"], 9))[0]
            # Use suggested_action if available, otherwise fall back to Be aware prefix
            if top.get("suggested_action"):
                next_action = top["suggested_action"]
            else:
                next_action = "Be aware: " + top["title"]

    return {
        "strength":    strength,
        "action_count": len(actions),
        "warning_count": len(warnings),
        "info_count":   len(info),
        "total":        len(insights),
        "next_action":  next_action
    }


def print_summary_block(schedule: dict, summary: dict):
    name    = schedule.get("policy_meta", {}).get("insured_name", "Unknown")
    policy  = schedule.get("_schema_meta", {}).get("policy_number", "")
    product = schedule.get("_schema_meta", {}).get("product_id", "")

    strength_icon = {"STRONG": "🟢", "MODERATE": "🟡", "WEAK": "🔴"}.get(summary["strength"], "⚪")

    print("\n" + "=" * 70)
    print(f"  EZER POLICY REPORT — {name}")
    print(f"  Policy: {policy}  |  Product: {product}")
    print("=" * 70)
    print(f"\n  {strength_icon} Policy Strength: {summary['strength']}")
    print(f"  Actions Required: {summary['action_count']}  |  "
          f"Risks Identified: {summary['warning_count']}  |  "
          f"Total Insights: {summary['total']}")
    if summary["next_action"]:
        print(f"\n  ➡  Next Best Action: {summary['next_action']}")
    print()


def print_insight(idx: int, ins: dict):
    print(f"  [{idx}] {ins['confidence']} | {ins['type']} | {ins['priority']} | {ins['category']}")
    print(f"      {ins['title']}")
    for line in ins["body"].split("\n"):
        print(f"      {line}")
    if ins.get("draft_letter"):
        print(f"\n      ── DRAFT LETTER ──────────────────────────────────────")
        for line in ins["draft_letter"].split("\n"):
            print(f"      {line}")
        print(f"      ── END DRAFT LETTER ──────────────────────────────────")


def print_insights(schedule: dict, insights: list, timeline: list, renewal: list):
    summary = compute_summary(insights)
    print_summary_block(schedule, summary)

    # Group
    actions  = sorted([i for i in insights if i["type"] == "ACTION"],
                      key=lambda x: PRIORITY_ORDER.get(x["priority"], 9))
    warnings = sorted([i for i in insights if i["type"] == "WARNING"],
                      key=lambda x: PRIORITY_ORDER.get(x["priority"], 9))
    info     = sorted([i for i in insights if i["type"] == "INFO"],
                      key=lambda x: PRIORITY_ORDER.get(x["priority"], 9))

    idx = 1

    if actions:
        print("  ── IMMEDIATE ACTIONS " + "─" * 49)
        for ins in actions:
            print()
            print_insight(idx, ins)
            idx += 1

    if warnings:
        print("\n  ── RISKS & WARNINGS " + "─" * 50)
        for ins in warnings:
            print()
            print_insight(idx, ins)
            idx += 1

    if info:
        print("\n  ── COVERAGE & BENEFITS " + "─" * 47)
        for ins in info:
            print()
            print_insight(idx, ins)
            idx += 1

    # Renewal Guidance
    if renewal:
        print("\n  ── RENEWAL GUIDANCE " + "─" * 50)
        for i, item in enumerate(renewal, 1):
            print(f"\n  [R{i}] {item}")

    # Policy Evolution Timeline — omit entirely if empty
    if timeline:
        print("\n  ── POLICY EVOLUTION TIMELINE " + "─" * 41)
        for milestone in timeline:
            print(f"\n  📅 {milestone['date']}")
            for event in milestone["events"]:
                print(f"      → {event}")

    print("\n" + "=" * 70 + "\n")


# ── Main ──────────────────────────────────────────────────────────────────────

def run_all():
    schedules = list(SCHEDULE_DIR.glob("*.json"))
    if not schedules:
        print("No user schedules found in data/user_schedules/")
        return

    for path in sorted(schedules):
        schedule = load_json(path)
        try:
            pid = schedule.get("_schema_meta", {}).get("product_id", "")
            library = load_product_library(pid)
            insights = generate_insights(schedule)
            timeline = generate_evolution_timeline(schedule)
            renewal  = generate_renewal_guidance(library, schedule)
            print_insights(schedule, insights, timeline, renewal)
        except Exception as e:
            name = schedule.get("policy_meta", {}).get("insured_name", str(path))
            print(f"\n❌ Error processing {name}: {e}")


if __name__ == "__main__":
    run_all()
