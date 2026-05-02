"""
Ezer V3.2 — Audit Engine
audit_engine.py

Deterministic settlement adjudication engine.
Reads settlement_GPS_main.json, validates schema via Pydantic,
and produces the Total Asymmetry Payload.

Zero LLM calls. Zero inference. Only what the data defines.
"""

import json
import sys
from pathlib import Path
from enum import Enum
from typing import Optional
from pydantic import BaseModel, field_validator, model_validator

# ── Path Setup ─────────────────────────────────────────────────────────────────

# Navigate to the Ezer V3 data folder relative to this engine file
ENGINE_DIR  = Path(__file__).parent                          # engine/
V3_DIR      = ENGINE_DIR.parent                              # Ezer V3/
DATA_DIR    = V3_DIR / "data"
SETTLEMENTS = DATA_DIR / "settlements"

SETTLEMENT_FILE = SETTLEMENTS / "settlement_GPS_main.json"


# ── Custom Exception ────────────────────────────────────────────────────────────

class DataIntegrityError(Exception):
    """Raised when settlement totals do not reconcile within ±₹0.01 tolerance."""
    pass


# ── Enums — Hard Gates ─────────────────────────────────────────────────────────

class EzerClassification(str, Enum):
    """Every line item must be one of these four states. No exceptions."""
    SETTLED          = "SETTLED"
    RIDER_DEPENDENT  = "RIDER_DEPENDENT"
    NON_PAYABLE      = "NON_PAYABLE"
    HOSPITAL_FLAG    = "HOSPITAL_FLAG"


class InsurerAction(str, Enum):
    """What HDFC ERGO actually did with the line item."""
    PAID       = "PAID"
    DEDUCTED   = "DEDUCTED"
    DISCOUNTED = "DISCOUNTED"


class FlagType(str, Enum):
    """Hospital flag sub-type. Only valid for HOSPITAL_FLAG classified items."""
    DUPLICATE_CHARGE  = "DUPLICATE_CHARGE"
    QUANTITY_ANOMALY  = "QUANTITY_ANOMALY"
    DEFINITION_REQUIRED = "DEFINITION_REQUIRED"
    GHOST_CONSULTATION  = "GHOST_CONSULTATION"
    HOSPITAL_FLAG     = "HOSPITAL_FLAG"      # Generic — use specific type where possible


class ContestTarget(str, Enum):
    """Who the user should contest the item with."""
    HOSPITAL = "HOSPITAL"
    INSURER  = "INSURER"


# ── Pydantic Models ─────────────────────────────────────────────────────────────

class LineItem(BaseModel):
    """One row from the settlement letter line_items array."""
    bill_no:            str
    service_type:       str
    item:               str
    claimed_amount:     float
    deduction_amount:   float
    discount:           float
    settled_amount:     float
    insurer_action:     InsurerAction            # Hard enum gate
    ezer_classification: EzerClassification      # Hard enum gate
    flag_type:          Optional[FlagType] = None
    flag_reason:        Optional[str]      = None
    insurer_leakage:    bool
    contestable:        bool
    contest_target:     Optional[ContestTarget] = None
    plain_english:      str
    simulation_mode_recoverable: Optional[bool] = False

    @field_validator("deduction_amount", "settled_amount", "claimed_amount", "discount")
    @classmethod
    def must_be_non_negative(cls, v: float) -> float:
        """Amounts cannot be negative — catch data entry errors."""
        if v < 0:
            raise ValueError(f"Amount cannot be negative: {v}")
        return v


class HospitalFlag(BaseModel):
    """One entry from the hospital_flags array."""
    flag_id:            str
    item:               str
    amount:             float
    insurer_action:     InsurerAction            # Should always be PAID
    ezer_classification: EzerClassification      # Should always be HOSPITAL_FLAG
    flag_type:          FlagType                 # Hard enum gate — specific type required
    flag_reason:        str
    insurer_leakage:    bool                     # Should always be True
    contestable:        bool
    contest_target:     ContestTarget            # Should always be HOSPITAL
    plain_english:      str
    evidence_required:  str

    @field_validator("insurer_leakage")
    @classmethod
    def must_be_leakage(cls, v: bool) -> bool:
        """All hospital flags must be insurer leakage by definition."""
        if not v:
            raise ValueError("Hospital flags must have insurer_leakage: true")
        return v


class ReconciliationTotals(BaseModel):
    """Top-level reconciliation block from the JSON."""
    total_claimed:                      float
    total_deducted_by_insurer:          float
    total_discount_mou:                 float
    total_settled:                      float
    gst:                                float
    grand_total_settled:                float
    rider_dependent_recoverable:        float
    non_payable:                        float
    hospital_flags_paid_without_audit:  float
    total_asymmetry_payload:            float


