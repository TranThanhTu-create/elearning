"""
Admin API — Quản lý người dùng: xem, kích hoạt/khóa, đặt lại mật khẩu.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.order import Order
from app.models.course import Enrollment, Course
from app.schemas.common import PaginatedResponse, MessageResponse
from app.utils.deps import get_db, require_admin, PaginationParams
from app.utils.formatters import format_vnd, format_number_vn
from app.utils.timezone import vn_isoformat, now_utc
from app.utils.logger import get_logger
from pydantic import BaseModel, Field

logger = get_logger(__name__)
router = APIRouter()


# ── Schemas ───────────────────────────────────────────────

class AdminUpdateUserRequest(BaseModel):
    name: Optional[str]     = Field(None, min_length=2, max_length=100)
    phone: Optional[str]    = Field(None, max_length=20)
    role: Optional[str]     = Field(None, pattern="^(admin|student)$")
    is_active: Optional[bool] = None


class ResetPasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=6, max_length=128)


# ── List ──────────────────────────────────────────────────

@router.get("", summary="Danh sách người dùng (admin)")
async def list_users(
    search: Optional[str]     = Query(None, description="Tìm theo tên, email, SĐT"),
    role: Optional[str]       = Query(None, pattern="^(admin|student)$"),
    is_active: Optional[bool] = Query(None),
    page: int                 = Query(1, ge=1),
    page_size: int            = Query(20, ge=1, le=100),
    db: AsyncSession          = Depends(get_db),
    admin                     = Depends(require_admin),
):
    pagination = PaginationParams(page=page, page_size=page_size)

    q = select(User).where(User.deleted_at.is_(None))
    filters = []
    if search:
        filters.append(
            or_(
                User.name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.phone.ilike(f"%{search}%"),
            )
        )
    if role:
        filters.append(User.role == role)
    if is_active is not None:
        filters.append(User.is_active == is_active)
    if filters:
        q = q.where(and_(*filters))

    total_r = await db.execute(select(func.count()).select_from(q.subquery()))
    total = total_r.scalar_one()

    q = q.order_by(User.created_at.desc()).offset(pagination.offset).limit(pagination.page_size)
    users = (await db.execute(q)).scalars().all()

    # Lấy stats tổng hợp cho từng user
    user_ids = [u.id for u in users]
    courses_count_map: dict = {}
    total_spent_map: dict = {}

    if user_ids:
        enroll_r = await db.execute(
            select(Enrollment.user_id, func.count().label("cnt"))
            .where(Enrollment.user_id.in_(user_ids))
            .group_by(Enrollment.user_id)
        )
        for row in enroll_r.all():
            courses_count_map[row.user_id] = row.cnt

        orders_r = await db.execute(
            select(Order.user_id, func.sum(Order.amount).label("total"))
            .where(Order.user_id.in_(user_ids), Order.status == "completed")
            .group_by(Order.user_id)
        )
        for row in orders_r.all():
            total_spent_map[row.user_id] = row.total or 0

    items = [
        {
            "id": str(u.id),
            "email": u.email,
            "name": u.name,
            "phone": u.phone,
            "role": u.role,
            "is_active": u.is_active,
            "is_email_verified": u.is_email_verified,
            "courses_count": courses_count_map.get(u.id, 0),
            "total_spent": total_spent_map.get(u.id, 0),
            "total_spent_fmt": format_vnd(total_spent_map.get(u.id, 0)),
            "ref_code": u.ref_code,
            "last_login_at": vn_isoformat(u.last_login_at),
            "created_at": vn_isoformat(u.created_at),
        }
        for u in users
    ]
    return PaginatedResponse.build(items, total, page, page_size)


# ── Detail ────────────────────────────────────────────────

@router.get("/{user_id}", summary="Chi tiết người dùng")
async def get_user_detail(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Không tìm thấy user")

    # Orders
    orders_r = await db.execute(
        select(Order, Course.title.label("course_title"))
        .join(Course, Order.course_id == Course.id)
        .where(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .limit(20)
    )
    orders = [
        {
            "id": str(r.Order.id),
            "order_code": r.Order.order_code,
            "course_title": r.course_title,
            "amount": r.Order.amount,
            "amount_fmt": format_vnd(r.Order.amount),
            "status": r.Order.status,
            "created_at": vn_isoformat(r.Order.created_at),
        }
        for r in orders_r.all()
    ]

    # Enrollments
    enrolls_r = await db.execute(
        select(Enrollment, Course.title.label("course_title"), Course.slug.label("course_slug"))
        .join(Course, Enrollment.course_id == Course.id)
        .where(Enrollment.user_id == user_id)
        .order_by(Enrollment.enrolled_at.desc())
    )
    enrollments = [
        {
            "course_id": str(r.Enrollment.course_id),
            "course_title": r.course_title,
            "course_slug": r.course_slug,
            "progress_percent": r.Enrollment.progress_percent,
            "enrolled_at": vn_isoformat(r.Enrollment.enrolled_at),
        }
        for r in enrolls_r.all()
    ]

    total_spent = sum(o["amount"] for o in orders if o.get("status") == "completed")

    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "phone": user.phone,
        "avatar_url": user.avatar_url,
        "role": user.role,
        "is_active": user.is_active,
        "is_email_verified": user.is_email_verified,
        "ref_code": user.ref_code,
        "google_id": user.google_id,
        "total_spent": total_spent,
        "total_spent_fmt": format_vnd(total_spent),
        "courses_count": len(enrollments),
        "last_login_at": vn_isoformat(user.last_login_at),
        "created_at": vn_isoformat(user.created_at),
        "orders": orders,
        "enrollments": enrollments,
    }


# ── Update ────────────────────────────────────────────────

@router.patch("/{user_id}", summary="Cập nhật thông tin user")
async def update_user(
    user_id: UUID,
    body: AdminUpdateUserRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    if user_id == admin.id and body.role == "student":
        raise HTTPException(400, "Không thể tự hạ quyền của chính mình")

    result = await db.execute(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Không tìm thấy user")

    for field, val in body.model_dump(exclude_unset=True).items():
        setattr(user, field, val)

    logger.info(f"Admin {admin.email} cập nhật user: {user.email}")
    return MessageResponse(message="Cập nhật thành công")


@router.patch("/{user_id}/toggle-active", summary="Kích hoạt / khóa tài khoản")
async def toggle_user_active(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    if user_id == admin.id:
        raise HTTPException(400, "Không thể tự khóa tài khoản của chính mình")

    result = await db.execute(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Không tìm thấy user")

    user.is_active = not user.is_active
    action = "Kích hoạt" if user.is_active else "Khóa"
    logger.info(f"Admin {admin.email} {action.lower()} tài khoản: {user.email}")
    return {"is_active": user.is_active, "message": f"{action} tài khoản thành công"}


@router.post("/{user_id}/reset-password", summary="Đặt lại mật khẩu user")
async def admin_reset_password(
    user_id: UUID,
    body: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    from app.utils.security import hash_password

    result = await db.execute(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Không tìm thấy user")

    user.password_hash = hash_password(body.new_password)
    logger.info(f"Admin {admin.email} reset password cho: {user.email}")
    return MessageResponse(message="Đã đặt lại mật khẩu thành công")


# ── Soft delete ───────────────────────────────────────────

@router.delete("/{user_id}", summary="Xóa tài khoản user (soft delete)")
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    if user_id == admin.id:
        raise HTTPException(400, "Không thể tự xóa tài khoản của chính mình")

    result = await db.execute(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Không tìm thấy user")

    user.deleted_at = now_utc()
    user.is_active = False
    logger.info(f"Admin {admin.email} xóa (soft) tài khoản: {user.email}")
    return MessageResponse(message="Đã xóa tài khoản thành công")
