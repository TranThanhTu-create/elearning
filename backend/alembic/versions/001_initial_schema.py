"""001 initial schema — toàn bộ 32 bảng

Revision ID: 001
Revises:
Create Date: 2026-05-29 15:00:00.000000

Bảng tạo theo thứ tự dependency (parent trước, child sau):
 1. users
 2. password_reset_tokens
 3. email_verifications
 4. course_categories
 5. courses
 6. course_outcomes
 7. course_requirements
 8. course_faqs
 9. course_reviews
10. chapters
11. lessons
12. lesson_attachments
13. enrollments
14. lesson_progress
15. lesson_notes
16. coupons
17. orders
18. coupon_usages
19. affiliates
20. affiliate_clicks
21. commissions
22. withdrawal_requests
23. categories
24. tags
25. posts
26. post_tags
27. post_courses
28. leads
29. video_watch_events
30. video_watch_checkpoints
31. page_view_events
32. checkout_sessions
33. audit_logs
34. site_settings
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def _create_enum(bind, name: str, values: list) -> None:
    exists = bind.execute(
        text("SELECT 1 FROM pg_type WHERE typname = :n"), {"n": name}
    ).fetchone()
    if not exists:
        vals = ", ".join(f"'{v}'" for v in values)
        bind.execute(text(f"CREATE TYPE {name} AS ENUM ({vals})"))


def upgrade() -> None:
    bind = op.get_bind()

    # ─── ENUMS ───────────────────────────────────────────────
    _create_enum(bind, "user_role", ["admin", "student"])
    _create_enum(bind, "course_badge", ["bestseller", "new", "sale", "hot"])
    _create_enum(bind, "course_level", ["beginner", "intermediate", "advanced"])
    _create_enum(bind, "order_status", ["pending", "completed", "expired", "cancelled", "refunded"])
    _create_enum(bind, "payment_method", ["bank_transfer", "qr"])
    _create_enum(bind, "discount_type", ["percent", "fixed"])
    _create_enum(bind, "post_status", ["draft", "published", "archived"])
    _create_enum(bind, "commission_status", ["pending", "approved", "paid", "cancelled"])
    _create_enum(bind, "withdrawal_status", ["pending", "approved", "rejected"])
    _create_enum(bind, "page_type", ["home", "course_list", "course_detail", "blog", "blog_detail", "checkout"])
    _create_enum(bind, "checkout_outcome", ["pending", "completed", "abandoned", "expired"])

    # ─── 1. USERS ─────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("avatar_url", sa.Text, nullable=True),
        sa.Column("role", sa.Enum("admin", "student", name="user_role", create_type=False), default="student", nullable=False),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.Column("is_email_verified", sa.Boolean, default=False, nullable=False),
        sa.Column("google_id", sa.String(255), nullable=True),
        sa.Column("ref_code", sa.String(20), nullable=True),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_google_id", "users", ["google_id"], unique=True)
    op.create_index("ix_users_ref_code", "users", ["ref_code"], unique=True)
    op.create_index("ix_users_role", "users", ["role"])
    op.create_index("ix_users_email_active", "users", ["email", "is_active"])

    # ─── 2. PASSWORD RESET TOKENS ─────────────────────────────
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token", sa.String(255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("ix_pwd_reset_token", "password_reset_tokens", ["token"], unique=True)

    # ─── 3. EMAIL VERIFICATIONS ───────────────────────────────
    op.create_table(
        "email_verifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token", sa.String(255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("ix_email_verify_token", "email_verifications", ["token"], unique=True)

    # ─── 4. COURSE CATEGORIES ────────────────────────────────
    op.create_table(
        "course_categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("icon", sa.String(10), nullable=True),
        sa.Column("order_index", sa.Integer, default=0),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("ix_course_categories_slug", "course_categories", ["slug"], unique=True)

    # ─── 5. COURSES ───────────────────────────────────────────
    op.create_table(
        "courses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("course_categories.id"), nullable=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("slug", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("short_desc", sa.String(500), nullable=True),
        sa.Column("thumbnail_url", sa.Text, nullable=True),
        sa.Column("trailer_video_id", sa.String(50), nullable=True),
        sa.Column("price", sa.BigInteger, nullable=False),
        sa.Column("original_price", sa.BigInteger, nullable=True),
        sa.Column("is_published", sa.Boolean, default=False, nullable=False),
        sa.Column("badge", sa.Enum("bestseller", "new", "sale", "hot", name="course_badge", create_type=False), nullable=True),
        sa.Column("level", sa.Enum("beginner", "intermediate", "advanced", name="course_level", create_type=False), default="beginner"),
        sa.Column("total_lessons", sa.Integer, default=0),
        sa.Column("total_duration_seconds", sa.Integer, default=0),
        sa.Column("total_students", sa.Integer, default=0),
        sa.Column("avg_rating", sa.Float, default=0.0),
        sa.Column("total_reviews", sa.Integer, default=0),
        sa.Column("order_index", sa.Integer, default=0),
        sa.Column("meta_title", sa.String(255), nullable=True),
        sa.Column("meta_desc", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.CheckConstraint("price >= 0", name="ck_courses_price_positive"),
    )
    op.create_index("ix_courses_slug", "courses", ["slug"], unique=True)
    op.create_index("ix_courses_published", "courses", ["is_published"])
    op.create_index("ix_courses_published_category", "courses", ["is_published", "category_id"])

    # ─── 6. COURSE OUTCOMES ───────────────────────────────────
    op.create_table(
        "course_outcomes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content", sa.String(500), nullable=False),
        sa.Column("order_index", sa.Integer, default=0),
    )
    op.create_index("ix_outcomes_course", "course_outcomes", ["course_id"])

    # ─── 7. COURSE REQUIREMENTS ───────────────────────────────
    op.create_table(
        "course_requirements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content", sa.String(500), nullable=False),
        sa.Column("order_index", sa.Integer, default=0),
    )
    op.create_index("ix_requirements_course", "course_requirements", ["course_id"])

    # ─── 8. COURSE FAQS ───────────────────────────────────────
    op.create_table(
        "course_faqs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question", sa.String(500), nullable=False),
        sa.Column("answer", sa.Text, nullable=False),
        sa.Column("order_index", sa.Integer, default=0),
    )
    op.create_index("ix_faqs_course", "course_faqs", ["course_id"])

    # ─── 9. COURSE REVIEWS ────────────────────────────────────
    op.create_table(
        "course_reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rating", sa.Integer, nullable=False),
        sa.Column("comment", sa.Text, nullable=True),
        sa.Column("is_visible", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.UniqueConstraint("course_id", "user_id", name="uq_review_course_user"),
        sa.CheckConstraint("rating BETWEEN 1 AND 5", name="ck_review_rating_range"),
    )
    op.create_index("ix_reviews_course_visible", "course_reviews", ["course_id", "is_visible"])

    # ─── 10. CHAPTERS ─────────────────────────────────────────
    op.create_table(
        "chapters",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("order_index", sa.Integer, default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("ix_chapters_course_order", "chapters", ["course_id", "order_index"])

    # ─── 11. LESSONS ──────────────────────────────────────────
    op.create_table(
        "lessons",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("youtube_video_id", sa.String(50), nullable=True),
        sa.Column("is_free", sa.Boolean, default=False, nullable=False),
        sa.Column("duration_seconds", sa.Integer, default=0),
        sa.Column("order_index", sa.Integer, default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("ix_lessons_chapter_order", "lessons", ["chapter_id", "order_index"])

    # ─── 12. LESSON ATTACHMENTS ───────────────────────────────
    op.create_table(
        "lesson_attachments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("lesson_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("file_name", sa.String(500), nullable=False),
        sa.Column("file_url", sa.Text, nullable=False),
        sa.Column("file_size", sa.BigInteger, default=0),
        sa.Column("mime_type", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("ix_attachments_lesson", "lesson_attachments", ["lesson_id"])

    # ─── 13. ENROLLMENTS ──────────────────────────────────────
    op.create_table(
        "enrollments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("enrolled_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("last_lesson_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lessons.id"), nullable=True),
        sa.Column("progress_percent", sa.Float, default=0.0),
        sa.UniqueConstraint("user_id", "course_id", name="uq_enrollment_user_course"),
    )
    op.create_index("ix_enrollments_user", "enrollments", ["user_id"])
    op.create_index("ix_enrollments_course", "enrollments", ["course_id"])

    # ─── 14. LESSON PROGRESS ──────────────────────────────────
    op.create_table(
        "lesson_progress",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lesson_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("is_completed", sa.Boolean, default=False),
        sa.Column("watch_seconds", sa.Integer, default=0),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.UniqueConstraint("user_id", "lesson_id", name="uq_progress_user_lesson"),
    )
    op.create_index("ix_progress_user_lesson", "lesson_progress", ["user_id", "lesson_id"])

    # ─── 15. LESSON NOTES ─────────────────────────────────────
    op.create_table(
        "lesson_notes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lesson_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.UniqueConstraint("user_id", "lesson_id", name="uq_note_user_lesson"),
    )

    # ─── 16. COUPONS ──────────────────────────────────────────
    op.create_table(
        "coupons",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("description", sa.String(255), nullable=True),
        sa.Column("discount_type", sa.Enum("percent", "fixed", name="discount_type", create_type=False), nullable=False),
        sa.Column("discount_value", sa.BigInteger, nullable=False),
        sa.Column("min_order_amount", sa.BigInteger, default=0),
        sa.Column("max_uses", sa.Integer, nullable=True),
        sa.Column("max_uses_per_user", sa.Integer, default=1),
        sa.Column("used_count", sa.Integer, default=0),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id"), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.CheckConstraint("discount_value > 0", name="ck_coupon_discount_positive"),
    )
    op.create_index("ix_coupons_code", "coupons", ["code"], unique=True)
    op.create_index("ix_coupons_active_expires", "coupons", ["is_active", "expires_at"])

    # ─── 17. ORDERS ───────────────────────────────────────────
    op.create_table(
        "orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("order_code", sa.String(50), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id"), nullable=False),
        sa.Column("original_amount", sa.BigInteger, nullable=False),
        sa.Column("discount_amount", sa.BigInteger, default=0),
        sa.Column("amount", sa.BigInteger, nullable=False),
        sa.Column("coupon_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("coupons.id"), nullable=True),
        sa.Column("affiliate_code", sa.String(20), nullable=True),
        sa.Column("affiliate_id", postgresql.UUID(as_uuid=True), nullable=True),  # FK thêm sau
        sa.Column("utm_source", sa.String(100), nullable=True),
        sa.Column("utm_medium", sa.String(100), nullable=True),
        sa.Column("utm_campaign", sa.String(100), nullable=True),
        sa.Column("utm_content", sa.String(100), nullable=True),
        sa.Column("sepay_txn_id", sa.String(255), nullable=True),
        sa.Column("payment_method", sa.Enum("bank_transfer", "qr", name="payment_method", create_type=False), default="qr"),
        sa.Column("status", sa.Enum("pending", "completed", "expired", "cancelled", "refunded", name="order_status", create_type=False), default="pending", nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("refunded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("refund_note", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.CheckConstraint("amount >= 0", name="ck_orders_amount_positive"),
    )
    op.create_index("ix_orders_order_code", "orders", ["order_code"], unique=True)
    op.create_index("ix_orders_sepay_txn", "orders", ["sepay_txn_id"], unique=True)
    op.create_index("ix_orders_user_status", "orders", ["user_id", "status"])
    op.create_index("ix_orders_course_status", "orders", ["course_id", "status"])
    op.create_index("ix_orders_status", "orders", ["status"])
    op.create_index("ix_orders_created_at", "orders", ["created_at"])
    op.create_index("ix_orders_affiliate_code", "orders", ["affiliate_code"])

    # ─── 18. COUPON USAGES ────────────────────────────────────
    op.create_table(
        "coupon_usages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("coupon_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("coupons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("orders.id"), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("ix_coupon_usages_user_coupon", "coupon_usages", ["user_id", "coupon_id"])

    # ─── 19. AFFILIATES ───────────────────────────────────────
    op.create_table(
        "affiliates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ref_code", sa.String(20), nullable=False),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("total_clicks", sa.Integer, default=0),
        sa.Column("total_orders", sa.Integer, default=0),
        sa.Column("total_earnings", sa.BigInteger, default=0),
        sa.Column("paid_earnings", sa.BigInteger, default=0),
        sa.Column("pending_withdrawal", sa.BigInteger, default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.UniqueConstraint("user_id", name="uq_affiliates_user"),
    )
    op.create_index("ix_affiliates_ref_code", "affiliates", ["ref_code"], unique=True)

    # Thêm FK affiliate_id vào orders
    op.create_foreign_key("fk_orders_affiliate", "orders", "affiliates", ["affiliate_id"], ["id"])

    # ─── 20. AFFILIATE CLICKS ─────────────────────────────────
    op.create_table(
        "affiliate_clicks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("affiliate_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("affiliates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("visitor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("landing_url", sa.Text, nullable=True),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id"), nullable=True),
        sa.Column("cookie_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("converted_order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("orders.id"), nullable=True),
        sa.Column("converted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column("utm_source", sa.String(100), nullable=True),
        sa.Column("utm_medium", sa.String(100), nullable=True),
        sa.Column("utm_campaign", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("ix_aff_clicks_affiliate_date", "affiliate_clicks", ["affiliate_id", "created_at"])
    op.create_index("ix_aff_clicks_cookie", "affiliate_clicks", ["cookie_expires_at"])

    # ─── 21. COMMISSIONS ──────────────────────────────────────
    op.create_table(
        "commissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("affiliate_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("affiliates.id"), nullable=False),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("orders.id"), nullable=False),
        sa.Column("amount", sa.BigInteger, nullable=False),
        sa.Column("rate", sa.Integer, default=40),
        sa.Column("status", sa.Enum("pending", "approved", "paid", "cancelled", name="commission_status", create_type=False), default="pending", nullable=False),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.UniqueConstraint("order_id", name="uq_commission_order"),
    )
    op.create_index("ix_commissions_affiliate_status", "commissions", ["affiliate_id", "status"])
    op.create_index("ix_commissions_created_at", "commissions", ["created_at"])

    # ─── 22. WITHDRAWAL REQUESTS ──────────────────────────────
    op.create_table(
        "withdrawal_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("affiliate_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("affiliates.id"), nullable=False),
        sa.Column("amount", sa.BigInteger, nullable=False),
        sa.Column("bank_name", sa.String(100), nullable=False),
        sa.Column("account_number", sa.String(50), nullable=False),
        sa.Column("account_name", sa.String(255), nullable=False),
        sa.Column("status", sa.Enum("pending", "approved", "rejected", name="withdrawal_status", create_type=False), default="pending", nullable=False),
        sa.Column("admin_note", sa.Text, nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("ix_withdrawals_affiliate_status", "withdrawal_requests", ["affiliate_id", "status"])
    op.create_index("ix_withdrawals_created_at", "withdrawal_requests", ["created_at"])

    # ─── 23. CATEGORIES (Blog) ────────────────────────────────
    op.create_table(
        "categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("order_index", sa.Integer, default=0),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("ix_categories_slug", "categories", ["slug"], unique=True)

    # ─── 24. TAGS ─────────────────────────────────────────────
    op.create_table(
        "tags",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("ix_tags_slug", "tags", ["slug"], unique=True)

    # ─── 25. POSTS ────────────────────────────────────────────
    op.create_table(
        "posts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("categories.id"), nullable=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("slug", sa.String(500), nullable=False),
        sa.Column("content", postgresql.JSONB, nullable=True),
        sa.Column("content_html", sa.Text, nullable=True),
        sa.Column("excerpt", sa.String(500), nullable=True),
        sa.Column("thumbnail_url", sa.Text, nullable=True),
        sa.Column("status", sa.Enum("draft", "published", "archived", name="post_status", create_type=False), default="draft", nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("view_count", sa.Integer, default=0),
        sa.Column("reading_time", sa.Integer, default=0),
        sa.Column("meta_title", sa.String(255), nullable=True),
        sa.Column("meta_desc", sa.String(500), nullable=True),
        sa.Column("featured_course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("ix_posts_slug", "posts", ["slug"], unique=True)
    op.create_index("ix_posts_status_published", "posts", ["status", "published_at"])
    op.create_index("ix_posts_category_status", "posts", ["category_id", "status"])

    # ─── 26. POST TAGS ────────────────────────────────────────
    op.create_table(
        "post_tags",
        sa.Column("post_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
    )

    # ─── 27. POST COURSES ─────────────────────────────────────
    op.create_table(
        "post_courses",
        sa.Column("post_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True),
    )

    # ─── 28. LEADS ────────────────────────────────────────────
    op.create_table(
        "leads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("source_url", sa.Text, nullable=True),
        sa.Column("utm_source", sa.String(100), nullable=True),
        sa.Column("utm_medium", sa.String(100), nullable=True),
        sa.Column("utm_campaign", sa.String(100), nullable=True),
        sa.Column("utm_content", sa.String(100), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("synced_to_sheet", sa.Boolean, default=False, nullable=False),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_leads_email", "leads", ["email"])
    op.create_index("ix_leads_utm_source", "leads", ["utm_source"])
    op.create_index("ix_leads_created_at", "leads", ["created_at"])

    # ─── 29. VIDEO WATCH EVENTS ───────────────────────────────
    op.create_table(
        "video_watch_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("lesson_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("watch_percent", sa.Integer, nullable=False),
        sa.Column("watch_seconds", sa.Integer, default=0),
        sa.Column("session_id", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("ix_watch_events_lesson_percent", "video_watch_events", ["lesson_id", "watch_percent"])
    op.create_index("ix_watch_events_created_at", "video_watch_events", ["created_at"])

    # ─── 30. VIDEO WATCH CHECKPOINTS ──────────────────────────
    op.create_table(
        "video_watch_checkpoints",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("lesson_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("checkpoint_pct", sa.Integer, nullable=False),
        sa.Column("viewer_count", sa.Integer, default=0),
        sa.Column("total_views", sa.Integer, default=0),
        sa.Column("retention_rate", sa.Float, default=0.0),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("ix_checkpoint_lesson_pct", "video_watch_checkpoints", ["lesson_id", "checkpoint_pct"], unique=True)

    # ─── 31. PAGE VIEW EVENTS ─────────────────────────────────
    op.create_table(
        "page_view_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id"), nullable=True),
        sa.Column("page_type", sa.Enum("home", "course_list", "course_detail", "blog", "blog_detail", "checkout", name="page_type", create_type=False), nullable=False),
        sa.Column("page_url", sa.Text, nullable=True),
        sa.Column("referrer", sa.Text, nullable=True),
        sa.Column("session_id", sa.String(100), nullable=True),
        sa.Column("utm_source", sa.String(100), nullable=True),
        sa.Column("utm_medium", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("ix_page_views_course_type", "page_view_events", ["course_id", "page_type"])
    op.create_index("ix_page_views_created_at", "page_view_events", ["created_at"])

    # ─── 32. CHECKOUT SESSIONS ────────────────────────────────
    op.create_table(
        "checkout_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id"), nullable=False),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("orders.id"), nullable=True),
        sa.Column("outcome", sa.Enum("pending", "completed", "abandoned", "expired", name="checkout_outcome", create_type=False), default="pending", nullable=False),
        sa.Column("session_id", sa.String(100), nullable=True),
        sa.Column("utm_source", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("ix_checkout_sessions_created_at", "checkout_sessions", ["created_at"])
    op.create_index("ix_checkout_sessions_course", "checkout_sessions", ["course_id", "outcome"])

    # ─── 33. AUDIT LOGS ───────────────────────────────────────
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource", sa.String(100), nullable=True),
        sa.Column("resource_id", sa.String(255), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("old_data", postgresql.JSONB, nullable=True),
        sa.Column("new_data", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_audit_logs_user_action", "audit_logs", ["user_id", "action"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])

    # ─── 34. SITE SETTINGS ────────────────────────────────────
    op.create_table(
        "site_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("section", sa.String(50), nullable=False),
        sa.Column("key", sa.String(100), nullable=False),
        sa.Column("value", sa.Text, nullable=True),
        sa.Column("value_json", postgresql.JSONB, nullable=True),
        sa.Column("is_secret", sa.Boolean, default=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_settings_section_key", "site_settings", ["section", "key"], unique=True)


def downgrade() -> None:
    tables = [
        "site_settings", "audit_logs", "checkout_sessions", "page_view_events",
        "video_watch_checkpoints", "video_watch_events", "leads",
        "post_courses", "post_tags", "posts", "tags", "categories",
        "withdrawal_requests", "commissions", "affiliate_clicks", "affiliates",
        "coupon_usages", "orders", "coupons",
        "lesson_notes", "lesson_progress", "enrollments",
        "lesson_attachments", "lessons", "chapters",
        "course_reviews", "course_faqs", "course_requirements", "course_outcomes",
        "courses", "course_categories",
        "email_verifications", "password_reset_tokens", "users",
    ]
    for table in tables:
        op.drop_table(table)

    enums = [
        "user_role", "course_badge", "course_level", "order_status",
        "payment_method", "discount_type", "post_status", "commission_status",
        "withdrawal_status", "page_type", "checkout_outcome",
    ]
    for enum in enums:
        op.execute(f"DROP TYPE IF EXISTS {enum}")