class SettlementData(BaseModel):
    """Top-level model. Validates entire settlement JSON on load."""
    line_items:             list[LineItem]
    hospital_flags:         list[HospitalFlag]
    reconciliation_totals:  ReconciliationTotals

    @model_validator(mode="after")
    def validate_counts(self) -> "SettlementData":
        """Sanity check — must have at least one line item and one flag."""
        if not self.line_items:
            raise ValueError("Settlement must have at least one line item")
        if not self.hospital_flags:
            raise ValueError("Settlement must have at least one hospital flag")
        return self


# ── Data Loader ─────────────────────────────────────────────────────────────────

def load_settlement(path: Path = SETTLEMENT_FILE) -> SettlementData:
    """
    Load and validate the settlement JSON.
    Pydantic raises ValidationError immediately if any field fails schema.
    """
    if not path.exists():
        raise FileNotFoundError(f"Settlement file not found: {path}")

    raw = json.loads(path.read_text(encoding="utf-8"))

    # Pydantic validates enums, types, and constraints here
    # Any violation raises ValidationError with the exact field and reason
    return SettlementData(**raw)


# ── Function 1: Integrity Check ─────────────────────────────────────────────────

def verify_integrity(data: SettlementData) -> dict:
    """
    Verify that settlement totals reconcile mathematically.
    Uses reconciliation_totals from JSON — avoids GST double-count.

    Formula: total_claimed ≈ total_settled + total_deducted + total_discount

    Tolerance: ±₹0.01 (handles floating point rounding in hospital bills)
    Raises DataIntegrityError if variance exceeds tolerance.
    """
    t = data.reconciliation_totals

    # Expected: claimed = settled + deducted + discount (before GST)
    expected = t.total_settled + t.total_deducted_by_insurer + t.total_discount_mou
    variance = abs(t.total_claimed - expected)

    # GST is added on top — grand total = settled + GST
    gst_check = abs(t.grand_total_settled - (t.total_settled + t.gst))

    if variance > 0.01:
        raise DataIntegrityError(
            f"Settlement totals do not reconcile. "
            f"Expected claimed = ₹{expected:,.2f}, "
            f"Actual claimed = ₹{t.total_claimed:,.2f}, "
            f"Variance = ₹{variance:,.2f}"
        )

    if gst_check > 0.50:  # Settlement letter rounds grand total to nearest rupee
        raise DataIntegrityError(
            f"Grand total GST check failed. "
            f"Expected grand total = ₹{t.total_settled + t.gst:,.2f}, "
            f"Actual = ₹{t.grand_total_settled:,.2f}"
        )

    # Build warnings list — ternary state (Pass / Warning / Fail)
    warnings = []
    if 0.01 < gst_check <= 0.50:
        warnings.append(
            f"GST rounding variance of ₹{gst_check:.4f} detected. "
            f"Within tolerance but flagged for pattern monitoring. "
            f"Hospital may be rounding in their favour."
        )

    return {
        "status":          "VERIFIED",
        "total_claimed":   t.total_claimed,
        "total_settled":   t.total_settled,
        "total_deducted":  t.total_deducted_by_insurer,
        "total_discount":  t.total_discount_mou,
        "gst":             t.gst,
        "grand_total":     t.grand_total_settled,
        "variance":        round(variance, 4),
        "gst_variance":    round(gst_check, 4),
        "warnings":        warnings
    }


# ── Function 2: Asymmetry Aggregator ───────────────────────────────────────────

def calculate_asymmetry(data: SettlementData) -> dict:
    """
    Compute the Total Asymmetry Payload.

    Layer 1 — Invisible Loss:
        Sum of all hospital_flags where insurer_leakage is True.
        These are charges the insurer PAID without auditing.

    Layer 2 — Visible Loss:
        Sum of all line_items where insurer_action is DEDUCTED.
        These are charges the patient KNOWS about.

    Total Asymmetry = Layer 1 + Layer 2
    """
    # Layer 1 — Invisible (hospital paid without audit)
    layer1_flags = [
        {
            "flag_id":     f.flag_id,
            "item":        f.item,
            "amount":      f.amount,
            "flag_type":   f.flag_type.value,
            "contest_target": f.contest_target.value
        }
        for f in data.hospital_flags
        if f.insurer_leakage
    ]
    layer1_total = sum(f["amount"] for f in layer1_flags)

    # Layer 2 — Visible (insurer deductions the patient received)
    layer2_items = [
        {
            "item":                i.item,
            "amount":              i.deduction_amount,
            "ezer_classification": i.ezer_classification.value,
            "contest_target":      i.contest_target.value if i.contest_target else None
        }
        for i in data.line_items
        if i.insurer_action == InsurerAction.DEDUCTED
    ]
    layer2_total = sum(i["amount"] for i in layer2_items)

    total_asymmetry = layer1_total + layer2_total

    return {
        "layer_1_invisible_loss": {
            "label":  "Hospital charges paid by insurer without audit",
            "flags":  layer1_flags,
            "total":  round(layer1_total, 2)
        },
        "layer_2_visible_loss": {
            "label":  "Insurer deductions — patient-facing",
            "items":  layer2_items,
            "total":  round(layer2_total, 2)
        },
        "total_asymmetry_payload": round(total_asymmetry, 2)
    }


