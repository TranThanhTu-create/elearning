"""
Nhóm bảng: Analytics, Leads & Audit
- leads                  : Popup lead magnet (index.html, course-detail.html, blog-detail.html)
- video_watch_events     : Sự kiện xem video (25/50/75/100%) — GA4 + internal
- video_watch_checkpoints: Dữ liệu heatmap % xem — admin-dashboard.html
- page_view_events       : Lượt xem trang (funnel step 2: xem landing page)
- checkout_sessions      : Phiên checkout (funnel step 3: vào trang checkout)
- audit_logs             : Lịch sử hành động admin (ai làm gì lúc mấy giờ UTC+7)
"""

import uuid
from sqlalchemy import (
    Column, String, Boolean, Integer, BigInteger, Text, DateTime,
    ForeignKey, Enum as SAEnum, Index, Float
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Lead(Base):
    """
    Lead từ popup lead magnet.
    Thu thập: họ tên + email + SĐT.
    Lưu vào DB + Google Sheets (8 cột theo PRD).
    Filter tại admin-leads.html: nguồn, ngày, đã mua/chưa mua.
    """
    __tablename__ = "leads"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name         = Column(String(255), nullable=False)
    email        = Column(String(255), nullable=False)
    phone        = Column(String(20), nullable=True)
    # Trang nguồn + UTM — 8 cột Google Sheet
    source_url   = Column(Text, nullable=True)
    utm_source   = Column(String(100), nullable=True)  # facebook, tiktok, organic...
    utm_medium   = Column(String(100), nullable=True)
    utm_campaign = Column(String(100), nullable=True)
    utm_content  = Column(String(100), nullable=True)
    # Đã trở thành user chưa?
    user_id      = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    # Đã đồng bộ Google Sheets chưa?
    synced_to_sheet = Column(Boolean, default=False, nullable=False)
    synced_at    = Column(DateTime(timezone=True), nullable=True)
    ip_address   = Column(String(45), nullable=True)
    # Ngày giờ VN UTC+7 — filter trong admin-leads.html
    created_at   = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="leads")

    __table_args__ = (
        Index("ix_leads_utm_source", "utm_source"),
        Index("ix_leads_created_at", "created_at"),
        Index("ix_leads_email", "email"),
    )


class VideoWatchEvent(Base):
    """
    Sự kiện xem video — ghi nhận tại các mốc 25%, 50%, 75%, 100%.
    Dùng cho:
    - Cột "→ mua khóa" trong admin-dashboard.html (funnel video → mua)
    - Tính tỷ lệ hoàn thành TB mỗi bài học
    - Gửi event lên GA4 (video_progress, video_complete)
    """
    __tablename__ = "video_watch_events"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id       = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # NULL = chưa đăng nhập
    lesson_id     = Column(UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    watch_percent = Column(Integer, nullable=False)   # 25 | 50 | 75 | 100
    watch_seconds = Column(Integer, default=0)
    session_id    = Column(String(100), nullable=True)  # Browser session
    created_at    = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    lesson = relationship("Lesson", back_populates="watch_events")

    __table_args__ = (
        Index("ix_watch_events_lesson_percent", "lesson_id", "watch_percent"),
        Index("ix_watch_events_user_lesson", "user_id", "lesson_id"),
        Index("ix_watch_events_created_at", "created_at"),
    )


class VideoWatchCheckpoint(Base):
    """
    Aggregate dữ liệu xem video theo % thời lượng (0–100%).
    Dùng cho heatmap "Tỷ lệ xem video theo % thời lượng" trong admin-dashboard.html.
    Cập nhật realtime hoặc batch job hàng giờ.
    Mỗi record = 1 lesson + 1 mốc phần trăm.
    """
    __tablename__ = "video_watch_checkpoints"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lesson_id       = Column(UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    # Mốc % (0, 10, 20, ..., 100)
    checkpoint_pct  = Column(Integer, nullable=False)
    # Số lượt xem còn đến mốc này
    viewer_count    = Column(Integer, default=0)
    # Tổng viewer tại checkpoint 0 (để tính %)
    total_views     = Column(Integer, default=0)
    # % retention = viewer_count / total_views
    retention_rate  = Column(Float, default=0.0)
    updated_at      = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    lesson = relationship("Lesson", back_populates="watch_checkpoints")

    __table_args__ = (
        # Unique constraint — mỗi lesson chỉ có 1 record per checkpoint
        Index("ix_checkpoint_lesson_pct", "lesson_id", "checkpoint_pct", unique=True),
    )


class PageViewEvent(Base):
    """
    Lượt xem trang — funnel step 2: Xem video free → Xem landing page khóa.
    Ghi nhận khi user vào /courses/[slug].
    Dùng cho funnel chart trong admin-dashboard.html.
    """
    __tablename__ = "page_view_events"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id    = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    course_id  = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=True)
    page_type  = Column(
        SAEnum("home", "course_list", "course_detail", "blog", "blog_detail", "checkout", name="page_type"),
        nullable=False, index=True
    )
    page_url   = Column(Text, nullable=True)
    referrer   = Column(Text, nullable=True)
    session_id = Column(String(100), nullable=True, index=True)
    utm_source = Column(String(100), nullable=True)
    utm_medium = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    __table_args__ = (
        Index("ix_page_views_course_type", "course_id", "page_type"),
        Index("ix_page_views_created_at", "created_at"),
    )


class CheckoutSession(Base):
    """
    Phiên checkout — funnel step 3: Vào trang checkout.
    Tạo khi user click "Mua ngay", liên kết với order_id.
    Dùng để đo tỷ lệ bỏ giỏ (cart abandonment) trong admin-dashboard.html.
    """
    __tablename__ = "checkout_sessions"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id    = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    course_id  = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    order_id   = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=True)
    # Kết quả: completed | abandoned | expired
    outcome    = Column(
        SAEnum("pending", "completed", "abandoned", "expired", name="checkout_outcome"),
        default="pending", nullable=False, index=True
    )
    session_id = Column(String(100), nullable=True)
    utm_source = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("ix_checkout_sessions_created_at", "created_at"),
        Index("ix_checkout_sessions_course", "course_id", "outcome"),
    )


class AuditLog(Base):
    """
    Ghi log mọi hành động của admin (PRD 4.10 #112).
    VD: "Duyệt rút tiền", "Xóa khóa học", "Tắt mã giảm giá".
    Hiển thị tại admin-settings.html (Phase 2).
    """
    __tablename__ = "audit_logs"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id     = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action      = Column(String(100), nullable=False, index=True)  # VD: "approve_withdrawal"
    resource    = Column(String(100), nullable=True, index=True)   # VD: "withdrawal_requests"
    resource_id = Column(String(255), nullable=True)               # UUID của resource
    description = Column(Text, nullable=True)                       # Mô tả chi tiết
    ip_address  = Column(String(45), nullable=True)
    # Snapshot trước/sau thay đổi
    old_data    = Column(JSONB, nullable=True)
    new_data    = Column(JSONB, nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="audit_logs")

    __table_args__ = (
        Index("ix_audit_logs_user_action", "user_id", "action"),
        Index("ix_audit_logs_created_at", "created_at"),
    )
