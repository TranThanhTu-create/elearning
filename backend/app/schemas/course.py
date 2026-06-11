"""
Pydantic schemas cho Course, Chapter, Lesson, Progress, Notes.
"""

from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


# ── Lesson ────────────────────────────────────────────────

class LessonBase(BaseModel):
    title: str       = Field(..., min_length=1, max_length=255)
    order_index: int = Field(0, ge=0)
    is_free: bool    = False
    duration_seconds: int = Field(0, ge=0)


class LessonPublic(BaseModel):
    """Trả cho user chưa mua — KHÔNG có video_id."""
    id: UUID
    title: str
    order_index: int
    is_free: bool
    duration_seconds: int
    duration_fmt: str         # "12:34"
    is_completed: bool = False

    model_config = {"from_attributes": True}


class LessonWithVideo(LessonPublic):
    """Trả cho user đã mua — CÓ video_id."""
    video_id: Optional[str] = None    # YouTube video ID
    attachment_url: Optional[str] = None
    attachment_name: Optional[str] = None
    content: Optional[str] = None     # Mô tả bài học


class LessonCreateRequest(BaseModel):
    title: str            = Field(..., min_length=1, max_length=255)
    youtube_video_id: Optional[str] = None
    order_index: int      = Field(0, ge=0)
    is_free: bool         = False
    duration_seconds: int = Field(0, ge=0)
    content: Optional[str] = None


class LessonUpdateRequest(LessonCreateRequest):
    title: Optional[str] = None


# ── Chapter ───────────────────────────────────────────────

class ChapterPublic(BaseModel):
    id: UUID
    title: str
    order_index: int
    lessons: List[LessonPublic] = []
    lessons_count: int = 0
    total_duration_seconds: int = 0
    total_duration_fmt: str = "0:00"

    model_config = {"from_attributes": True}


class ChapterWithVideo(ChapterPublic):
    lessons: List[LessonWithVideo] = []


class ChapterCreateRequest(BaseModel):
    title: str       = Field(..., min_length=1, max_length=255)
    order_index: int = Field(0, ge=0)
    lessons: List[LessonCreateRequest] = []


class ChapterUpdateRequest(BaseModel):
    title: Optional[str]       = None
    order_index: Optional[int] = None


# ── Course ────────────────────────────────────────────────

class CourseListItem(BaseModel):
    id: UUID
    title: str
    slug: str
    subtitle: Optional[str] = None
    thumbnail_url: Optional[str] = None
    price: float
    price_fmt: str              # "1.490.000 ₫"
    original_price: Optional[float] = None
    original_price_fmt: Optional[str] = None
    discount_percent: Optional[int] = None   # 25 (%)
    badge: Optional[str] = None  # "Bestseller" | "Mới" | "Sale"
    level: Optional[str] = None
    category: Optional[str] = None
    total_lessons: int = 0
    total_duration_fmt: str = "0 giờ"
    students_count: int = 0
    is_enrolled: bool = False    # nếu user đã đăng nhập + mua

    model_config = {"from_attributes": True}


class CourseLandingPage(CourseListItem):
    """Đầy đủ thông tin cho /courses/[slug] — landing page bán hàng."""
    description: Optional[str] = None
    outcomes: List[str] = []        # Học viên sẽ học được gì
    requirements: List[str] = []    # Yêu cầu đầu vào
    faq: List[dict] = []           # [{"q": "...", "a": "..."}]
    trailer_video_id: Optional[str] = None
    chapters: List[ChapterPublic] = []
    # SEO
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    # Thống kê
    total_chapters: int = 0
    last_updated: Optional[str] = None   # "29/05/2026"
    # Progress nếu đã mua
    progress_percent: int = 0
    last_lesson_id: Optional[UUID] = None


class CourseCreateRequest(BaseModel):
    title: str            = Field(..., min_length=2, max_length=255)
    subtitle: Optional[str] = Field(None, max_length=500)
    slug: Optional[str]   = None
    description: Optional[str] = None
    outcomes: List[str]   = []
    requirements: List[str] = []
    faq: List[dict]        = []
    price: float           = Field(..., ge=0)
    original_price: Optional[float] = Field(None, ge=0)
    category: Optional[str] = None
    level: Optional[str]   = None
    badge: Optional[str]   = None
    is_published: bool     = False
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    trailer_youtube_id: Optional[str] = None
    chapters: List[ChapterCreateRequest] = []


class CourseUpdateRequest(BaseModel):
    title: Optional[str]    = Field(None, min_length=2, max_length=255)
    subtitle: Optional[str] = None
    slug: Optional[str]     = None
    description: Optional[str] = None
    outcomes: Optional[List[str]] = None
    requirements: Optional[List[str]] = None
    faq: Optional[List[dict]] = None
    price: Optional[float]  = Field(None, ge=0)
    original_price: Optional[float] = None
    category: Optional[str] = None
    level: Optional[str]    = None
    badge: Optional[str]    = None
    is_published: Optional[bool] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    trailer_youtube_id: Optional[str] = None


# ── Progress & Notes ──────────────────────────────────────

class MarkLessonDoneRequest(BaseModel):
    lesson_id: UUID
    watch_seconds: Optional[int] = None  # Số giây đã xem


class LessonNoteCreate(BaseModel):
    lesson_id: UUID
    content: str  = Field(..., min_length=1, max_length=2000)
    timestamp_seconds: Optional[int] = None


class LessonNoteResponse(BaseModel):
    id: UUID
    lesson_id: UUID
    content: str
    timestamp_seconds: Optional[int] = None
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


# ── Dashboard: My Courses ─────────────────────────────────

class EnrolledCourse(BaseModel):
    course_id: UUID
    title: str
    slug: str
    thumbnail_url: Optional[str] = None
    progress_percent: int
    completed_lessons: int
    total_lessons: int
    last_lesson_id: Optional[UUID] = None
    last_lesson_title: Optional[str] = None
    enrolled_at: str

    model_config = {"from_attributes": True}
