"""
Nhóm bảng: Orders & Payments
- orders       : Đơn hàng (checkout.html, admin-orders.html)
- coupons      : Mã giảm giá (admin-coupons.html, checkout.html)
- coupon_usages: Lịch sử sử dụng mã giảm (giới hạn per-user)
"""

import uuid
from sqlalchemy import (
    Column, String, Boolean, Integer, BigInteger, Text, DateTime,
    ForeignKey, Enum as SAEnum, UniqueConstraint, Index, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Order(Base):
    """
    Đơn hàng — tạo khi user click "Mua ngay", hoàn thành khi SePay webhook OK.
    Trang checkout.html polling /orders/:id/status mỗi 3 giây.
    Admin xem + lọc tại admin-orders.html (filter: status, course, date range).
    """
    __tablename__ = "orders"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Mã đơn hiển thị cho user: DH20260529001
    order_code      = Column(String(50), unique=True, nullable=False, index=True)
    user_id         = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    course_id       = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    # Giá tiền
    original_amount = Column(BigInteger, nullable=False)  # Giá gốc khóa học
    discount_amount = Column(BigInteger, default=0)       # Số tiền được giảm
    amount          = Column(BigInteger, nullable=False)  # Số tiền thực tế thanh toán
    # Coupon
    coupon_id       = Column(UUID(as_uuid=True), ForeignKey("coupons.id"), nullable=True)
    # Affiliate
    affiliate_code  = Column(String(20), nullable=True, index=True)  # ref code
    affiliate_id    = Column(UUID(as_uuid=True), ForeignKey("affiliates.id"), nullable=True)
    # UTM tracking — lọc nguồn trong admin-leads.html và analytics
    utm_source      = Column(String(100), nullable=True)
    utm_medium      = Column(String(100), nullable=True)
    utm_campaign    = Column(String(100), nullable=True)
    utm_content     = Column(String(100), nullable=True)
    # SePay
    sepay_txn_id    = Column(String(255), unique=True, nullable=True)  # Idempotency key
    payment_method  = Column(SAEnum("bank_transfer", "qr", name="payment_method"), default="qr")
    # Trạng thái — filter trong admin-orders.html
    status          = Column(
        SAEnum("pending", "completed", "expired", "cancelled", "refunded", name="order_status"),
        default="pending", nullable=False, index=True
    )
    expires_at      = Column(DateTime(timezone=True), nullable=True)   # +30 phút
    completed_at    = Column(DateTime(timezone=True), nullable=True)
    refunded_at     = Column(DateTime(timezone=True), nullable=True)
    refund_note     = Column(Text, nullable=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user     = relationship("User", back_populates="orders")
    course   = relationship("Course", back_populates="orders")
    coupon   = relationship("Coupon", back_populates="orders")
    affiliate = relationship("Affiliate", back_populates="orders", foreign_keys=[affiliate_id])
    commission = relationship("Commission", back_populates="order", uselist=False)

    __table_args__ = (
        Index("ix_orders_user_status", "user_id", "status"),
        Index("ix_orders_course_status", "course_id", "status"),
        # Filter theo ngày tháng trong admin-orders.html
        Index("ix_orders_created_at", "created_at"),
        Index("ix_orders_status_created", "status", "created_at"),
        CheckConstraint("amount >= 0", name="ck_orders_amount_positive"),
    )


class Coupon(Base):
    """
    Mã giảm giá — CRUD tại admin-coupons.html.
    Nhập mã tại checkout.html (applyCoupon function).
    Filter: status, loại, search code.
    Tạo ngẫu nhiên: genCode() button.
    """
    __tablename__ = "coupons"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code           = Column(String(50), unique=True, nullable=False, index=True)
    description    = Column(String(255), nullable=True)
    discount_type  = Column(SAEnum("percent", "fixed", name="discount_type"), nullable=False)
    discount_value = Column(BigInteger, nullable=False)  # % hoặc số đồng VND
    # Giới hạn
    min_order_amount = Column(BigInteger, default=0)     # Đơn tối thiểu để dùng mã
    max_uses       = Column(Integer, nullable=True)      # NULL = không giới hạn
    max_uses_per_user = Column(Integer, default=1)       # Giới hạn mỗi tài khoản
    used_count     = Column(Integer, default=0)
    # Áp dụng cho khóa cụ thể hay tất cả
    course_id      = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=True)  # NULL = tất cả
    # Thời hạn
    expires_at     = Column(DateTime(timezone=True), nullable=True)  # NULL = không hết hạn
    # Trạng thái — filter trong admin-coupons.html
    is_active      = Column(Boolean, default=True, nullable=False, index=True)
    created_at     = Column(DateTime(timezone=True), server_default=func.now())
    updated_at     = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    orders = relationship("Order", back_populates="coupon")
    usages = relationship("CouponUsage", back_populates="coupon", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_coupons_active_expires", "is_active", "expires_at"),
        CheckConstraint("discount_value > 0", name="ck_coupon_discount_positive"),
    )


class CouponUsage(Base):
    """
    Theo dõi mỗi user đã dùng mã nào bao nhiêu lần.
    Dùng để enforce max_uses_per_user trong Coupon.
    """
    __tablename__ = "coupon_usages"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    coupon_id  = Column(UUID(as_uuid=True), ForeignKey("coupons.id", ondelete="CASCADE"), nullable=False)
    user_id    = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    order_id   = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    used_at    = Column(DateTime(timezone=True), server_default=func.now())

    coupon = relationship("Coupon", back_populates="usages")

    __table_args__ = (
        Index("ix_coupon_usages_user_coupon", "user_id", "coupon_id"),
    )