# ── Function 3: Rider Simulation ────────────────────────────────────────────────

def simulate_rider_impact(data: SettlementData, status: bool = True) -> dict:
    """
    Simulate what the settlement would have been if the Protector Rider were active.

    status=True  → Rider active: move RIDER_DEPENDENT items from deducted to recovered
    status=False → Actual settlement: return as-is

    Never mutates original data. Works on computed values only.
    """
    if not status:
        # Return actual settlement — no simulation
        return {
            "simulation_active":    False,
            "protector_rider":      "INACTIVE",
            "actual_grand_total":   data.reconciliation_totals.grand_total_settled,
            "recoverable_amount":   0,
            "revised_grand_total":  data.reconciliation_totals.grand_total_settled,
            "message": "Protector Rider is inactive. Settlement as actually received."
        }

    # Find all rider-dependent items
    rider_items = [
        {
            "item":   i.item,
            "amount": i.deduction_amount
        }
        for i in data.line_items
        if i.ezer_classification == EzerClassification.RIDER_DEPENDENT
        and i.insurer_action == InsurerAction.DEDUCTED
    ]
    recoverable = sum(r["amount"] for r in rider_items)

    actual_grand_total  = data.reconciliation_totals.grand_total_settled
    revised_grand_total = actual_grand_total + recoverable

    return {
        "simulation_active":    True,
        "protector_rider":      "SIMULATED ACTIVE",
        "actual_grand_total":   actual_grand_total,
        "recoverable_amount":   round(recoverable, 2),
        "revised_grand_total":  round(revised_grand_total, 2),
        "rider_dependent_items": rider_items,
        "eligibility_note": (
            "Note: Protector Rider availability may be subject to age-based "
            "underwriting (typically 60+). Verify with HDFC ERGO before assuming "
            "this amount is recoverable at renewal."
        ),
        "message": (
            f"If the Protector Rider were active, ₹{recoverable:,.2f} "
            f"would have been paid. Grand total would be ₹{revised_grand_total:,.2f} "
            f"instead of ₹{actual_grand_total:,.2f}."
        )
    }


# ── Function 4: Talking Memo Data Prep ─────────────────────────────────────────

def prepare_talking_memo(data: SettlementData) -> dict:
    """
    Extract plain_english and evidence_required from all hospital flags.
    Returns structured data ready for the Symmetry Report generator.
    PII-free — no patient name or account number in output.
    """
    memo_items = []
    for i, flag in enumerate(data.hospital_flags, 1):
        memo_items.append({
            "flag_number":      i,
            "flag_id":          flag.flag_id,
            "item":             flag.item,
            "amount":           flag.amount,
            "flag_type":        flag.flag_type.value,
            "plain_english":    flag.plain_english,
            "evidence_required": flag.evidence_required,
            "contest_target":   flag.contest_target.value
        })

    total_flags_amount = sum(f.amount for f in data.hospital_flags)

    return {
        "total_flags":        len(memo_items),
        "total_amount":       round(total_flags_amount, 2),
        "claim_reference":    "RR-HS25-15050055",  # Non-PII claim ref only
        "flags":              memo_items
    }


# ── Terminal Output ─────────────────────────────────────────────────────────────

