"""
Courses API — Public routes cho danh sách khóa học, landing page, học video.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.models.course import Course, CourseCategory, Chapter, Lesson, Enrollment, LessonProgress, LessonNote
from app.schemas.course import (
    CourseListItem, CourseLandingPage, ChapterPublic, ChapterWithVideo,
    LessonPublic, LessonWithVideo, EnrolledCourse,
    MarkLessonDoneRequest, LessonNoteCreate, LessonNoteResponse,
)
from app.schemas.common import PaginatedResponse, MessageResponse
from app.utils.deps import get_db, get_current_user, get_current_user_optional, PaginationParams
from app.utils.formatters import format_vnd, format_number_vn
from app.utils.timezone import vn_isoformat, format_vn_date
from app.utils.logger import get_logger, log_db

logger = get_logger(__name__)
router = APIRouter()


# ── Helpers ───────────────────────────────────────────────

def _fmt_duration(seconds: int) -> str:
    if seconds <= 0:
        return "0:00"
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def _fmt_total_hours(seconds: int) -> str:
    h = seconds / 3600
    if h >= 1:
        return f"{h:.0f} giờ {(seconds % 3600) // 60} phút"
    m = seconds // 60
    return f"{m} phút"


async def _is_enrolled(db: AsyncSession, user_id, course_id) -> bool:
    r = await db.execute(
        select(Enrollment).where(
            Enrollment.user_id == user_id,
            Enrollment.course_id == course_id,
        )
    )
    return r.scalar_one_or_none() is not None


def _course_to_list_item(course: Course, is_enrolled: bool = False) -> CourseListItem:
    original_price = course.original_price
    price = course.price
    discount_pct = None
    if original_price and original_price > price:
        discount_pct = int(round((1 - price / original_price) * 100))

    return CourseListItem(
        id=course.id,
        title=course.title,
        slug=course.slug,
        subtitle=course.short_desc,
        thumbnail_url=course.thumbnail_url,
        price=price,
        price_fmt=format_vnd(price),
        original_price=original_price,
        original_price_fmt=format_vnd(original_price) if original_price else None,
        discount_percent=discount_pct,
        badge=course.badge,
        level=course.level,
        category=course.category.name if course.category else None,
        total_lessons=course.total_lessons or 0,
        total_duration_fmt=_fmt_total_hours(course.total_duration_seconds or 0),
        students_count=course.total_students or 0,
        avg_rating=course.avg_rating or 0.0,
        is_enrolled=is_enrolled,
    )


# ── Categories (public) ──────────────────────────────────

@router.get("/categories", summary="Danh sách danh mục khóa học (public)")
async def list_course_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CourseCategory)
        .where(CourseCategory.is_active == True)
        .order_by(CourseCategory.order_index.asc())
    )
    cats = result.scalars().all()
    return [{"id": c.id, "name": c.name, "slug": c.slug, "icon": c.icon} for c in cats]


# ── List Courses ──────────────────────────────────────────

@router.get("", response_model=PaginatedResponse[CourseListItem],
            summary="Danh sách khóa học (public) — filter, sort, search")
async def list_courses(
    q: Optional[str]        = Query(None, description="Tìm kiếm tên khóa học"),
    category: Optional[str] = Query(None, description="Slug danh mục"),
    level: Optional[str]    = Query(None),
    sort: str               = Query("newest", description="newest|price_asc|price_desc|popular"),
    page: int               = Query(1, ge=1),
    page_size: int          = Query(12, ge=1, le=50),
    db: AsyncSession        = Depends(get_db),
    current_user            = Depends(get_current_user_optional),
):
    logger.info(f"List courses | q={q} category={category} level={level} sort={sort} page={page}")

    filters = [Course.is_published == True]

    if q:
        filters.append(
            or_(
                Course.title.ilike(f"%{q}%"),
                Course.short_desc.ilike(f"%{q}%"),
            )
        )
    if category:
        filters.append(Course.category.has(CourseCategory.slug == category))
    if level:
        filters.append(Course.level == level)

    count_result = await db.execute(select(func.count()).select_from(Course).where(*filters))
    total = count_result.scalar()

    sort_map = {
        "newest":     Course.created_at.desc(),
        "price_asc":  Course.price.asc(),
        "price_desc": Course.price.desc(),
        "popular":    Course.total_students.desc(),
    }
    order_by = sort_map.get(sort, Course.created_at.desc())

    offset = (page - 1) * page_size
    result = await db.execute(
        select(Course)
        .where(*filters)
        .options(selectinload(Course.category))
        .order_by(order_by)
        .offset(offset)
        .limit(page_size)
    )
    courses = result.scalars().all()

    log_db("SELECT", "courses", detail=f"total={total} page={page}")

    items = []
    for c in courses:
        enrolled = False
        if current_user:
            enrolled = await _is_enrolled(db, current_user.id, c.id)
        items.append(_course_to_list_item(c, enrolled))

    return PaginatedResponse.build(items, total, page, page_size)


# ── Course Landing Page ───────────────────────────────────

@router.get("/{slug}", response_model=CourseLandingPage,
            summary="Landing page chi tiết khóa học")
async def get_course_detail(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user_optional),
):
    logger.info(f"Course detail | slug={slug} user={getattr(current_user, 'email', 'anon')}")

    result = await db.execute(
        select(Course)
        .where(Course.slug == slug)
        .options(
            selectinload(Course.category),
            selectinload(Course.chapters).selectinload(Chapter.lessons),
            selectinload(Course.outcomes),
            selectinload(Course.requirements),
            selectinload(Course.faqs),
        )
    )
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=404, detail="Không tìm thấy khóa học.")

    if not course.is_published:
        if not current_user or current_user.role != "admin":
            raise HTTPException(status_code=404, detail="Khóa học không tồn tại.")

    is_enrolled = False
    progress_percent = 0
    last_lesson_id = None

    if current_user:
        is_enrolled = await _is_enrolled(db, current_user.id, course.id)
        if is_enrolled:
            enrollment_result = await db.execute(
                select(Enrollment).where(
                    Enrollment.user_id == current_user.id,
                    Enrollment.course_id == course.id,
                )
            )
            enrollment = enrollment_result.scalar_one_or_none()
            if enrollment:
                progress_percent = int(enrollment.progress_percent or 0)
                last_lesson_id = enrollment.last_lesson_id

    chapters_out = []
    total_lessons = 0
    total_duration = 0

    for chapter in sorted(course.chapters, key=lambda c: c.order_index):
        lessons_out = []
        for lesson in sorted(chapter.lessons, key=lambda l: l.order_index):
            total_lessons += 1
            total_duration += lesson.duration_seconds or 0

            is_completed = False
            if current_user and is_enrolled:
                prog = await db.execute(
                    select(LessonProgress).where(
                        LessonProgress.user_id == current_user.id,
                        LessonProgress.lesson_id == lesson.id,
                        LessonProgress.is_completed == True,
                    )
                )
                is_completed = prog.scalar_one_or_none() is not None

            lessons_out.append(LessonPublic(
                id=lesson.id,
                title=lesson.title,
                order_index=lesson.order_index,
                is_free=lesson.is_free,
                duration_seconds=lesson.duration_seconds or 0,
                duration_fmt=_fmt_duration(lesson.duration_seconds or 0),
                is_completed=is_completed,
                video_id=lesson.youtube_video_id if lesson.is_free else None,
            ))

        chapter_duration = sum(l.duration_seconds or 0 for l in chapter.lessons)
        chapters_out.append(ChapterPublic(
            id=chapter.id,
            title=chapter.title,
            order_index=chapter.order_index,
            lessons=lessons_out,
            lessons_count=len(chapter.lessons),
            total_duration_seconds=chapter_duration,
            total_duration_fmt=_fmt_duration(chapter_duration),
        ))

    original_price = course.original_price
    price = course.price
    discount_pct = None
    if original_price and original_price > price:
        discount_pct = int(round((1 - price / original_price) * 100))

    outcomes_list = [o.content for o in course.outcomes]
    requirements_list = [r.content for r in course.requirements]
    faq_list = [{"q": f.question, "a": f.answer} for f in course.faqs]

    return CourseLandingPage(
        id=course.id,
        title=course.title,
        slug=course.slug,
        subtitle=course.short_desc,
        thumbnail_url=course.thumbnail_url,
        price=price,
        price_fmt=format_vnd(price),
        original_price=original_price,
        original_price_fmt=format_vnd(original_price) if original_price else None,
        discount_percent=discount_pct,
        badge=course.badge,
        level=course.level,
        category=course.category.name if course.category else None,
        description=course.description,
        outcomes=outcomes_list,
        requirements=requirements_list,
        faq=faq_list,
        trailer_video_id=course.trailer_video_id,
        chapters=chapters_out,
        total_lessons=total_lessons,
        total_chapters=len(course.chapters),
        total_duration_fmt=_fmt_total_hours(total_duration),
        students_count=course.total_students or 0,
        avg_rating=course.avg_rating or 0.0,
        meta_title=course.meta_title,
        meta_description=course.meta_desc,
        last_updated=format_vn_date(course.updated_at),
        is_enrolled=is_enrolled,
        progress_percent=progress_percent,
        last_lesson_id=last_lesson_id,
    )


# ── Watch Lesson (protected) ──────────────────────────────

@router.get("/{slug}/learn/{lesson_id}", response_model=LessonWithVideo,
            summary="Xem bài học — yêu cầu đã mua hoặc bài free")
async def watch_lesson(
    slug: str,
    lesson_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user_optional),
):
    logger.info(f"Watch lesson | slug={slug} lesson={lesson_id} user={getattr(current_user,'email','anon')}")

    result = await db.execute(
        select(Lesson)
        .join(Chapter)
        .join(Course)
        .where(
            Lesson.id == lesson_id,
            Course.slug == slug,
        )
        .options(selectinload(Lesson.attachments))
    )
    lesson = result.scalar_one_or_none()

    if not lesson:
        raise HTTPException(status_code=404, detail="Bài học không tồn tại.")

    can_watch = lesson.is_free

    if current_user:
        course_result = await db.execute(
            select(Course).join(Chapter).where(Chapter.id == lesson.chapter_id)
        )
        course = course_result.scalar_one_or_none()

        if course:
            if current_user.role == "admin":
                can_watch = True
            elif await _is_enrolled(db, current_user.id, course.id):
                can_watch = True
                enrollment_result = await db.execute(
                    select(Enrollment).where(
                        Enrollment.user_id == current_user.id,
                        Enrollment.course_id == course.id,
                    )
                )
                enrollment = enrollment_result.scalar_one_or_none()
                if enrollment:
                    enrollment.last_lesson_id = lesson_id
                    await db.commit()

    if not can_watch:
        raise HTTPException(
            status_code=403,
            detail="Bạn cần mua khóa học để xem bài này.",
        )

    is_completed = False
    if current_user:
        prog = await db.execute(
            select(LessonProgress).where(
                LessonProgress.user_id == current_user.id,
                LessonProgress.lesson_id == lesson.id,
            )
        )
        lp = prog.scalar_one_or_none()
        is_completed = lp.is_completed if lp else False

    attachment = lesson.attachments[0] if lesson.attachments else None

    return LessonWithVideo(
        id=lesson.id,
        title=lesson.title,
        order_index=lesson.order_index,
        is_free=lesson.is_free,
        duration_seconds=lesson.duration_seconds or 0,
        duration_fmt=_fmt_duration(lesson.duration_seconds or 0),
        video_id=lesson.youtube_video_id,
        attachment_url=attachment.file_url if attachment else None,
        attachment_name=attachment.file_name if attachment else None,
        content=lesson.content,
        is_completed=is_completed,
    )


# ── Progress ──────────────────────────────────────────────

@router.post("/progress", response_model=MessageResponse,
             summary="Đánh dấu bài học đã hoàn thành")
async def mark_lesson_done(
    req: MarkLessonDoneRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    from app.utils.timezone import now_utc
    logger.info(f"Mark done | lesson={req.lesson_id} user={current_user.email}")

    result = await db.execute(select(Lesson).where(Lesson.id == req.lesson_id))
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="Bài học không tồn tại.")

    chapter_result = await db.execute(select(Chapter).where(Chapter.id == lesson.chapter_id))
    chapter = chapter_result.scalar_one_or_none()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chương học không tồn tại.")

    enrolled = await _is_enrolled(db, current_user.id, chapter.course_id)
    if not enrolled and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Bạn chưa mua khóa học này.")

    prog_result = await db.execute(
        select(LessonProgress).where(
            LessonProgress.user_id == current_user.id,
            LessonProgress.lesson_id == req.lesson_id,
        )
    )
    lp = prog_result.scalar_one_or_none()

    if lp:
        lp.is_completed = True
        if req.watch_seconds:
            lp.watch_seconds = req.watch_seconds
        lp.completed_at = now_utc()
    else:
        lp = LessonProgress(
            user_id=current_user.id,
            lesson_id=req.lesson_id,
            is_completed=True,
            watch_seconds=req.watch_seconds or 0,
            completed_at=now_utc(),
        )
        db.add(lp)

    await db.flush()

    total_count = await db.execute(
        select(func.count(Lesson.id))
        .join(Chapter)
        .where(Chapter.course_id == chapter.course_id)
    )
    total = total_count.scalar() or 1

    done_count = await db.execute(
        select(func.count(LessonProgress.id))
        .join(Lesson)
        .join(Chapter)
        .where(
            Chapter.course_id == chapter.course_id,
            LessonProgress.user_id == current_user.id,
            LessonProgress.is_completed == True,
        )
    )
    done = done_count.scalar() or 0
    percent = int(round(done / total * 100))

    enrollment_result = await db.execute(
        select(Enrollment).where(
            Enrollment.user_id == current_user.id,
            Enrollment.course_id == chapter.course_id,
        )
    )
    enrollment = enrollment_result.scalar_one_or_none()
    if enrollment:
        enrollment.progress_percent = percent
        enrollment.last_lesson_id = req.lesson_id
        if percent >= 100:
            enrollment.completed_at = now_utc()

    await db.commit()
    logger.info(f"   Progress: {done}/{total} = {percent}%")
    return MessageResponse(message=f"Đã ghi nhận hoàn thành. Tiến độ: {percent}%")


# ── Notes ─────────────────────────────────────────────────

@router.get("/notes/{lesson_id}", response_model=List[LessonNoteResponse],
            summary="Lấy ghi chú của bài học")
async def get_notes(
    lesson_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    result = await db.execute(
        select(LessonNote)
        .where(LessonNote.user_id == current_user.id, LessonNote.lesson_id == lesson_id)
        .order_by(LessonNote.timestamp_seconds.asc().nullsfirst(), LessonNote.created_at.asc())
    )
    notes = result.scalars().all()

    return [LessonNoteResponse(
        id=n.id,
        lesson_id=n.lesson_id,
        content=n.content,
        timestamp_seconds=n.timestamp_seconds,
        created_at=vn_isoformat(n.created_at),
        updated_at=vn_isoformat(n.updated_at),
    ) for n in notes]


@router.post("/notes", response_model=LessonNoteResponse, status_code=201,
             summary="Thêm ghi chú bài học")
async def create_note(
    req: LessonNoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    note = LessonNote(
        user_id=current_user.id,
        lesson_id=req.lesson_id,
        content=req.content,
        timestamp_seconds=req.timestamp_seconds,
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)
    log_db("INSERT", "lesson_notes", note.id)

    return LessonNoteResponse(
        id=note.id,
        lesson_id=note.lesson_id,
        content=note.content,
        timestamp_seconds=note.timestamp_seconds,
        created_at=vn_isoformat(note.created_at),
        updated_at=vn_isoformat(note.updated_at),
    )


@router.delete("/notes/{note_id}", response_model=MessageResponse,
               summary="Xóa ghi chú")
async def delete_note(
    note_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    result = await db.execute(
        select(LessonNote).where(
            LessonNote.id == note_id,
            LessonNote.user_id == current_user.id,
        )
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Ghi chú không tồn tại.")

    await db.delete(note)
    await db.commit()
    log_db("DELETE", "lesson_notes", note_id)
    return MessageResponse(message="Đã xóa ghi chú.")
