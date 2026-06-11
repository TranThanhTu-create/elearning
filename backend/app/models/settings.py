"""
Nhóm bảng: Site Settings
- site_settings: Key-value store cho toàn bộ admin-settings.html
  (7 section: general, payment, email, analytics, affiliate, lead_magnet, integrations)
"""

import uuid
from sqlalchemy import Column, String, Text, Boolean, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.database import Base


class SiteSetting(Base):
    """
    Key-value store cho cấu hình toàn hệ thống.
    Admin chỉnh tại admin-settings.html — saveAll() gọi PATCH /admin/settings.

    Các key theo từng section:
    --- general ---
    site_name, site_url, site_description, contact_email, contact_phone
    facebook_url, tiktok_url, youtube_url, zalo_url
    logo_url, favicon_url

    --- payment (SePay) ---
    sepay_api_key, sepay_webhook_secret
    bank_account_number, bank_name, bank_account_name
    order_expire_minutes, order_code_prefix

    --- email (Resend) ---
    resend_api_key, email_from, email_from_name
    email_welcome_enabled, email_order_confirm_enabled
    email_lead_magnet_enabled, email_reminder_enabled
    email_affiliate_payout_enabled

    --- analytics ---
    ga4_measurement_id, meta_pixel_id, clarity_project_id
    video_tracking_enabled, video_ga4_events_enabled

    --- affiliate ---
    affiliate_commission_rate, affiliate_cookie_days
    affiliate_min_withdrawal, affiliate_auto_approve
    affiliate_require_approval

    --- lead_magnet ---
    lead_popup_enabled, lead_popup_delay_seconds
    lead_popup_title, lead_popup_description, lead_cta_text
    lead_zoom_link
    google_sheet_id, google_sheet_name

    --- integrations ---
    google_client_id, google_client_secret
    r2_account_id, r2_bucket_name, r2_public_url
    """
    __tablename__ = "site_settings"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    section     = Column(String(50), nullable=False, index=True)  # general | payment | email | ...
    key         = Column(String(100), nullable=False)
    value       = Column(Text, nullable=True)                     # String value
    value_json  = Column(JSONB, nullable=True)                    # JSON value cho complex settings
    is_secret   = Column(Boolean, default=False)                  # True = mask trong UI
    description = Column(Text, nullable=True)                     # Tooltip trong admin-settings.html
    updated_at  = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by  = Column(UUID(as_uuid=True), nullable=True)       # Admin user_id

    __table_args__ = (
        # Mỗi key là unique trong toàn bộ bảng
        Index("ix_settings_section_key", "section", "key", unique=True),
    )

    def __repr__(self):
        return f"<SiteSetting {self.section}.{self.key}>"
