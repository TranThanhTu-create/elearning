"""
Admin API — Quản lý mã giảm giá (CRUD, toggle, xem lịch sử dùng).
"""

from typing import Optional
from uuid import UUID
import secrets
import string

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.order import Coupon, CouponUsage
from app.models.course import Course
from app.schemas.common import PaginatedResponse, MessageResponse
from app.utils.deps import get_db, require_admin, PaginationParams
from app.utils.formatters import format_vnd, format_number_vn
from app.utils.timezone import vn_isoformat, now_utc
from app.utils.logger import get_logger
from pydantic import BaseModel, Field

logger = get_logger(__name__)
router = APIRouter()


def _coupon_status(coupon: Coupon) -> tuple[str, str]:
    """Tính status + label của coupon."""
    from app.utils.timezone import now_utc
    now = now_utc()
    if not coupon.is_active:
        return "inactive", "Không hoạt động"
    if coupon.expires_at and coupon.expires_at < now:
        return "expired", "Hết hạn"
    if coupon.max_uses and coupon.used_count >= coupon.max_uses:
        return "exhausted", "Đã hết lượt"
    return "active", "Hoạt động"


def _discount_label(coupon: Coupon) -> str:
    if coupon.discount_type == "percent":
        return f"Giảm {int(coupon.discount_value)}%"
    return f"Giảm {format_vnd(coupon.discount_value)}"


# ── Schemas ───────────────────────────────────────────────

