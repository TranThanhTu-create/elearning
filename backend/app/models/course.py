"""
Nhóm bảng: Courses
- course_categories : Danh mục khóa học (filter tabs — courses.html)
- courses           : Khóa học (CRUD admin-courses.html)
- course_outcomes   : "Bạn sẽ học được gì" (course-detail.html)
- course_requirements: Yêu cầu đầu vào (course-detail.html)
- course_faqs       : FAQ accordion (course-detail.html)
- course_reviews    : Đánh giá sao + nhận xét (course-detail.html)
- chapters          : Chương học (admin-courses.html lessons view)
- lessons           : Bài học (admin-courses.html lessons view)
- lesson_attachments: Tài liệu đính kèm (learn.html tab Tài liệu)
- enrollments       : Quyền truy cập khóa (sau thanh toán)
- lesson_progress   : Tiến độ bài học (checkbox learn.html)
- lesson_notes      : Ghi chú trong khi học (learn.html tab Ghi chú)
"""

import uuid
from sqlalchemy import (
    Column, String, Boolean, Integer, BigInteger, Text, DateTime,
    Float, ForeignKey, Enum as SAEnum, UniqueConstraint, Index, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class CourseCategory(Base):
    """
    Danh mục khóa học — dùng cho filter tabs ở courses.html
    VD: Marketing Online, Kinh Doanh, Quay Video, TikTok, Facebook Ads
    """
    __tablename__ = "course_categories"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name        = Column(String(100), nullable=False, unique=True)
    slug        = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    icon        = Column(String(10), nullable=True)   # emoji icon
    order_index = Column(Integer, default=0)
    is_active   = Column(Boolean, default=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    courses = relationship("Course", back_populates="category", lazy="select")


class Course(Base):
    """
    Khóa học — trung tâm của hệ thống.
    Admin CRUD tại admin-courses.html (view list + view edit).
    """
    __tablename__ = "courses"

    id               = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id      = Column(UUID(as_uuid=True), ForeignKey("course_categories.id"), nullable=True)
    title            = Column(String(500), nullable=False)
    slug             = Column(String(500), unique=True, nullable=False, index=True)
    description      = Column(Text, nullable=True)        # Mô tả dài
    short_desc       = Column(String(500), nullable=True) # Mô tả ngắn (hero section)
    thumbnail_url    = Column(Text, nullable=True)
    trailer_video_id = Column(String(50), nullable=True)  # YouTube videoId public (preview)
    price            = Column(BigInteger, nullable=False)             # VND, đơn vị đồng
    original_price   = Column(BigInteger, nullable=True)             # Giá gốc nếu đang sale
    is_published     = Column(Boolean, default=False, nullable=False, index=True)
    badge            = Column(SAEnum("bestseller", "new", "sale", "hot", name="course_badge"), nullable=True)
    level            = Column(SAEnum("beginner", "intermediate", "advanced", name="course_level"), default="beginner")
    total_lessons    = Column(Integer, default=0)         # Được cập nhật tự động
    total_duration_seconds = Column(Integer, default=0)  # Tổng thời lượng
    total_students   = Column(Integer, default=0)         # Số học viên
    avg_rating       = Column(Float, default=0.0)         # Rating TB (0–5)
    total_reviews    = Column(Integer, default=0)
    order_index      = Column(Integer, default=0)
    # SEO fields (admin-courses.html edit view)
    meta_title       = Column(String(255), nullable=True)
    meta_desc        = Column(String(500), nullable=True)
    created_at       = Column(DateTime(timezone=True), server_default=func.now())
    updated_at       = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    category      = relationship("CourseCategory", back_populates="courses")
    outcomes      = relationship("CourseOutcome", back_populates="course", order_by="CourseOutcome.order_index", cascade="all, delete-orphan")
    requirements  = relationship("CourseRequirement", back_populates="course", order_by="CourseRequirement.order_index", cascade="all, delete-orphan")
    faqs          = relationship("CourseFaq", back_populates="course", order_by="CourseFaq.order_index", cascade="all, delete-orphan")
    reviews       = relationship("CourseReview", back_populates="course", cascade="all, delete-orphan")
    chapters      = relationship("Chapter", back_populates="course", order_by="Chapter.order_index", cascade="all, delete-orphan")
    enrollments   = relationship("Enrollment", back_populates="course")
    orders        = relationship("Order", back_populates="course")
    post_courses  = relationship("PostCourse", back_populates="course")

    __table_args__ = (
        Index("ix_courses_published_category", "is_published", "category_id"),
        CheckConstraint("price >= 0", name="ck_courses_price_positive"),
    )


class CourseOutcome(Base):
    """
    "Bạn sẽ học được gì" — danh sách 4–8 điểm trong course-detail.html
    """
    __tablename__ = "course_outcomes"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id   = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    content     = Column(String(500), nullable=False)
    order_index = Column(Integer, default=0)

    course = relationship("Course", back_populates="outcomes")


class CourseRequirement(Base):
    """
    Yêu cầu đầu vào / điều kiện tiên quyết — course-detail.html
    """
    __tablename__ = "course_requirements"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id   = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    content     = Column(String(500), nullable=False)
    order_index = Column(Integer, default=0)

    course = relationship("Course", back_populates="requirements")


class CourseFaq(Base):
    """
    FAQ accordion trong course-detail.html — toggleFaq()
    """
    __tablename__ = "course_faqs"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id   = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    question    = Column(String(500), nullable=False)
    answer      = Column(Text, nullable=False)
    order_index = Column(Integer, default=0)

    course = relationship("Course", back_populates="faqs")


class CourseReview(Base):
    """
    Đánh giá sao + nhận xét từ học viên — course-detail.html
    Mỗi học viên chỉ review 1 lần / khóa.
    """
    __tablename__ = "course_reviews"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id  = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    user_id    = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    rating     = Column(Integer, nullable=False)         # 1–5 sao
    comment    = Column(Text, nullable=True)
    is_visible = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    course = relationship("Course", back_populates="reviews")
    user   = relationship("User", back_populates="course_reviews")

    __table_args__ = (
        UniqueConstraint("course_id", "user_id", name="uq_review_course_user"),
        CheckConstraint("rating BETWEEN 1 AND 5", name="ck_review_rating_range"),
        Index("ix_reviews_course_visible", "course_id", "is_visible"),
    )


class Chapter(Base):
    """
    Chương học — cấp 2 trong cấu trúc Khóa → Chương → Bài.
    Hiển thị collapse trong course-detail.html và admin-courses.html lessons view.
    """
    __tablename__ = "chapters"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id   = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    title       = Column(String(500), nullable=False)
    order_index = Column(Integer, default=0)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    course  = relationship("Course", back_populates="chapters")
    lessons = relationship("Lesson", back_populates="chapter", order_by="Lesson.order_index", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_chapters_course_order", "course_id", "order_index"),
    )


class Lesson(Base):
    """
    Bài học — cấp 3 trong cấu trúc.
    Admin nhập YouTube videoId tại admin-courses.html.
    is_free toggle → hiển thị free/locked icon trong course-detail.html syllabus.
    """
    __tablename__ = "lessons"

    id               = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id       = Column(UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False)
    title            = Column(String(500), nullable=False)
    youtube_video_id = Column(String(50), nullable=True)   # CHỈ backend + admin thấy nếu is_free=False
    is_free          = Column(Boolean, default=False, nullable=False)
    duration_seconds = Column(Integer, default=0)
    content          = Column(Text, nullable=True)          # Mô tả / ghi chú bài học
    order_index      = Column(Integer, default=0)
    created_at       = Column(DateTime(timezone=True), server_default=func.now())
    updated_at       = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    chapter     = relationship("Chapter", back_populates="lessons")
    attachments = relationship("LessonAttachment", back_populates="lesson", cascade="all, delete-orphan")
    progress    = relationship("LessonProgress", back_populates="lesson", cascade="all, delete-orphan")
    notes       = relationship("LessonNote", back_populates="lesson", cascade="all, delete-orphan")
    watch_events = relationship("VideoWatchEvent", back_populates="lesson", cascade="all, delete-orphan")
    watch_checkpoints = relationship("VideoWatchCheckpoint", back_populates="lesson", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_lessons_chapter_order", "chapter_id", "order_index"),
    )


class LessonAttachment(Base):
    """
    Tài liệu đính kèm (PDF, ZIP...) — tab "Tài liệu (2)" trong learn.html.
    File lưu trên Cloudflare R2.
    """
    __tablename__ = "lesson_attachments"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lesson_id  = Column(UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    file_name  = Column(String(500), nullable=False)
    file_url   = Column(Text, nullable=False)      # Cloudflare R2 URL
    file_size  = Column(BigInteger, default=0)     # bytes
    mime_type  = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    lesson = relationship("Lesson", back_populates="attachments")


class Enrollment(Base):
    """
    Quyền truy cập khóa học của học viên.
    Tạo sau khi webhook SePay xác nhận thanh toán.
    Dùng để check quyền xem video trong learn.html.
    """
    __tablename__ = "enrollments"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id     = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id   = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    last_lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id"), nullable=True)
    progress_percent = Column(Float, default=0.0)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    user   = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    last_lesson = relationship("Lesson", foreign_keys=[last_lesson_id])

    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_enrollment_user_course"),
        Index("ix_enrollments_user", "user_id"),
        Index("ix_enrollments_course", "course_id"),
    )


class LessonProgress(Base):
    """
    Tiến độ từng bài học — checkbox trong sidebar learn.html.
    Mỗi user/lesson có 1 record duy nhất.
    """
    __tablename__ = "lesson_progress"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id      = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lesson_id    = Column(UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    is_completed = Column(Boolean, default=False)
    watch_seconds = Column(Integer, default=0)    # Tổng thời gian xem (seconds)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at   = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user   = relationship("User", back_populates="lesson_progress")
    lesson = relationship("Lesson", back_populates="progress")

    __table_args__ = (
        UniqueConstraint("user_id", "lesson_id", name="uq_progress_user_lesson"),
        Index("ix_progress_user_lesson", "user_id", "lesson_id"),
    )


class LessonNote(Base):
    """
    Ghi chú trong khi xem video — tab "Ghi chú" trong learn.html.
    Auto-save khi người dùng nhập.
    """
    __tablename__ = "lesson_notes"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id    = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lesson_id  = Column(UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    content    = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user   = relationship("User", back_populates="lesson_notes")
    lesson = relationship("Lesson", back_populates="notes")

    __table_args__ = (
        UniqueConstraint("user_id", "lesson_id", name="uq_note_user_lesson"),
    )
