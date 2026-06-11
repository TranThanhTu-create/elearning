"""
Pydantic schemas cho Order, Coupon, Payment.
"""

from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


# ── Coupon ────────────────────────────────────────────────

class CouponCheckRequest(BaseModel):
    code: str     = Field(..., min_length=1, max_length=50)
    course_id: UUID

    @classmethod
    def __get_validators__(cls):
        yield cls


class CouponCheckResponse(BaseModel):
    valid: bool
    message: str
    discount_type: Optional[str] = None   # "percent" | "fixed"
    discount_value: Optional[float] = None
    discount_amount: Optional[float] = None  # số tiền giảm thực tế
    discount_amount_fmt: Optional[str] = None  # "298.000 ₫"
    final_price: Optional[float] = None
    final_price_fmt: Optional[str] = None


class CouponCreateRequest(BaseModel):
    code: str              = Field(..., min_length=3, max_length=50)
    discount_type: str     = Field(..., pattern="^(percent|fixed)$")
    discount_value: float  = Field(..., gt=0)
    applies_to: str        = Field("all", description="all | course_id")
    course_id: Optional[UUID] = None
    max_uses: Optional[int] = Field(None, ge=1)
    max_uses_per_user: int = Field(0, ge=0)   # 0 = không giới hạn
    expires_at: Optional[str] = None
    min_order_amount: float = 0
    is_active: bool = True


class CouponUpdateRequest(BaseModel):
    discount_type: Optional[str]    = None
    discount_value: Optional[float] = None
    max_uses: Optional[int]         = None
    max_uses_per_user: Optional[int] = None
    expires_at: Optional[str]       = None
    min_order_amount: Optional[float] = None
    is_active: Optional[bool]       = None


class CouponAdminItem(BaseModel):
    id: UUID
    code: str
    discount_type: str
    discount_value: float
    discount_label: str    # "Giảm 20%" hoặc "Giảm 200.000 ₫"
    applies_to: str
    course_title: Optional[str] = None
    uses_count: int
    uses_count_fmt: str    # "247"
    max_uses: Optional[int]
    max_uses_per_user: int
    expires_at: Optional[str]
    is_active: bool
    status: str            # "active" | "expired" | "exhausted" | "inactive"
    status_label: str      # "Hoạt động" | "Hết hạn" | ...
    created_at: str

    model_config = {"from_attributes": True}


# ── Checkout / Order ──────────────────────────────────────

class CreateOrderRequest(BaseModel):
    course_id: UUID
    coupon_code: Optional[str] = None


class OrderSummary(BaseModel):
    """Thông tin đơn hàng trả về khi tạo checkout."""
    order_id: UUID
    order_code: str          # "DH20260529ABC123"
    course_id: UUID
    course_title: str
    course_thumbnail: Optional[str] = None
    # Giá
    original_price: float
    original_price_fmt: str
    discount_amount: float = 0
    discount_amount_fmt: str = "0 ₫"
    coupon_code: Optional[str] = None
    coupon_discount: float = 0
    coupon_discount_fmt: str = "0 ₫"
    final_price: float
    final_price_fmt: str
    # Thanh toán
    bank_name: str
    bank_account_number: str
    bank_account_name: str
    transfer_content: str    # = order_code
    qr_url: Optional[str] = None
    # Thời gian
    expires_at: str          # "29/05/2026 15:00:00"
    expires_seconds: int     # giây còn lại (30 phút = 1800)
    status: str              # "pending" | "paid" | "expired" | "cancelled"


class OrderListItem(BaseModel):
    id: UUID
    order_code: str
    course_title: str
    course_thumbnail: Optional[str] = None
    final_price: float
    final_price_fmt: str
    status: str
    status_label: str        # "Thành công" | "Chờ thanh toán" | ...
    paid_at: Optional[str] = None
    created_at: str

    model_config = {"from_attributes": True}


class AdminOrderItem(OrderListItem):
    user_id: UUID
    user_name: str
    user_email: str
    original_price: float
    original_price_fmt: str
    discount_amount: float
    coupon_code: Optional[str] = None
    payment_method: Optional[str] = None

    model_config = {"from_attributes": True}


# ── SePay Webhook ─────────────────────────────────────────

class SePayWebhookPayload(BaseModel):
    """
    Payload từ SePay webhook khi nhận được giao dịch ngân hàng.
    https://sepay.vn/docs/webhook
    """
    id: Optional[int] = None
    gateway: Optional[str] = None
    transactionDate: Optional[str] = None
    accountNumber: Optional[str] = None
    subAccount: Optional[str] = None
    transferType: Optional[str] = None
    transferAmount: Optional[float] = None
    accumulated: Optional[float] = None
    code: Optional[str] = None           # Mã đơn hàng trong nội dung CK
    content: Optional[str] = None        # Nội dung chuyển khoản
    referenceCode: Optional[str] = None
    description: Optional[str] = None

    model_config = {"extra": "allow"}    # SePay có thể gửi thêm fields
