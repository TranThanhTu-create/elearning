"""
FastAPI Dependencies — get_db, get_current_user, require_admin, v.v.
"""

from typing import AsyncGenerator, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.utils.security import decode_token
from app.utils.logger import get_logger
from app.config import settings

logger = get_logger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)


# ── Database session ──────────────────────────────────────

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency inject DB session cho mỗi request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
            logger.debug("🗄️  DB session committed")
        except Exception as exc:
            await session.rollback()
            logger.error(f"💥 DB session rollback: {exc}", exc_info=True)
            raise
        finally:
            await session.close()


# ── Auth ──────────────────────────────────────────────────

async def _get_token_payload(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Optional[dict]:
    """Extract JWT payload từ Authorization header. Trả None nếu không có."""
    if not credentials:
        return None
    payload = decode_token(
        credentials.credentials,
        settings.JWT_SECRET_KEY,
        settings.JWT_ALGORITHM,
    )
    return payload


async def get_current_user_optional(
    db: AsyncSession = Depends(get_db),
    payload: Optional[dict] = Depends(_get_token_payload),
):
    """
    Trả user hiện tại nếu có token hợp lệ, ngược lại trả None.
    Dùng cho các route public có thể có auth (vd: course detail).
    """
    if payload is None:
        return None
    return await _load_user(db, payload)


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    payload: Optional[dict] = Depends(_get_token_payload),
):
    """
    Yêu cầu đăng nhập. Raise 401 nếu không có token hoặc token lỗi.
    """
    if payload is None:
        logger.warning("🚫 Request thiếu token hoặc token không hợp lệ")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bạn cần đăng nhập để thực hiện thao tác này",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await _load_user(db, payload)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản không tồn tại hoặc đã bị xóa",
        )
    return user


async def require_admin(user=Depends(get_current_user)):
    """
    Chỉ cho phép admin. Raise 403 nếu không phải admin.
    """
    if user.role != "admin":
        logger.warning(f"🚫 User {user.email} cố truy cập admin route (role={user.role})")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập tính năng này",
        )
    logger.debug(f"✅ Admin access granted: {user.email}")
    return user


async def _load_user(db: AsyncSession, payload: dict):
    """Load user từ DB theo sub trong JWT payload."""
    from app.models.user import User

    user_id_str = payload.get("sub")
    token_type  = payload.get("type", "access")

    if token_type != "access":
        logger.warning(f"⚠️ Wrong token type: {token_type}")
        return None

    try:
        user_id = UUID(user_id_str)
    except (TypeError, ValueError):
        logger.warning(f"⚠️ Invalid UUID in token: {user_id_str}")
        return None

    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.deleted_at.is_(None),
            User.is_active == True,
        )
    )
    user = result.scalar_one_or_none()

    if user:
        logger.debug(f"👤 Token user loaded: {user.email} [{user.role}]")
    else:
        logger.warning(f"⚠️ User not found or inactive: {user_id_str}")

    return user


# ── Pagination ────────────────────────────────────────────

class PaginationParams:
    def __init__(
        self,
        page: int = 1,
        page_size: int = 20,
    ):
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 1
        if page_size > 100:
            page_size = 100
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size

    def __repr__(self):
        return f"<Pagination page={self.page} size={self.page_size}>"
