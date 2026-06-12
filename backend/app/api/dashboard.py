"""
Dashboard API — Học viên: My Courses, Orders, Profile, Delete Account.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.course import Enrollment, Course, Lesson, Chapter, LessonProgress, LessonNote
from app.models.order import Order
from app.schemas.user import UserProfile, UpdateProfileRequest, DeleteAccountRequest
from app.schemas.course import EnrolledCourse
from app.schemas.order import OrderListItem
from app.schemas.common import MessageResponse
from app.utils.deps import get_db, get_current_user
from app.utils.formatters import format_vnd, format_number_vn
from app.utils.timezone import now_utc, vn_isoformat, format_vn_datetime
from app.utils.security import verify_password, hash_password
from app.utils.logger import get_logger, log_db

logger = get_logger(__name__)
router = APIRouter()


# ── My Courses ────────────────────────────────────────────

@router.get("/my-courses", response_model=List[EnrolledCourse],
            summary="Danh sách khóa học đã mua")
async def get_my_courses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.info(f"📚 My courses | user={current_user.email}")

    result = await db.execute(
        select(Enrollment)
        .where(Enrollment.user_id == current_user.id)
        .options(selectinload(Enrollment.course))
        .order_by(Enrollment.enrolled_at.desc())
    )
    enrollments = result.scalars().all()
    log_db("SELECT", "enrollments", detail=f"user={current_user.id} count={len(enrollments)}")

    items = []
    for e in enrollments:
        c = e.course
        if not c or c.deleted_at is not None:
            continue

        # Đếm tổng bài và bài đã xong
        total_result = await db.execute(
            select(func.count(Lesson.id)).join(Chapter).where(Chapter.course_id == c.id)
        )
        total_lessons = total_result.scalar() or 0

        done_result = await db.execute(
            select(func.count(LessonProgress.id))
            .join(Lesson).join(Chapter)
            .where(
                Chapter.course_id == c.id,
                LessonProgress.user_id == current_user.id,
                LessonProgress.is_completed == True,
            )
        )
        completed = done_result.scalar() or 0

        # Lấy lesson cuối
        last_lesson_title = None
        if e.last_lesson_id:
            ln_result = await db.execute(
                select(Lesson).where(Lesson.id == e.last_lesson_id)
            )
            ln = ln_result.scalar_one_or_none()
            last_lesson_title = ln.title if ln else None

        items.append(EnrolledCourse(
            course_id=c.id,
            title=c.title,
            slug=c.slug,
            thumbnail_url=c.thumbnail_url,
            progress_percent=e.progress_percent or 0,
            completed_lessons=completed,
            total_lessons=total_lessons,
            last_lesson_id=e.last_lesson_id,
            last_lesson_title=last_lesson_title,
            enrolled_at=vn_isoformat(e.enrolled_at),
        ))

    return items


# ── My Orders ─────────────────────────────────────────────

@router.get("/orders", response_model=List[OrderListItem],
            summary="Lịch sử giao dịch cá nhân")
async def get_my_orders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.info(f"🧾 My orders | user={current_user.email}")

    result = await db.execute(
        select(Order)
        .where(Order.user_id == current_user.id)
        .options(selectinload(Order.course))
        .order_by(Order.created_at.desc())
    )
    orders = result.scalars().all()
    log_db("SELECT", "orders", detail=f"user={current_user.id} count={len(orders)}")

    STATUS_LABELS = {
        "pending":   "Chờ thanh toán",
        "completed": "Thành công",
        "expired":   "Hết hạn",
        "cancelled": "Đã hủy",
        "refunded":  "Hoàn tiền",
    }

    return [OrderListItem(
        id=o.id,
        order_code=o.order_code,
        course_title=o.course.title if o.course else "—",
        course_thumbnail=o.course.thumbnail_url if o.course else None,
        final_price=o.amount,
        final_price_fmt=format_vnd(o.amount),
        status=o.status,
        status_label=STATUS_LABELS.get(o.status, o.status),
        paid_at=vn_isoformat(o.completed_at),
        created_at=vn_isoformat(o.created_at),
    ) for o in orders]


# ── Profile ───────────────────────────────────────────────

@router.get("/profile", response_model=UserProfile,
            summary="Thông tin hồ sơ cá nhân")
async def get_profile(current_user: User = Depends(get_current_user)):
    logger.debug(f"👤 Profile | user={current_user.email}")
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        phone=current_user.phone,
        avatar_url=current_user.avatar_url,
        role=current_user.role,
        is_email_verified=current_user.is_email_verified,
        ref_code=current_user.ref_code,
        created_at=vn_isoformat(current_user.created_at),
    )


@router.put("/profile", response_model=UserProfile,
            summary="Cập nhật thông tin cá nhân")
async def update_profile(
    req: UpdateProfileRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.info(f"✏️ Update profile | user={current_user.email}")

    if req.name is not None:
        current_user.name = req.name.strip()
    if req.phone is not None:
        current_user.phone = req.phone

    await db.commit()
    await db.refresh(current_user)
    log_db("UPDATE", "users", current_user.id, "profile updated")

    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        phone=current_user.phone,
        avatar_url=current_user.avatar_url,
        role=current_user.role,
        is_email_verified=current_user.is_email_verified,
        ref_code=current_user.ref_code,
        created_at=vn_isoformat(current_user.created_at),
    )


# ── Lesson Progress ───────────────────────────────────────

@router.post("/lessons/{lesson_id}/complete", response_model=MessageResponse,
             summary="Đánh dấu bài học hoàn thành")
async def complete_lesson(
    lesson_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Kiểm tra lesson tồn tại
    lesson_result = await db.execute(
        select(Lesson).join(Chapter).where(Lesson.id == lesson_id)
    )
    lesson = lesson_result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="Bài học không tồn tại.")

    # Kiểm tra đã enrolled chưa
    chapter_result = await db.execute(select(Chapter).where(Chapter.id == lesson.chapter_id))
    chapter = chapter_result.scalar_one_or_none()
    if chapter:
        enrolled = await db.execute(
            select(Enrollment).where(
                Enrollment.user_id == current_user.id,
                Enrollment.course_id == chapter.course_id,
            )
        )
        enrollment = enrolled.scalar_one_or_none()
        if not enrollment:
            raise HTTPException(status_code=403, detail="Bạn chưa đăng ký khóa học này.")

        # Lưu / cập nhật progress
        prog_result = await db.execute(
            select(LessonProgress).where(
                LessonProgress.user_id == current_user.id,
                LessonProgress.lesson_id == lesson_id,
            )
        )
        prog = prog_result.scalar_one_or_none()
        if not prog:
            prog = LessonProgress(
                user_id=current_user.id,
                lesson_id=lesson_id,
                is_completed=True,
                completed_at=now_utc(),
            )
            db.add(prog)
        else:
            prog.is_completed = True
            prog.completed_at = now_utc()

        # Cập nhật last_lesson + progress_percent
        enrollment.last_lesson_id = lesson_id

        total_result = await db.execute(
            select(func.count(Lesson.id)).join(Chapter).where(Chapter.course_id == chapter.course_id)
        )
        total = total_result.scalar() or 1

        done_result = await db.execute(
            select(func.count(LessonProgress.id))
            .join(Lesson).join(Chapter)
            .where(Chapter.course_id == chapter.course_id, LessonProgress.user_id == current_user.id, LessonProgress.is_completed == True)
        )
        done = (done_result.scalar() or 0) + 1  # +1 vì chưa commit

        enrollment.progress_percent = min(100, int(done / total * 100))
        enrollment.is_completed = enrollment.progress_percent == 100

        await db.commit()
        log_db("UPDATE", "lesson_progress", lesson_id, f"user={current_user.id}")

    return MessageResponse(message="Đã đánh dấu hoàn thành!")


# ── Delete Account ────────────────────────────────────────

@router.delete("/account", response_model=MessageResponse,
               summary="Tự xóa tài khoản (soft delete, 2 bước xác nhận)")
async def delete_account(
    req: DeleteAccountRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.warning(f"⚠️ Delete account request | user={current_user.email}")

    # Xác nhận mật khẩu
    if current_user.password_hash:
        if not verify_password(req.password, current_user.password_hash):
            raise HTTPException(status_code=400, detail="Mật khẩu không đúng.")

    # confirm_text đã validate trong schema

    # Soft delete
    current_user.deleted_at = now_utc()
    current_user.is_active = False
    current_user.email = f"deleted_{current_user.id}@deleted.local"  # giải phóng email

    await db.commit()
    logger.warning(f"🗑️ Account DELETED (soft): id={current_user.id}")

    return MessageResponse(message="Tài khoản của bạn đã được xóa thành công.")
