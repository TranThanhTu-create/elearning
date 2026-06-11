"""
Admin API — Quản lý đơn hàng, hoàn tiền, cập nhật trạng thái.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.models.order import Order, Coupon
from app.models.course import Course, Enrollment
from app.models.user import User
from app.schemas.common import PaginatedResponse, MessageResponse
from app.utils.deps import get_db, require_admin, PaginationParams
from app.utils.formatters import format_vnd, format_number_vn
from app.utils.timezone import vn_isoformat, format_vn_datetime, now_utc
from app.utils.logger import get_logger
from pydantic import BaseModel, Field

logger = get_logger(__name__)
router = APIRouter()

STATUS_LABELS = {
    "pending": "Chờ thanh toán",
    "completed": "Thành công",
    "expired": "Hết hạn",
    "cancelled": "Đã hủy",
    "refunded": "Đã hoàn tiền",
}


# ── Schemas ───────────────────────────────────────────────

class OrderStatusUpdateRequest(BaseModel):
    status: str       = Field(..., pattern="^(completed|cancelled|refunded)$")
    refund_note: Optional[str] = Field(None, max_length=500)


class ManualEnrollRequest(BaseModel):
    user_id: UUID
    course_id: UUID
    note: Optional[str] = None


# ── List & Filter ─────────────────────────────────────────

@router.get("", summary="Danh sách đơn hàng (admin)")
async def list_orders(
    search: Optional[str]       = Query(None, description="Tìm theo mã đơn, tên/email user"),
    status: Optional[str]       = Query(None),
    course_id: Optional[UUID]   = Query(None),
    date_from: Optional[str]    = Query(None, description="YYYY-MM-DD"),
    date_to: Optional[str]      = Query(None, description="YYYY-MM-DD"),
    page: int                   = Query(1, ge=1),
    page_size: int              = Query(20, ge=1, le=100),
    db: AsyncSession            = Depends(get_db),
    admin                       = Depends(require_admin),
):
    pagination = PaginationParams(page=page, page_size=page_size)

    q = (
        select(Order, User.name.label("user_name"), User.email.label("user_email"), Course.title.label("course_title"))
        .join(User, Order.user_id == User.id)
        .join(Course, Order.course_id == Course.id)
    )
    filters = []
    if search:
        filters.append(
            and_(
                Order.order_code.ilike(f"%{search}%")
            ) if "@" not in search else
            and_(
                User.email.ilike(f"%{search}%")
            )
        )
        if not filters:
            filters.append(
                Order.order_code.ilike(f"%{search}%")
            )
    if status:
        filters.append(Order.status == status)
    if course_id:
        filters.append(Order.course_id == course_id)
    if date_from:
        from datetime import datetime
        try:
            dt = datetime.fromisoformat(date_from)
            filters.append(Order.created_at >= dt)
        except ValueError:
            pass
    if date_to:
        from datetime import datetime
        try:
            dt = datetime.fromisoformat(date_to + "T23:59:59")
            filters.append(Order.created_at <= dt)
        except ValueError:
            pass

    if filters:
        q = q.where(and_(*filters))

    total_r = await db.execute(select(func.count()).select_from(q.subquery()))
    total = total_r.scalar_one()

    q = q.order_by(Order.created_at.desc()).offset(pagination.offset).limit(pagination.page_size)
    rows = (await db.execute(q)).all()

    items = [
        {
            "id": str(r.Order.id),
            "order_code": r.Order.order_code,
            "user_name": r.user_name,
            "user_email": r.user_email,
            "course_title": r.course_title,
            "original_amount": r.Order.original_amount,
            "original_amount_fmt": format_vnd(r.Order.original_amount),
            "discount_amount": r.Order.discount_amount,
            "discount_amount_fmt": format_vnd(r.Order.discount_amount),
            "amount": r.Order.amount,
            "amount_fmt": format_vnd(r.Order.amount),
            "coupon_code": None,  # loaded separately if needed
            "affiliate_code": r.Order.affiliate_code,
            "payment_method": r.Order.payment_method,
            "status": r.Order.status,
            "status_label": STATUS_LABELS.get(r.Order.status, r.Order.status),
            "completed_at": vn_isoformat(r.Order.completed_at),
            "created_at": vn_isoformat(r.Order.created_at),
        }
        for r in rows
    ]
    return PaginatedResponse.build(items, total, page, page_size)


@router.get("/stats", summary="Thống kê đơn hàng nhanh")
async def order_stats(
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    total_r = await db.execute(select(func.count()).select_from(Order))
    total = total_r.scalar_one()

    completed_r = await db.execute(
        select(func.count(), func.sum(Order.amount))
        .where(Order.status == "completed")
    )
    row = completed_r.one()
    completed_count, total_revenue = row[0], row[1] or 0

    pending_r = await db.execute(
        select(func.count()).where(Order.status == "pending")
    )
    pending_count = pending_r.scalar_one()

    return {
        "total_orders": format_number_vn(total),
        "completed_orders": format_number_vn(completed_count),
        "pending_orders": format_number_vn(pending_count),
        "total_revenue": format_vnd(total_revenue),
        "total_revenue_raw": total_revenue,
    }


# ── Detail ────────────────────────────────────────────────

@router.get("/{order_id}", summary="Chi tiết đơn hàng")
async def get_order_detail(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.user),
            selectinload(Order.course),
            selectinload(Order.coupon),
        )
        .where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(404, "Không tìm thấy đơn hàng")

    return {
        "id": str(order.id),
        "order_code": order.order_code,
        "user": {
            "id": str(order.user.id),
            "name": order.user.name,
            "email": order.user.email,
            "phone": order.user.phone,
        },
        "course": {
            "id": str(order.course.id),
            "title": order.course.title,
            "slug": order.course.slug,
            "thumbnail_url": order.course.thumbnail_url,
        },
        "original_amount": order.original_amount,
        "original_amount_fmt": format_vnd(order.original_amount),
        "discount_amount": order.discount_amount,
        "discount_amount_fmt": format_vnd(order.discount_amount),
        "amount": order.amount,
        "amount_fmt": format_vnd(order.amount),
        "coupon_code": order.coupon.code if order.coupon else None,
        "affiliate_code": order.affiliate_code,
        "payment_method": order.payment_method,
        "sepay_txn_id": order.sepay_txn_id,
        "utm_source": order.utm_source,
        "utm_medium": order.utm_medium,
        "utm_campaign": order.utm_campaign,
        "status": order.status,
        "status_label": STATUS_LABELS.get(order.status, order.status),
        "expires_at": vn_isoformat(order.expires_at),
        "completed_at": vn_isoformat(order.completed_at),
        "refunded_at": vn_isoformat(order.refunded_at),
        "refund_note": order.refund_note,
        "created_at": vn_isoformat(order.created_at),
    }


# ── Update status ─────────────────────────────────────────

@router.patch("/{order_id}/status", summary="Cập nhật trạng thái đơn hàng")
async def update_order_status(
    order_id: UUID,
    body: OrderStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(
        select(Order).options(selectinload(Order.course)).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(404, "Không tìm thấy đơn hàng")

    if order.status == body.status:
        raise HTTPException(400, f"Đơn hàng đã ở trạng thái '{STATUS_LABELS.get(body.status)}'")

    old_status = order.status
    order.status = body.status

    if body.status == "completed":
        order.completed_at = now_utc()
        # Tạo enrollment nếu chưa có
        enroll_r = await db.execute(
            select(Enrollment).where(
                Enrollment.user_id == order.user_id,
                Enrollment.course_id == order.course_id,
            )
        )
        if not enroll_r.scalar_one_or_none():
            db.add(Enrollment(user_id=order.user_id, course_id=order.course_id))
            # Tăng students count
            from sqlalchemy import update
            await db.execute(
                update(Course)
                .where(Course.id == order.course_id)
                .values(total_students=Course.total_students + 1)
            )

    elif body.status == "refunded":
        order.refunded_at = now_utc()
        order.refund_note = body.refund_note
        # Xóa enrollment nếu hoàn tiền
        enroll_r = await db.execute(
            select(Enrollment).where(
                Enrollment.user_id == order.user_id,
                Enrollment.course_id == order.course_id,
            )
        )
        enrollment = enroll_r.scalar_one_or_none()
        if enrollment:
            await db.delete(enrollment)
            from sqlalchemy import update
            await db.execute(
                update(Course)
                .where(Course.id == order.course_id)
                .values(total_students=func.greatest(Course.total_students - 1, 0))
            )

    logger.info(f"Admin {admin.email} cập nhật đơn {order.order_code}: {old_status} → {body.status}")
    return MessageResponse(message=f"Đã cập nhật trạng thái: {STATUS_LABELS.get(body.status)}")


# ── Manual enrollment ─────────────────────────────────────

@router.post("/manual-enroll", status_code=201, summary="Cấp quyền học thủ công")
async def manual_enroll(
    body: ManualEnrollRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    user_r = await db.execute(select(User).where(User.id == body.user_id))
    user = user_r.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Không tìm thấy user")

    course_r = await db.execute(select(Course).where(Course.id == body.course_id))
    course = course_r.scalar_one_or_none()
    if not course:
        raise HTTPException(404, "Không tìm thấy khóa học")

    existing = await db.execute(
        select(Enrollment).where(
            Enrollment.user_id == body.user_id,
            Enrollment.course_id == body.course_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(400, f"{user.name} đã được ghi danh vào khóa này rồi")

    db.add(Enrollment(user_id=body.user_id, course_id=body.course_id))
    logger.info(f"Admin {admin.email} ghi danh thủ công: {user.email} → {course.title}")
    return MessageResponse(message=f"Đã cấp quyền học cho {user.name}")
