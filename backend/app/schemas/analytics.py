"""
Pydantic schemas cho Analytics, Leads, Dashboard thống kê.
"""

from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


# ── Lead ──────────────────────────────────────────────────

class LeadSubmitRequest(BaseModel):
    name: str   = Field(..., min_length=2, max_length=100)
    email: str  = Field(..., min_length=5, max_length=255)
    phone: str  = Field(..., min_length=9, max_length=20)
    # UTM tracking (optional)
    utm_source: Optional[str]   = None
    utm_medium: Optional[str]   = None
    utm_campaign: Optional[str] = None
    utm_term: Optional[str]     = None
    utm_content: Optional[str]  = None
    page_url: Optional[str]     = None


class AdminLeadItem(BaseModel):
    id: UUID
    name: str
    email: str
    phone: Optional[str] = None
    source: Optional[str] = None       # facebook | tiktok | organic | ...
    utm_campaign: Optional[str] = None
    page_url: Optional[str] = None
    is_converted: bool = False          # đã mua khóa học chưa
    status_label: str = "Chưa mua"
    created_at: str

    model_config = {"from_attributes": True}


# ── Analytics Dashboard ───────────────────────────────────

class RevenueByDay(BaseModel):
    date: str            # "29/05"
    date_iso: str        # "2026-05-29"
    revenue: float
    revenue_fmt: str     # "4.500.000 ₫"
    orders_count: int


class TopCourse(BaseModel):
    course_id: UUID
    title: str
    revenue: float
    revenue_fmt: str
    orders_count: int
    students_count: int


class FunnelStep(BaseModel):
    step: int
    label: str           # "Khách truy cập"
    count: int
    count_fmt: str       # "2.480"
    cvr_from_prev: Optional[float] = None   # 0.299 = 29.9%
    cvr_from_prev_fmt: Optional[str] = None  # "29,9%"


class UtmCampaignRow(BaseModel):
    campaign: str
    source: Optional[str] = None
    medium: Optional[str] = None
    page_views: int
    page_views_fmt: str
    leads: int
    leads_fmt: str
    orders: int
    orders_fmt: str
    revenue: float
    revenue_fmt: str
    cvr_fmt: str         # "3,8%"


class VideoAnalyticsRow(BaseModel):
    lesson_id: UUID
    lesson_title: str
    course_title: str
    total_views: int
    total_views_fmt: str
    completion_rate_fmt: str   # "67,3%"
    avg_watch_seconds: int
    avg_watch_fmt: str          # "8:32"


class AdminOverviewStats(BaseModel):
    """Tổng quan admin dashboard."""
    # Revenue
    revenue_today: float
    revenue_today_fmt: str
    revenue_this_month: float
    revenue_this_month_fmt: str
    revenue_last_month: float
    revenue_change_pct_fmt: str   # "↑ 23,5%"
    revenue_change_positive: bool
    # Orders
    orders_today: int
    orders_today_fmt: str
    orders_this_month: int
    orders_this_month_fmt: str
    # Students
    new_students_this_month: int
    new_students_fmt: str
    total_students: int
    total_students_fmt: str
    # Leads
    leads_this_month: int
    leads_this_month_fmt: str
    # Charts
    revenue_30_days: List[RevenueByDay] = []
    top_courses: List[TopCourse] = []
