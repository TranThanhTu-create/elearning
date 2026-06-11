"""
Nhóm bảng: Users & Authentication
- users              : Tài khoản người dùng (admin + học viên)
- password_reset_tokens : Token reset mật khẩu (forgot-password.html)
- email_verifications   : Token xác thực email sau đăng ký
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, DateTime, Text, Enum as SAEnum,
    ForeignKey, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email         = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)       # NULL nếu đăng ký Google
    name          = Column(String(255), nullable=False)
    phone         = Column(String(20), nullable=True)
    avatar_url    = Column(Text, nullable=True)
    role          = Column(SAEnum("admin", "student", name="user_role"), default="student", nullable=False)
    is_active     = Column(Boolean, default=True, nullable=False)
    is_email_verified = Column(Boolean, default=False, nullable=False)
    google_id     = Column(String(255), unique=True, nullable=True)
    # Affiliate ref code — tự động tạo khi đăng ký
    ref_code      = Column(String(20), unique=True, nullable=True, index=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    deleted_at    = Column(DateTime(timezone=True), nullable=True)  # soft delete
    created_at    = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at    = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    enrollments         = relationship("Enrollment", back_populates="user", lazy="select")
    orders              = relationship("Order", back_populates="user", lazy="select")
    lesson_progress     = relationship("LessonProgress", back_populates="user", lazy="select")
    lesson_notes        = relationship("LessonNote", back_populates="user", lazy="select")
    course_reviews      = relationship("CourseReview", back_populates="user", lazy="select")
    affiliate           = relationship("Affiliate", back_populates="user", uselist=False, lazy="select")
    leads               = relationship("Lead", back_populates="user", lazy="select")
    audit_logs          = relationship("AuditLog", back_populates="user", lazy="select")
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user", lazy="select")
    email_verifications = relationship("EmailVerification", back_populates="user", lazy="select")

    __table_args__ = (
        Index("ix_users_email_active", "email", "is_active"),
        Index("ix_users_role", "role"),
    )

    def __repr__(self):
        return f"<User {self.email} [{self.role}]>"


class PasswordResetToken(Base):
    """
    Dùng cho forgot-password.html — 4 bước:
    1. Nhập email → tạo token
    2. Gửi link email
    3. Click link → verify token → đặt mật khẩu mới
    4. Xóa token
    """
    __tablename__ = "password_reset_tokens"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id    = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token      = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)  # +1 giờ từ lúc tạo
    used_at    = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="password_reset_tokens")


class EmailVerification(Base):
    """
    Xác thực email sau đăng ký tài khoản.
    Token hết hạn sau 24 giờ.
    """
    __tablename__ = "email_verifications"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id    = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token      = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="email_verifications")