def print_audit_report(
    integrity:  dict,
    asymmetry:  dict,
    simulation: dict,
    memo:       dict,
    item_count: int,
    flag_count: int
) -> None:
    """
    Human-readable terminal output.
    PII GUARDRAIL: patient_name and account_number are never printed.
    """
    W = 70  # Width

    print("\n" + "═" * W)
    print("  EZER AUDIT ENGINE — V3.2")
    print(f"  Claim: {memo['claim_reference']}")
    print("═" * W)

    # Integrity
    print(f"\n  ✅ Data Integrity:      {integrity['status']}")
    print(f"  ✅ Schema Validation:   {item_count} line items, {flag_count} hospital flags — PASSED")
    print(f"     Variance:            ₹{integrity['variance']:.4f}  (tolerance ±₹0.01)")
    print(f"     GST Variance:        ₹{integrity['gst_variance']:.4f}  (tolerance ±₹0.50)")

    # GST warnings — ternary state
    if integrity.get("warnings"):
        for w in integrity["warnings"]:
            print(f"\n  ⚠️  GST WARNING: {w}")

    # Asymmetry
    print(f"\n  {'── ASYMMETRY PAYLOAD ':─<{W-2}}")
    print(f"\n  Layer 1 — Invisible Loss (Hospital Flags):")
    for flag in asymmetry["layer_1_invisible_loss"]["flags"]:
        print(f"    [{flag['flag_type']:<22}]  {flag['item'][:30]:<30}  ₹{flag['amount']:>10,.2f}")
    print(f"  {'':40}  {'─'*12}")
    print(f"  {'Layer 1 Total':>40}   ₹{asymmetry['layer_1_invisible_loss']['total']:>10,.2f}")

    print(f"\n  Layer 2 — Visible Loss (Insurer Deductions):")
    for item in asymmetry["layer_2_visible_loss"]["items"]:
        print(f"    [{item['ezer_classification']:<22}]  {item['item'][:30]:<30}  ₹{item['amount']:>10,.2f}")
    print(f"  {'':40}  {'─'*12}")
    print(f"  {'Layer 2 Total':>40}   ₹{asymmetry['layer_2_visible_loss']['total']:>10,.2f}")

    print(f"\n  {'':40}  {'═'*12}")
    print(f"  {'TOTAL ASYMMETRY PAYLOAD':>40}   ₹{asymmetry['total_asymmetry_payload']:>10,.2f}")

    # Simulation
    print(f"\n  {'── SIMULATION — Protector Rider ACTIVE ':─<{W-2}}")
    print(f"\n  Actual Grand Total:              ₹{simulation['actual_grand_total']:>12,.2f}")
    print(f"  Recoverable (Rider Dependent):   ₹{simulation['recoverable_amount']:>12,.2f}")
    print(f"  Revised Grand Total:             ₹{simulation['revised_grand_total']:>12,.2f}")
    print(f"\n  ⚠️  {simulation['eligibility_note']}")

    # Talking Memo
    print(f"\n  {'── HOSPITAL FLAGS — SYMMETRY REPORT ':─<{W-2}}")
    print(f"\n  {memo['total_flags']} flags prepared  |  Total: ₹{memo['total_amount']:,.2f}")
    print()
    for flag in memo["flags"]:
        print(f"  [{flag['flag_id']}] {flag['item']}")
        print(f"        Amount:   ₹{flag['amount']:,.2f}")
        print(f"        Type:     {flag['flag_type']}")
        print(f"        Plain:    {flag['plain_english'][:80]}...")
        print(f"        Evidence: {flag['evidence_required'][:80]}...")
        print()

    print("═" * W + "\n")


# ── Main ────────────────────────────────────────────────────────────────────────

def run_audit(settlement_path: Path = SETTLEMENT_FILE) -> dict:
    """
    Full audit pipeline. Returns all results as structured dict.
    Call this from API, report generator, or future frontend.
    """
    # Load and validate
    data = load_settlement(settlement_path)

    # Run all four functions
    integrity  = verify_integrity(data)
    asymmetry  = calculate_asymmetry(data)
    simulation = simulate_rider_impact(data, status=True)
    memo       = prepare_talking_memo(data)

    return {
        "integrity":  integrity,
        "asymmetry":  asymmetry,
        "simulation": simulation,
        "memo":       memo
    }


if __name__ == "__main__":
    try:
        # Load and validate
        data = load_settlement()

        # Run pipeline
        integrity  = verify_integrity(data)
        asymmetry  = calculate_asymmetry(data)
        simulation = simulate_rider_impact(data, status=True)
        memo       = prepare_talking_memo(data)

        # Print — PII never touches terminal
        print_audit_report(
            integrity  = integrity,
            asymmetry  = asymmetry,
            simulation = simulation,
            memo       = memo,
            item_count = len(data.line_items),
            flag_count = len(data.hospital_flags)
        )

    except FileNotFoundError as e:
        print(f"\n❌ File Error: {e}")
        sys.exit(1)

    except DataIntegrityError as e:
        print(f"\n❌ Data Integrity Error: {e}")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Validation Error: {e}")
        sys.exit(1)
