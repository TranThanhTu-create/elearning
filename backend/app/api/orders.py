"""
Orders API — Tạo đơn checkout, apply coupon, SePay webhook, order status.
"""

import hashlib
import hmac
import json
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models.order import Order, Coupon, CouponUsage
from app.models.course import Course, Enrollment
from app.models.user import User
from app.schemas.order import (
    CreateOrderRequest, OrderSummary,
    CouponCheckRequest, CouponCheckResponse,
    SePayWebhookPayload,
)
from app.schemas.common import MessageResponse
from app.utils.deps import get_db, get_current_user
from app.utils.security import generate_order_code
from app.utils.formatters import format_vnd, format_number_vn
from app.utils.timezone import now_utc, now_vn, vn_isoformat, format_vn_datetime
from app.utils.logger import get_logger, log_db, log_payment, log_webhook, log_error
from app.config import settings

logger = get_logger(__name__)
router = APIRouter()


# ── Helpers ───────────────────────────────────────────────

STATUS_LABELS = {
    "pending":   "Chờ thanh toán",
    "paid":      "Thành công",
    "expired":   "Hết hạn",
    "cancelled": "Đã hủy",
    "refunded":  "Hoàn tiền",
}


async def _calc_coupon(
    db: AsyncSession,
    code: str,
    course_id: UUID,
    user_id: UUID,
    original_price: float,
) -> tuple[Optional[Coupon], float, str]:
    """
    Tính toán coupon discount.
    Returns: (coupon_obj, discount_amount, error_message)
    """
    result = await db.execute(
        select(Coupon).where(
            Coupon.code == code.upper().strip(),
            Coupon.is_active == True,
        )
    )
    coupon = result.scalar_one_or_none()

    if not coupon:
        return None, 0, "Mã giảm giá không tồn tại hoặc đã bị tắt."

    # Kiểm tra hết hạn
    if coupon.expires_at and coupon.expires_at < now_utc():
        return None, 0, "Mã giảm giá đã hết hạn."

    # Kiểm tra số lượt dùng tổng
    if coupon.max_uses and coupon.used_count >= coupon.max_uses:
        return None, 0, "Mã giảm giá đã hết lượt sử dụng."

    # Kiểm tra coupon chỉ áp dụng cho khóa cụ thể
    if coupon.course_id is not None and coupon.course_id != course_id:
        return None, 0, "Mã giảm giá không áp dụng cho khóa học này."

    # Kiểm tra đơn tối thiểu
    if coupon.min_order_amount and original_price < coupon.min_order_amount:
        return None, 0, f"Đơn hàng tối thiểu {format_vnd(coupon.min_order_amount)} để dùng mã này."

    # Kiểm tra giới hạn /tài khoản
    if coupon.max_uses_per_user and coupon.max_uses_per_user > 0:
        user_usage_count = await db.execute(
            select(func.count(CouponUsage.id)).where(
                CouponUsage.coupon_id == coupon.id,
                CouponUsage.user_id == user_id,
            )
        )
        if (user_usage_count.scalar() or 0) >= coupon.max_uses_per_user:
            return None, 0, f"Bạn đã dùng mã này {coupon.max_uses_per_user} lần rồi."

    # Tính discount
    if coupon.discount_type == "percent":
        discount = original_price * (coupon.discount_value / 100)
    else:
        discount = min(coupon.discount_value, original_price)

    discount = round(discount)
    logger.debug(f"🎫 Coupon {code}: discount={format_vnd(discount)} type={coupon.discount_type}")
    return coupon, discount, ""


# ── Check Coupon ──────────────────────────────────────────

@router.post("/coupon/check", response_model=CouponCheckResponse,
             summary="Kiểm tra mã giảm giá")
