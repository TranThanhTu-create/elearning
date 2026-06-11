"""
Nhóm bảng: Affiliate System
- affiliates           : Thông tin đối tác affiliate (dashboard-affiliate.html)
- affiliate_clicks     : Từng lượt click link affiliate (tracking chuyển đổi)
- commissions          : Hoa hồng từng đơn hàng
- withdrawal_requests  : Yêu cầu rút tiền (admin-affiliate.html duyệt thủ công)
"""

import uuid
from sqlalchemy import (
    Column, String, Boolean, Integer, BigInteger, Text, DateTime,
    ForeignKey, Enum as SAEnum, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Affiliate(Base):
    """
    Mỗi user có 1 affiliate record sau khi kích hoạt.
    ref_code = chuỗi 6 ký tự duy nhất (VD: AN8X2K).
    Thống kê aggregate: total_clicks, total_earnings, pending_withdrawal.
    Hiển thị tại dashboard-affiliate.html và admin-affiliate.html.
    """
    __tablename__ = "affiliates"

    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id             = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    ref_code            = Column(String(20), unique=True, nullable=False)
    is_active           = Column(Boolean, default=True)
    # Aggregate stats — cập nhật khi có click/đơn mới
    total_clicks        = Column(Integer, default=0)
    total_orders        = Column(Integer, default=0)
    total_earnings      = Column(BigInteger, default=0)    # VND — tổng hoa hồng từ trước đến nay
    paid_earnings       = Column(BigInteger, default=0)    # Đã được rút/trả
    pending_withdrawal  = Column(BigInteger, default=0)    # Đang chờ rút
    created_at          = Column(DateTime(timezone=True), server_default=func.now())

    user                = relationship("User", back_populates="affiliate")
    clicks              = relationship("AffiliateClick", back_populates="affiliate", cascade="all, delete-orphan")
    commissions         = relationship("Commission", back_populates="affiliate")
    withdrawal_requests = relationship("WithdrawalRequest", back_populates="affiliate")
    orders              = relationship("Order", back_populates="affiliate", foreign_keys="Order.affiliate_id")

    __table_args__ = (
        Index("ix_affiliates_ref_code", "ref_code"),
    )


class AffiliateClick(Base):
    """
    Từng lượt click link affiliate — tracking chi tiết.
    VD: eduvietpro.vn/courses?ref=AN8X2K
    Cookie 30 ngày → nếu user mua trong 30 ngày, tính hoa hồng cho affiliate.
    Dùng cho biểu đồ click theo tháng trong dashboard-affiliate.html.
    """
    __tablename__ = "affiliate_clicks"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    affiliate_id  = Column(UUID(as_uuid=True), ForeignKey("affiliates.id", ondelete="CASCADE"), nullable=False)
    # User click (có thể NULL nếu chưa đăng nhập)
    visitor_id    = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    # Trang đích
    landing_url   = Column(Text, nullable=True)
    course_id     = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=True)
    # Cookie tracking
    cookie_expires_at = Column(DateTime(timezone=True), nullable=True)  # +30 ngày
    # Đã chuyển đổi thành đơn hàng?
    converted_order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=True)
    converted_at  = Column(DateTime(timezone=True), nullable=True)
    # Device + UTM
    ip_address    = Column(String(45), nullable=True)
    user_agent    = Column(Text, nullable=True)
    utm_source    = Column(String(100), nullable=True)
    utm_medium    = Column(String(100), nullable=True)
    utm_campaign  = Column(String(100), nullable=True)
    created_at    = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    affiliate = relationship("Affiliate", back_populates="clicks")

    __table_args__ = (
        Index("ix_aff_clicks_affiliate_date", "affiliate_id", "created_at"),
        Index("ix_aff_clicks_cookie_expires", "cookie_expires_at"),
    )


class Commission(Base):
    """
    Hoa hồng từng đơn hàng.
    Tạo sau khi SePay webhook thành công + có affiliate_code trong order.
    Hoa hồng = 40% * order.amount.
    Hiển thị trong dashboard-affiliate.html (lịch sử hoa hồng)
    và admin-affiliate.html (quản lý đối tác).
    """
    __tablename__ = "commissions"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    affiliate_id = Column(UUID(as_uuid=True), ForeignKey("affiliates.id"), nullable=False)
    order_id     = Column(UUID(as_uuid=True), ForeignKey("orders.id"), unique=True, nullable=False)
    amount       = Column(BigInteger, nullable=False)    # VND — 40% * order.amount
    rate         = Column(Integer, default=40)           # % hoa hồng tại thời điểm tạo
    # Trạng thái — filter trong admin-affiliate.html và dashboard-affiliate.html
    status       = Column(
        SAEnum("pending", "approved", "paid", "cancelled", name="commission_status"),
        default="pending", nullable=False, index=True
    )
    paid_at      = Column(DateTime(timezone=True), nullable=True)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

    affiliate = relationship("Affiliate", back_populates="commissions")
    order     = relationship("Order", back_populates="commission")

    __table_args__ = (
        Index("ix_commissions_affiliate_status", "affiliate_id", "status"),
        Index("ix_commissions_created_at", "created_at"),
    )


class WithdrawalRequest(Base):
    """
    Yêu cầu rút tiền của affiliate.
    Học viên nhập STK tại dashboard-affiliate.html (modal rút tiền).
    Admin duyệt/từ chối tại admin-affiliate.html tab "Yêu cầu rút tiền".
    Tối thiểu 500.000 ₫.
    """
    __tablename__ = "withdrawal_requests"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    affiliate_id   = Column(UUID(as_uuid=True), ForeignKey("affiliates.id"), nullable=False)
    amount         = Column(BigInteger, nullable=False)    # Số tiền yêu cầu rút (VND)
    # Thông tin ngân hàng — nhập trong modal dashboard-affiliate.html
    bank_name      = Column(String(100), nullable=False)
    account_number = Column(String(50), nullable=False)
    account_name   = Column(String(255), nullable=False)   # Tên chủ TK (in hoa)
    # Trạng thái — admin-affiliate.html duyệt từng yêu cầu
    status         = Column(
        SAEnum("pending", "approved", "rejected", name="withdrawal_status"),
        default="pending", nullable=False, index=True
    )
    admin_note     = Column(Text, nullable=True)           # Ghi chú từ admin khi từ chối
    processed_at   = Column(DateTime(timezone=True), nullable=True)
    created_at     = Column(DateTime(timezone=True), server_default=func.now())

    affiliate = relationship("Affiliate", back_populates="withdrawal_requests")

    __table_args__ = (
        Index("ix_withdrawals_affiliate_status", "affiliate_id", "status"),
        Index("ix_withdrawals_created_at", "created_at"),
    )
