"""
Admin API — Cài đặt hệ thống: đọc/ghi từng section.
Sections: general | payment | email | analytics | affiliate | lead_magnet | integrations
"""

from typing import Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.settings import SiteSetting
from app.schemas.common import MessageResponse
from app.utils.deps import get_db, require_admin
from app.utils.timezone import vn_isoformat
from app.utils.logger import get_logger
from pydantic import BaseModel

logger = get_logger(__name__)
router = APIRouter()

VALID_SECTIONS = {"general", "payment", "email", "analytics", "affiliate", "lead_magnet", "integrations"}


# ── Schemas ───────────────────────────────────────────────

class SettingUpdateItem(BaseModel):
    value: Optional[str] = None
    value_json: Optional[Any] = None


class SectionUpdateRequest(BaseModel):
    settings: Dict[str, SettingUpdateItem]


class BulkSettingItem(BaseModel):
    section: str
    key: str
    value: Optional[str] = None
    value_json: Optional[Any] = None


class BulkUpdateRequest(BaseModel):
    settings: list[BulkSettingItem]


# ── Helper ────────────────────────────────────────────────

def _mask_secret(key: str, value: Optional[str]) -> Optional[str]:
    """Che giá trị bí mật (API key, password...) trong response."""
    if value and len(value) > 8:
        return value[:4] + "****" + value[-4:]
    return "****" if value else None


async def _get_section(db: AsyncSession, section: str) -> dict:
    result = await db.execute(
        select(SiteSetting).where(SiteSetting.section == section)
        .order_by(SiteSetting.key)
    )
    settings = result.scalars().all()
    return {
        s.key: {
            "value": _mask_secret(s.key, s.value) if s.is_secret else s.value,
            "value_json": s.value_json,
            "is_secret": s.is_secret,
            "description": s.description,
            "updated_at": vn_isoformat(s.updated_at),
        }
        for s in settings
    }


# ── Routes ────────────────────────────────────────────────

@router.get("", summary="Tất cả cài đặt (theo section)")
async def get_all_settings(
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(select(SiteSetting).order_by(SiteSetting.section, SiteSetting.key))
    all_settings = result.scalars().all()

    grouped: dict = {}
    for s in all_settings:
        if s.section not in grouped:
            grouped[s.section] = {}
        grouped[s.section][s.key] = {
            "value": _mask_secret(s.key, s.value) if s.is_secret else s.value,
            "value_json": s.value_json,
            "is_secret": s.is_secret,
            "description": s.description,
            "updated_at": vn_isoformat(s.updated_at),
        }
    return grouped


@router.get("/{section}", summary="Cài đặt theo section")
async def get_section_settings(
    section: str,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    if section not in VALID_SECTIONS:
        raise HTTPException(400, f"Section không hợp lệ. Chọn: {', '.join(sorted(VALID_SECTIONS))}")
    return await _get_section(db, section)


@router.patch("/{section}", summary="Cập nhật cài đặt trong section")
async def update_section_settings(
    section: str,
    body: SectionUpdateRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    if section not in VALID_SECTIONS:
        raise HTTPException(400, f"Section không hợp lệ. Chọn: {', '.join(sorted(VALID_SECTIONS))}")

    updated = []
    for key, item in body.settings.items():
        result = await db.execute(
            select(SiteSetting).where(
                SiteSetting.section == section,
                SiteSetting.key == key,
            )
        )
        setting = result.scalar_one_or_none()

        if setting:
            if item.value is not None:
                setting.value = item.value
            if item.value_json is not None:
                setting.value_json = item.value_json
            setting.updated_by = admin.id
        else:
            # Tạo mới nếu chưa tồn tại
            setting = SiteSetting(
                section=section,
                key=key,
                value=item.value,
                value_json=item.value_json,
                updated_by=admin.id,
            )
            db.add(setting)

        updated.append(key)

    logger.info(f"Admin {admin.email} cập nhật settings [{section}]: {', '.join(updated)}")
    return {"updated_keys": updated, "message": f"Đã lưu {len(updated)} cài đặt"}


@router.post("/bulk-update", summary="Cập nhật nhiều settings cùng lúc (multi-section)")
async def bulk_update_settings(
    body: BulkUpdateRequest,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    for item in body.settings:
        if item.section not in VALID_SECTIONS:
            raise HTTPException(400, f"Section không hợp lệ: {item.section}")

    updated_count = 0
    for item in body.settings:
        result = await db.execute(
            select(SiteSetting).where(
                SiteSetting.section == item.section,
                SiteSetting.key == item.key,
            )
        )
        setting = result.scalar_one_or_none()

        if setting:
            if item.value is not None:
                setting.value = item.value
            if item.value_json is not None:
                setting.value_json = item.value_json
            setting.updated_by = admin.id
        else:
            setting = SiteSetting(
                section=item.section,
                key=item.key,
                value=item.value,
                value_json=item.value_json,
                updated_by=admin.id,
            )
            db.add(setting)

        updated_count += 1

    logger.info(f"Admin {admin.email} bulk update {updated_count} settings")
    return {"updated_count": updated_count, "message": f"Đã lưu {updated_count} cài đặt"}


@router.delete("/{section}/{key}", summary="Xóa một setting")
async def delete_setting(
    section: str,
    key: str,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    if section not in VALID_SECTIONS:
        raise HTTPException(400, "Section không hợp lệ")

    result = await db.execute(
        select(SiteSetting).where(SiteSetting.section == section, SiteSetting.key == key)
    )
    setting = result.scalar_one_or_none()
    if not setting:
        raise HTTPException(404, f"Không tìm thấy setting '{section}.{key}'")

    await db.delete(setting)
    return MessageResponse(message=f"Đã xóa setting '{key}'")
