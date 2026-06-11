"""
Pydantic schemas cho Site Settings.
"""

from typing import Optional
from pydantic import BaseModel


class SiteSettingsResponse(BaseModel):
    site_name: str
    site_description: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    facebook_url: Optional[str] = None
    youtube_url: Optional[str] = None
    tiktok_url: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_account_name: Optional[str] = None
    sepay_api_key_masked: Optional[str] = None   # chỉ hiện 4 ký tự cuối
    google_sheet_id: Optional[str] = None
    google_analytics_id: Optional[str] = None
    meta_pixel_id: Optional[str] = None
    resend_api_key_masked: Optional[str] = None


class SiteSettingsUpdateRequest(BaseModel):
    site_name: Optional[str] = None
    site_description: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    facebook_url: Optional[str] = None
    youtube_url: Optional[str] = None
    tiktok_url: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_account_name: Optional[str] = None
    sepay_api_key: Optional[str] = None
    sepay_webhook_secret: Optional[str] = None
    google_sheet_id: Optional[str] = None
    google_analytics_id: Optional[str] = None
    meta_pixel_id: Optional[str] = None
    resend_api_key: Optional[str] = None
    google_service_account_json: Optional[str] = None   # JSON string
