"""
Bảo mật: password hashing, JWT, ref code generation.
"""

import secrets
import string
import hashlib
import hmac
from datetime import timedelta
from typing import Optional, Union
from uuid import UUID

import bcrypt as _bcrypt
from jose import JWTError, jwt

from app.utils.logger import get_logger
from app.utils.timezone import now_utc

logger = get_logger(__name__)


# ── Password ──────────────────────────────────────────────

def hash_password(plain: str) -> str:
    hashed = _bcrypt.hashpw(plain.encode("utf-8"), _bcrypt.gensalt(12)).decode("utf-8")
    logger.debug("Password hashed (bcrypt)")
    return hashed


def verify_password(plain: str, hashed: str) -> bool:
    try:
        result = _bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        result = False
    logger.debug(f"Password verify → {'OK' if result else 'FAIL'}")
    return result


# ── JWT ───────────────────────────────────────────────────

def create_access_token(
    subject: Union[str, UUID],
    role: str,
    secret_key: str,
    algorithm: str = "HS256",
    expires_minutes: int = 10080,
    extra: Optional[dict] = None,
) -> str:
    """
    Tạo JWT access token.
    Payload: sub (user_id), role, iat, exp
    """
    expire = now_utc() + timedelta(minutes=expires_minutes)
    payload = {
        "sub": str(subject),
        "role": role,
        "exp": expire,
        "iat": now_utc(),
        "type": "access",
    }
    if extra:
        payload.update(extra)

    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    logger.debug(f"🎫 JWT created | sub={subject} role={role} expires={expire.isoformat()}")
    return token


def create_refresh_token(
    subject: Union[str, UUID],
    secret_key: str,
    algorithm: str = "HS256",
    expires_days: int = 30,
) -> str:
    expire = now_utc() + timedelta(days=expires_days)
    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": now_utc(),
        "type": "refresh",
    }
    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    logger.debug(f"🔄 Refresh token created | sub={subject}")
    return token


def decode_token(token: str, secret_key: str,
                 algorithm: str = "HS256") -> Optional[dict]:
    """
    Giải mã JWT. Trả về payload dict hoặc None nếu lỗi.
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        logger.debug(f"🎫 JWT decoded | sub={payload.get('sub')} type={payload.get('type')}")
        return payload
    except JWTError as e:
        logger.warning(f"⚠️ JWT decode failed: {e}")
        return None


# ── Tokens ────────────────────────────────────────────────

def generate_token(length: int = 64) -> str:
    """Tạo token ngẫu nhiên an toàn (cho reset password, email verify)."""
    return secrets.token_urlsafe(length)


def generate_ref_code(length: int = 8) -> str:
    """
    Tạo mã giới thiệu affiliate.
    VD: "EDUVIET8X", "ABCD1234"
    """
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_order_code() -> str:
    """
    Tạo mã đơn hàng duy nhất.
    VD: "DH20260529001" → dùng timestamp + random suffix
    """
    from app.utils.timezone import now_vn
    now = now_vn()
    date_part = now.strftime("%Y%m%d")
    rand_part = secrets.token_hex(3).upper()[:6]
    code = f"DH{date_part}{rand_part}"
    logger.debug(f"📋 Order code generated: {code}")
    return code


# ── HMAC (SePay webhook) ──────────────────────────────────

def verify_hmac_sha256(payload: bytes, signature: str, secret: str) -> bool:
    """
    Xác minh HMAC-SHA256 từ SePay webhook.
    """
    expected = hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256
    ).hexdigest()
    result = hmac.compare_digest(expected.lower(), signature.lower())
    logger.debug(f"🔐 HMAC verify → {'OK' if result else 'FAIL'} | expected={expected[:16]}...")
    return result
