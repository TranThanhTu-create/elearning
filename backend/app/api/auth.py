"""
Auth API — Đăng ký, Đăng nhập, Refresh, Logout, Verify Email, Reset Password.

Login hỗ trợ: email HOẶC username (field `login`).
Demo: admin / admin  hoặc  admin@eduvietpro.vn / admin
"""

import secrets
from datetime import timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func

from app.database import AsyncSessionLocal
from app.models.user import User, PasswordResetToken, EmailVerification
from app.schemas.user import (
    RegisterRequest, LoginRequest, TokenResponse, RefreshTokenRequest,
    ForgotPasswordRequest, ResetPasswordRequest, ChangePasswordRequest,
    UserProfile,
)
from app.schemas.common import MessageResponse
from app.utils.deps import get_db, get_current_user
from app.utils.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
    generate_token, generate_ref_code,
)
from app.utils.timezone import now_utc, vn_isoformat, format_vn_datetime
from app.utils.logger import get_logger, log_auth, log_email, log_error
from app.config import settings

logger = get_logger(__name__)
router = APIRouter()


# ── Helpers ───────────────────────────────────────────────

def _build_token_response(user: User) -> TokenResponse:
    access = create_access_token(
        subject=user.id,
        role=user.role,
        secret_key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    refresh = create_refresh_token(
        subject=user.id,
        secret_key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        expires_days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
    )
    profile = UserProfile(
        id=user.id,
        email=user.email,
        name=user.name,
        phone=user.phone,
        avatar_url=user.avatar_url,
        role=user.role,
        is_email_verified=user.is_email_verified,
        ref_code=user.ref_code,
        created_at=vn_isoformat(user.created_at),
    )
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=profile,
    )


async def _send_verify_email_bg(user_id: str, email: str, name: str, token: str):
    """Background task: gửi email xác thực."""
    from app.utils.email import send_email, render_welcome_email
    verify_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    html = render_welcome_email(name=name, verify_link=verify_link)
    await send_email(to=email, subject="Xác thực tài khoản EduVietPro", html=html)


async def _send_reset_password_bg(email: str, name: str, token: str):
    """Background task: gửi email reset password."""
    from app.utils.email import send_email, render_reset_password_email
    reset_link = f"{settings.FRONTEND_URL}/forgot-password?token={token}&step=3"
    html = render_reset_password_email(name=name, reset_link=reset_link)
    await send_email(to=email, subject="Đặt lại mật khẩu EduVietPro", html=html)


# ── Endpoints ─────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=201,
             summary="Đăng ký tài khoản mới bằng email + mật khẩu")
async def register(
    req: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"📝 Đăng ký mới | email={req.email} name={req.name}")

    # Kiểm tra email đã tồn tại
    existing = await db.execute(
        select(User).where(User.email == req.email.lower(), User.deleted_at.is_(None))
    )
    if existing.scalar_one_or_none():
        logger.warning(f"⚠️ Email đã tồn tại: {req.email}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email này đã được đăng ký. Vui lòng dùng email khác hoặc đăng nhập.",
        )

    # Tạo ref_code duy nhất
    ref_code = None
    for _ in range(5):
        candidate = generate_ref_code()
        check = await db.execute(select(User).where(User.ref_code == candidate))
        if not check.scalar_one_or_none():
            ref_code = candidate
            break

    # Tạo user
    user = User(
        email=req.email.lower().strip(),
        name=req.name.strip(),
        phone=req.phone,
        password_hash=hash_password(req.password),
        role="student",
        ref_code=ref_code,
        is_email_verified=False,
    )
    db.add(user)
    await db.flush()  # Lấy user.id

    logger.debug(f"👤 User tạo mới: id={user.id} ref_code={ref_code}")

    # Tạo email verification token
    verify_token = generate_token()
    ev = EmailVerification(
        user_id=user.id,
        token=verify_token,
        expires_at=now_utc() + timedelta(hours=24),
    )
    db.add(ev)
    await db.flush()

    # Tạo Affiliate record tự động
    from app.models.affiliate import Affiliate
    aff_ref = generate_ref_code()
    aff = Affiliate(user_id=user.id, ref_code=aff_ref, is_active=True)
    db.add(aff)

    await db.commit()
    await db.refresh(user)

    log_auth("REGISTER", user.email, True)

    # Gửi email xác thực (background)
    background_tasks.add_task(_send_verify_email_bg, str(user.id), user.email, user.name, verify_token)

    logger.info(f"✅ Đăng ký thành công: {user.email} (id={user.id})")
    return _build_token_response(user)


