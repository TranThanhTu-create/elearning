"""
Pydantic schemas cho Affiliate.
"""

from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class AffiliateStats(BaseModel):
    """Stats cho /dashboard → tab Affiliate."""
    ref_code: str
    ref_link: str                        # https://eduvietpro.vn?ref=XXXXX
    total_clicks: int = 0
    total_clicks_fmt: str = "0"          # "1.234"
    total_orders: int = 0
    total_commission: float = 0
    total_commission_fmt: str = "0 ₫"
    paid_commission: float = 0
    paid_commission_fmt: str = "0 ₫"
    pending_commission: float = 0
    pending_commission_fmt: str = "0 ₫"
    conversion_rate_fmt: str = "0%"      # clicks → orders


class AffiliateOrderItem(BaseModel):
    id: UUID
    order_code: str
    course_title: str
    order_amount: float
    order_amount_fmt: str
    commission_amount: float
    commission_amount_fmt: str
    status: str             # "pending" | "approved" | "paid" | "rejected"
    status_label: str
    created_at: str

    model_config = {"from_attributes": True}


class WithdrawalRequest(BaseModel):
    amount: float    = Field(..., gt=0, description="Số tiền muốn rút (VND)")
    bank_name: str   = Field(..., min_length=2, max_length=100)
    bank_account: str = Field(..., min_length=6, max_length=50)
    account_name: str = Field(..., min_length=2, max_length=100)
    note: Optional[str] = Field(None, max_length=500)


class WithdrawalItem(BaseModel):
    id: UUID
    amount: float
    amount_fmt: str
    bank_name: str
    bank_account: str
    account_name: str
    status: str         # "pending" | "approved" | "paid" | "rejected"
    status_label: str
    note: Optional[str] = None
    admin_note: Optional[str] = None
    created_at: str
    processed_at: Optional[str] = None

    model_config = {"from_attributes": True}


# ── Admin ─────────────────────────────────────────────────

class AdminAffiliateItem(BaseModel):
    user_id: UUID
    user_name: str
    user_email: str
    ref_code: str
    total_clicks: int
    total_clicks_fmt: str
    total_orders: int
    total_commission: float
    total_commission_fmt: str
    pending_commission: float
    pending_commission_fmt: str
    status: str    # "active" | "suspended"
    joined_at: str

    model_config = {"from_attributes": True}


class AdminWithdrawalItem(WithdrawalItem):
    user_id: UUID
    user_name: str
    user_email: str


class AdminWithdrawalUpdateRequest(BaseModel):
    status: str        = Field(..., pattern="^(approved|paid|rejected)$")
    admin_note: Optional[str] = None
