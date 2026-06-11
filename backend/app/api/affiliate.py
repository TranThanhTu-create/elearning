"""
Affiliate API — Dashboard cá nhân: stats, hoa hồng, rút tiền.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.affiliate import Affiliate, Commission, WithdrawalRequest, AffiliateClick
from app.models.order import Order
from app.models.course import Course
from app.schemas.affiliate import (
    AffiliateStats, AffiliateOrderItem, WithdrawalItem,
    WithdrawalRequest as WithdrawalRequestSchema,
)
from app.schemas.common import PaginatedResponse, MessageResponse
from app.utils.deps import get_db, get_current_user, PaginationParams
from app.utils.formatters import format_vnd, format_number_vn, format_percent
from app.utils.timezone import vn_isoformat, now_utc
from app.utils.logger import get_logger
from app.config import settings

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


async def _get_or_create_affiliate(db: AsyncSession, user) -> Affiliate:
    result = await db.execute(select(Affiliate).where(Affiliate.user_id == user.id))
    aff = result.scalar_one_or_none()
    if not aff:
        ref_code = user.ref_code
        if not ref_code:
            from app.utils.security import generate_ref_code
            ref_code = generate_ref_code()
            user.ref_code = ref_code
        aff = Affiliate(user_id=user.id, ref_code=ref_code)
        db.add(aff)
        await db.flush()
    return aff


@router.get("/stats", response_model=AffiliateStats, summary="Thống kê affiliate của tôi")
async def get_affiliate_stats(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    aff = await _get_or_create_affiliate(db, user)
    site_url = getattr(settings, "FRONTEND_URL", "https://eduvietpro.vn")
    ref_link = f"{site_url}?ref={aff.ref_code}"

    cvr = (aff.total_orders / aff.total_clicks * 100) if aff.total_clicks > 0 else 0

    return AffiliateStats(
        ref_code=aff.ref_code,
        ref_link=ref_link,
        total_clicks=aff.total_clicks,
        total_clicks_fmt=format_number_vn(aff.total_clicks),
        total_orders=aff.total_orders,
        total_commission=aff.total_earnings,
        total_commission_fmt=format_vnd(aff.total_earnings),
        paid_commission=aff.paid_earnings,
        paid_commission_fmt=format_vnd(aff.paid_earnings),
        pending_commission=aff.pending_withdrawal,
        pending_commission_fmt=format_vnd(aff.pending_withdrawal),
        conversion_rate_fmt=f"{cvr:.1f}%".replace(".", ","),
    )


@router.get("/commissions", summary="Lịch sử hoa hồng")
async def list_my_commissions(
    status: Optional[str] = Query(None),
    page: int             = Query(1, ge=1),
    page_size: int        = Query(20, ge=1, le=50),
    db: AsyncSession      = Depends(get_db),
    user                  = Depends(get_current_user),
):
    pagination = PaginationParams(page=page, page_size=page_size)
    aff = await _get_or_create_affiliate(db, user)

    q = (
        select(Commission, Order.order_code, Order.amount.label("order_amount"), Course.title.label("course_title"))
        .join(Order, Commission.order_id == Order.id)
        .join(Course, Order.course_id == Course.id)
        .where(Commission.affiliate_id == aff.id)
    )
    if status:
        q = q.where(Commission.status == status)

    total_r = await db.execute(select(func.count()).select_from(q.subquery()))
    total = total_r.scalar_one()

    q = q.order_by(Commission.created_at.desc()).offset(pagination.offset).limit(pagination.page_size)
    rows = (await db.execute(q)).all()

    items = [
        {
            "id": str(r.Commission.id),
            "order_code": r.order_code,
            "course_title": r.course_title,
            "order_amount": r.order_amount,
            "order_amount_fmt": format_vnd(r.order_amount),
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


@router.get("/withdrawals", summary="Lịch sử rút tiền")
async def list_my_withdrawals(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    aff = await _get_or_create_affiliate(db, user)
    result = await db.execute(
        select(WithdrawalRequest)
        .where(WithdrawalRequest.affiliate_id == aff.id)
        .order_by(WithdrawalRequest.created_at.desc())
    )
    reqs = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "amount": r.amount,
            "amount_fmt": format_vnd(r.amount),
            "bank_name": r.bank_name,
            "account_number": r.account_number,
            "account_name": r.account_name,
            "status": r.status,
            "status_label": WITHDRAWAL_STATUS_LABELS.get(r.status, r.status),
            "admin_note": r.admin_note,
            "created_at": vn_isoformat(r.created_at),
            "processed_at": vn_isoformat(r.processed_at),
        }
        for r in reqs
    ]


@router.post("/withdrawals", status_code=201, summary="Yêu cầu rút tiền")
async def request_withdrawal(
    body: WithdrawalRequestSchema,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    aff = await _get_or_create_affiliate(db, user)

    min_withdrawal = 500_000
    if body.amount < min_withdrawal:
        raise HTTPException(400, f"Số tiền rút tối thiểu là {format_vnd(min_withdrawal)}")

    if body.amount > aff.pending_withdrawal:
        raise HTTPException(400, f"Số dư chờ rút chỉ có {format_vnd(aff.pending_withdrawal)}")

    # Kiểm tra có yêu cầu đang chờ không
    pending_r = await db.execute(
        select(WithdrawalRequest).where(
            WithdrawalRequest.affiliate_id == aff.id,
            WithdrawalRequest.status == "pending",
        )
    )
    if pending_r.scalar_one_or_none():
        raise HTTPException(400, "Bạn đã có yêu cầu rút tiền đang chờ xử lý")

    req = WithdrawalRequest(
        affiliate_id=aff.id,
        amount=int(body.amount),
        bank_name=body.bank_name,
        account_number=body.bank_account,
        account_name=body.account_name.upper(),
    )
    db.add(req)
    logger.info(f"Withdrawal request: {user.email} → {format_vnd(body.amount)}")
    return MessageResponse(message=f"Đã gửi yêu cầu rút {format_vnd(body.amount)}. Admin sẽ xử lý trong 1-3 ngày làm việc.")
