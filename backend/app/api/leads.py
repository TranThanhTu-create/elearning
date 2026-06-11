"""
Leads API — Public route: submit form popup lead magnet.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.analytics import Lead
from app.models.user import User
from app.schemas.analytics import LeadSubmitRequest
from app.schemas.common import MessageResponse
from app.utils.deps import get_db
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("", response_model=MessageResponse, status_code=201, summary="Submit form lead magnet")
async def submit_lead(
    body: LeadSubmitRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    # Lấy IP
    ip = request.headers.get("X-Forwarded-For",
         request.headers.get("X-Real-IP",
         request.client.host if request.client else None))

    # Kiểm tra user đã tồn tại chưa
    user_id = None
    user_r = await db.execute(select(User).where(User.email == body.email))
    existing_user = user_r.scalar_one_or_none()
    if existing_user:
        user_id = existing_user.id

    lead = Lead(
        name=body.name,
        email=body.email,
        phone=body.phone,
        utm_source=body.utm_source,
        utm_medium=body.utm_medium,
        utm_campaign=body.utm_campaign,
        utm_content=body.utm_content,
        source_url=body.page_url,
        user_id=user_id,
        ip_address=ip,
    )
    db.add(lead)
    logger.info(f"New lead: {body.email} from {body.utm_source or 'organic'}")
    return MessageResponse(message="Đăng ký thành công! Chúng tôi sẽ liên hệ với bạn sớm.")
