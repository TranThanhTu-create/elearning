"""
Admin API — Quản lý bài viết blog, danh mục, tag.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, delete
from sqlalchemy.orm import selectinload

from app.models.blog import Post, Category, Tag, PostTag, PostCourse
from app.schemas.blog import BlogCreateRequest, BlogUpdateRequest
from app.schemas.common import PaginatedResponse, MessageResponse
from app.utils.deps import get_db, require_admin, PaginationParams
from app.utils.timezone import vn_isoformat, now_utc
from app.utils.logger import get_logger
from pydantic import BaseModel, Field

logger = get_logger(__name__)
router = APIRouter()


# ── Schemas ───────────────────────────────────────────────

class CategoryCreateRequest(BaseModel):
    name: str           = Field(..., min_length=2, max_length=100)
    slug: Optional[str] = None
    description: Optional[str] = None
    order_index: int    = 0
    is_active: bool     = True


class TagCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: Optional[str] = None


# ── Categories ────────────────────────────────────────────

@router.get("/categories", summary="Danh sách danh mục blog")
async def list_blog_categories(
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(
        select(Category).order_by(Category.order_index, Category.name)
    )
    cats = result.scalars().all()
    return [
        {
            "id": str(c.id),
            "name": c.name,
            "slug": c.slug,
            "description": c.description,
            "order_index": c.order_index,
            "is_active": c.is_active,
            "created_at": vn_isoformat(c.created_at),
        }
        for c in cats
    ]


@router.post("/categories", status_code=201, summary="Tạo danh mục blog")
async def create_blog_category(
    body: CategoryCreateRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    from slugify import slugify
    slug = body.slug or slugify(body.name, allow_unicode=False)

    existing = await db.execute(select(Category).where(Category.slug == slug))
    if existing.scalar_one_or_none():
        raise HTTPException(400, f"Slug '{slug}' đã tồn tại")

    cat = Category(name=body.name, slug=slug, description=body.description,
                   order_index=body.order_index, is_active=body.is_active)
    db.add(cat)
    await db.flush()
    return {"id": str(cat.id), "message": "Tạo danh mục thành công"}


@router.patch("/categories/{cat_id}", summary="Cập nhật danh mục blog")
async def update_blog_category(
    cat_id: UUID,
    body: CategoryCreateRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(select(Category).where(Category.id == cat_id))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(404, "Không tìm thấy danh mục")
    for field, val in body.model_dump(exclude_unset=True).items():
        setattr(cat, field, val)
    return MessageResponse(message="Cập nhật thành công")


@router.delete("/categories/{cat_id}", summary="Xóa danh mục blog")
async def delete_blog_category(
    cat_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(select(Category).where(Category.id == cat_id))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(404, "Không tìm thấy danh mục")
    await db.delete(cat)
    return MessageResponse(message="Đã xóa danh mục")


# ── Tags ──────────────────────────────────────────────────

@router.get("/tags", summary="Danh sách tag")
async def list_tags(
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(select(Tag).order_by(Tag.name))
    tags = result.scalars().all()
    return [{"id": str(t.id), "name": t.name, "slug": t.slug} for t in tags]


@router.post("/tags", status_code=201, summary="Tạo tag mới")
async def create_tag(
    body: TagCreateRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    from slugify import slugify
    slug = body.slug or slugify(body.name, allow_unicode=False)

    existing = await db.execute(select(Tag).where(Tag.slug == slug))
    if existing.scalar_one_or_none():
        raise HTTPException(400, f"Tag '{slug}' đã tồn tại")

    tag = Tag(name=body.name, slug=slug)
    db.add(tag)
    await db.flush()
    return {"id": str(tag.id), "message": "Tạo tag thành công"}


@router.delete("/tags/{tag_id}", summary="Xóa tag")
async def delete_tag(
    tag_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(404, "Không tìm thấy tag")
    await db.delete(tag)
    return MessageResponse(message="Đã xóa tag")


# ── Posts ─────────────────────────────────────────────────

@router.get("", summary="Danh sách bài viết (admin)")
async def list_posts(
    search: Optional[str]     = Query(None),
    status: Optional[str]     = Query(None),
    category_id: Optional[UUID] = Query(None),
    page: int                 = Query(1, ge=1),
    page_size: int            = Query(20, ge=1, le=100),
    db: AsyncSession          = Depends(get_db),
    admin                     = Depends(require_admin),
):
    pagination = PaginationParams(page=page, page_size=page_size)

    q = select(Post).options(selectinload(Post.category), selectinload(Post.post_tags).selectinload(PostTag.tag))
    filters = []
    if search:
        filters.append(Post.title.ilike(f"%{search}%"))
    if status:
        filters.append(Post.status == status)
    if category_id:
        filters.append(Post.category_id == category_id)
    if filters:
        q = q.where(and_(*filters))

    total_r = await db.execute(select(func.count()).select_from(q.subquery()))
    total = total_r.scalar_one()

    q = q.order_by(Post.created_at.desc()).offset(pagination.offset).limit(pagination.page_size)
    posts = (await db.execute(q)).scalars().all()

    items = [
        {
            "id": str(p.id),
            "title": p.title,
            "slug": p.slug,
            "excerpt": p.excerpt,
            "thumbnail_url": p.thumbnail_url,
            "category": p.category.name if p.category else None,
            "tags": [pt.tag.name for pt in p.post_tags if pt.tag],
            "status": p.status,
            "view_count": p.view_count,
            "reading_time": p.reading_time,
            "published_at": vn_isoformat(p.published_at),
            "created_at": vn_isoformat(p.created_at),
            "updated_at": vn_isoformat(p.updated_at),
        }
        for p in posts
    ]
    return PaginatedResponse.build(items, total, page, page_size)


@router.get("/{post_id}", summary="Chi tiết bài viết (admin)")
async def get_post_detail(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(
        select(Post)
        .options(
            selectinload(Post.category),
            selectinload(Post.post_tags).selectinload(PostTag.tag),
            selectinload(Post.post_courses).selectinload(PostCourse.course),
        )
        .where(Post.id == post_id)
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(404, "Không tìm thấy bài viết")

    return {
        "id": str(post.id),
        "title": post.title,
        "slug": post.slug,
        "excerpt": post.excerpt,
        "content": post.content,
        "content_html": post.content_html,
        "thumbnail_url": post.thumbnail_url,
        "category_id": str(post.category_id) if post.category_id else None,
        "category": post.category.name if post.category else None,
        "tags": [pt.tag.name for pt in post.post_tags if pt.tag],
        "status": post.status,
        "view_count": post.view_count,
        "reading_time": post.reading_time,
        "meta_title": post.meta_title,
        "meta_desc": post.meta_desc,
        "published_at": vn_isoformat(post.published_at),
        "featured_course_id": str(post.featured_course_id) if post.featured_course_id else None,
        "related_courses": [str(pc.course_id) for pc in post.post_courses],
        "created_at": vn_isoformat(post.created_at),
        "updated_at": vn_isoformat(post.updated_at),
    }


@router.post("", status_code=201, summary="Tạo bài viết mới")
async def create_post(
    body: BlogCreateRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    from slugify import slugify
    from datetime import datetime
    import math

    slug = body.slug or slugify(body.title, allow_unicode=False)
    existing = await db.execute(select(Post).where(Post.slug == slug))
    if existing.scalar_one_or_none():
        raise HTTPException(400, f"Slug '{slug}' đã tồn tại")

    # Tìm category_id từ tên category
    category_id = None
    if body.category:
        cat_r = await db.execute(select(Category).where(Category.name == body.category))
        cat = cat_r.scalar_one_or_none()
        if cat:
            category_id = cat.id

    # Tính reading_time xấp xỉ từ content
    reading_time = 5
    if body.content:
        word_count = len(body.content.split())
        reading_time = max(1, math.ceil(word_count / 200))

    # Parse published_at
    published_at = None
    if body.published_at:
        try:
            published_at = datetime.fromisoformat(body.published_at)
        except ValueError:
            pass

    post = Post(
        title=body.title,
        slug=slug,
        excerpt=body.excerpt,
        content=body.content,
        content_html=body.content,
        thumbnail_url=body.thumbnail_url,
        category_id=category_id,
        status=body.status,
        published_at=published_at,
        meta_title=body.meta_title,
        meta_desc=body.meta_description,
        reading_time=reading_time,
        featured_course_id=body.related_course_id,
    )
    db.add(post)
    await db.flush()

    # Thêm tags
    for tag_name in body.tags:
        tag_r = await db.execute(select(Tag).where(Tag.name == tag_name))
        tag = tag_r.scalar_one_or_none()
        if not tag:
            from slugify import slugify as sl
            tag = Tag(name=tag_name, slug=sl(tag_name, allow_unicode=False))
            db.add(tag)
            await db.flush()
        db.add(PostTag(post_id=post.id, tag_id=tag.id))

    logger.info(f"Admin {admin.email} tạo bài viết: {post.title}")
    return {"id": str(post.id), "slug": slug, "message": "Tạo bài viết thành công"}


@router.patch("/{post_id}", summary="Cập nhật bài viết")
async def update_post(
    post_id: UUID,
    body: BlogUpdateRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    from datetime import datetime

    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(404, "Không tìm thấy bài viết")

    data = body.model_dump(exclude_unset=True)
    tags = data.pop("tags", None)

    if "category" in data:
        cat_name = data.pop("category")
        if cat_name:
            cat_r = await db.execute(select(Category).where(Category.name == cat_name))
            cat = cat_r.scalar_one_or_none()
            post.category_id = cat.id if cat else None
        else:
            post.category_id = None

    if "published_at" in data:
        val = data.pop("published_at")
        try:
            post.published_at = datetime.fromisoformat(val) if val else None
        except ValueError:
            pass

    if "meta_description" in data:
        post.meta_desc = data.pop("meta_description")

    if "related_course_id" in data:
        post.featured_course_id = data.pop("related_course_id")

    for field, val in data.items():
        if hasattr(post, field):
            setattr(post, field, val)

    if tags is not None:
        await db.execute(delete(PostTag).where(PostTag.post_id == post_id))
        for tag_name in tags:
            tag_r = await db.execute(select(Tag).where(Tag.name == tag_name))
            tag = tag_r.scalar_one_or_none()
            if not tag:
                from slugify import slugify as sl
                tag = Tag(name=tag_name, slug=sl(tag_name, allow_unicode=False))
                db.add(tag)
                await db.flush()
            db.add(PostTag(post_id=post_id, tag_id=tag.id))

    logger.info(f"Admin {admin.email} cập nhật bài viết: {post.title}")
    return MessageResponse(message="Cập nhật bài viết thành công")


@router.delete("/{post_id}", summary="Xóa bài viết")
async def delete_post(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(404, "Không tìm thấy bài viết")
    await db.delete(post)
    logger.info(f"Admin {admin.email} xóa bài viết: {post.title}")
    return MessageResponse(message="Đã xóa bài viết")


@router.patch("/{post_id}/publish", summary="Xuất bản / ẩn bài viết")
async def toggle_post_publish(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    from app.utils.timezone import now_utc
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(404, "Không tìm thấy bài viết")

    if post.status == "published":
        post.status = "draft"
        msg = "Đã ẩn bài viết"
    else:
        post.status = "published"
        if not post.published_at:
            post.published_at = now_utc()
        msg = "Đã xuất bản bài viết"

    return {"status": post.status, "message": msg}
