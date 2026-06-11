"""
Admin API — Quản lý khóa học, danh mục, chương, bài học, đánh giá.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, update, delete
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal
from app.models.course import (
    Course, CourseCategory, CourseOutcome, CourseRequirement, CourseFaq,
    CourseReview, Chapter, Lesson, LessonAttachment, Enrollment,
)
from app.schemas.common import PaginatedResponse, MessageResponse
from app.utils.deps import get_db, require_admin, PaginationParams
from app.utils.formatters import format_vnd, format_number_vn
from app.utils.timezone import vn_isoformat, format_vn_datetime, format_vn_date, now_utc
from app.utils.logger import get_logger
from pydantic import BaseModel, Field

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


# ── Schemas ───────────────────────────────────────────────

class AdminCourseListItem(BaseModel):
    id: UUID
    title: str
    slug: str
    price: int
    price_fmt: str
    category: Optional[str] = None
    is_published: bool
    total_lessons: int
    total_students: int
    avg_rating: float
    created_at: str
    updated_at: Optional[str] = None

    model_config = {"from_attributes": True}


class AdminCourseDetail(AdminCourseListItem):
    description: Optional[str] = None
    short_desc: Optional[str] = None
    original_price: Optional[int] = None
    original_price_fmt: Optional[str] = None
    thumbnail_url: Optional[str] = None
    trailer_video_id: Optional[str] = None
    badge: Optional[str] = None
    level: Optional[str] = None
    meta_title: Optional[str] = None
    meta_desc: Optional[str] = None
    outcomes: List[str] = []
    requirements: List[str] = []
    faqs: List[dict] = []
    chapters: List[dict] = []
    total_reviews: int = 0
    order_index: int = 0


class CourseCreateRequest(BaseModel):
    title: str              = Field(..., min_length=2, max_length=500)
    slug: Optional[str]     = None
    description: Optional[str] = None
    short_desc: Optional[str] = Field(None, max_length=500)
    price: int              = Field(..., ge=0)
    original_price: Optional[int] = Field(None, ge=0)
    category_id: Optional[UUID] = None
    level: Optional[str]    = Field(None, pattern="^(beginner|intermediate|advanced)$")
    badge: Optional[str]    = Field(None, pattern="^(bestseller|new|sale|hot)$")
    is_published: bool       = False
    thumbnail_url: Optional[str] = None
    trailer_video_id: Optional[str] = None
    meta_title: Optional[str] = Field(None, max_length=255)
    meta_desc: Optional[str]  = Field(None, max_length=500)
    order_index: int          = 0
    outcomes: List[str]       = []
    requirements: List[str]   = []
    faqs: List[dict]          = []


class CourseUpdateRequest(BaseModel):
    title: Optional[str]        = Field(None, min_length=2, max_length=500)
    slug: Optional[str]         = None
    description: Optional[str]  = None
    short_desc: Optional[str]   = None
    price: Optional[int]        = Field(None, ge=0)
    original_price: Optional[int] = None
    category_id: Optional[UUID] = None
    level: Optional[str]        = None
    badge: Optional[str]        = None
    is_published: Optional[bool] = None
    thumbnail_url: Optional[str] = None
    trailer_video_id: Optional[str] = None
    meta_title: Optional[str]   = None
    meta_desc: Optional[str]    = None
    order_index: Optional[int]  = None
    outcomes: Optional[List[str]] = None
    requirements: Optional[List[str]] = None
    faqs: Optional[List[dict]]  = None


class CategoryCreateRequest(BaseModel):
    name: str           = Field(..., min_length=2, max_length=100)
    slug: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=10)
    order_index: int    = 0
    is_active: bool     = True


class ChapterCreateRequest(BaseModel):
    title: str          = Field(..., min_length=1, max_length=500)
    order_index: int    = 0


class ChapterUpdateRequest(BaseModel):
    title: Optional[str]       = None
    order_index: Optional[int] = None


class LessonCreateRequest(BaseModel):
    title: str                   = Field(..., min_length=1, max_length=500)
    youtube_video_id: Optional[str] = None
    is_free: bool                = False
    duration_seconds: int        = Field(0, ge=0)
    order_index: int             = 0


class LessonUpdateRequest(BaseModel):
    title: Optional[str]            = None
    youtube_video_id: Optional[str] = None
    is_free: Optional[bool]         = None
    duration_seconds: Optional[int] = None
    order_index: Optional[int]      = None


class ReviewVisibilityRequest(BaseModel):
    is_visible: bool


# ── Categories ────────────────────────────────────────────

@router.get("/categories", summary="Danh sách danh mục khóa học")
async def list_categories(
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(
        select(CourseCategory).order_by(CourseCategory.order_index, CourseCategory.name)
    )
    cats = result.scalars().all()
    return [
        {
            "id": str(c.id),
            "name": c.name,
            "slug": c.slug,
            "description": c.description,
            "icon": c.icon,
            "order_index": c.order_index,
            "is_active": c.is_active,
            "created_at": vn_isoformat(c.created_at),
        }
        for c in cats
    ]


@router.post("/categories", status_code=201, summary="Tạo danh mục mới")
async def create_category(
    body: CategoryCreateRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    from slugify import slugify
    slug = body.slug or slugify(body.name, allow_unicode=False)

    existing = await db.execute(select(CourseCategory).where(CourseCategory.slug == slug))
    if existing.scalar_one_or_none():
        raise HTTPException(400, f"Slug '{slug}' đã tồn tại")

    cat = CourseCategory(
        name=body.name,
        slug=slug,
        description=body.description,
        icon=body.icon,
        order_index=body.order_index,
        is_active=body.is_active,
    )
    db.add(cat)
    await db.flush()
    return {"id": str(cat.id), "message": "Tạo danh mục thành công"}


@router.patch("/categories/{cat_id}", summary="Cập nhật danh mục")
async def update_category(
    cat_id: UUID,
    body: CategoryCreateRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(select(CourseCategory).where(CourseCategory.id == cat_id))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(404, "Không tìm thấy danh mục")

    for field, val in body.model_dump(exclude_unset=True).items():
        setattr(cat, field, val)
    return MessageResponse(message="Cập nhật thành công")


@router.delete("/categories/{cat_id}", summary="Xóa danh mục")
async def delete_category(
    cat_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(select(CourseCategory).where(CourseCategory.id == cat_id))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(404, "Không tìm thấy danh mục")
    await db.delete(cat)
    return MessageResponse(message="Đã xóa danh mục")


# ── Courses ───────────────────────────────────────────────

@router.get("", summary="Danh sách khóa học (admin)")
async def list_courses(
    search: Optional[str]    = Query(None),
    category_id: Optional[UUID] = Query(None),
    is_published: Optional[bool] = Query(None),
    page: int                = Query(1, ge=1),
    page_size: int           = Query(20, ge=1, le=100),
    db: AsyncSession         = Depends(get_db),
    admin                    = Depends(require_admin),
):
    pagination = PaginationParams(page=page, page_size=page_size)

    q = select(Course).options(selectinload(Course.category))
    filters = []
    if search:
        filters.append(Course.title.ilike(f"%{search}%"))
    if category_id:
        filters.append(Course.category_id == category_id)
    if is_published is not None:
        filters.append(Course.is_published == is_published)
    if filters:
        q = q.where(and_(*filters))

    total_r = await db.execute(select(func.count()).select_from(q.subquery()))
    total = total_r.scalar_one()

    q = q.order_by(Course.order_index, Course.created_at.desc())
    q = q.offset(pagination.offset).limit(pagination.page_size)
    result = await db.execute(q)
    courses = result.scalars().all()

    items = [
        AdminCourseListItem(
            id=c.id,
            title=c.title,
            slug=c.slug,
            price=c.price,
            price_fmt=format_vnd(c.price),
            category=c.category.name if c.category else None,
            is_published=c.is_published,
            total_lessons=c.total_lessons,
            total_students=c.total_students,
            avg_rating=round(c.avg_rating or 0, 1),
            created_at=vn_isoformat(c.created_at),
            updated_at=vn_isoformat(c.updated_at),
        )
        for c in courses
    ]
    return PaginatedResponse.build(items, total, page, page_size)


@router.get("/{course_id}", summary="Chi tiết khóa học (admin)")
async def get_course_detail(
    course_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(
        select(Course)
        .options(
            selectinload(Course.category),
            selectinload(Course.outcomes),
            selectinload(Course.requirements),
            selectinload(Course.faqs),
            selectinload(Course.chapters).selectinload(Chapter.lessons),
        )
        .where(Course.id == course_id)
    )
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(404, "Không tìm thấy khóa học")

    chapters_data = []
    for ch in sorted(course.chapters, key=lambda x: x.order_index):
        lessons_data = [
            {
                "id": str(l.id),
                "title": l.title,
                "youtube_video_id": l.youtube_video_id,
                "is_free": l.is_free,
                "duration_seconds": l.duration_seconds,
                "duration_fmt": _fmt_duration(l.duration_seconds),
                "order_index": l.order_index,
            }
            for l in sorted(ch.lessons, key=lambda x: x.order_index)
        ]
        chapters_data.append({
            "id": str(ch.id),
            "title": ch.title,
            "order_index": ch.order_index,
            "lessons": lessons_data,
            "lessons_count": len(ch.lessons),
        })

    return AdminCourseDetail(
        id=course.id,
        title=course.title,
        slug=course.slug,
        price=course.price,
        price_fmt=format_vnd(course.price),
        original_price=course.original_price,
        original_price_fmt=format_vnd(course.original_price) if course.original_price else None,
        description=course.description,
        short_desc=course.short_desc,
        thumbnail_url=course.thumbnail_url,
        trailer_video_id=course.trailer_video_id,
        badge=course.badge,
        level=course.level,
        is_published=course.is_published,
        category=course.category.name if course.category else None,
        total_lessons=course.total_lessons,
        total_students=course.total_students,
        avg_rating=round(course.avg_rating or 0, 1),
        total_reviews=course.total_reviews,
        order_index=course.order_index,
        meta_title=course.meta_title,
        meta_desc=course.meta_desc,
        outcomes=[o.content for o in sorted(course.outcomes, key=lambda x: x.order_index)],
        requirements=[r.content for r in sorted(course.requirements, key=lambda x: x.order_index)],
        faqs=[{"question": f.question, "answer": f.answer} for f in sorted(course.faqs, key=lambda x: x.order_index)],
        chapters=chapters_data,
        created_at=vn_isoformat(course.created_at),
        updated_at=vn_isoformat(course.updated_at),
    )


@router.post("", status_code=201, summary="Tạo khóa học mới")
async def create_course(
    body: CourseCreateRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    from slugify import slugify
    slug = body.slug or slugify(body.title, allow_unicode=False)

    existing = await db.execute(select(Course).where(Course.slug == slug))
    if existing.scalar_one_or_none():
        raise HTTPException(400, f"Slug '{slug}' đã tồn tại")

    course = Course(
        title=body.title,
        slug=slug,
        description=body.description,
        short_desc=body.short_desc,
        price=body.price,
        original_price=body.original_price,
        category_id=body.category_id,
        level=body.level,
        badge=body.badge,
        is_published=body.is_published,
        thumbnail_url=body.thumbnail_url,
        trailer_video_id=body.trailer_video_id,
        meta_title=body.meta_title,
        meta_desc=body.meta_desc,
        order_index=body.order_index,
    )
    db.add(course)
    await db.flush()

    for i, text in enumerate(body.outcomes):
        db.add(CourseOutcome(course_id=course.id, content=text, order_index=i))
    for i, text in enumerate(body.requirements):
        db.add(CourseRequirement(course_id=course.id, content=text, order_index=i))
    for i, faq in enumerate(body.faqs):
        db.add(CourseFaq(course_id=course.id, question=faq.get("question", ""), answer=faq.get("answer", ""), order_index=i))

    logger.info(f"Admin {admin.email} tạo khóa học: {course.title}")
    return {"id": str(course.id), "slug": slug, "message": "Tạo khóa học thành công"}


@router.patch("/{course_id}", summary="Cập nhật khóa học")
async def update_course(
    course_id: UUID,
    body: CourseUpdateRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(404, "Không tìm thấy khóa học")

    data = body.model_dump(exclude_unset=True)
    outcomes = data.pop("outcomes", None)
    requirements = data.pop("requirements", None)
    faqs = data.pop("faqs", None)

    for field, val in data.items():
        setattr(course, field, val)

    if outcomes is not None:
        await db.execute(delete(CourseOutcome).where(CourseOutcome.course_id == course_id))
        for i, text in enumerate(outcomes):
            db.add(CourseOutcome(course_id=course_id, content=text, order_index=i))

    if requirements is not None:
        await db.execute(delete(CourseRequirement).where(CourseRequirement.course_id == course_id))
        for i, text in enumerate(requirements):
            db.add(CourseRequirement(course_id=course_id, content=text, order_index=i))

    if faqs is not None:
        await db.execute(delete(CourseFaq).where(CourseFaq.course_id == course_id))
        for i, faq in enumerate(faqs):
            db.add(CourseFaq(course_id=course_id, question=faq.get("question", ""), answer=faq.get("answer", ""), order_index=i))

    logger.info(f"Admin {admin.email} cập nhật khóa học: {course.title}")
    return MessageResponse(message="Cập nhật khóa học thành công")


@router.delete("/{course_id}", summary="Xóa khóa học")
async def delete_course(
    course_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(404, "Không tìm thấy khóa học")

    enrollments = await db.execute(select(func.count()).where(Enrollment.course_id == course_id))
    if enrollments.scalar_one() > 0:
        raise HTTPException(400, "Không thể xóa khóa học đã có học viên mua. Hãy ẩn thay vì xóa.")

    await db.delete(course)
    logger.info(f"Admin {admin.email} xóa khóa học: {course.title}")
    return MessageResponse(message="Đã xóa khóa học")


@router.patch("/{course_id}/publish", summary="Xuất bản / ẩn khóa học")
async def toggle_publish(
    course_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(404, "Không tìm thấy khóa học")
    course.is_published = not course.is_published
    msg = "Đã xuất bản khóa học" if course.is_published else "Đã ẩn khóa học"
    return {"is_published": course.is_published, "message": msg}


# ── Chapters ──────────────────────────────────────────────

@router.post("/{course_id}/chapters", status_code=201, summary="Thêm chương mới")
async def create_chapter(
    course_id: UUID,
    body: ChapterCreateRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    course = (await db.execute(select(Course).where(Course.id == course_id))).scalar_one_or_none()
    if not course:
        raise HTTPException(404, "Không tìm thấy khóa học")

    chapter = Chapter(course_id=course_id, title=body.title, order_index=body.order_index)
    db.add(chapter)
    await db.flush()
    return {"id": str(chapter.id), "message": "Tạo chương thành công"}


@router.patch("/{course_id}/chapters/{chapter_id}", summary="Cập nhật chương")
async def update_chapter(
    course_id: UUID,
    chapter_id: UUID,
    body: ChapterUpdateRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(
        select(Chapter).where(Chapter.id == chapter_id, Chapter.course_id == course_id)
    )
    chapter = result.scalar_one_or_none()
    if not chapter:
        raise HTTPException(404, "Không tìm thấy chương")

    for field, val in body.model_dump(exclude_unset=True).items():
        setattr(chapter, field, val)
    return MessageResponse(message="Cập nhật chương thành công")


@router.delete("/{course_id}/chapters/{chapter_id}", summary="Xóa chương")
async def delete_chapter(
    course_id: UUID,
    chapter_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(
        select(Chapter).where(Chapter.id == chapter_id, Chapter.course_id == course_id)
    )
    chapter = result.scalar_one_or_none()
    if not chapter:
        raise HTTPException(404, "Không tìm thấy chương")
    await db.delete(chapter)
    return MessageResponse(message="Đã xóa chương")


# ── Lessons ───────────────────────────────────────────────

@router.post("/{course_id}/chapters/{chapter_id}/lessons", status_code=201, summary="Thêm bài học")
async def create_lesson(
    course_id: UUID,
    chapter_id: UUID,
    body: LessonCreateRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(
        select(Chapter).where(Chapter.id == chapter_id, Chapter.course_id == course_id)
    )
    chapter = result.scalar_one_or_none()
    if not chapter:
        raise HTTPException(404, "Không tìm thấy chương")

    lesson = Lesson(
        chapter_id=chapter_id,
        title=body.title,
        youtube_video_id=body.youtube_video_id,
        is_free=body.is_free,
        duration_seconds=body.duration_seconds,
        order_index=body.order_index,
    )
    db.add(lesson)
    await db.flush()

    # Cập nhật tổng bài học trong course
    await db.execute(
        update(Course)
        .where(Course.id == course_id)
        .values(total_lessons=Course.total_lessons + 1)
    )
    return {"id": str(lesson.id), "message": "Tạo bài học thành công"}


@router.patch("/{course_id}/chapters/{chapter_id}/lessons/{lesson_id}", summary="Cập nhật bài học")
async def update_lesson(
    course_id: UUID,
    chapter_id: UUID,
    lesson_id: UUID,
    body: LessonUpdateRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(
        select(Lesson).where(Lesson.id == lesson_id, Lesson.chapter_id == chapter_id)
    )
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(404, "Không tìm thấy bài học")

    for field, val in body.model_dump(exclude_unset=True).items():
        setattr(lesson, field, val)
    return MessageResponse(message="Cập nhật bài học thành công")


@router.delete("/{course_id}/chapters/{chapter_id}/lessons/{lesson_id}", summary="Xóa bài học")
async def delete_lesson(
    course_id: UUID,
    chapter_id: UUID,
    lesson_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(
        select(Lesson).where(Lesson.id == lesson_id, Lesson.chapter_id == chapter_id)
    )
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(404, "Không tìm thấy bài học")
    await db.delete(lesson)

    await db.execute(
        update(Course)
        .where(Course.id == course_id)
        .values(total_lessons=func.greatest(Course.total_lessons - 1, 0))
    )
    return MessageResponse(message="Đã xóa bài học")


# ── Reviews ───────────────────────────────────────────────

@router.get("/{course_id}/reviews", summary="Danh sách đánh giá")
async def list_reviews(
    course_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    from app.models.user import User
    pagination = PaginationParams(page=page, page_size=page_size)

    q = (
        select(CourseReview, User.name.label("user_name"), User.email.label("user_email"))
        .join(User, CourseReview.user_id == User.id)
        .where(CourseReview.course_id == course_id)
    )
    total_r = await db.execute(select(func.count()).select_from(q.subquery()))
    total = total_r.scalar_one()

    q = q.order_by(CourseReview.created_at.desc()).offset(pagination.offset).limit(pagination.page_size)
    rows = (await db.execute(q)).all()

    items = [
        {
            "id": str(r.CourseReview.id),
            "user_name": r.user_name,
            "user_email": r.user_email,
            "rating": r.CourseReview.rating,
            "comment": r.CourseReview.comment,
            "is_visible": r.CourseReview.is_visible,
            "created_at": vn_isoformat(r.CourseReview.created_at),
        }
        for r in rows
    ]
    return PaginatedResponse.build(items, total, page, page_size)


@router.patch("/{course_id}/reviews/{review_id}/visibility", summary="Ẩn/hiện đánh giá")
async def set_review_visibility(
    course_id: UUID,
    review_id: UUID,
    body: ReviewVisibilityRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(
        select(CourseReview).where(CourseReview.id == review_id, CourseReview.course_id == course_id)
    )
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(404, "Không tìm thấy đánh giá")
    review.is_visible = body.is_visible
    msg = "Đã hiện đánh giá" if body.is_visible else "Đã ẩn đánh giá"
    return MessageResponse(message=msg)


@router.delete("/{course_id}/reviews/{review_id}", summary="Xóa đánh giá")
async def delete_review(
    course_id: UUID,
    review_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(
        select(CourseReview).where(CourseReview.id == review_id, CourseReview.course_id == course_id)
    )
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(404, "Không tìm thấy đánh giá")
    await db.delete(review)
    return MessageResponse(message="Đã xóa đánh giá")
