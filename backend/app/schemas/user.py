"""
Pydantic schemas cho User, Auth, Profile.
"""

import re
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator


# ── Đăng ký / Đăng nhập ──────────────────────────────────

class RegisterRequest(BaseModel):
    name: str        = Field(..., min_length=2, max_length=100, description="Họ và tên")
    email: EmailStr  = Field(..., description="Email đăng nhập")
    password: str    = Field(..., min_length=6, max_length=128, description="Mật khẩu (tối thiểu 6 ký tự)")
    phone: Optional[str] = Field(None, max_length=20)
    ref_code: Optional[str] = Field(None, description="Mã giới thiệu affiliate")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v and not re.match(r"^(0|\+84)[0-9]{8,10}$", v.replace(" ", "")):
            raise ValueError("Số điện thoại không hợp lệ")
        return v.replace(" ", "") if v else v


class LoginRequest(BaseModel):
    """
    Hỗ trợ đăng nhập bằng email HOẶC username.
    Demo: admin / admin
    """
    login: str    = Field(..., description="Email hoặc username (VD: admin)")
    password: str = Field(..., min_length=1)

    @field_validator("login")
    @classmethod
    def clean_login(cls, v):
        return v.strip().lower()


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int   # giây
    user: "UserProfile"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ── Password ──────────────────────────────────────────────

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6, max_length=128)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=128)

    @field_validator("new_password")
    @classmethod
    def not_same_as_current(cls, v, info):
        # Không cần check ở đây, service sẽ verify
        return v


# ── Profile ───────────────────────────────────────────────

class UserProfile(BaseModel):
    id: UUID
    email: str
    name: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str
    is_email_verified: bool
    ref_code: Optional[str] = None
    created_at: Optional[str] = None  # ISO format UTC+7

    model_config = {"from_attributes": True}


class UpdateProfileRequest(BaseModel):
    name: Optional[str]  = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v and not re.match(r"^(0|\+84)[0-9]{8,10}$", v.replace(" ", "")):
            raise ValueError("Số điện thoại không hợp lệ")
        return v.replace(" ", "") if v else v


class DeleteAccountRequest(BaseModel):
    password: str = Field(..., description="Xác nhận mật khẩu trước khi xóa")
    confirm_text: str = Field(..., description="Nhập 'XOA TAI KHOAN' để xác nhận")

    @field_validator("confirm_text")
    @classmethod
    def must_match(cls, v):
        if v.strip().upper() != "XOA TAI KHOAN":
            raise ValueError("Vui lòng nhập đúng 'XOA TAI KHOAN'")
        return v


# ── Admin User List ───────────────────────────────────────

class AdminUserItem(BaseModel):
    id: UUID
    email: str
    name: str
    phone: Optional[str] = None
    role: str
    is_active: bool
    is_email_verified: bool
    courses_count: int = 0
    total_spent: float = 0        # số nguyên VND
    total_spent_fmt: str = "0 ₫"  # định dạng VN
    last_login_at: Optional[str] = None
    created_at: str

    model_config = {"from_attributes": True}


class AdminUserDetail(AdminUserItem):
    ref_code: Optional[str] = None
    google_id: Optional[str] = None
    avatar_url: Optional[str] = None
    orders: list = []
    enrollments: list = []
