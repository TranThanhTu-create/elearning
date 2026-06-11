"""
Blog API — Public routes: danh sách bài viết, chi tiết, tìm kiếm.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.models.blog import Post, Category, Tag, PostTag, PostCourse
from app.schemas.blog import BlogListItem, BlogDetail
from app.schemas.common import PaginatedResponse
from app.utils.deps import get_db, PaginationParams
from app.utils.formatters import format_number_vn
from app.utils.timezone import vn_isoformat, format_vn_date, now_utc
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


def _build_list_item(post: Post) -> dict:
    return {
        "id": str(post.id),
        "title": post.title,
        "slug": post.slug,
        "excerpt": post.excerpt,
        "thumbnail_url": post.thumbnail_url,
        "category": post.category.name if post.category else None,
        "tags": [pt.tag.name for pt in post.post_tags if pt.tag],
        "reading_time_minutes": post.reading_time or 5,
        "view_count": post.view_count,
        "view_count_fmt": format_number_vn(post.view_count),
        "status": post.status,
        "published_at": format_vn_date(post.published_at) if post.published_at else None,
        "author_name": "EduVietPro",
    }


@router.get("", summary="Danh sách bài viết (public)")
async def list_posts(
    category: Optional[str] = Query(None),
    tag: Optional[str]      = Query(None),
    search: Optional[str]   = Query(None),
    page: int               = Query(1, ge=1),
    page_size: int          = Query(12, ge=1, le=50),
    db: AsyncSession        = Depends(get_db),
):
    pagination = PaginationParams(page=page, page_size=page_size)
    now = now_utc()

    q = (
        select(Post)
        .options(
            selectinload(Post.category),
            selectinload(Post.post_tags).selectinload(PostTag.tag),
        )
        .where(Post.status == "published", Post.published_at <= now)
    )
    filters = []
    if search:
        filters.append(Post.title.ilike(f"%{search}%"))
    if category:
        cat_r = await db.execute(select(Category).where(Category.slug == category))
        cat = cat_r.scalar_one_or_none()
        if cat:
            filters.append(Post.category_id == cat.id)
    if tag:
        tag_r = await db.execute(select(Tag).where(Tag.slug == tag))
        t = tag_r.scalar_one_or_none()
        if t:
            tag_post_ids_r = await db.execute(
                select(PostTag.post_id).where(PostTag.tag_id == t.id)
            )
            tag_post_ids = [r[0] for r in tag_post_ids_r.all()]
            filters.append(Post.id.in_(tag_post_ids))
    if filters:
        q = q.where(and_(*filters))

    total_r = await db.execute(select(func.count()).select_from(q.subquery()))
    total = total_r.scalar_one()

    q = q.order_by(Post.published_at.desc()).offset(pagination.offset).limit(pagination.page_size)
    posts = (await db.execute(q)).scalars().all()

    items = [_build_list_item(p) for p in posts]
    return PaginatedResponse.build(items, total, page, page_size)


@router.get("/categories", summary="Danh sách danh mục blog (public)")
async def list_public_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Category).where(Category.is_active == True)
        .order_by(Category.order_index, Category.name)
    )
    cats = result.scalars().all()
    return [{"id": str(c.id), "name": c.name, "slug": c.slug} for c in cats]


@router.get("/{slug}", summary="Chi tiết bài viết (public)")
async def get_post_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    now = now_utc()
    result = await db.execute(
        select(Post)
        .options(
            selectinload(Post.category),
            selectinload(Post.post_tags).selectinload(PostTag.tag),
            selectinload(Post.post_courses).selectinload(PostCourse.course),
            selectinload(Post.featured_course),
        )
        .where(Post.slug == slug, Post.status == "published", Post.published_at <= now)
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(404, "Không tìm thấy bài viết")

    # Tăng lượt xem
    post.view_count = (post.view_count or 0) + 1

    # Bài viết liên quan (cùng category, exclude current)
    related = []
    if post.category_id:
        related_r = await db.execute(
            select(Post)
            .options(
                selectinload(Post.category),
                selectinload(Post.post_tags).selectinload(PostTag.tag),
            )
            .where(
                Post.category_id == post.category_id,
                Post.id != post.id,
                Post.status == "published",
                Post.published_at <= now,
            )
            .order_by(Post.published_at.desc())
            .limit(3)
        )
        related = [_build_list_item(p) for p in related_r.scalars().all()]

    featured_course = post.featured_course
    return {
        **_build_list_item(post),
        "content_html": post.content_html,
        "meta_title": post.meta_title or post.title,
        "meta_description": post.meta_desc or post.excerpt,
        "related_course_id": str(featured_course.id) if featured_course else None,
        "related_course_title": featured_course.title if featured_course else None,
        "related_course_slug": featured_course.slug if featured_course else None,
        "related_course_thumbnail": featured_course.thumbnail_url if featured_course else None,
        "related_posts": related,
    }
