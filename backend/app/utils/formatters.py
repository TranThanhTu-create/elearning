"""
Định dạng số, tiền tệ theo chuẩn Việt Nam.
- Phân cách hàng nghìn bằng dấu chấm (.)
- Dấu thập phân bằng dấu phẩy (,) — nhưng tiền VND không có thập phân
- Ký hiệu tiền: ₫ (đặt sau số)
"""

from typing import Optional, Union


def format_vnd(amount: Optional[Union[int, float]],
               show_symbol: bool = True) -> str:
    """
    Định dạng số tiền VND theo chuẩn Việt Nam.
    VD: 1490000 → "1.490.000 ₫"
         0      → "0 ₫"
    """
    if amount is None:
        return "0 ₫" if show_symbol else "0"
    try:
        value = int(round(amount))
        # Python format: {:,} dùng dấu phẩy, ta thay bằng dấu chấm
        formatted = f"{value:,}".replace(",", ".")
        return f"{formatted} ₫" if show_symbol else formatted
    except (TypeError, ValueError):
        return "0 ₫" if show_symbol else "0"


def format_vnd_short(amount: Optional[Union[int, float]]) -> str:
    """
    Rút gọn số tiền lớn.
    VD: 1_500_000 → "1,5 triệu ₫"
        500_000   → "500K ₫"
        85_000_000 → "85 triệu ₫"
    """
    if amount is None:
        return "0 ₫"
    try:
        value = int(round(amount))
        if value >= 1_000_000_000:
            v = value / 1_000_000_000
            s = f"{v:.1f}".rstrip("0").rstrip(".")
            return f"{s} tỷ ₫"
        elif value >= 1_000_000:
            v = value / 1_000_000
            # Dùng phẩy cho phần thập phân
            s = f"{v:.1f}".replace(".", ",").rstrip("0").rstrip(",")
            return f"{s} triệu ₫"
        elif value >= 1_000:
            v = value / 1_000
            s = f"{v:.0f}"
            return f"{s}K ₫"
        else:
            return f"{value} ₫"
    except (TypeError, ValueError):
        return "0 ₫"


def format_number_vn(value: Optional[Union[int, float]],
                     decimals: int = 0) -> str:
    """
    Định dạng số thông thường theo chuẩn VN (phân cách nghìn bằng chấm).
    VD: 2847 → "2.847"
         312  → "312"
    """
    if value is None:
        return "0"
    try:
        if decimals == 0:
            formatted = f"{int(round(value)):,}".replace(",", ".")
        else:
            formatted = f"{value:,.{decimals}f}".replace(",", "TEMP").replace(".", ",").replace("TEMP", ".")
        return formatted
    except (TypeError, ValueError):
        return "0"


def format_percent(value: Optional[float], decimals: int = 1) -> str:
    """
    Định dạng phần trăm.
    VD: 0.151 → "15,1%"   (nếu value là 0-1)
         15.1  → "15,1%"   (nếu value là 0-100)
    """
    if value is None:
        return "0%"
    try:
        # Nếu value <= 1 thì nhân 100
        if abs(value) <= 1.0:
            value = value * 100
        formatted = f"{value:.{decimals}f}".replace(".", ",")
        return f"{formatted}%"
    except (TypeError, ValueError):
        return "0%"


def parse_vnd(text: str) -> int:
    """
    Parse chuỗi tiền VND về số nguyên.
    "1.490.000 ₫" → 1490000
    "1490000"      → 1490000
    """
    cleaned = text.replace("₫", "").replace(".", "").replace(",", "").strip()
    try:
        return int(float(cleaned))
    except ValueError:
        return 0