async def check_coupon(
    req: CouponCheckRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.info(f"🎫 Check coupon | code={req.code} course={req.course_id} user={current_user.email}")

    # Lấy giá gốc
    course_result = await db.execute(select(Course).where(Course.id == req.course_id))
    course = course_result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Khóa học không tồn tại.")

    coupon, discount, error = await _calc_coupon(
        db, req.code, req.course_id, current_user.id, course.price
    )

    if error:
        return CouponCheckResponse(valid=False, message=error)

    final_price = max(0, course.price - discount)
    return CouponCheckResponse(
        valid=True,
        message="Áp dụng mã thành công!",
        discount_type=coupon.discount_type,
        discount_value=coupon.discount_value,
        discount_amount=discount,
        discount_amount_fmt=format_vnd(discount),
        final_price=final_price,
        final_price_fmt=format_vnd(final_price),
    )


# ── Create Order (Checkout) ───────────────────────────────

@router.post("/create", response_model=OrderSummary, status_code=201,
             summary="Tạo đơn hàng mới — bước 1 checkout")
async def create_order(
    req: CreateOrderRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.info(f"🛒 Create order | course={req.course_id} user={current_user.email} coupon={req.coupon_code}")

    # Lấy khóa học
    course_result = await db.execute(
        select(Course).where(Course.id == req.course_id, Course.is_published == True)
    )
    course = course_result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Khóa học không tồn tại.")

    # Kiểm tra đã mua chưa
    existing_enrollment = await db.execute(
        select(Enrollment).where(
            Enrollment.user_id == current_user.id,
            Enrollment.course_id == req.course_id,
        )
    )
    if existing_enrollment.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Bạn đã mua khóa học này rồi.")

    # Kiểm tra có đơn pending chưa hết hạn
    pending_order = await db.execute(
        select(Order).where(
            Order.user_id == current_user.id,
            Order.course_id == req.course_id,
            Order.status == "pending",
            Order.expires_at > now_utc(),
        )
    )
    existing_pending = pending_order.scalar_one_or_none()
    if existing_pending:
        # Trả lại đơn cũ
        logger.info(f"   Trả lại đơn pending cũ: {existing_pending.order_code}")
        return await _build_order_summary(existing_pending, course, db)

    # Tính giá
    original_price = course.price
    discount_amount = 0
    coupon_discount = 0
    coupon_obj = None
    coupon_code = None

    # Giảm giá từ sale (original_price > price)
    if course.original_price and course.original_price > original_price:
        discount_amount = course.original_price - original_price
        original_price = course.original_price

    # Coupon
    if req.coupon_code:
        coupon_obj, coupon_discount, error = await _calc_coupon(
            db, req.coupon_code, req.course_id, current_user.id, course.price
        )
        if error:
            raise HTTPException(status_code=400, detail=error)
        coupon_code = req.coupon_code.upper().strip()

    final_price = max(0, course.price - coupon_discount)

    # Tạo order
    order_code = generate_order_code()
    expires_at = now_utc() + __import__("datetime").timedelta(minutes=settings.ORDER_EXPIRE_MINUTES)

    order = Order(
        user_id=current_user.id,
        course_id=req.course_id,
        order_code=order_code,
        original_amount=original_price,
        discount_amount=discount_amount,
        amount=final_price,
        coupon_id=coupon_obj.id if coupon_obj else None,
        status="pending",
        expires_at=expires_at,
        payment_method="bank_transfer",
    )
    db.add(order)
    await db.flush()

    log_db("INSERT", "orders", order.id, f"code={order_code} amount={format_vnd(final_price)}")
    log_payment("CREATE", order_code, int(final_price))

    # Ghi coupon usage tạm (sẽ confirm khi thanh toán)
    if coupon_obj:
        usage = CouponUsage(
            coupon_id=coupon_obj.id,
            user_id=current_user.id,
            order_id=order.id,
        )
        db.add(usage)

    await db.commit()
    await db.refresh(order)

    return await _build_order_summary(order, course, db)


async def _build_order_summary(order: Order, course: Course, db: AsyncSession) -> OrderSummary:
    from app.utils.timezone import now_utc
    expires_seconds = max(0, int((order.expires_at - now_utc()).total_seconds())) if order.expires_at else 0

    transfer_content = order.order_code
    qr_url = (
        f"https://img.vietqr.io/image/{settings.BANK_NAME}-"
        f"{settings.BANK_ACCOUNT_NUMBER}-compact2.png"
        f"?amount={int(order.amount)}&addInfo={transfer_content}"
        f"&accountName={settings.BANK_ACCOUNT_NAME}"
    ) if settings.BANK_ACCOUNT_NUMBER else None

    logger.debug(f"   QR URL: {qr_url[:80] + '...' if qr_url and len(qr_url) > 80 else qr_url}")

    return OrderSummary(
        order_id=order.id,
        order_code=order.order_code,
        course_id=course.id,
        course_title=course.title,
        course_thumbnail=course.thumbnail_url,
        original_price=order.original_amount,
        original_price_fmt=format_vnd(order.original_amount),
        discount_amount=order.discount_amount or 0,
        discount_amount_fmt=format_vnd(order.discount_amount or 0),
        coupon_code=None,
        coupon_discount=0,
        coupon_discount_fmt="0 ₫",
        final_price=order.amount,
        final_price_fmt=format_vnd(order.amount),
        bank_name=settings.BANK_NAME,
        bank_account_number=settings.BANK_ACCOUNT_NUMBER,
        bank_account_name=settings.BANK_ACCOUNT_NAME,
        transfer_content=transfer_content,
        qr_url=qr_url,
        expires_at=format_vn_datetime(order.expires_at, "%d/%m/%Y %H:%M:%S"),
        expires_seconds=expires_seconds,
        status=order.status,
    )


# ── Order Status ──────────────────────────────────────────

@router.get("/{order_code}", response_model=OrderSummary,
            summary="Lấy trạng thái đơn hàng")
async def get_order_status(
    order_code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.info(f"📋 Order status | code={order_code} user={current_user.email}")

    result = await db.execute(
        select(Order).where(
            Order.order_code == order_code,
            Order.user_id == current_user.id,
        )
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Đơn hàng không tồn tại.")

    course_result = await db.execute(select(Course).where(Course.id == order.course_id))
    course = course_result.scalar_one_or_none()

    # Tự động expire nếu quá hạn
    if order.status == "pending" and order.expires_at and order.expires_at < now_utc():
        order.status = "expired"
        await db.commit()
        logger.info(f"   Đơn hàng tự động expire: {order_code}")

    return await _build_order_summary(order, course, db)


# ── SePay Webhook ─────────────────────────────────────────

@router.post("/webhook/sepay", include_in_schema=True,
             summary="SePay webhook — tự động mở khóa khi nhận tiền")
async def sepay_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    SePay gọi endpoint này khi có giao dịch ngân hàng.
    Verify HMAC-SHA256 signature, tìm order theo nội dung CK, mở khóa khóa học.
    """
    body = await request.body()
    log_webhook("SePay", "payment", body[:200].decode("utf-8", errors="replace"))

    # Verify HMAC signature
    signature = request.headers.get("X-Webhook-Signature", "")
    if settings.SEPAY_WEBHOOK_SECRET and signature:
        expected = hmac.new(
            settings.SEPAY_WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected.lower(), signature.lower()):
            logger.error(f"❌ SePay webhook signature KHÔNG hợp lệ | expected={expected[:16]}...")
            return {"status": "error", "message": "Invalid signature"}
        logger.debug("✅ SePay webhook signature OK")
    else:
        logger.warning("⚠️ SePay webhook không có signature — bỏ qua verify (dev mode)")

    # Parse payload
    try:
        payload = json.loads(body)
    except Exception as e:
        logger.error(f"❌ SePay webhook parse JSON lỗi: {e}")
        return {"status": "error", "message": "Invalid JSON"}

    content = payload.get("content", "") or payload.get("description", "")
    transfer_amount = float(payload.get("transferAmount", 0) or payload.get("amount", 0))

    logger.info(f"💳 SePay payload | content='{content}' amount={format_vnd(transfer_amount)}")

    # Tìm order trong nội dung chuyển khoản
    # Nội dung CK thường chứa order_code: "DH20260529ABC123"
    order = None
    if content:
        import re
        match = re.search(r"DH\w{14}", content.upper())
        if match:
            order_code = match.group(0)
            logger.info(f"   Tìm thấy order code: {order_code}")
            result = await db.execute(
                select(Order).where(Order.order_code == order_code, Order.status == "pending")
            )
            order = result.scalar_one_or_none()

    if not order:
        logger.warning(f"⚠️ SePay webhook: không tìm thấy order trong content='{content}'")
        return {"status": "ok", "message": "Order not found — ignored"}

    # Kiểm tra số tiền
    if transfer_amount < order.amount * 0.99:  # cho phép lệch 1%
        logger.warning(
            f"⚠️ Số tiền không khớp | expected={format_vnd(order.amount)} "
            f"received={format_vnd(transfer_amount)}"
        )
        return {"status": "error", "message": "Amount mismatch"}

    # Mở khóa khóa học
    log_payment("CONFIRMED", order.order_code, int(transfer_amount), "webhook")

    order.status = "completed"
    order.completed_at = now_utc()
    order.sepay_txn_id = str(payload.get("id", ""))

    # Tạo enrollment
    existing = await db.execute(
        select(Enrollment).where(
            Enrollment.user_id == order.user_id,
            Enrollment.course_id == order.course_id,
        )
    )
    if not existing.scalar_one_or_none():
        enrollment = Enrollment(
            user_id=order.user_id,
            course_id=order.course_id,
            order_id=order.id,
        )
        db.add(enrollment)
        log_db("INSERT", "enrollments", detail=f"user={order.user_id} course={order.course_id}")

    # Cập nhật students_count
    course_result = await db.execute(select(Course).where(Course.id == order.course_id))
    course = course_result.scalar_one_or_none()
    if course:
        course.total_students = (course.total_students or 0) + 1

    # Xác nhận coupon usage
    if order.coupon_id:
        coupon_result = await db.execute(select(Coupon).where(Coupon.id == order.coupon_id))
        coupon = coupon_result.scalar_one_or_none()
        if coupon:
            coupon.used_count = (coupon.used_count or 0) + 1
            log_db("UPDATE", "coupons", coupon.id, f"used_count+1")

    await db.commit()

    log_payment("ENROLLED", order.order_code, int(transfer_amount))
    logger.info(f"🎉 Thanh toán thành công! order={order.order_code} user={order.user_id}")

    # Gửi email xác nhận (background)
    background_tasks.add_task(_send_payment_success_email, order.id)

    return {"status": "ok", "message": "Payment confirmed"}


async def _send_payment_success_email(order_id: UUID):
    """Background task: gửi email xác nhận thanh toán."""
    from app.database import AsyncSessionLocal
    from app.utils.email import send_email, render_order_success_email
    from sqlalchemy.orm import selectinload

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.user), selectinload(Order.course))
        )
        order = result.scalar_one_or_none()
        if not order or not order.user or not order.course:
            logger.warning(f"📧 [BG] Không tìm thấy order/user/course cho email | order_id={order_id}")
            return

    learn_link = f"{settings.FRONTEND_URL}/learn/{order.course.slug}"
    html = render_order_success_email(
        name=order.user.name,
        order_code=order.order_code,
        course_title=order.course.title,
        amount_fmt=format_vnd(order.amount),
        learn_link=learn_link,
    )
    await send_email(
        to=order.user.email,
        subject=f"Xác nhận thanh toán #{order.order_code} — EduVietPro",
        html=html,
    )
