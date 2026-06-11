"""
Email utility — gửi email qua Resend.com API.
Nếu RESEND_API_KEY không được cấu hình, chỉ log ra console (dev mode).
"""

import json
import urllib.request
import urllib.error
from typing import Optional

from app.config import settings
from app.utils.logger import get_logger, log_email

logger = get_logger(__name__)

BRAND = "Tú Marketing"
BRAND_COLOR = "#00d4ff"
BG_DARK = "#070b14"
BG_CARD = "#0d1526"
TEXT_LIGHT = "#e2e8f0"
TEXT_MUTED = "#8892a4"


async def send_email(
    to: str,
    subject: str,
    html: str,
    from_email: Optional[str] = None,
    from_name: Optional[str] = None,
) -> bool:
    from_addr = f"{from_name or settings.EMAIL_FROM_NAME} <{from_email or settings.EMAIL_FROM}>"

    if not settings.RESEND_API_KEY or settings.RESEND_API_KEY == "test":
        logger.warning(f"[EMAIL DEV] To: {to} | Subject: {subject}")
        logger.debug(f"[EMAIL DEV] HTML preview (100 chars): {html[:100]}")
        log_email(to, subject, False)
        return False

    try:
        payload = json.dumps({
            "from": from_addr,
            "to": [to],
            "subject": subject,
            "html": html,
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.resend.com/emails",
            data=payload,
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            logger.info(f"[EMAIL] Sent | to={to} subject='{subject}' id={result.get('id')}")
            log_email(to, subject, True)
            return True

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        logger.error(f"[EMAIL] Resend HTTP error {e.code}: {body}")
        log_email(to, subject, False)
        return False
    except Exception as e:
        logger.error(f"[EMAIL] Send failed: {e}")
        log_email(to, subject, False)
        return False


def _base_template(title: str, content: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{title}</title>
</head>
<body style="margin:0;padding:0;background:{BG_DARK};font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,sans-serif">
  <div style="max-width:560px;margin:32px auto;padding:0 16px">
    <!-- Header -->
    <div style="text-align:center;padding:28px 0 20px">
      <div style="font-size:24px;font-weight:900;background:linear-gradient(135deg,#00d4ff,#7b2fff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;letter-spacing:-0.5px">{BRAND}</div>
      <div style="width:60px;height:2px;background:linear-gradient(90deg,#00d4ff,#7b2fff);margin:10px auto 0;border-radius:2px"></div>
    </div>
    <!-- Card -->
    <div style="background:{BG_CARD};border:1px solid rgba(0,212,255,0.15);border-radius:16px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,0.5)">
      {content}
    </div>
    <!-- Footer -->
    <div style="text-align:center;padding:20px 0 32px;font-size:12px;color:#4a5568">
      © 2026 {BRAND} · Đào tạo AI Agent & Marketing Automation<br>
      <a href="{settings.FRONTEND_URL}" style="color:{BRAND_COLOR};text-decoration:none">{settings.FRONTEND_URL.replace('https://','').replace('http://','')}</a>
    </div>
  </div>
</body>
</html>"""


def render_welcome_email(name: str, verify_link: str) -> str:
    content = f"""
      <div style="padding:36px 32px">
        <div style="font-size:48px;text-align:center;margin-bottom:20px">🎉</div>
        <h1 style="font-size:22px;font-weight:800;color:{TEXT_LIGHT};margin:0 0 12px;text-align:center">Chào mừng, {name}!</h1>
        <p style="color:{TEXT_MUTED};line-height:1.75;margin:0 0 28px;text-align:center;font-size:15px">
          Cảm ơn bạn đã tham gia cộng đồng <strong style="color:{TEXT_LIGHT}">{BRAND}</strong>.<br>
          Xác thực email để bắt đầu hành trình AI Agent của bạn.
        </p>
        <div style="text-align:center">
          <a href="{verify_link}" style="display:inline-block;background:linear-gradient(135deg,#00d4ff,#7b2fff);color:#070b14;padding:14px 36px;border-radius:10px;text-decoration:none;font-weight:800;font-size:15px;letter-spacing:0.3px">
            ✅ Xác thực Email ngay
          </a>
        </div>
        <p style="color:#4a5568;font-size:12px;margin-top:24px;text-align:center;line-height:1.6">
          Link có hiệu lực trong 24 giờ.<br>Nếu không phải bạn đăng ký, hãy bỏ qua email này.
        </p>
      </div>
    """
    return _base_template(f"Xác thực email — {BRAND}", content)


def render_order_success_email(name: str, order_code: str, course_title: str, amount_fmt: str, learn_link: str) -> str:
    content = f"""
      <div style="padding:36px 32px">
        <div style="font-size:48px;text-align:center;margin-bottom:16px">🎊</div>
        <h1 style="font-size:22px;font-weight:800;color:{TEXT_LIGHT};margin:0 0 8px;text-align:center">Thanh toán thành công!</h1>
        <p style="color:{TEXT_MUTED};text-align:center;margin:0 0 28px;font-size:15px">
          Chào <strong style="color:{TEXT_LIGHT}">{name}</strong>, đơn hàng của bạn đã được xác nhận.
        </p>
        <div style="background:rgba(0,212,255,0.05);border:1px solid rgba(0,212,255,0.15);border-radius:10px;padding:20px;margin-bottom:28px">
          <div style="display:flex;justify-content:space-between;margin-bottom:10px;font-size:14px">
            <span style="color:{TEXT_MUTED}">Mã đơn hàng</span>
            <strong style="color:{BRAND_COLOR}">{order_code}</strong>
          </div>
          <div style="display:flex;justify-content:space-between;margin-bottom:10px;font-size:14px">
            <span style="color:{TEXT_MUTED}">Khóa học</span>
            <strong style="color:{TEXT_LIGHT};max-width:200px;text-align:right">{course_title}</strong>
          </div>
          <div style="display:flex;justify-content:space-between;padding-top:12px;border-top:1px solid rgba(0,212,255,0.1);font-size:14px">
            <span style="color:{TEXT_MUTED}">Số tiền</span>
            <strong style="font-size:18px;color:#00ff88">{amount_fmt}</strong>
          </div>
        </div>
        <div style="text-align:center">
          <a href="{learn_link}" style="display:inline-block;background:linear-gradient(135deg,#00d4ff,#7b2fff);color:#070b14;padding:14px 36px;border-radius:10px;text-decoration:none;font-weight:800;font-size:15px">
            🚀 Bắt đầu học ngay →
          </a>
        </div>
      </div>
    """
    return _base_template(f"Xác nhận thanh toán #{order_code} — {BRAND}", content)


def render_reset_password_email(name: str, reset_link: str) -> str:
    content = f"""
      <div style="padding:36px 32px">
        <div style="font-size:48px;text-align:center;margin-bottom:20px">🔐</div>
        <h1 style="font-size:22px;font-weight:800;color:{TEXT_LIGHT};margin:0 0 12px;text-align:center">Đặt lại mật khẩu</h1>
        <p style="color:{TEXT_MUTED};line-height:1.75;margin:0 0 28px;text-align:center;font-size:15px">
          Chào <strong style="color:{TEXT_LIGHT}">{name}</strong>, chúng tôi nhận được yêu cầu đặt lại mật khẩu của bạn.
          Nhấn nút bên dưới để tạo mật khẩu mới.
        </p>
        <div style="text-align:center">
          <a href="{reset_link}" style="display:inline-block;background:linear-gradient(135deg,#00d4ff,#7b2fff);color:#070b14;padding:14px 36px;border-radius:10px;text-decoration:none;font-weight:800;font-size:15px">
            🔑 Đặt lại mật khẩu
          </a>
        </div>
        <p style="color:#4a5568;font-size:12px;margin-top:24px;text-align:center;line-height:1.6">
          Link có hiệu lực trong 1 giờ.<br>Nếu không phải bạn yêu cầu, hãy bỏ qua email này.
        </p>
      </div>
    """
    return _base_template(f"Đặt lại mật khẩu — {BRAND}", content)
