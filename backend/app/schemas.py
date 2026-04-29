# Ezer Schemas - schemas.py
# -------------------------------------------------------
# PURPOSE: Central data structures for the Ezer backend.
# Single source of truth. All extractors import from here.
# -------------------------------------------------------

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class DocumentType(str, Enum):
    ORIGINAL_DENIAL = "ORIGINAL_DENIAL"
    CGO_REJECTION = "CGO_REJECTION"
    EZER_CLAIM_FILE = "EZER_CLAIM_FILE"
    SETTLEMENT_ADVICE = "SETTLEMENT_ADVICE"
    POLICY_DOCUMENT = "POLICY_DOCUMENT"
    UNKNOWN = "UNKNOWN"


class RiderAddon(BaseModel):
    name: str
    sum_insured: Optional[str] = "Not specified"
    active: bool = True
    uin_number: Optional[str] = None
    notes: Optional[str] = None


class DeclaredPreExistingCondition(BaseModel):
    member_name: str
    condition_name: str
    icd_code: Optional[str] = None
    waiting_period_details: Optional[str] = None
    portability_renewal_benefit: Optional[str] = None


class PolicyDocument(BaseModel):
    # Identity
    policyholder_name: str = "Not found in document"
    policy_number: str = "Not found in document"
    insurer_name: str = "Not found in document"
    product_name: str = "Not found in document"
    policy_type: str = "Not found in document"

    # Dates
    policy_start_date: str = "Not found in document"
    policy_end_date: str = "Not found in document"
    first_inception_date: str = "Not found in document"
    policy_issuance_date: str = "Not found in document"

    # Sum insured and premium
    base_sum_insured: str = "Not found in document"
    total_sum_insured: str = "Not found in document"
    previous_year_sum_insured: str = "Not found in document"
    gross_premium: str = "Not found in document"

    # Coverage
    room_rent_limit: str = "Not found in document"
    pre_hospitalisation_days: str = "Not found in document"
    post_hospitalisation_days: str = "Not found in document"

    # Waiting periods
    waiting_period_initial: str = "Not found in document"
    waiting_period_specific_diseases: str = "Not found in document"
    waiting_period_pre_existing: str = "Not found in document"
    moratorium_period: str = "Not found in document"

    # Critical rider flags - explicit because Ezer reasons about these
    protector_rider_active: bool = False
    unlimited_restore_active: bool = False
    one_time_restore_active: bool = False
    co_payment_percentage: str = "0"
    aggregate_deductible: str = "0"

    # People
    insured_persons: List[dict] = []
    policyholder_is_insured: bool = True

    # Pre-existing conditions
    declared_pre_existing_conditions: List[DeclaredPreExistingCondition] = []

    # All riders - flexible open list for future products
    riders_and_addons: List[RiderAddon] = []

    # Exclusions and endorsements
    key_exclusions: List[str] = []
    endorsements: List[dict] = []

    # Address and contacts
    policy_address: str = "Not found in document"
    grievance_email: str = "Not found in document"
    cgo_email: str = "Not found in document"
    customer_service_number: str = "Not found in document"

    # Renewal
    previous_policy_number: str = "Not found in document"
    is_renewal: bool = False

    # Extraction quality
    extraction_confidence: str = "MEDIUM"
    extraction_completeness: float = 0.0
    final_confidence: str = "MEDIUM"
    confidence_statement: str = ""
    soft_warning: bool = False
    password_required: bool = False
    user_confirmed: bool = False
    discrepancy_flagged: bool = False
    discrepancy_description: str = ""


class SettlementLineItem(BaseModel):
    bill_number: str = ""
    service_type: str = ""
    claimed_amount: float = 0.0
    deduction_amount: float = 0.0
    discount_amount: float = 0.0
    settled_amount: float = 0.0
    remarks: str = ""


class SettlementExtraction(BaseModel):
    # Document identification
    claim_reference: str = "Not found in document"
    policy_number: str = "Not found in document"
    hdfc_ergo_id: str = "Not found in document"
    utr_number: str = "Not found in document"
    settlement_date: str = "Not found in document"
    transaction_date: str = "Not found in document"

    # Claim details
    patient_name: str = "Not found in document"
    main_member_name: str = "Not found in document"
    relationship: str = "Not found in document"
    hospital_name: str = "Not found in document"
    ailment: str = "Not found in document"
    hospitalization_from: str = "Not found in document"
    hospitalization_to: str = "Not found in document"
    claim_type: str = "Not found in document"
    payee_name: str = "Not found in document"

    # Financials
    claimed_amount: float = 0.0
    deduction_amount: float = 0.0
    mou_discount: float = 0.0
    settled_amount: float = 0.0
    gst_amount: float = 0.0
    grand_total_paid: float = 0.0

    # Post-settlement balances
    balance_sum_insured: float = 0.0
    balance_cumulative_bonus: float = 0.0
    protector_rider_balance: float = 0.0

    # Flags
    without_prejudice: bool = False
    mou_clause_present: bool = False

    # Consumables - only populated if Protector Rider confirmed
    has_protector_rider: bool = False
    consumables_deducted: List[SettlementLineItem] = []
    consumables_deducted_total: float = 0.0

    # Full line items
    line_items: List[SettlementLineItem] = []

    # Extraction quality
    settlement_extraction_confidence: str = "MEDIUM"
    soft_warning: bool = False