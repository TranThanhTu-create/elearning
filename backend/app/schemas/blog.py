"""
Pydantic schemas cho Blog.
"""

from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class BlogListItem(BaseModel):
    id: UUID
    title: str
    slug: str
    excerpt: Optional[str] = None
    thumbnail_url: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = []
    reading_time_minutes: int = 5
    view_count: int = 0
    view_count_fmt: str = "0"      # "2.341"
    status: str = "published"
    published_at: Optional[str] = None  # "28/05/2026"
    author_name: str = "EduVietPro"

    model_config = {"from_attributes": True}


class BlogDetail(BlogListItem):
    content: Optional[str] = None    # HTML từ TipTap
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    # CTA khóa học liên quan
    related_course_id: Optional[UUID] = None
    related_course_title: Optional[str] = None
    related_course_slug: Optional[str] = None
    related_course_thumbnail: Optional[str] = None
    # Related posts
    related_posts: List["BlogListItem"] = []


class BlogCreateRequest(BaseModel):
    title: str              = Field(..., min_length=2, max_length=255)
    slug: Optional[str]     = None
    excerpt: Optional[str]  = Field(None, max_length=500)
    content: Optional[str]  = None
    thumbnail_url: Optional[str] = None
    category: Optional[str] = None
    tags: List[str]          = []
    status: str              = Field("draft", pattern="^(draft|published|archived)$")
    published_at: Optional[str] = None    # ISO string — nếu tương lai thì schedule
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    related_course_id: Optional[UUID] = None


class BlogUpdateRequest(BaseModel):
    title: Optional[str]        = Field(None, min_length=2, max_length=255)
    slug: Optional[str]         = None
    excerpt: Optional[str]      = None
    content: Optional[str]      = None
    thumbnail_url: Optional[str] = None
    category: Optional[str]     = None
    tags: Optional[List[str]]   = None
    status: Optional[str]       = None
    published_at: Optional[str] = None
    meta_title: Optional[str]   = None
    meta_description: Optional[str] = None
    related_course_id: Optional[UUID] = None
