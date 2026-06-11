"""
Admin API — Quản lý affiliate: danh sách, hoa hồng, duyệt rút tiền.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.affiliate import Affiliate, Commission, WithdrawalRequest
from app.models.user import User
from app.models.order import Order
from app.models.course import Course
from app.schemas.common import PaginatedResponse, MessageResponse
from app.utils.deps import get_db, require_admin, PaginationParams
from app.utils.formatters import format_vnd, format_number_vn
from app.utils.timezone import vn_isoformat, now_utc
from app.utils.logger import get_logger
from pydantic import BaseModel, Field

logger = get_logger(__name__)
router = APIRouter()

COMMISSION_STATUS_LABELS = {
    "pending": "Chờ duyệt",
    "approved": "Đã duyệt",
    "paid": "Đã trả",
    "cancelled": "Đã hủy",
}

WITHDRAWAL_STATUS_LABELS = {
    "pending": "Chờ duyệt",
    "approved": "Đã duyệt",
    "rejected": "Từ chối",
}


# ── Schemas ───────────────────────────────────────────────

class CommissionUpdateRequest(BaseModel):
    status: str        = Field(..., pattern="^(approved|paid|cancelled)$")
    note: Optional[str] = None


class WithdrawalUpdateRequest(BaseModel):
    status: str          = Field(..., pattern="^(approved|rejected)$")
    admin_note: Optional[str] = Field(None, max_length=500)


# ── Affiliates ────────────────────────────────────────────

@router.get("", summary="Danh sách affiliates")
async def list_affiliates(
    search: Optional[str]      = Query(None, description="Tìm theo tên, email, ref_code"),
    is_active: Optional[bool]  = Query(None),
    page: int                  = Query(1, ge=1),
    page_size: int             = Query(20, ge=1, le=100),
    db: AsyncSession           = Depends(get_db),
    admin                      = Depends(require_admin),
):
    pagination = PaginationParams(page=page, page_size=page_size)

    q = (
        select(Affiliate, User.name.label("user_name"), User.email.label("user_email"))
        .join(User, Affiliate.user_id == User.id)
        .where(User.deleted_at.is_(None))
    )
    filters = []
    if search:
        filters.append(
            User.name.ilike(f"%{search}%") |
            User.email.ilike(f"%{search}%") |
            Affiliate.ref_code.ilike(f"%{search}%")
        )
    if is_active is not None:
        filters.append(Affiliate.is_active == is_active)
    if filters:
        q = q.where(and_(*filters))

    total_r = await db.execute(select(func.count()).select_from(q.subquery()))
    total = total_r.scalar_one()

    q = q.order_by(Affiliate.total_earnings.desc()).offset(pagination.offset).limit(pagination.page_size)
    rows = (await db.execute(q)).all()

    items = [
        {
            "affiliate_id": str(r.Affiliate.id),
            "user_id": str(r.Affiliate.user_id),
            "user_name": r.user_name,
            "user_email": r.user_email,
            "ref_code": r.Affiliate.ref_code,
            "is_active": r.Affiliate.is_active,
            "total_clicks": r.Affiliate.total_clicks,
            "total_clicks_fmt": format_number_vn(r.Affiliate.total_clicks),
            "total_orders": r.Affiliate.total_orders,
            "total_earnings": r.Affiliate.total_earnings,
            "total_earnings_fmt": format_vnd(r.Affiliate.total_earnings),
            "paid_earnings": r.Affiliate.paid_earnings,
            "paid_earnings_fmt": format_vnd(r.Affiliate.paid_earnings),
            "pending_withdrawal": r.Affiliate.pending_withdrawal,
            "pending_withdrawal_fmt": format_vnd(r.Affiliate.pending_withdrawal),
            "created_at": vn_isoformat(r.Affiliate.created_at),
        }
        for r in rows
    ]
    return PaginatedResponse.build(items, total, page, page_size)


@router.get("/{affiliate_id}", summary="Chi tiết affiliate")
async def get_affiliate_detail(
    affiliate_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(
        select(Affiliate, User.name.label("user_name"), User.email.label("user_email"), User.phone.label("user_phone"))
        .join(User, Affiliate.user_id == User.id)
        .where(Affiliate.id == affiliate_id)
    )
    row = result.one_or_none()
    if not row:
        raise HTTPException(404, "Không tìm thấy affiliate")

    aff = row.Affiliate
    return {
        "affiliate_id": str(aff.id),
        "user_id": str(aff.user_id),
        "user_name": row.user_name,
        "user_email": row.user_email,
        "user_phone": row.user_phone,
        "ref_code": aff.ref_code,
        "is_active": aff.is_active,
        "total_clicks": aff.total_clicks,
        "total_clicks_fmt": format_number_vn(aff.total_clicks),
        "total_orders": aff.total_orders,
        "total_earnings": aff.total_earnings,
        "total_earnings_fmt": format_vnd(aff.total_earnings),
        "paid_earnings": aff.paid_earnings,
        "paid_earnings_fmt": format_vnd(aff.paid_earnings),
        "pending_withdrawal": aff.pending_withdrawal,
        "pending_withdrawal_fmt": format_vnd(aff.pending_withdrawal),
        "created_at": vn_isoformat(aff.created_at),
    }


@router.patch("/{affiliate_id}/toggle-active", summary="Bật/tắt affiliate")
async def toggle_affiliate_active(
    affiliate_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(select(Affiliate).where(Affiliate.id == affiliate_id))
    aff = result.scalar_one_or_none()
    if not aff:
        raise HTTPException(404, "Không tìm thấy affiliate")
    aff.is_active = not aff.is_active
    msg = "Đã kích hoạt affiliate" if aff.is_active else "Đã tắt affiliate"
    return {"is_active": aff.is_active, "message": msg}


# ── Commissions ───────────────────────────────────────────

@router.get("/commissions/all", summary="Tất cả hoa hồng (lọc theo trạng thái)")
async def list_commissions(
    status: Optional[str]        = Query(None),
    affiliate_id: Optional[UUID] = Query(None),
    page: int                    = Query(1, ge=1),
    page_size: int               = Query(20, ge=1, le=100),
    db: AsyncSession             = Depends(get_db),
    admin                        = Depends(require_admin),
):
    pagination = PaginationParams(page=page, page_size=page_size)

    q = (
        select(
            Commission,
            User.name.label("user_name"),
            User.email.label("user_email"),
            Order.order_code,
            Order.amount.label("order_amount"),
            Course.title.label("course_title"),
        )
        .join(Affiliate, Commission.affiliate_id == Affiliate.id)
        .join(User, Affiliate.user_id == User.id)
        .join(Order, Commission.order_id == Order.id)
        .join(Course, Order.course_id == Course.id)
    )
    filters = []
    if status:
        filters.append(Commission.status == status)
    if affiliate_id:
        filters.append(Commission.affiliate_id == affiliate_id)
    if filters:
        q = q.where(and_(*filters))

    total_r = await db.execute(select(func.count()).select_from(q.subquery()))
    total = total_r.scalar_one()

    q = q.order_by(Commission.created_at.desc()).offset(pagination.offset).limit(pagination.page_size)
    rows = (await db.execute(q)).all()

    items = [
        {
            "commission_id": str(r.Commission.id),
            "affiliate_id": str(r.Commission.affiliate_id),
            "user_name": r.user_name,
            "user_email": r.user_email,
            "order_code": r.order_code,
            "order_amount": r.order_amount,
            "order_amount_fmt": format_vnd(r.order_amount),
            "course_title": r.course_title,
            "commission_amount": r.Commission.amount,
            "commission_amount_fmt": format_vnd(r.Commission.amount),
            "rate": r.Commission.rate,
            "status": r.Commission.status,
            "status_label": COMMISSION_STATUS_LABELS.get(r.Commission.status, r.Commission.status),
            "paid_at": vn_isoformat(r.Commission.paid_at),
            "created_at": vn_isoformat(r.Commission.created_at),
        }
        for r in rows
    ]
    return PaginatedResponse.build(items, total, page, page_size)


@router.patch("/commissions/{commission_id}", summary="Cập nhật trạng thái hoa hồng")
async def update_commission_status(
    commission_id: UUID,
    body: CommissionUpdateRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(select(Commission).where(Commission.id == commission_id))
    commission = result.scalar_one_or_none()
    if not commission:
        raise HTTPException(404, "Không tìm thấy hoa hồng")

    old_status = commission.status
    commission.status = body.status

    if body.status == "paid":
        commission.paid_at = now_utc()
        # Cập nhật aggregate cho affiliate
        aff_r = await db.execute(select(Affiliate).where(Affiliate.id == commission.affiliate_id))
        aff = aff_r.scalar_one_or_none()
        if aff:
            aff.paid_earnings += commission.amount
            aff.pending_withdrawal = max(0, aff.pending_withdrawal - commission.amount)

    logger.info(f"Admin {admin.email} cập nhật hoa hồng {commission_id}: {old_status} → {body.status}")
    return MessageResponse(message=f"Đã cập nhật: {COMMISSION_STATUS_LABELS.get(body.status)}")


# ── Withdrawal requests ───────────────────────────────────

@router.get("/withdrawals/all", summary="Tất cả yêu cầu rút tiền")
async def list_withdrawals(
    status: Optional[str]  = Query(None),
    page: int              = Query(1, ge=1),
    page_size: int         = Query(20, ge=1, le=100),
    db: AsyncSession       = Depends(get_db),
    admin                  = Depends(require_admin),
):
    pagination = PaginationParams(page=page, page_size=page_size)

    q = (
        select(WithdrawalRequest, User.name.label("user_name"), User.email.label("user_email"))
        .join(Affiliate, WithdrawalRequest.affiliate_id == Affiliate.id)
        .join(User, Affiliate.user_id == User.id)
    )
    if status:
        q = q.where(WithdrawalRequest.status == status)

    total_r = await db.execute(select(func.count()).select_from(q.subquery()))
    total = total_r.scalar_one()

    q = q.order_by(WithdrawalRequest.created_at.desc()).offset(pagination.offset).limit(pagination.page_size)
    rows = (await db.execute(q)).all()

    items = [
        {
            "id": str(r.WithdrawalRequest.id),
            "affiliate_id": str(r.WithdrawalRequest.affiliate_id),
            "user_name": r.user_name,
            "user_email": r.user_email,
            "amount": r.WithdrawalRequest.amount,
            "amount_fmt": format_vnd(r.WithdrawalRequest.amount),
            "bank_name": r.WithdrawalRequest.bank_name,
            "account_number": r.WithdrawalRequest.account_number,
            "account_name": r.WithdrawalRequest.account_name,
            "status": r.WithdrawalRequest.status,
            "status_label": WITHDRAWAL_STATUS_LABELS.get(r.WithdrawalRequest.status, r.WithdrawalRequest.status),
            "admin_note": r.WithdrawalRequest.admin_note,
            "processed_at": vn_isoformat(r.WithdrawalRequest.processed_at),
            "created_at": vn_isoformat(r.WithdrawalRequest.created_at),
        }
        for r in rows
    ]
    return PaginatedResponse.build(items, total, page, page_size)


@router.patch("/withdrawals/{withdrawal_id}", summary="Duyệt / từ chối yêu cầu rút tiền")
async def process_withdrawal(
    withdrawal_id: UUID,
    body: WithdrawalUpdateRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(
        select(WithdrawalRequest).where(WithdrawalRequest.id == withdrawal_id)
    )
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(404, "Không tìm thấy yêu cầu rút tiền")

    if req.status != "pending":
        raise HTTPException(400, f"Yêu cầu đã được xử lý (status: {req.status})")

    req.status = body.status
    req.admin_note = body.admin_note
    req.processed_at = now_utc()

    if body.status == "approved":
        aff_r = await db.execute(select(Affiliate).where(Affiliate.id == req.affiliate_id))
        aff = aff_r.scalar_one_or_none()
        if aff:
            aff.pending_withdrawal = max(0, aff.pending_withdrawal - req.amount)
            aff.paid_earnings += req.amount

    label = "Đã duyệt" if body.status == "approved" else "Đã từ chối"
    logger.info(f"Admin {admin.email} {label.lower()} rút tiền {withdrawal_id}: {format_vnd(req.amount)}")
    return {"status": req.status, "message": f"{label} yêu cầu rút tiền {format_vnd(req.amount)}"}
