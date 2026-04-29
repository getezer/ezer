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
            draft_letter: str = None) -> dict:
    obj = {
        "category":   category,
        "confidence": confidence,
        "title":      title,
        "body":       body
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
            "policy — most buyers don't know they have it."
        ))
    else:
        addon_info = lib.get("restore_benefit", {}).get("unlimited_restore_addon", {})
        insights.append(insight(
            "GAP_FEATURE", VERIFIED,
            "Unlimited Restore is NOT active",
            "Your policy only restores your SI once per year. If you exhaust it twice in "
            "the same year, you are on your own for the second claim. Unlimited Restore "
            "can be added at next renewal — ask your agent for the premium."
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
            "Most policies deduct these from every settlement. Yours does not."
        ))
    else:
        insights.append(insight(
            "GAP_FEATURE", VERIFIED,
            "Protect Benefit has been removed",
            "Annexure B consumables are NOT covered on your policy. You will face deductions "
            "of ₹10,000–30,000 per hospitalisation for gloves, masks, syringes and similar items."
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
            "these — ask your agent to add it at next renewal."
        ))
    else:
        insights.append(insight(
            "ACTIVE_FEATURE", VERIFIED,
            "Protector Rider ACTIVE — consumables covered",
            "Annexure I non-medical items are covered via your Protector Rider. "
            "You will not face consumable deductions at settlement."
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
                f"stones, joint replacement are NOT claimable on this block until then."
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
                f"{expiry}. Any declared PED claim on this block will be denied until then."
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
        insights.append(insight(
            "SCHEDULE_INTEGRITY_ERROR", VERIFIED,
            f"⚠️  Schedule Error Detected [{priority} PRIORITY]",
            f"{desc}\n\n"
            f"Correct structure: {correct}\n\n"
            f"Action required: {action}"
        ))
    return insights


def check_ped_quality(lib: dict, sch: dict) -> list:
    insights = []
    peds = sch.get("declared_peds", [])

    for ped in peds:
        flags = ped.get("ezer_flags", [])
        for flag in flags:
            insights.append(insight(
                "PED_QUALITY_FLAG", EXTRACTED,
                f"⚠️  PED Risk Flag — {ped.get('condition_name', 'Unknown')}",
                flag.get("description", "")
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
                    f"{ped.get('condition_name')} will be denied until then."
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
            f"misrepresentation — except in cases of proven fraud."
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
                f"of claims — this is NOT a no-claim bonus."
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
                f"This effectively doubles your base SI at no extra premium."
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
            "the 180-day window closes."
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
        f"are unaware of this benefit."
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
        if flag.get("priority") in ("HIGH", "MEDIUM"):
            letter = draft_schedule_correction_letter(sch, flag)
            insights.append(insight(
                "ACTION_REQUIRED", VERIFIED,
                "Action Required — Send Schedule Correction Request to HDFC ERGO",
                "A schedule error has been detected that requires a formal written "
                "correction request to HDFC ERGO. A draft letter is provided below — "
                "review, fill in your contact details, and send to care@hdfcergo.com "
                "and grievance@hdfcergo.com. Keep a copy and note the date sent.",
                draft_letter=letter
            ))

    # PED ICD vagueness action letters
    peds = sch.get("declared_peds", [])
    for ped in peds:
        for flag in ped.get("ezer_flags", []):
            if flag.get("flag_type") == "PED_ICD_VAGUENESS":
                letter = draft_ped_clarification_letter(sch, ped)
                insights.append(insight(
                    "ACTION_REQUIRED", EXTRACTED,
                    f"Action Required — Request Written PED Scope Confirmation for "
                    f"'{ped.get('condition_name', '')}'",
                    "The ICD code for this declared PED is vague or a catch-all category. "
                    "At claim time, HDFC ERGO may attempt to argue the specific condition "
                    "is outside the declared PED scope. Obtain written confirmation now, "
                    "before any claim arises. A draft letter is provided below.",
                    draft_letter=letter
                ))

    return insights
    days = sch.get("schedule_of_benefits", {}).get("post_hospitalisation_days", 0)
    if days >= 180:
        return [insight(
            "ACTIVE_FEATURE", VERIFIED,
            "180-Day Post-Hospitalisation Coverage",
            "Post-discharge expenses — follow-up visits, medicines, physiotherapy — "
            "are covered for 180 days from discharge. Industry standard is 60-90 days. "
            "Keep all post-discharge receipts and file one consolidated claim before "
            "the 180-day window closes."
        )]
    return []


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


# ── Printer ───────────────────────────────────────────────────────────────────

def print_insights(schedule: dict, insights: list):
    name = schedule.get("policy_meta", {}).get("insured_name", "Unknown")
    policy = schedule.get("_schema_meta", {}).get("policy_number", "")
    product = schedule.get("_schema_meta", {}).get("product_id", "")

    print("\n" + "=" * 70)
    print(f"  EZER INSIGHTS — {name}")
    print(f"  Policy: {policy}")
    print(f"  Product: {product}")
    print("=" * 70)

    for i, ins in enumerate(insights, 1):
        print(f"\n[{i}] {ins['confidence']}  |  {ins['category']}")
        print(f"    {ins['title']}")
        for line in ins['body'].split('\n'):
            print(f"    {line}")
        if ins.get("draft_letter"):
            print(f"\n    ── DRAFT LETTER ──────────────────────────────────────")
            for line in ins["draft_letter"].split('\n'):
                print(f"    {line}")
            print(f"    ── END DRAFT LETTER ──────────────────────────────────")

    print(f"\n  Total insights: {len(insights)}")
    print("=" * 70 + "\n")


# ── Main ──────────────────────────────────────────────────────────────────────

def run_all():
    schedules = list(SCHEDULE_DIR.glob("*.json"))
    if not schedules:
        print("No user schedules found in data/user_schedules/")
        return

    for path in sorted(schedules):
        schedule = load_json(path)
        try:
            insights = generate_insights(schedule)
            print_insights(schedule, insights)
        except Exception as e:
            name = schedule.get("policy_meta", {}).get("insured_name", str(path))
            print(f"\n❌ Error processing {name}: {e}")


if __name__ == "__main__":
    run_all()