class CouponCreateRequest(BaseModel):
    code: str                 = Field(..., min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    discount_type: str        = Field(..., pattern="^(percent|fixed)$")
    discount_value: int       = Field(..., gt=0)
    min_order_amount: int     = Field(0, ge=0)
    max_uses: Optional[int]   = Field(None, ge=1)
    max_uses_per_user: int    = Field(1, ge=0)
    course_id: Optional[UUID] = None
    expires_at: Optional[str] = None
    is_active: bool           = True


class CouponUpdateRequest(BaseModel):
    description: Optional[str]   = None
    discount_type: Optional[str] = Field(None, pattern="^(percent|fixed)$")
    discount_value: Optional[int] = Field(None, gt=0)
    min_order_amount: Optional[int] = None
    max_uses: Optional[int]       = None
    max_uses_per_user: Optional[int] = None
    course_id: Optional[UUID]     = None
    expires_at: Optional[str]     = None
    is_active: Optional[bool]     = None


# ── CRUD ──────────────────────────────────────────────────

@router.get("", summary="Danh sách mã giảm giá")
async def list_coupons(
    search: Optional[str]      = Query(None),
    status: Optional[str]      = Query(None, description="active|expired|exhausted|inactive"),
    discount_type: Optional[str] = Query(None),
    page: int                  = Query(1, ge=1),
    page_size: int             = Query(20, ge=1, le=100),
    db: AsyncSession           = Depends(get_db),
    admin                      = Depends(require_admin),
):
    pagination = PaginationParams(page=page, page_size=page_size)

    q = select(Coupon)
    filters = []
    if search:
        filters.append(Coupon.code.ilike(f"%{search}%"))
    if discount_type:
        filters.append(Coupon.discount_type == discount_type)
    if filters:
        q = q.where(and_(*filters))

    total_r = await db.execute(select(func.count()).select_from(q.subquery()))
    total = total_r.scalar_one()

    q = q.order_by(Coupon.created_at.desc()).offset(pagination.offset).limit(pagination.page_size)
    coupons = (await db.execute(q)).scalars().all()

    # Lấy tên khóa học nếu có course_id
    course_ids = [c.course_id for c in coupons if c.course_id]
    course_map: dict = {}
    if course_ids:
        courses_r = await db.execute(
            select(Course.id, Course.title).where(Course.id.in_(course_ids))
        )
        for row in courses_r.all():
            course_map[row.id] = row.title

    items = []
    for c in coupons:
        c_status, c_label = _coupon_status(c)
        if status and c_status != status:
            continue
        items.append({
            "id": str(c.id),
            "code": c.code,
            "description": c.description,
            "discount_type": c.discount_type,
            "discount_value": c.discount_value,
            "discount_label": _discount_label(c),
            "min_order_amount": c.min_order_amount,
            "min_order_amount_fmt": format_vnd(c.min_order_amount) if c.min_order_amount else None,
            "max_uses": c.max_uses,
            "max_uses_per_user": c.max_uses_per_user,
            "used_count": c.used_count,
            "course_id": str(c.course_id) if c.course_id else None,
            "course_title": course_map.get(c.course_id) if c.course_id else None,
            "expires_at": vn_isoformat(c.expires_at),
            "is_active": c.is_active,
            "status": c_status,
            "status_label": c_label,
            "created_at": vn_isoformat(c.created_at),
        })

    return PaginatedResponse.build(items, total, page, page_size)


@router.post("", status_code=201, summary="Tạo mã giảm giá mới")
async def create_coupon(
    body: CouponCreateRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    from datetime import datetime

    existing = await db.execute(select(Coupon).where(Coupon.code == body.code.upper()))
    if existing.scalar_one_or_none():
        raise HTTPException(400, f"Mã '{body.code.upper()}' đã tồn tại")

    expires_at = None
    if body.expires_at:
        try:
            expires_at = datetime.fromisoformat(body.expires_at)
        except ValueError:
            raise HTTPException(400, "Định dạng ngày hết hạn không hợp lệ (ISO 8601)")

    coupon = Coupon(
        code=body.code.upper(),
        description=body.description,
        discount_type=body.discount_type,
        discount_value=body.discount_value,
        min_order_amount=body.min_order_amount,
        max_uses=body.max_uses,
        max_uses_per_user=body.max_uses_per_user,
        course_id=body.course_id,
        expires_at=expires_at,
        is_active=body.is_active,
    )
    db.add(coupon)
    await db.flush()
    logger.info(f"Admin {admin.email} tạo coupon: {coupon.code}")
    return {"id": str(coupon.id), "code": coupon.code, "message": "Tạo mã giảm giá thành công"}


@router.get("/generate-code", summary="Tạo mã ngẫu nhiên")
async def generate_coupon_code(
    length: int = Query(8, ge=6, le=20),
    admin=Depends(require_admin),
):
    chars = string.ascii_uppercase + string.digits
    code = "".join(secrets.choice(chars) for _ in range(length))
    return {"code": code}


@router.get("/{coupon_id}", summary="Chi tiết mã giảm giá")
async def get_coupon_detail(
    coupon_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(select(Coupon).where(Coupon.id == coupon_id))
    coupon = result.scalar_one_or_none()
    if not coupon:
        raise HTTPException(404, "Không tìm thấy mã giảm giá")

    c_status, c_label = _coupon_status(coupon)
    return {
        "id": str(coupon.id),
        "code": coupon.code,
        "description": coupon.description,
        "discount_type": coupon.discount_type,
        "discount_value": coupon.discount_value,
        "discount_label": _discount_label(coupon),
        "min_order_amount": coupon.min_order_amount,
        "max_uses": coupon.max_uses,
        "max_uses_per_user": coupon.max_uses_per_user,
        "used_count": coupon.used_count,
        "course_id": str(coupon.course_id) if coupon.course_id else None,
        "expires_at": vn_isoformat(coupon.expires_at),
        "is_active": coupon.is_active,
        "status": c_status,
        "status_label": c_label,
        "created_at": vn_isoformat(coupon.created_at),
    }


@router.patch("/{coupon_id}", summary="Cập nhật mã giảm giá")
async def update_coupon(
    coupon_id: UUID,
    body: CouponUpdateRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    from datetime import datetime

    result = await db.execute(select(Coupon).where(Coupon.id == coupon_id))
    coupon = result.scalar_one_or_none()
    if not coupon:
        raise HTTPException(404, "Không tìm thấy mã giảm giá")

    data = body.model_dump(exclude_unset=True)
    if "expires_at" in data:
        val = data.pop("expires_at")
        try:
            coupon.expires_at = datetime.fromisoformat(val) if val else None
        except ValueError:
            raise HTTPException(400, "Định dạng ngày hết hạn không hợp lệ")

    for field, val in data.items():
        setattr(coupon, field, val)

    return MessageResponse(message="Cập nhật mã giảm giá thành công")


@router.patch("/{coupon_id}/toggle", summary="Bật/tắt mã giảm giá")
async def toggle_coupon(
    coupon_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(select(Coupon).where(Coupon.id == coupon_id))
    coupon = result.scalar_one_or_none()
    if not coupon:
        raise HTTPException(404, "Không tìm thấy mã giảm giá")
    coupon.is_active = not coupon.is_active
    msg = "Đã bật mã giảm giá" if coupon.is_active else "Đã tắt mã giảm giá"
    return {"is_active": coupon.is_active, "message": msg}


@router.delete("/{coupon_id}", summary="Xóa mã giảm giá")
async def delete_coupon(
    coupon_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(select(Coupon).where(Coupon.id == coupon_id))
    coupon = result.scalar_one_or_none()
    if not coupon:
        raise HTTPException(404, "Không tìm thấy mã giảm giá")

    if coupon.used_count > 0:
        raise HTTPException(400, "Không thể xóa mã đã được sử dụng. Hãy tắt thay vì xóa.")

    await db.delete(coupon)
    return MessageResponse(message="Đã xóa mã giảm giá")


@router.get("/{coupon_id}/usages", summary="Lịch sử sử dụng mã")
async def coupon_usages(
    coupon_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    from app.models.user import User
    from app.models.order import Order

    pagination = PaginationParams(page=page, page_size=page_size)
    coupon = (await db.execute(select(Coupon).where(Coupon.id == coupon_id))).scalar_one_or_none()
    if not coupon:
        raise HTTPException(404, "Không tìm thấy mã giảm giá")

    q = (
        select(CouponUsage, User.name.label("user_name"), User.email.label("user_email"))
        .join(User, CouponUsage.user_id == User.id)
        .where(CouponUsage.coupon_id == coupon_id)
    )
    total_r = await db.execute(select(func.count()).select_from(q.subquery()))
    total = total_r.scalar_one()

    q = q.order_by(CouponUsage.used_at.desc()).offset(pagination.offset).limit(pagination.page_size)
    rows = (await db.execute(q)).all()

    items = [
        {
            "id": str(r.CouponUsage.id),
            "user_name": r.user_name,
            "user_email": r.user_email,
            "order_id": str(r.CouponUsage.order_id),
            "used_at": vn_isoformat(r.CouponUsage.used_at),
        }
        for r in rows
    ]
    return PaginatedResponse.build(items, total, page, page_size)
