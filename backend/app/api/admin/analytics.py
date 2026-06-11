"""
Admin API — Dashboard analytics: doanh thu, học viên, funnel, UTM, video.
"""

from typing import Optional
from uuid import UUID

import pytz

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, extract

from app.models.order import Order
from app.models.course import Course, Enrollment
from app.models.user import User
from app.models.analytics import Lead, PageViewEvent, CheckoutSession, VideoWatchEvent
from app.schemas.analytics import AdminOverviewStats, RevenueByDay, TopCourse, FunnelStep
from app.schemas.common import MessageResponse
from app.utils.deps import get_db, require_admin
from app.utils.formatters import format_vnd, format_number_vn, format_percent
from app.utils.timezone import now_utc, to_vn, format_vn_date
from app.utils.logger import get_logger
from datetime import timedelta, datetime

logger = get_logger(__name__)
router = APIRouter()


# ── Overview ──────────────────────────────────────────────

@router.get("/overview", response_model=AdminOverviewStats, summary="Tổng quan dashboard")
async def get_overview(
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    now = now_utc()
    now_vn = to_vn(now)

    # Today: từ 00:00 đến hiện tại (theo VN)
    today_start = now_vn.replace(hour=0, minute=0, second=0, microsecond=0)
    today_start_utc = today_start.astimezone(pytz.utc)

    # This month
    month_start = now_vn.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_start_utc = month_start.astimezone(pytz.utc)

    # Last month
    if month_start.month == 1:
        last_month_start = month_start.replace(year=month_start.year - 1, month=12)
    else:
        last_month_start = month_start.replace(month=month_start.month - 1)
    last_month_start_utc = last_month_start.astimezone(pytz.utc)

    # Revenue today
    rev_today_r = await db.execute(
        select(func.coalesce(func.sum(Order.amount), 0))
        .where(Order.status == "completed", Order.completed_at >= today_start_utc)
    )
    revenue_today = rev_today_r.scalar_one()

    # Revenue this month
    rev_month_r = await db.execute(
        select(func.coalesce(func.sum(Order.amount), 0))
        .where(Order.status == "completed", Order.completed_at >= month_start_utc)
    )
    revenue_this_month = rev_month_r.scalar_one()

    # Revenue last month
    rev_last_r = await db.execute(
        select(func.coalesce(func.sum(Order.amount), 0))
        .where(
            Order.status == "completed",
            Order.completed_at >= last_month_start_utc,
            Order.completed_at < month_start_utc,
        )
    )
    revenue_last_month = rev_last_r.scalar_one()

    # Revenue change
    if revenue_last_month > 0:
        change_pct = (revenue_this_month - revenue_last_month) / revenue_last_month * 100
        change_positive = change_pct >= 0
        sign = "↑" if change_positive else "↓"
        change_fmt = f"{sign} {abs(change_pct):.1f}% so với tháng trước".replace(".", ",")
    else:
        change_fmt = "—"
        change_positive = True

    # Orders today
    orders_today_r = await db.execute(
        select(func.count())
        .where(Order.status == "completed", Order.completed_at >= today_start_utc)
    )
    orders_today = orders_today_r.scalar_one()

    # Orders this month
    orders_month_r = await db.execute(
        select(func.count())
        .where(Order.status == "completed", Order.completed_at >= month_start_utc)
    )
    orders_this_month = orders_month_r.scalar_one()

    # New students this month (new user registrations via enrollment)
    new_students_r = await db.execute(
        select(func.count())
        .where(User.created_at >= month_start_utc, User.role == "student", User.deleted_at.is_(None))
    )
    new_students = new_students_r.scalar_one()

    # Total students
    total_students_r = await db.execute(
        select(func.count()).where(User.role == "student", User.deleted_at.is_(None))
    )
    total_students = total_students_r.scalar_one()

    # Leads this month
    leads_month_r = await db.execute(
        select(func.count()).where(Lead.created_at >= month_start_utc)
    )
    leads_this_month = leads_month_r.scalar_one()

    # Revenue 30 days
    thirty_days_ago = now - timedelta(days=29)
    daily_r = await db.execute(
        select(
            func.date(Order.completed_at).label("day"),
            func.sum(Order.amount).label("revenue"),
            func.count().label("cnt"),
        )
        .where(Order.status == "completed", Order.completed_at >= thirty_days_ago)
        .group_by(func.date(Order.completed_at))
        .order_by(func.date(Order.completed_at))
    )
    daily_rows = {str(r.day): (r.revenue, r.cnt) for r in daily_r.all()}

    revenue_30_days = []
    for i in range(30):
        day = (thirty_days_ago + timedelta(days=i)).date()
        day_str = str(day)
        rev, cnt = daily_rows.get(day_str, (0, 0))
        revenue_30_days.append(RevenueByDay(
            date=day.strftime("%d/%m"),
            date_iso=day_str,
            revenue=rev or 0,
            revenue_fmt=format_vnd(rev or 0),
            orders_count=cnt or 0,
        ))

    # Top courses (by revenue)
    top_r = await db.execute(
        select(
            Course.id.label("course_id"),
            Course.title,
            func.sum(Order.amount).label("revenue"),
            func.count(Order.id).label("orders_count"),
        )
        .join(Order, Order.course_id == Course.id)
        .where(Order.status == "completed")
        .group_by(Course.id, Course.title)
        .order_by(func.sum(Order.amount).desc())
        .limit(5)
    )
    top_courses = [
        TopCourse(
            course_id=r.course_id,
            title=r.title,
            revenue=r.revenue,
            revenue_fmt=format_vnd(r.revenue),
            orders_count=r.orders_count,
            students_count=r.orders_count,
        )
        for r in top_r.all()
    ]

    return AdminOverviewStats(
        revenue_today=revenue_today,
        revenue_today_fmt=format_vnd(revenue_today),
        revenue_this_month=revenue_this_month,
        revenue_this_month_fmt=format_vnd(revenue_this_month),
        revenue_last_month=revenue_last_month,
        revenue_change_pct_fmt=change_fmt,
        revenue_change_positive=change_positive,
        orders_today=orders_today,
        orders_today_fmt=format_number_vn(orders_today),
        orders_this_month=orders_this_month,
        orders_this_month_fmt=format_number_vn(orders_this_month),
        new_students_this_month=new_students,
        new_students_fmt=format_number_vn(new_students),
        total_students=total_students,
        total_students_fmt=format_number_vn(total_students),
        leads_this_month=leads_this_month,
        leads_this_month_fmt=format_number_vn(leads_this_month),
        revenue_30_days=revenue_30_days,
        top_courses=top_courses,
    )


# ── Revenue chart ─────────────────────────────────────────

@router.get("/revenue", summary="Biểu đồ doanh thu theo ngày / tháng")
async def revenue_chart(
    period: str             = Query("30d", description="7d | 30d | 90d | 12m"),
    course_id: Optional[UUID] = Query(None),
    db: AsyncSession        = Depends(get_db),
    admin                   = Depends(require_admin),
):
    now = now_utc()
    period_map = {"7d": 7, "30d": 30, "90d": 90, "12m": 365}
    days = period_map.get(period, 30)
    start = now - timedelta(days=days)

    q = (
        select(
            func.date(Order.completed_at).label("day"),
            func.sum(Order.amount).label("revenue"),
            func.count().label("cnt"),
        )
        .where(Order.status == "completed", Order.completed_at >= start)
    )
    if course_id:
        q = q.where(Order.course_id == course_id)

    if period == "12m":
        q = (
            select(
                extract("year", Order.completed_at).label("yr"),
                extract("month", Order.completed_at).label("mo"),
                func.sum(Order.amount).label("revenue"),
                func.count().label("cnt"),
            )
            .where(Order.status == "completed", Order.completed_at >= start)
        )
        if course_id:
            q = q.where(Order.course_id == course_id)
        q = q.group_by("yr", "mo").order_by("yr", "mo")
        rows = (await db.execute(q)).all()
        data = [
            {
                "label": f"{int(r.mo):02d}/{int(r.yr)}",
                "revenue": r.revenue or 0,
                "revenue_fmt": format_vnd(r.revenue or 0),
                "orders_count": r.cnt,
            }
            for r in rows
        ]
    else:
        q = q.group_by(func.date(Order.completed_at)).order_by(func.date(Order.completed_at))
        rows = (await db.execute(q)).all()
        row_map = {str(r.day): (r.revenue, r.cnt) for r in rows}
        data = []
        for i in range(days):
            day = (start + timedelta(days=i)).date()
            rev, cnt = row_map.get(str(day), (0, 0))
            data.append({
                "label": day.strftime("%d/%m"),
                "date_iso": str(day),
                "revenue": rev or 0,
                "revenue_fmt": format_vnd(rev or 0),
                "orders_count": cnt or 0,
            })

    total_rev = sum(d["revenue"] for d in data)
    total_orders = sum(d["orders_count"] for d in data)
    return {
        "period": period,
        "total_revenue": total_rev,
        "total_revenue_fmt": format_vnd(total_rev),
        "total_orders": total_orders,
        "data": data,
    }


# ── Course performance ────────────────────────────────────

@router.get("/courses-performance", summary="Hiệu suất từng khóa học")
async def courses_performance(
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(
        select(
            Course.id,
            Course.title,
            Course.is_published,
            Course.price,
            Course.total_students,
            Course.avg_rating,
            func.coalesce(func.sum(Order.amount), 0).label("total_revenue"),
            func.count(Order.id).label("total_orders"),
        )
        .outerjoin(Order, and_(Order.course_id == Course.id, Order.status == "completed"))
        .group_by(Course.id)
        .order_by(func.coalesce(func.sum(Order.amount), 0).desc())
    )
    rows = result.all()

    return [
        {
            "course_id": str(r.id),
            "title": r.title,
            "is_published": r.is_published,
            "price": r.price,
            "price_fmt": format_vnd(r.price),
            "total_students": r.total_students,
            "total_students_fmt": format_number_vn(r.total_students),
            "avg_rating": round(r.avg_rating or 0, 1),
            "total_revenue": r.total_revenue,
            "total_revenue_fmt": format_vnd(r.total_revenue),
            "total_orders": r.total_orders,
        }
        for r in rows
    ]


# ── Funnel ────────────────────────────────────────────────

@router.get("/funnel", summary="Funnel chuyển đổi")
async def conversion_funnel(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str]   = Query(None),
    db: AsyncSession         = Depends(get_db),
    admin                    = Depends(require_admin),
):
    filters = []
    if date_from:
        try:
            filters.append(datetime.fromisoformat(date_from))
        except ValueError:
            pass

    # Step 1: Lượt xem trang
    views_r = await db.execute(select(func.count()).select_from(PageViewEvent))
    total_views = views_r.scalar_one() or 1  # tránh chia 0

    # Step 2: Xem landing page khóa học
    course_views_r = await db.execute(
        select(func.count()).where(PageViewEvent.page_type == "course_detail")
    )
    course_views = course_views_r.scalar_one()

    # Step 3: Vào trang checkout
    checkout_r = await db.execute(select(func.count()).select_from(CheckoutSession))
    checkouts = checkout_r.scalar_one()

    # Step 4: Đơn hoàn thành
    completed_r = await db.execute(
        select(func.count()).where(Order.status == "completed")
    )
    completed_orders = completed_r.scalar_one()

    steps = [
        FunnelStep(
            step=1, label="Lượt truy cập",
            count=total_views, count_fmt=format_number_vn(total_views),
        ),
        FunnelStep(
            step=2, label="Xem khóa học",
            count=course_views, count_fmt=format_number_vn(course_views),
            cvr_from_prev=course_views / total_views if total_views else 0,
            cvr_from_prev_fmt=f"{course_views / total_views * 100:.1f}%".replace(".", ",") if total_views else "0%",
        ),
        FunnelStep(
            step=3, label="Vào thanh toán",
            count=checkouts, count_fmt=format_number_vn(checkouts),
            cvr_from_prev=checkouts / course_views if course_views else 0,
            cvr_from_prev_fmt=f"{checkouts / course_views * 100:.1f}%".replace(".", ",") if course_views else "0%",
        ),
        FunnelStep(
            step=4, label="Đơn thành công",
            count=completed_orders, count_fmt=format_number_vn(completed_orders),
            cvr_from_prev=completed_orders / checkouts if checkouts else 0,
            cvr_from_prev_fmt=f"{completed_orders / checkouts * 100:.1f}%".replace(".", ",") if checkouts else "0%",
        ),
    ]
    return steps


# ── UTM Campaigns ─────────────────────────────────────────

@router.get("/utm-campaigns", summary="Hiệu quả từng chiến dịch UTM")
async def utm_campaigns(
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(
        select(
            Order.utm_source,
            Order.utm_medium,
            Order.utm_campaign,
            func.count(Order.id).label("orders"),
            func.sum(Order.amount).label("revenue"),
        )
        .where(Order.status == "completed", Order.utm_campaign.is_not(None))
        .group_by(Order.utm_source, Order.utm_medium, Order.utm_campaign)
        .order_by(func.sum(Order.amount).desc())
        .limit(50)
    )
    rows = result.all()

    return [
        {
            "utm_source": r.utm_source,
            "utm_medium": r.utm_medium,
            "utm_campaign": r.utm_campaign,
            "orders": r.orders,
            "orders_fmt": format_number_vn(r.orders),
            "revenue": r.revenue or 0,
            "revenue_fmt": format_vnd(r.revenue or 0),
        }
        for r in rows
    ]
