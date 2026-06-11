"""
Logger toàn hệ thống EduVietPro — debug cực kỳ chi tiết.
Mọi request/response, DB query, webhook, email, error đều được ghi log.
"""

import logging
import sys
import json
import traceback
from datetime import datetime
from typing import Any, Optional
import pytz

VN_TZ = pytz.timezone("Asia/Ho_Chi_Minh")


def _vn_time() -> str:
    return datetime.now(VN_TZ).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


class VNFormatter(logging.Formatter):
    """Formatter hiển thị giờ Việt Nam (UTC+7) thay vì UTC."""

    COLORS = {
        "DEBUG":    "\033[36m",   # Cyan
        "INFO":     "\033[32m",   # Green
        "WARNING":  "\033[33m",   # Yellow
        "ERROR":    "\033[31m",   # Red
        "CRITICAL": "\033[35m",   # Magenta
        "RESET":    "\033[0m",
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, "")
        reset = self.COLORS["RESET"]
        vn_time = _vn_time()

        # Module ngắn gọn
        module = record.name.split(".")[-1] if "." in record.name else record.name

        level_str = f"{color}[{record.levelname:<8}]{reset}"
        time_str  = f"\033[90m{vn_time}\033[0m"  # Xám
        src_str   = f"\033[94m{module}:{record.lineno}\033[0m"  # Xanh nhạt

        msg = record.getMessage()

        # Nếu có exception thì in traceback
        if record.exc_info:
            msg += "\n" + "".join(traceback.format_exception(*record.exc_info)).rstrip()

        return f"{time_str} {level_str} {src_str} | {msg}"


def get_logger(name: str) -> logging.Logger:
    """
    Lấy logger theo module.
    Dùng: logger = get_logger(__name__)
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(VNFormatter())
        logger.addHandler(handler)
        logger.propagate = False

    return logger


def setup_root_logger(debug: bool = False) -> None:
    """Gọi 1 lần trong main.py để thiết lập root logger."""
    level = logging.DEBUG if debug else logging.INFO
    root = logging.getLogger()
    root.setLevel(level)

    # Tắt spam từ uvicorn/sqlalchemy khi không debug
    if not debug:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    else:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(VNFormatter())

    # Xóa handler cũ, thêm mới
    root.handlers.clear()
    root.addHandler(handler)


# ──────────────────────────────────────────────────────────
# Helpers log có cấu trúc (structured logging)
# ──────────────────────────────────────────────────────────

_app_logger = get_logger("eduvietpro")


def log_request(method: str, path: str, user_id: Optional[str] = None,
                ip: str = "?", params: Any = None) -> None:
    extra = f"user={user_id or 'anon'} ip={ip}"
    if params:
        extra += f" params={json.dumps(params, ensure_ascii=False, default=str)}"
    _app_logger.info(f"→ {method} {path} | {extra}")


def log_response(method: str, path: str, status: int, duration_ms: float) -> None:
    emoji = "✅" if status < 400 else ("⚠️" if status < 500 else "❌")
    _app_logger.info(f"{emoji} {method} {path} {status} [{duration_ms:.1f}ms]")


def log_db(action: str, table: str, record_id: Any = None, detail: str = "") -> None:
    _app_logger.debug(f"🗄️  DB {action} → {table}" +
                      (f" id={record_id}" if record_id else "") +
                      (f" | {detail}" if detail else ""))


def log_auth(event: str, email: str, success: bool, reason: str = "") -> None:
    icon = "🔐" if success else "🚫"
    _app_logger.info(f"{icon} AUTH {event} | email={email} success={success}" +
                     (f" reason={reason}" if reason else ""))


def log_payment(event: str, order_code: str, amount: int = 0,
                detail: str = "") -> None:
    _app_logger.info(
        f"💳 PAYMENT {event} | order={order_code}"
        + (f" amount={amount:,}₫".replace(",", ".") if amount else "")
        + (f" | {detail}" if detail else "")
    )


def log_webhook(source: str, event: str, payload_preview: str = "") -> None:
    _app_logger.info(f"🔔 WEBHOOK {source}/{event}" +
                     (f" | {payload_preview[:200]}" if payload_preview else ""))


def log_email(to: str, subject: str, success: bool, error: str = "") -> None:
    icon = "📧" if success else "📭"
    _app_logger.info(f"{icon} EMAIL to={to} subject='{subject}' success={success}" +
                     (f" error={error}" if error else ""))


def log_error(context: str, error: Exception, extra: str = "") -> None:
    _app_logger.error(
        f"💥 ERROR in {context}: {type(error).__name__}: {str(error)}" +
        (f" | {extra}" if extra else ""),
        exc_info=True
    )
