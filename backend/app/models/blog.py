"""
Nhóm bảng: Blog
- categories  : Danh mục bài viết (filter tabs blog.html + admin-blog.html)
- tags        : Tag bài viết
- posts       : Bài viết blog (CRUD admin-blog.html TipTap editor)
- post_tags   : Many-to-many posts ↔ tags
- post_courses: Khóa học liên quan cuối bài (blog-detail.html CTA)
"""

import uuid
from sqlalchemy import (
    Column, String, Boolean, Integer, Text, DateTime,
    ForeignKey, Enum as SAEnum, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Category(Base):
    """
    Danh mục blog — filter tabs trong blog.html và admin-blog.html.
    VD: Marketing Online, Kinh Doanh, Quay Video, TikTok, Facebook Ads
    """
    __tablename__ = "categories"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name        = Column(String(100), nullable=False, unique=True)
    slug        = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, default=0)
    is_active   = Column(Boolean, default=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    posts = relationship("Post", back_populates="category", lazy="select")


class Tag(Base):
    """
    Tag bài viết — tag pills trong blog-detail.html, search tags.
    Admin thêm tag khi viết bài (press Enter) trong admin-blog.html.
    """
    __tablename__ = "tags"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name       = Column(String(100), nullable=False, unique=True)
    slug       = Column(String(100), nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    post_tags = relationship("PostTag", back_populates="tag", cascade="all, delete-orphan")


class Post(Base):
    """
    Bài viết blog — CRUD tại admin-blog.html.
    Editor: TipTap → lưu JSON (content) + rendered HTML (content_html).
    Status: draft | published | archived (filter admin-blog.html).
    Hỗ trợ lên lịch đăng: published_at tương lai.
    SEO fields: meta_title, meta_desc, slug.
    """
    __tablename__ = "posts"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id   = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    title         = Column(String(500), nullable=False)
    slug          = Column(String(500), unique=True, nullable=False, index=True)
    # TipTap content — JSONB để query linh hoạt
    content       = Column(JSONB, nullable=True)
    content_html  = Column(Text, nullable=True)     # Rendered HTML để hiển thị
    excerpt       = Column(String(500), nullable=True)
    thumbnail_url = Column(Text, nullable=True)
    # Trạng thái — filter trong admin-blog.html
    status        = Column(
        SAEnum("draft", "published", "archived", name="post_status"),
        default="draft", nullable=False, index=True
    )
    # Lên lịch đăng — published_at tương lai
    published_at  = Column(DateTime(timezone=True), nullable=True, index=True)
    # Thống kê
    view_count    = Column(Integer, default=0)       # Tăng mỗi lần load trang
    reading_time  = Column(Integer, default=0)       # Phút đọc (auto-calculate)
    # SEO — admin-blog.html editor sidebar
    meta_title    = Column(String(255), nullable=True)
    meta_desc     = Column(String(500), nullable=True)
    # Khóa học liên quan để hiển thị CTA cuối bài
    featured_course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=True)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    updated_at    = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    category       = relationship("Category", back_populates="posts")
    post_tags      = relationship("PostTag", back_populates="post", cascade="all, delete-orphan")
    post_courses   = relationship("PostCourse", back_populates="post", cascade="all, delete-orphan")
    featured_course = relationship("Course", foreign_keys=[featured_course_id])

    __table_args__ = (
        Index("ix_posts_status_published", "status", "published_at"),
        Index("ix_posts_category_status", "category_id", "status"),
    )


class PostTag(Base):
    """Many-to-many: posts ↔ tags"""
    __tablename__ = "post_tags"

    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    tag_id  = Column(UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)

    post = relationship("Post", back_populates="post_tags")
    tag  = relationship("Tag", back_populates="post_tags")


class PostCourse(Base):
    """
    Khóa học liên quan cho bài viết.
    Hiển thị CTA mua khóa ở cuối blog-detail.html.
    Admin gán trong admin-blog.html sidebar.
    """
    __tablename__ = "post_courses"

    post_id   = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True)

    post   = relationship("Post", back_populates="post_courses")
    course = relationship("Course", back_populates="post_courses")
