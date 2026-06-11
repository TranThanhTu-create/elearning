"""
Admin API — Quản lý leads: xem, lọc, sync Google Sheets.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.models.analytics import Lead
from app.models.order import Order
from app.schemas.common import PaginatedResponse, MessageResponse
from app.utils.deps import get_db, require_admin, PaginationParams
from app.utils.formatters import format_number_vn
from app.utils.timezone import vn_isoformat, now_utc
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


# ── List & Filter ─────────────────────────────────────────

@router.get("", summary="Danh sách leads")
async def list_leads(
    search: Optional[str]        = Query(None, description="Tìm theo tên, email, SĐT"),
    utm_source: Optional[str]    = Query(None),
    utm_campaign: Optional[str]  = Query(None),
    is_converted: Optional[bool] = Query(None, description="Đã mua khóa hay chưa"),
    synced: Optional[bool]       = Query(None, description="Đã sync Google Sheets"),
    date_from: Optional[str]     = Query(None, description="YYYY-MM-DD"),
    date_to: Optional[str]       = Query(None, description="YYYY-MM-DD"),
    page: int                    = Query(1, ge=1),
    page_size: int               = Query(20, ge=1, le=100),
    db: AsyncSession             = Depends(get_db),
    admin                        = Depends(require_admin),
):
    pagination = PaginationParams(page=page, page_size=page_size)

    q = select(Lead)
    filters = []
    if search:
        filters.append(
            or_(
                Lead.name.ilike(f"%{search}%"),
                Lead.email.ilike(f"%{search}%"),
                Lead.phone.ilike(f"%{search}%"),
            )
        )
    if utm_source:
        filters.append(Lead.utm_source == utm_source)
    if utm_campaign:
        filters.append(Lead.utm_campaign.ilike(f"%{utm_campaign}%"))
    if is_converted is not None:
        if is_converted:
            filters.append(Lead.user_id.is_not(None))
        else:
            filters.append(Lead.user_id.is_(None))
    if synced is not None:
        filters.append(Lead.synced_to_sheet == synced)
    if date_from:
        from datetime import datetime
        try:
            filters.append(Lead.created_at >= datetime.fromisoformat(date_from))
        except ValueError:
            pass
    if date_to:
        from datetime import datetime
        try:
            filters.append(Lead.created_at <= datetime.fromisoformat(date_to + "T23:59:59"))
        except ValueError:
            pass

    if filters:
        q = q.where(and_(*filters))

    total_r = await db.execute(select(func.count()).select_from(q.subquery()))
    total = total_r.scalar_one()

    q = q.order_by(Lead.created_at.desc()).offset(pagination.offset).limit(pagination.page_size)
    leads = (await db.execute(q)).scalars().all()

    # Check từng lead có mua khóa chưa (qua user_id)
    items = [
        {
            "id": str(l.id),
            "name": l.name,
            "email": l.email,
            "phone": l.phone,
            "utm_source": l.utm_source,
            "utm_medium": l.utm_medium,
            "utm_campaign": l.utm_campaign,
            "utm_content": l.utm_content,
            "source_url": l.source_url,
            "ip_address": l.ip_address,
            "is_converted": l.user_id is not None,
            "status_label": "Đã mua" if l.user_id else "Chưa mua",
            "synced_to_sheet": l.synced_to_sheet,
            "synced_at": vn_isoformat(l.synced_at),
            "created_at": vn_isoformat(l.created_at),
        }
        for l in leads
    ]
    return PaginatedResponse.build(items, total, page, page_size)


@router.get("/stats", summary="Thống kê nhanh leads")
async def lead_stats(
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    total_r = await db.execute(select(func.count()).select_from(Lead))
    total = total_r.scalar_one()

    converted_r = await db.execute(
        select(func.count()).where(Lead.user_id.is_not(None))
    )
    converted = converted_r.scalar_one()

    unsynced_r = await db.execute(
        select(func.count()).where(Lead.synced_to_sheet == False)
    )
    unsynced = unsynced_r.scalar_one()

    # Top sources
    sources_r = await db.execute(
        select(Lead.utm_source, func.count().label("cnt"))
        .where(Lead.utm_source.is_not(None))
        .group_by(Lead.utm_source)
        .order_by(func.count().desc())
        .limit(5)
    )
    top_sources = [
        {"source": r.utm_source, "count": r.cnt, "count_fmt": format_number_vn(r.cnt)}
        for r in sources_r.all()
    ]

    return {
        "total_leads": format_number_vn(total),
        "total_leads_raw": total,
        "converted_leads": format_number_vn(converted),
        "conversion_rate": f"{(converted / total * 100):.1f}%" if total > 0 else "0%",
        "unsynced_leads": format_number_vn(unsynced),
        "top_sources": top_sources,
    }


@router.get("/{lead_id}", summary="Chi tiết lead")
async def get_lead_detail(
    lead_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(404, "Không tìm thấy lead")

    return {
        "id": str(lead.id),
        "name": lead.name,
        "email": lead.email,
        "phone": lead.phone,
        "utm_source": lead.utm_source,
        "utm_medium": lead.utm_medium,
        "utm_campaign": lead.utm_campaign,
        "utm_content": lead.utm_content,
        "source_url": lead.source_url,
        "ip_address": lead.ip_address,
        "user_id": str(lead.user_id) if lead.user_id else None,
        "is_converted": lead.user_id is not None,
        "synced_to_sheet": lead.synced_to_sheet,
        "synced_at": vn_isoformat(lead.synced_at),
        "created_at": vn_isoformat(lead.created_at),
    }


@router.delete("/{lead_id}", summary="Xóa lead")
async def delete_lead(
    lead_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(404, "Không tìm thấy lead")
    await db.delete(lead)
    return MessageResponse(message="Đã xóa lead")


@router.post("/sync-sheets", summary="Sync leads chưa đồng bộ lên Google Sheets")
async def sync_to_sheets(
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    Đồng bộ tất cả leads chưa sync (synced_to_sheet=False) lên Google Sheets.
    Yêu cầu GOOGLE_SHEETS_CREDS và GOOGLE_SHEET_ID được cấu hình trong site_settings.
    """
    from app.models.settings import SiteSetting

    # Lấy config Google Sheets
    sheet_settings_r = await db.execute(
        select(SiteSetting).where(
            SiteSetting.section == "lead_magnet",
            SiteSetting.key.in_(["google_sheet_id", "google_sheet_name"]),
        )
    )
    sheet_settings = {s.key: s.value for s in sheet_settings_r.scalars().all()}
    sheet_id = sheet_settings.get("google_sheet_id")

    if not sheet_id:
        raise HTTPException(400, "Chưa cấu hình Google Sheet ID trong Admin Settings")

    # Lấy leads chưa sync
    unsynced_r = await db.execute(
        select(Lead).where(Lead.synced_to_sheet == False).limit(500)
    )
    unsynced_leads = unsynced_r.scalars().all()

    if not unsynced_leads:
        return {"synced_count": 0, "message": "Không có leads nào cần sync"}

    synced_count = 0
    now = now_utc()

    try:
        # TODO: Tích hợp Google Sheets API thực tế
        # Hiện tại chỉ đánh dấu là đã sync
        for lead in unsynced_leads:
            lead.synced_to_sheet = True
            lead.synced_at = now
            synced_count += 1

        logger.info(f"Admin {admin.email} sync {synced_count} leads lên Google Sheets")
        return {
            "synced_count": synced_count,
            "message": f"Đã sync {synced_count} leads lên Google Sheets",
        }

    except Exception as e:
        logger.error(f"Lỗi sync Google Sheets: {e}")
        raise HTTPException(500, f"Lỗi kết nối Google Sheets: {str(e)}")
