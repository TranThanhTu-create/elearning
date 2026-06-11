"""
Xử lý múi giờ Việt Nam (UTC+7 / Asia/Ho_Chi_Minh).
Mọi datetime trong DB lưu UTC, hiển thị ra ngoài đều convert sang VN.
"""

from datetime import datetime, timezone
from typing import Optional
import pytz

VN_TZ = pytz.timezone("Asia/Ho_Chi_Minh")
UTC_TZ = pytz.utc


def now_vn() -> datetime:
    """Trả về datetime hiện tại theo múi giờ Việt Nam."""
    return datetime.now(VN_TZ)


def now_utc() -> datetime:
    """Trả về datetime hiện tại UTC (để lưu DB)."""
    return datetime.now(timezone.utc)


def to_vn(dt: Optional[datetime]) -> Optional[datetime]:
    """Convert datetime (UTC hoặc naive) sang múi giờ Việt Nam."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        # Naive datetime — giả sử là UTC
        dt = UTC_TZ.localize(dt)
    return dt.astimezone(VN_TZ)


def to_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """Convert datetime (VN hoặc bất kỳ tz) sang UTC."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = VN_TZ.localize(dt)
    return dt.astimezone(UTC_TZ)


def format_vn_datetime(dt: Optional[datetime],
                       fmt: str = "%H:%M · %d/%m/%Y") -> str:
    """
    Format datetime ra chuỗi theo chuẩn Việt Nam.
    Mặc định: "14:35 · 29/05/2026"
    """
    if dt is None:
        return "—"
    vn = to_vn(dt)
    return vn.strftime(fmt)


def format_vn_date(dt: Optional[datetime], fmt: str = "%d/%m/%Y") -> str:
    """Format chỉ ngày: "29/05/2026" """
    if dt is None:
        return "—"
    vn = to_vn(dt)
    return vn.strftime(fmt)


def format_vn_time(dt: Optional[datetime], fmt: str = "%H:%M") -> str:
    """Format chỉ giờ: "14:35" """
    if dt is None:
        return "—"
    vn = to_vn(dt)
    return vn.strftime(fmt)


def vn_isoformat(dt: Optional[datetime]) -> Optional[str]:
    """
    Trả về ISO 8601 có offset +07:00 để frontend hiển thị đúng.
    VD: "2026-05-29T14:35:00+07:00"
    """
    if dt is None:
        return None
    vn = to_vn(dt)
    return vn.isoformat()