@router.post("/login", response_model=TokenResponse,
             summary="Đăng nhập bằng email HOẶC username. Demo: admin/admin")
async def login(
    req: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Trường `login` chấp nhận:
    - Email:    admin@eduvietpro.vn
    - Username: admin  (khớp với phần trước @ của email)

    Demo credentials:
    - admin / admin
    - student1@demo.vn / demo1234
    """
    logger.info(f"🔐 Đăng nhập | login={req.login}")

    # Tìm user bằng email HOẶC username (phần trước @ của email)
    login_val = req.login.strip().lower()

    # Nếu chứa @ → tìm theo email
    # Nếu không → tìm theo phần trước @ (username từ email)
    if "@" in login_val:
        query = select(User).where(
            User.email == login_val,
            User.deleted_at.is_(None),
        )
    else:
        # username = phần trước @ của email
        # VD: "admin" khớp "admin@eduvietpro.vn"
        query = select(User).where(
            func.split_part(User.email, "@", 1) == login_val,
            User.deleted_at.is_(None),
        )

    result = await db.execute(query)
    user: Optional[User] = result.scalar_one_or_none()

    if not user:
        log_auth("LOGIN", req.login, False, "user not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email/username hoặc mật khẩu không đúng.",
        )

    # Kiểm tra mật khẩu
    if not user.password_hash or not verify_password(req.password, user.password_hash):
        log_auth("LOGIN", user.email, False, "wrong password")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email/username hoặc mật khẩu không đúng.",
        )

    # Kiểm tra tài khoản active
    if not user.is_active:
        log_auth("LOGIN", user.email, False, "account inactive")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị tạm khóa. Vui lòng liên hệ hỗ trợ.",
        )

    # Cập nhật last_login
    user.last_login_at = now_utc()
    await db.commit()
    await db.refresh(user)

    log_auth("LOGIN", user.email, True)
    logger.info(f"✅ Đăng nhập thành công: {user.email} [{user.role}] id={user.id}")

    return _build_token_response(user)


@router.post("/refresh", response_model=TokenResponse,
             summary="Làm mới access token bằng refresh token")
async def refresh_token(
    req: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    payload = decode_token(req.refresh_token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token không hợp lệ hoặc đã hết hạn.",
        )

    user_id = payload.get("sub")
    result = await db.execute(
        select(User).where(User.id == UUID(user_id), User.deleted_at.is_(None), User.is_active == True)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="Tài khoản không tồn tại.")

    logger.info(f"🔄 Token refreshed: {user.email}")
    return _build_token_response(user)


@router.post("/logout", response_model=MessageResponse,
             summary="Đăng xuất (client xóa token)")
async def logout(current_user: User = Depends(get_current_user)):
    # JWT là stateless — client tự xóa. Server có thể blacklist Redis ở đây.
    logger.info(f"👋 Logout: {current_user.email}")
    return MessageResponse(message="Đăng xuất thành công.")


# ── Email Verification ────────────────────────────────────

@router.post("/verify-email", response_model=MessageResponse,
             summary="Xác thực email sau đăng ký")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"📧 Xác thực email | token={token[:16]}...")

    result = await db.execute(
        select(EmailVerification).where(
            EmailVerification.token == token,
            EmailVerification.verified_at.is_(None),
        )
    )
    ev: Optional[EmailVerification] = result.scalar_one_or_none()

    if not ev:
        logger.warning(f"⚠️ Token xác thực không tồn tại: {token[:16]}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Link xác thực không hợp lệ.",
        )

    if ev.expires_at < now_utc():
        logger.warning(f"⚠️ Token xác thực đã hết hạn: email_verification.id={ev.id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Link xác thực đã hết hạn. Vui lòng yêu cầu gửi lại.",
        )

    # Mark verified
    ev.verified_at = now_utc()

    # Update user
    result2 = await db.execute(select(User).where(User.id == ev.user_id))
    user = result2.scalar_one_or_none()
    if user:
        user.is_email_verified = True
        logger.info(f"✅ Email verified: {user.email}")

    await db.commit()
    return MessageResponse(message="Xác thực email thành công! Bạn có thể đăng nhập ngay.")


@router.post("/resend-verification", response_model=MessageResponse,
             summary="Gửi lại email xác thực")
async def resend_verification(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.is_email_verified:
        return MessageResponse(message="Email của bạn đã được xác thực rồi.")

    # Tạo token mới
    verify_token = generate_token()
    ev = EmailVerification(
        user_id=current_user.id,
        token=verify_token,
        expires_at=now_utc() + timedelta(hours=24),
    )
    db.add(ev)
    await db.commit()

    background_tasks.add_task(
        _send_verify_email_bg, str(current_user.id), current_user.email, current_user.name, verify_token
    )
    logger.info(f"📧 Resend verification: {current_user.email}")
    return MessageResponse(message="Đã gửi lại email xác thực. Vui lòng kiểm tra hộp thư.")


# ── Reset Password ────────────────────────────────────────

@router.post("/forgot-password", response_model=MessageResponse,
             summary="Yêu cầu reset mật khẩu qua email")
async def forgot_password(
    req: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"🔑 Forgot password | email={req.email}")

    result = await db.execute(
        select(User).where(User.email == req.email.lower(), User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()

    # Luôn trả thành công dù email có tồn tại hay không (tránh user enumeration)
    if not user:
        logger.warning(f"⚠️ Forgot password: email không tồn tại {req.email}")
        return MessageResponse(
            message="Nếu email tồn tại trong hệ thống, bạn sẽ nhận được link đặt lại mật khẩu trong vài phút."
        )

    # Xóa token cũ chưa dùng
    old_tokens = await db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used_at.is_(None),
        )
    )
    for old_token in old_tokens.scalars().all():
        await db.delete(old_token)

    # Tạo token mới (hết hạn sau 1 giờ)
    reset_token = generate_token()
    prt = PasswordResetToken(
        user_id=user.id,
        token=reset_token,
        expires_at=now_utc() + timedelta(hours=1),
    )
    db.add(prt)
    await db.commit()

    background_tasks.add_task(_send_reset_password_bg, user.email, user.name, reset_token)
    logger.info(f"✅ Reset token tạo cho: {user.email}")

    return MessageResponse(
        message="Nếu email tồn tại trong hệ thống, bạn sẽ nhận được link đặt lại mật khẩu trong vài phút."
    )


@router.post("/reset-password", response_model=MessageResponse,
             summary="Đặt mật khẩu mới bằng token từ email")
async def reset_password(
    req: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"🔑 Reset password | token={req.token[:16]}...")

    result = await db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token == req.token,
            PasswordResetToken.used_at.is_(None),
        )
    )
    prt: Optional[PasswordResetToken] = result.scalar_one_or_none()

    if not prt:
        raise HTTPException(
            status_code=400,
            detail="Link đặt lại mật khẩu không hợp lệ hoặc đã được sử dụng.",
        )

    if prt.expires_at < now_utc():
        raise HTTPException(
            status_code=400,
            detail="Link đặt lại mật khẩu đã hết hạn. Vui lòng yêu cầu link mới.",
        )

    # Cập nhật mật khẩu
    result2 = await db.execute(select(User).where(User.id == prt.user_id))
    user = result2.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Tài khoản không tồn tại.")

    user.password_hash = hash_password(req.new_password)
    prt.used_at = now_utc()
    await db.commit()

    logger.info(f"✅ Mật khẩu đặt lại thành công: {user.email}")
    log_auth("RESET_PASSWORD", user.email, True)

    return MessageResponse(message="Mật khẩu đã được cập nhật thành công. Vui lòng đăng nhập lại.")


@router.post("/change-password", response_model=MessageResponse,
             summary="Đổi mật khẩu khi đang đăng nhập")
async def change_password(
    req: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"🔑 Change password | user={current_user.email}")

    if not current_user.password_hash:
        raise HTTPException(
            status_code=400,
            detail="Tài khoản đăng ký qua Google không có mật khẩu. Vui lòng dùng Google để đăng nhập.",
        )

    if not verify_password(req.current_password, current_user.password_hash):
        log_auth("CHANGE_PASSWORD", current_user.email, False, "wrong current password")
        raise HTTPException(
            status_code=400,
            detail="Mật khẩu hiện tại không đúng.",
        )

    current_user.password_hash = hash_password(req.new_password)
    await db.commit()

    log_auth("CHANGE_PASSWORD", current_user.email, True)
    logger.info(f"✅ Đổi mật khẩu thành công: {current_user.email}")
    return MessageResponse(message="Mật khẩu đã được cập nhật thành công.")


@router.get("/me", response_model=UserProfile,
            summary="Lấy thông tin user đang đăng nhập")
async def get_me(current_user: User = Depends(get_current_user)):
    logger.debug(f"👤 /me → {current_user.email}")
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        phone=current_user.phone,
        avatar_url=current_user.avatar_url,
        role=current_user.role,
        is_email_verified=current_user.is_email_verified,
        ref_code=current_user.ref_code,
        created_at=vn_isoformat(current_user.created_at),
    )
