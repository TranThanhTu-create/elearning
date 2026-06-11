"""
Seed data cho EduVietPro — dữ liệu mẫu tiếng Việt
Chạy: cd backend && python -m seeds.seed_data
"""
import os
import sys
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

import pytz
from passlib.context import CryptContext
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

from app.database import Base
import app.models  # noqa — register all models

VN = pytz.timezone("Asia/Ho_Chi_Minh")

def now_vn() -> datetime:
    return datetime.now(VN)

def dt(days_ago: int = 0, **kwargs) -> datetime:
    return now_vn() - timedelta(days=days_ago, **kwargs)


pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_engine():
    url = os.getenv("DATABASE_URL_SYNC")
    if not url:
        raise RuntimeError("DATABASE_URL_SYNC not set in .env")
    return create_engine(url, echo=False)


def seed(session: Session):
    print("🌱  Bắt đầu seed dữ liệu mẫu...")

    # ─── 1. USERS ──────────────────────────────────────────────────────────────
    print("  → Users")
    admin_id   = str(uuid.uuid4())
    student_ids = [str(uuid.uuid4()) for _ in range(6)]

    users = [
        {
            "id": admin_id,
            "email": "admin@eduvietpro.vn",
            "password_hash": pwd_ctx.hash("Admin@123456"),
            "name": "Nguyễn Khánh Hưng",
            "phone": "0901234567",
            "role": "admin",
            "is_active": True,
            "is_email_verified": True,
            "ref_code": "ADMIN01",
            "last_login_at": dt(0),
            "created_at": dt(180),
            "updated_at": dt(0),
        },
        {
            "id": student_ids[0],
            "email": "tuan.anh@gmail.com",
            "password_hash": pwd_ctx.hash("Password123"),
            "name": "Nguyễn Tuấn Anh",
            "phone": "0912345678",
            "role": "student",
            "is_active": True,
            "is_email_verified": True,
            "ref_code": "TUANANH",
            "last_login_at": dt(1),
            "created_at": dt(120),
            "updated_at": dt(1),
        },
        {
            "id": student_ids[1],
            "email": "thi.mai@gmail.com",
            "password_hash": pwd_ctx.hash("Password123"),
            "name": "Trần Thị Mai",
            "phone": "0923456789",
            "role": "student",
            "is_active": True,
            "is_email_verified": True,
            "ref_code": "THIMAI1",
            "last_login_at": dt(2),
            "created_at": dt(90),
            "updated_at": dt(2),
        },
        {
            "id": student_ids[2],
            "email": "van.duc@gmail.com",
            "password_hash": pwd_ctx.hash("Password123"),
            "name": "Lê Văn Đức",
            "phone": "0934567890",
            "role": "student",
            "is_active": True,
            "is_email_verified": True,
            "ref_code": "VANDUC1",
            "last_login_at": dt(3),
            "created_at": dt(75),
            "updated_at": dt(3),
        },
        {
            "id": student_ids[3],
            "email": "hoai.thu@gmail.com",
            "password_hash": pwd_ctx.hash("Password123"),
            "name": "Phạm Hoài Thu",
            "phone": "0945678901",
            "role": "affiliate",
            "is_active": True,
            "is_email_verified": True,
            "ref_code": "HOAITU1",
            "last_login_at": dt(1),
            "created_at": dt(60),
            "updated_at": dt(1),
        },
        {
            "id": student_ids[4],
            "email": "minh.khoa@gmail.com",
            "password_hash": pwd_ctx.hash("Password123"),
            "name": "Đỗ Minh Khoa",
            "phone": "0956789012",
            "role": "student",
            "is_active": True,
            "is_email_verified": False,
            "ref_code": "MINHKH1",
            "last_login_at": None,
            "created_at": dt(10),
            "updated_at": dt(10),
        },
        {
            "id": student_ids[5],
            "email": "bao.chau@gmail.com",
            "password_hash": pwd_ctx.hash("Password123"),
            "name": "Vũ Bảo Châu",
            "phone": "0967890123",
            "role": "student",
            "is_active": True,
            "is_email_verified": True,
            "ref_code": "BAOCHA1",
            "last_login_at": dt(5),
            "created_at": dt(45),
            "updated_at": dt(5),
        },
    ]

    for u in users:
        session.execute(text("""
            INSERT INTO users (id, email, password_hash, name, phone, role,
                is_active, is_email_verified, ref_code, last_login_at,
                created_at, updated_at)
            VALUES (:id, :email, :password_hash, :name, :phone, :role,
                :is_active, :is_email_verified, :ref_code, :last_login_at,
                :created_at, :updated_at)
            ON CONFLICT (email) DO NOTHING
        """), u)

    # ─── 2. COURSE CATEGORIES ──────────────────────────────────────────────────
    print("  → Course categories")
    cat_ids = {k: str(uuid.uuid4()) for k in [
        "all", "marketing", "kinh_doanh", "quay_video", "tiktok", "facebook_ads"
    ]}

    categories = [
        {"id": cat_ids["marketing"],    "name": "Marketing Online",   "slug": "marketing-online",   "icon": "📢", "order_index": 1},
        {"id": cat_ids["kinh_doanh"],   "name": "Kinh Doanh",         "slug": "kinh-doanh",         "icon": "💼", "order_index": 2},
        {"id": cat_ids["quay_video"],   "name": "Quay Video",         "slug": "quay-video",         "icon": "🎬", "order_index": 3},
        {"id": cat_ids["tiktok"],       "name": "TikTok Marketing",   "slug": "tiktok-marketing",   "icon": "📱", "order_index": 4},
        {"id": cat_ids["facebook_ads"], "name": "Facebook & Instagram Ads", "slug": "facebook-instagram-ads", "icon": "📣", "order_index": 5},
    ]

    for c in categories:
        session.execute(text("""
            INSERT INTO course_categories (id, name, slug, icon, order_index, created_at, updated_at)
            VALUES (:id, :name, :slug, :icon, :order_index, NOW(), NOW())
            ON CONFLICT (slug) DO NOTHING
        """), c)

    # ─── 3. COURSES ────────────────────────────────────────────────────────────
    print("  → Courses")
    course_ids = {k: str(uuid.uuid4()) for k in [
        "quay_video", "kinh_doanh", "marketing_az", "tiktok", "fb_ads",
        "content_creator", "email_marketing", "seo"
    ]}

    courses = [
        {
            "id": course_ids["quay_video"],
            "category_id": cat_ids["quay_video"],
            "title": "Quay Video Chuyên Nghiệp Bằng Điện Thoại",
            "slug": "quay-video-chuyen-nghiep-bang-dien-thoai",
            "subtitle": "Từ người mới bắt đầu đến chuyên gia quay phim bằng smartphone",
            "description": "Khóa học toàn diện giúp bạn tạo ra những video chuyên nghiệp chỉ bằng điện thoại thông minh. Học cách bố cục, ánh sáng, âm thanh và dựng phim cơ bản.",
            "thumbnail_url": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
            "preview_video_id": "dQw4w9WgXcQ",
            "price": 1490000,
            "original_price": 2990000,
            "level": "beginner",
            "badge": "bestseller",
            "is_published": True,
            "total_lessons": 24,
            "total_students": 1247,
            "avg_rating": 4.8,
            "total_reviews": 186,
            "total_duration_seconds": 54000,
            "meta_title": "Quay Video Chuyên Nghiệp Bằng Điện Thoại | EduVietPro",
            "meta_description": "Học cách quay video chuyên nghiệp chỉ bằng điện thoại. Khóa học được 1,247+ học viên tin chọn.",
            "published_at": dt(90),
            "created_at": dt(100),
            "updated_at": dt(2),
        },
        {
            "id": course_ids["kinh_doanh"],
            "category_id": cat_ids["kinh_doanh"],
            "title": "Kinh Doanh Online Từ Số 0",
            "slug": "kinh-doanh-online-tu-so-0",
            "subtitle": "Xây dựng cửa hàng online và bán hàng hiệu quả từ đầu",
            "description": "Khóa học thực chiến giúp bạn xây dựng kinh doanh online từ đầu. Từ chọn sản phẩm, tạo cửa hàng, đến marketing và chăm sóc khách hàng.",
            "thumbnail_url": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
            "preview_video_id": "ScMzIvxBSi4",
            "price": 1990000,
            "original_price": 3490000,
            "level": "beginner",
            "badge": "new",
            "is_published": True,
            "total_lessons": 32,
            "total_students": 892,
            "avg_rating": 4.9,
            "total_reviews": 134,
            "total_duration_seconds": 72000,
            "meta_title": "Kinh Doanh Online Từ Số 0 | EduVietPro",
            "meta_description": "Xây dựng kinh doanh online thành công từ đầu. 892+ học viên đã đăng ký.",
            "published_at": dt(60),
            "created_at": dt(70),
            "updated_at": dt(3),
        },
        {
            "id": course_ids["marketing_az"],
            "category_id": cat_ids["marketing"],
            "title": "Marketing Online A–Z",
            "slug": "marketing-online-a-z",
            "subtitle": "Toàn bộ kiến thức marketing online bạn cần biết",
            "description": "Khóa học marketing online toàn diện từ A đến Z. Bao gồm SEO, Content Marketing, Email Marketing, Social Media và Paid Ads.",
            "thumbnail_url": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
            "preview_video_id": "9bZkp7q19f0",
            "price": 990000,
            "original_price": 1990000,
            "level": "intermediate",
            "badge": None,
            "is_published": True,
            "total_lessons": 28,
            "total_students": 2103,
            "avg_rating": 4.7,
            "total_reviews": 312,
            "total_duration_seconds": 63000,
            "meta_title": "Marketing Online A–Z | EduVietPro",
            "meta_description": "Khóa học marketing online toàn diện. 2,103+ học viên tin chọn.",
            "published_at": dt(120),
            "created_at": dt(130),
            "updated_at": dt(1),
        },
        {
            "id": course_ids["tiktok"],
            "category_id": cat_ids["tiktok"],
            "title": "TikTok Marketing Thực Chiến",
            "slug": "tiktok-marketing-thuc-chien",
            "subtitle": "Bùng nổ TikTok, xây kênh triệu view và kiếm tiền từ TikTok",
            "description": "Học cách tạo nội dung viral trên TikTok, xây dựng kênh từ 0, chạy quảng cáo TikTok Ads và kiếm tiền từ nền tảng này.",
            "thumbnail_url": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
            "preview_video_id": "JGwWNGJdvx8",
            "price": 1290000,
            "original_price": 2490000,
            "level": "beginner",
            "badge": "hot",
            "is_published": True,
            "total_lessons": 20,
            "total_students": 1580,
            "avg_rating": 4.8,
            "total_reviews": 234,
            "total_duration_seconds": 45000,
            "meta_title": "TikTok Marketing Thực Chiến | EduVietPro",
            "meta_description": "Xây kênh TikTok triệu view và kiếm tiền. 1,580+ học viên đăng ký.",
            "published_at": dt(45),
            "created_at": dt(50),
            "updated_at": dt(1),
        },
        {
            "id": course_ids["fb_ads"],
            "category_id": cat_ids["facebook_ads"],
            "title": "Facebook & Instagram Ads Nâng Cao",
            "slug": "facebook-instagram-ads-nang-cao",
            "subtitle": "Chạy quảng cáo Facebook và Instagram hiệu quả, tối ưu ROAS",
            "description": "Nắm vững Facebook Ads Manager, tối ưu chiến dịch, retargeting và scaling quảng cáo để đạt ROAS cao nhất.",
            "thumbnail_url": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
            "preview_video_id": "kffacxfA7G4",
            "price": 1190000,
            "original_price": 2190000,
            "level": "intermediate",
            "badge": None,
            "is_published": True,
            "total_lessons": 22,
            "total_students": 743,
            "avg_rating": 4.6,
            "total_reviews": 98,
            "total_duration_seconds": 49500,
            "meta_title": "Facebook & Instagram Ads Nâng Cao | EduVietPro",
            "meta_description": "Tối ưu Facebook Ads đạt ROAS cao. 743+ học viên tin dùng.",
            "published_at": dt(75),
            "created_at": dt(80),
            "updated_at": dt(4),
        },
        {
            "id": course_ids["content_creator"],
            "category_id": cat_ids["marketing"],
            "title": "Content Creator Chuyên Nghiệp",
            "slug": "content-creator-chuyen-nghiep",
            "subtitle": "Tạo nội dung hấp dẫn cho mọi nền tảng mạng xã hội",
            "description": "Học cách lên ý tưởng, viết nội dung, thiết kế hình ảnh và tạo video ngắn thu hút cho Facebook, Instagram, TikTok, YouTube.",
            "thumbnail_url": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
            "preview_video_id": "hT_nvWreIhg",
            "price": 890000,
            "original_price": 1690000,
            "level": "beginner",
            "badge": None,
            "is_published": True,
            "total_lessons": 18,
            "total_students": 456,
            "avg_rating": 4.5,
            "total_reviews": 67,
            "total_duration_seconds": 40500,
            "meta_title": "Content Creator Chuyên Nghiệp | EduVietPro",
            "meta_description": "Tạo nội dung thu hút cho mọi nền tảng. 456+ học viên đăng ký.",
            "published_at": dt(30),
            "created_at": dt(35),
            "updated_at": dt(7),
        },
        {
            "id": course_ids["email_marketing"],
            "category_id": cat_ids["marketing"],
            "title": "Email Marketing Tự Động Hóa",
            "slug": "email-marketing-tu-dong-hoa",
            "subtitle": "Xây dựng hệ thống email marketing tự động và tăng tỷ lệ chuyển đổi",
            "description": "Học cách xây dựng danh sách email, tạo phễu email tự động, A/B testing và tối ưu tỷ lệ mở mail và click.",
            "thumbnail_url": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
            "preview_video_id": "YkgkThdzX-8",
            "price": 790000,
            "original_price": 1490000,
            "level": "intermediate",
            "badge": None,
            "is_published": False,
            "total_lessons": 15,
            "total_students": 0,
            "avg_rating": 0.0,
            "total_reviews": 0,
            "total_duration_seconds": 33750,
            "meta_title": "Email Marketing Tự Động Hóa | EduVietPro",
            "meta_description": "Xây dựng hệ thống email marketing tự động hiệu quả.",
            "published_at": None,
            "created_at": dt(15),
            "updated_at": dt(1),
        },
        {
            "id": course_ids["seo"],
            "category_id": cat_ids["marketing"],
            "title": "SEO Thực Chiến Từ A Đến Z",
            "slug": "seo-thuc-chien-tu-a-den-z",
            "subtitle": "Đưa website lên top Google và tăng traffic organic bền vững",
            "description": "Khóa học SEO toàn diện: nghiên cứu từ khóa, on-page SEO, off-page SEO, technical SEO và xây dựng backlink chất lượng.",
            "thumbnail_url": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
            "preview_video_id": "C0DPdy98e4c",
            "price": 1090000,
            "original_price": 1990000,
            "level": "intermediate",
            "badge": None,
            "is_published": False,
            "total_lessons": 26,
            "total_students": 0,
            "avg_rating": 0.0,
            "total_reviews": 0,
            "total_duration_seconds": 58500,
            "meta_title": "SEO Thực Chiến Từ A Đến Z | EduVietPro",
            "meta_description": "Đưa website lên top Google với SEO thực chiến.",
            "published_at": None,
            "created_at": dt(7),
            "updated_at": dt(1),
        },
    ]

    for c in courses:
        session.execute(text("""
            INSERT INTO courses (
                id, category_id, title, slug, subtitle, description,
                thumbnail_url, preview_video_id, price, original_price,
                level, badge, is_published, total_lessons, total_students,
                avg_rating, total_reviews, total_duration_seconds,
                meta_title, meta_description, published_at, created_at, updated_at
            ) VALUES (
                :id, :category_id, :title, :slug, :subtitle, :description,
                :thumbnail_url, :preview_video_id, :price, :original_price,
                :level, :badge, :is_published, :total_lessons, :total_students,
                :avg_rating, :total_reviews, :total_duration_seconds,
                :meta_title, :meta_description, :published_at, :created_at, :updated_at
            ) ON CONFLICT (slug) DO NOTHING
        """), c)

    # ─── 4. COURSE OUTCOMES ────────────────────────────────────────────────────
    print("  → Course outcomes")
    outcomes = [
        # Quay video
        (course_ids["quay_video"], "Quay video chuyên nghiệp chỉ bằng điện thoại", 1),
        (course_ids["quay_video"], "Hiểu và ứng dụng các kỹ thuật bố cục hình ảnh", 2),
        (course_ids["quay_video"], "Thiết lập ánh sáng tự nhiên và nhân tạo cho video", 3),
        (course_ids["quay_video"], "Xử lý âm thanh và thu âm chất lượng cao", 4),
        (course_ids["quay_video"], "Dựng phim cơ bản bằng CapCut và DaVinci Resolve", 5),
        (course_ids["quay_video"], "Tạo ra video YouTube, TikTok, Reels đẹp mắt", 6),
        # Kinh doanh
        (course_ids["kinh_doanh"], "Chọn được sản phẩm kinh doanh phù hợp", 1),
        (course_ids["kinh_doanh"], "Xây dựng cửa hàng trên Shopee, Lazada, TikTok Shop", 2),
        (course_ids["kinh_doanh"], "Viết mô tả sản phẩm thu hút và tối ưu từ khóa", 3),
        (course_ids["kinh_doanh"], "Chạy quảng cáo trên các sàn thương mại điện tử", 4),
        (course_ids["kinh_doanh"], "Quản lý đơn hàng và chăm sóc khách hàng hiệu quả", 5),
        # Marketing A-Z
        (course_ids["marketing_az"], "Nắm vững toàn bộ kiến thức marketing online", 1),
        (course_ids["marketing_az"], "Xây dựng chiến lược content marketing hiệu quả", 2),
        (course_ids["marketing_az"], "Chạy và tối ưu các loại quảng cáo trả phí", 3),
        (course_ids["marketing_az"], "Đo lường và phân tích hiệu quả các chiến dịch", 4),
        # TikTok
        (course_ids["tiktok"], "Tạo video TikTok viral từ 0", 1),
        (course_ids["tiktok"], "Xây dựng kênh TikTok từ 0 đến 100K followers", 2),
        (course_ids["tiktok"], "Chạy quảng cáo TikTok Ads hiệu quả", 3),
        (course_ids["tiktok"], "Kiếm tiền từ TikTok qua nhiều hình thức khác nhau", 4),
        # FB Ads
        (course_ids["fb_ads"], "Tạo và quản lý tài khoản quảng cáo Facebook chuyên nghiệp", 1),
        (course_ids["fb_ads"], "Thiết kế chiến dịch quảng cáo đúng mục tiêu", 2),
        (course_ids["fb_ads"], "Tối ưu CPC, CPM, ROAS đạt mức cao nhất", 3),
        (course_ids["fb_ads"], "Xây dựng phễu retargeting và lookalike audience", 4),
    ]

    for course_id, outcome, idx in outcomes:
        session.execute(text("""
            INSERT INTO course_outcomes (id, course_id, outcome, order_index, created_at, updated_at)
            VALUES (gen_random_uuid(), :course_id, :outcome, :order_index, NOW(), NOW())
        """), {"course_id": course_id, "outcome": outcome, "order_index": idx})

    # ─── 5. COURSE REQUIREMENTS ────────────────────────────────────────────────
    print("  → Course requirements")
    requirements = [
        (course_ids["quay_video"], "Có điện thoại thông minh (iPhone hoặc Android)", 1),
        (course_ids["quay_video"], "Không cần kinh nghiệm quay phim trước đó", 2),
        (course_ids["quay_video"], "Kết nối internet để xem video bài học", 3),
        (course_ids["kinh_doanh"], "Có máy tính hoặc điện thoại kết nối internet", 1),
        (course_ids["kinh_doanh"], "Có vốn khởi đầu tối thiểu 2–5 triệu đồng", 2),
        (course_ids["kinh_doanh"], "Sẵn sàng dành 2–3 giờ/ngày để học và thực hành", 3),
        (course_ids["tiktok"], "Có tài khoản TikTok (có thể tạo mới)", 1),
        (course_ids["tiktok"], "Có điện thoại thông minh để quay và đăng video", 2),
        (course_ids["fb_ads"], "Đã có tài khoản Facebook Business Manager", 1),
        (course_ids["fb_ads"], "Có ngân sách quảng cáo tối thiểu 1–2 triệu đồng để thực hành", 2),
        (course_ids["fb_ads"], "Hiểu biết cơ bản về Facebook (đã học Marketing A-Z là lợi thế)", 3),
    ]

    for course_id, req, idx in requirements:
        session.execute(text("""
            INSERT INTO course_requirements (id, course_id, requirement, order_index, created_at, updated_at)
            VALUES (gen_random_uuid(), :course_id, :requirement, :order_index, NOW(), NOW())
        """), {"course_id": course_id, "requirement": req, "order_index": idx})

    # ─── 6. COURSE FAQs ────────────────────────────────────────────────────────
    print("  → Course FAQs")
    faqs = [
        (course_ids["quay_video"], "Tôi cần điện thoại gì để học?", "Bất kỳ smartphone nào chụp ảnh được đều học được. Từ iPhone 8 hoặc Android 2018 trở lên là đủ tốt.", 1),
        (course_ids["quay_video"], "Khóa học có bao gồm phần dựng phim không?", "Có! Khóa học có 4 bài về dựng phim cơ bản với CapCut (miễn phí, trên điện thoại) và giới thiệu DaVinci Resolve.", 2),
        (course_ids["quay_video"], "Sau khi mua có xem được bao lâu?", "Bạn có quyền truy cập trọn đời, xem lại bất kỳ lúc nào kể cả khi có bản cập nhật mới.", 3),
        (course_ids["kinh_doanh"], "Tôi chưa có sản phẩm, học được không?", "Hoàn toàn được! Bài học đầu tiên sẽ hướng dẫn bạn chọn sản phẩm phù hợp với ngân sách và kỹ năng.", 1),
        (course_ids["kinh_doanh"], "Khóa học dạy bán hàng trên nền tảng nào?", "Shopee, Lazada, TikTok Shop và Facebook Marketplace. Bạn có thể chọn một hoặc tất cả.", 2),
        (course_ids["tiktok"], "TikTok có bị chặn ở Việt Nam không?", "TikTok hoạt động bình thường tại Việt Nam. Nếu gặp sự cố kết nối, dùng VPN là được.", 1),
        (course_ids["tiktok"], "Mất bao lâu để đạt 10K followers?", "Tùy vào nội dung và tần suất đăng. Học viên của chúng tôi trung bình đạt 10K trong 30–60 ngày.", 2),
    ]

    for course_id, question, answer, idx in faqs:
        session.execute(text("""
            INSERT INTO course_faqs (id, course_id, question, answer, order_index, created_at, updated_at)
            VALUES (gen_random_uuid(), :course_id, :question, :answer, :order_index, NOW(), NOW())
        """), {"course_id": course_id, "question": question, "answer": answer, "order_index": idx})

    # ─── 7. CHAPTERS & LESSONS ─────────────────────────────────────────────────
    print("  → Chapters & Lessons")

    chapter_data = {
        course_ids["quay_video"]: [
            {
                "title": "Giới Thiệu & Chuẩn Bị",
                "order_index": 1,
                "lessons": [
                    ("Chào mừng đến với khóa học", "dQw4w9WgXcQ", True, 480),
                    ("Thiết bị cần chuẩn bị", "dQw4w9WgXcQ", True, 720),
                    ("Cài đặt ứng dụng hỗ trợ", "dQw4w9WgXcQ", False, 600),
                ]
            },
            {
                "title": "Kỹ Thuật Quay Cơ Bản",
                "order_index": 2,
                "lessons": [
                    ("Bố cục hình ảnh — Rule of Thirds", "dQw4w9WgXcQ", False, 900),
                    ("Các góc máy phổ biến", "dQw4w9WgXcQ", False, 840),
                    ("Ổn định máy và gimbal", "dQw4w9WgXcQ", False, 780),
                ]
            },
            {
                "title": "Ánh Sáng Cho Video",
                "order_index": 3,
                "lessons": [
                    ("Ánh sáng tự nhiên — giờ vàng", "dQw4w9WgXcQ", False, 960),
                    ("Đèn LED ring light và softbox", "dQw4w9WgXcQ", False, 840),
                    ("Khắc phục vấn đề ánh sáng", "dQw4w9WgXcQ", False, 720),
                ]
            },
            {
                "title": "Âm Thanh & Thu Âm",
                "order_index": 4,
                "lessons": [
                    ("Micro lavalier và directional mic", "dQw4w9WgXcQ", False, 900),
                    ("Thu âm lồng tiếng chuyên nghiệp", "dQw4w9WgXcQ", False, 840),
                ]
            },
            {
                "title": "Dựng Phim Với CapCut",
                "order_index": 5,
                "lessons": [
                    ("Giao diện và workflow CapCut", "dQw4w9WgXcQ", False, 1080),
                    ("Cắt ghép và chuyển cảnh", "dQw4w9WgXcQ", False, 960),
                    ("Thêm nhạc, text và hiệu ứng", "dQw4w9WgXcQ", False, 900),
                    ("Xuất video đúng định dạng", "dQw4w9WgXcQ", False, 600),
                ]
            },
        ],
        course_ids["tiktok"]: [
            {
                "title": "Hiểu TikTok Algorithm",
                "order_index": 1,
                "lessons": [
                    ("TikTok hoạt động như thế nào?", "JGwWNGJdvx8", True, 720),
                    ("Tại sao video của bạn không viral?", "JGwWNGJdvx8", True, 840),
                    ("Tối ưu profile TikTok", "JGwWNGJdvx8", False, 600),
                ]
            },
            {
                "title": "Sản Xuất Nội Dung TikTok",
                "order_index": 2,
                "lessons": [
                    ("7 format video viral nhất TikTok", "JGwWNGJdvx8", False, 1080),
                    ("Hook 3 giây đầu tiên", "JGwWNGJdvx8", False, 960),
                    ("Dựng video TikTok bằng CapCut", "JGwWNGJdvx8", False, 1200),
                    ("Đăng bài đúng giờ vàng", "JGwWNGJdvx8", False, 480),
                ]
            },
            {
                "title": "TikTok Ads",
                "order_index": 3,
                "lessons": [
                    ("Tổng quan TikTok Ads Manager", "JGwWNGJdvx8", False, 900),
                    ("Tạo chiến dịch In-Feed Ads", "JGwWNGJdvx8", False, 1080),
                    ("Tối ưu và scale quảng cáo", "JGwWNGJdvx8", False, 960),
                ]
            },
            {
                "title": "Kiếm Tiền Từ TikTok",
                "order_index": 4,
                "lessons": [
                    ("TikTok Creator Fund", "JGwWNGJdvx8", False, 720),
                    ("Affiliate marketing trên TikTok", "JGwWNGJdvx8", False, 900),
                    ("TikTok Shop — bán hàng trực tiếp", "JGwWNGJdvx8", False, 1080),
                ]
            },
        ],
    }

    lesson_ids_by_course: dict[str, list[str]] = {}

    for course_id, chapters in chapter_data.items():
        lesson_ids_by_course[course_id] = []
        for chap in chapters:
            chapter_id = str(uuid.uuid4())
            session.execute(text("""
                INSERT INTO chapters (id, course_id, title, order_index, created_at, updated_at)
                VALUES (:id, :course_id, :title, :order_index, NOW(), NOW())
            """), {"id": chapter_id, "course_id": course_id, "title": chap["title"], "order_index": chap["order_index"]})

            for lesson_idx, (title, vid_id, is_free, duration) in enumerate(chap["lessons"], 1):
                lesson_id = str(uuid.uuid4())
                lesson_ids_by_course[course_id].append(lesson_id)
                session.execute(text("""
                    INSERT INTO lessons (id, chapter_id, title, youtube_video_id, is_free, duration_seconds, order_index, created_at, updated_at)
                    VALUES (:id, :chapter_id, :title, :youtube_video_id, :is_free, :duration_seconds, :order_index, NOW(), NOW())
                """), {
                    "id": lesson_id, "chapter_id": chapter_id, "title": title,
                    "youtube_video_id": vid_id, "is_free": is_free,
                    "duration_seconds": duration, "order_index": lesson_idx
                })

    # Thêm chapters đơn giản cho các course còn lại
    for course_key in ["kinh_doanh", "marketing_az", "fb_ads", "content_creator", "email_marketing", "seo"]:
        cid = course_ids[course_key]
        lesson_ids_by_course[cid] = []
        for chap_idx in range(1, 4):
            chapter_id = str(uuid.uuid4())
            session.execute(text("""
                INSERT INTO chapters (id, course_id, title, order_index, created_at, updated_at)
                VALUES (:id, :course_id, :title, :order_index, NOW(), NOW())
            """), {"id": chapter_id, "course_id": cid, "title": f"Chương {chap_idx}", "order_index": chap_idx})

            for less_idx in range(1, 4):
                lesson_id = str(uuid.uuid4())
                lesson_ids_by_course[cid].append(lesson_id)
                session.execute(text("""
                    INSERT INTO lessons (id, chapter_id, title, youtube_video_id, is_free, duration_seconds, order_index, created_at, updated_at)
                    VALUES (:id, :chapter_id, :title, :youtube_video_id, :is_free, :duration_seconds, :order_index, NOW(), NOW())
                """), {
                    "id": lesson_id, "chapter_id": chapter_id,
                    "title": f"Bài {less_idx} — Chương {chap_idx}",
                    "youtube_video_id": "dQw4w9WgXcQ",
                    "is_free": (less_idx == 1 and chap_idx == 1),
                    "duration_seconds": 600 + less_idx * 120,
                    "order_index": less_idx,
                })

    # ─── 8. COURSE REVIEWS ─────────────────────────────────────────────────────
    print("  → Course reviews")
    reviews = [
        (course_ids["quay_video"],   student_ids[0], 5, "Khóa học rất tuyệt vời! Tôi đã quay được video chuyên nghiệp chỉ sau 2 tuần. Thầy giảng rất dễ hiểu và có nhiều ví dụ thực tế."),
        (course_ids["quay_video"],   student_ids[1], 5, "Video bài học chất lượng cao, âm thanh rõ ràng. Tôi đặc biệt thích phần về ánh sáng — đã giúp tôi cải thiện video rất nhiều."),
        (course_ids["quay_video"],   student_ids[2], 4, "Nội dung tốt nhưng tôi mong có thêm bài về dựng phim trên máy tính. Vẫn rất đáng đồng tiền."),
        (course_ids["tiktok"],       student_ids[3], 5, "Sau khi học xong, kênh TikTok của tôi đã đạt 50K followers trong 45 ngày. Cách giảng thực chiến, dễ áp dụng ngay."),
        (course_ids["tiktok"],       student_ids[0], 5, "Phần TikTok Ads rất chi tiết và có số liệu thực tế. Tôi đã giảm được 40% chi phí quảng cáo sau khi áp dụng."),
        (course_ids["marketing_az"], student_ids[4], 4, "Tổng quan đầy đủ về marketing online. Tốt cho người mới bắt đầu muốn hiểu bức tranh toàn cảnh."),
        (course_ids["kinh_doanh"],   student_ids[1], 5, "Đã mở được cửa hàng Shopee và có đơn đầu tiên sau 2 tuần. Khóa học rất thực tế và step-by-step rõ ràng!"),
        (course_ids["fb_ads"],       student_ids[5], 4, "Phần targeting audience rất hay. Tôi học được nhiều tricks mà trước đây không biết. Sẽ giới thiệu cho bạn bè."),
    ]

    for course_id, user_id, rating, comment in reviews:
        session.execute(text("""
            INSERT INTO course_reviews (id, course_id, user_id, rating, comment, is_verified, created_at, updated_at)
            VALUES (gen_random_uuid(), :course_id, :user_id, :rating, :comment, TRUE, NOW() - INTERVAL '10 days', NOW())
            ON CONFLICT (course_id, user_id) DO NOTHING
        """), {"course_id": course_id, "user_id": user_id, "rating": rating, "comment": comment})

    # ─── 9. COUPONS ────────────────────────────────────────────────────────────
    print("  → Coupons")
    coupon_ids = {k: str(uuid.uuid4()) for k in ["eduviet20", "newmember", "tiktok30", "vip50"]}

    coupons = [
        {
            "id": coupon_ids["eduviet20"],
            "code": "EDUVIET20",
            "description": "Giảm 20% tất cả khóa học",
            "discount_type": "percent",
            "discount_value": 20,
            "min_order_amount": 500000,
            "max_discount_amount": 500000,
            "max_uses": 500,
            "used_count": 127,
            "max_uses_per_user": 1,
            "is_active": True,
            "expires_at": dt(-30),
        },
        {
            "id": coupon_ids["newmember"],
            "code": "NEWMEMBER",
            "description": "Học viên mới giảm 15%",
            "discount_type": "percent",
            "discount_value": 15,
            "min_order_amount": 0,
            "max_discount_amount": 300000,
            "max_uses": 1000,
            "used_count": 89,
            "max_uses_per_user": 1,
            "is_active": True,
            "expires_at": dt(-60),
        },
        {
            "id": coupon_ids["tiktok30"],
            "code": "TIKTOK30",
            "description": "Giảm 30% khóa TikTok Marketing",
            "discount_type": "percent",
            "discount_value": 30,
            "min_order_amount": 0,
            "max_discount_amount": 400000,
            "max_uses": 200,
            "used_count": 45,
            "max_uses_per_user": 1,
            "course_id": course_ids["tiktok"],
            "is_active": True,
            "expires_at": dt(-15),
        },
        {
            "id": coupon_ids["vip50"],
            "code": "VIP50",
            "description": "Giảm 500.000₫ cho khách VIP",
            "discount_type": "fixed",
            "discount_value": 500000,
            "min_order_amount": 1000000,
            "max_discount_amount": None,
            "max_uses": 50,
            "used_count": 12,
            "max_uses_per_user": 1,
            "is_active": True,
            "expires_at": dt(-90),
        },
    ]

    for c in coupons:
        course_id = c.pop("course_id", None)
        session.execute(text("""
            INSERT INTO coupons (
                id, code, description, discount_type, discount_value,
                min_order_amount, max_discount_amount, max_uses, used_count,
                max_uses_per_user, course_id, is_active, expires_at, created_at, updated_at
            ) VALUES (
                :id, :code, :description, :discount_type, :discount_value,
                :min_order_amount, :max_discount_amount, :max_uses, :used_count,
                :max_uses_per_user, :course_id, :is_active, :expires_at, NOW(), NOW()
            ) ON CONFLICT (code) DO NOTHING
        """), {**c, "course_id": course_id})

    # ─── 10. ORDERS ────────────────────────────────────────────────────────────
    print("  → Orders")
    order_ids = []

    order_data = [
        # (user_id, course_id, original, discount, final, coupon_id, status, days_ago)
        (student_ids[0], course_ids["quay_video"],   1490000, 298000, 1192000, coupon_ids["eduviet20"],  "completed",  85),
        (student_ids[0], course_ids["tiktok"],       1290000, 387000,  903000, coupon_ids["tiktok30"],  "completed",  40),
        (student_ids[1], course_ids["quay_video"],   1490000, 223500, 1266500, coupon_ids["newmember"], "completed",  78),
        (student_ids[1], course_ids["kinh_doanh"],   1990000,      0, 1990000, None,                   "completed",  55),
        (student_ids[2], course_ids["marketing_az"],  990000, 148500,  841500, coupon_ids["newmember"], "completed",  70),
        (student_ids[2], course_ids["fb_ads"],       1190000,      0, 1190000, None,                   "completed",  50),
        (student_ids[3], course_ids["tiktok"],       1290000, 387000,  903000, coupon_ids["tiktok30"],  "completed",  35),
        (student_ids[3], course_ids["kinh_doanh"],   1990000, 500000, 1490000, coupon_ids["vip50"],     "completed",  20),
        (student_ids[4], course_ids["quay_video"],   1490000,      0, 1490000, None,                   "pending",     1),
        (student_ids[5], course_ids["marketing_az"],  990000,      0,  990000, None,                   "completed",  40),
        (student_ids[5], course_ids["tiktok"],       1290000, 193500, 1096500, coupon_ids["newmember"], "refunded",   30),
    ]

    for i, (user_id, course_id, original, discount, final, coupon_id, status, days_ago) in enumerate(order_data):
        oid = str(uuid.uuid4())
        order_ids.append((oid, user_id, course_id, final, status, coupon_id))
        order_code = f"EVP{str(100001 + i)}"
        created = dt(days_ago)
        completed_at = created + timedelta(minutes=5) if status == "completed" else None
        refunded_at = created + timedelta(days=3) if status == "refunded" else None

        session.execute(text("""
            INSERT INTO orders (
                id, user_id, course_id, order_code, original_amount, discount_amount, amount,
                coupon_id, payment_method, status, expires_at,
                completed_at, refunded_at, created_at, updated_at
            ) VALUES (
                :id, :user_id, :course_id, :order_code, :original_amount, :discount_amount, :amount,
                :coupon_id, 'bank_transfer', :status, :expires_at,
                :completed_at, :refunded_at, :created_at, :updated_at
            ) ON CONFLICT (order_code) DO NOTHING
        """), {
            "id": oid, "user_id": user_id, "course_id": course_id,
            "order_code": order_code,
            "original_amount": original, "discount_amount": discount, "amount": final,
            "coupon_id": coupon_id, "status": status,
            "expires_at": created + timedelta(minutes=30),
            "completed_at": completed_at, "refunded_at": refunded_at,
            "created_at": created, "updated_at": created,
        })

    # ─── 11. ENROLLMENTS & LESSON PROGRESS ────────────────────────────────────
    print("  → Enrollments & lesson progress")
    for order_id, user_id, course_id, amount, status, _ in order_ids:
        if status != "completed":
            continue

        enrollment_id = str(uuid.uuid4())
        lessons_for_course = lesson_ids_by_course.get(course_id, [])
        last_lesson = lessons_for_course[3] if len(lessons_for_course) > 3 else (lessons_for_course[-1] if lessons_for_course else None)
        progress = 60 if len(lessons_for_course) > 5 else 40

        session.execute(text("""
            INSERT INTO enrollments (id, user_id, course_id, order_id, last_lesson_id, progress_percent, created_at, updated_at)
            VALUES (:id, :user_id, :course_id, :order_id, :last_lesson_id, :progress_percent, NOW() - INTERVAL '5 days', NOW())
            ON CONFLICT (user_id, course_id) DO NOTHING
        """), {
            "id": enrollment_id, "user_id": user_id, "course_id": course_id,
            "order_id": order_id, "last_lesson_id": last_lesson,
            "progress_percent": progress,
        })

        for lesson_id in lessons_for_course[:4]:
            session.execute(text("""
                INSERT INTO lesson_progress (id, user_id, lesson_id, is_completed, watch_seconds, completed_at, created_at, updated_at)
                VALUES (gen_random_uuid(), :user_id, :lesson_id, TRUE, 600, NOW() - INTERVAL '3 days', NOW() - INTERVAL '5 days', NOW())
                ON CONFLICT (user_id, lesson_id) DO NOTHING
            """), {"user_id": user_id, "lesson_id": lesson_id})

    # ─── 12. AFFILIATE ─────────────────────────────────────────────────────────
    print("  → Affiliates")
    affiliate_id = str(uuid.uuid4())
    session.execute(text("""
        INSERT INTO affiliates (
            id, user_id, ref_code, is_active,
            total_clicks, total_orders, total_earnings, paid_earnings,
            pending_withdrawal, created_at, updated_at
        ) VALUES (
            :id, :user_id, 'HOAITU1', TRUE,
            245, 8, 6432000, 3000000, 3432000, NOW() - INTERVAL '55 days', NOW()
        ) ON CONFLICT (user_id) DO NOTHING
    """), {"id": affiliate_id, "user_id": student_ids[3]})

    # Affiliate clicks
    for i in range(5):
        click_id = str(uuid.uuid4())
        session.execute(text("""
            INSERT INTO affiliate_clicks (
                id, affiliate_id, ref_code, ip_address, user_agent,
                landing_url, cookie_expires_at, created_at
            ) VALUES (
                :id, :aff_id, 'HOAITU1', '27.73.100.' || :ip,
                'Mozilla/5.0 Chrome/120', 'https://eduvietpro.vn/khoa-hoc',
                NOW() + INTERVAL '30 days', NOW() - INTERVAL ':days days'
            )
        """), {"id": click_id, "aff_id": affiliate_id, "ip": str(i + 1), "days": str(i * 5)})

    # Commissions
    completed_orders = [(oid, uid, cid, amt) for oid, uid, cid, amt, st, _ in order_ids if st == "completed"]
    for i, (order_id, user_id, course_id, amount) in enumerate(completed_orders[:4]):
        commission_amount = int(amount * 0.4)
        status = "paid" if i < 2 else "approved"
        session.execute(text("""
            INSERT INTO commissions (
                id, affiliate_id, order_id, amount, rate, status, created_at, updated_at
            ) VALUES (
                gen_random_uuid(), :aff_id, :order_id, :amount, 0.40, :status, NOW() - INTERVAL '20 days', NOW()
            ) ON CONFLICT (affiliate_id, order_id) DO NOTHING
        """), {"aff_id": affiliate_id, "order_id": order_id, "amount": commission_amount, "status": status})

    # Withdrawal request
    session.execute(text("""
        INSERT INTO withdrawal_requests (
            id, affiliate_id, amount, bank_name, account_number, account_name,
            status, admin_note, created_at, updated_at
        ) VALUES (
            gen_random_uuid(), :aff_id, 3000000,
            'Vietcombank', '0123456789', 'PHAM HOAI THU',
            'approved', 'Đã chuyển khoản ngày 20/05/2026', NOW() - INTERVAL '25 days', NOW()
        )
    """), {"aff_id": affiliate_id})

    # ─── 13. BLOG ──────────────────────────────────────────────────────────────
    print("  → Blog categories, tags, posts")

    blog_cat_ids = {k: str(uuid.uuid4()) for k in ["kinh_nghiem", "cong_cu", "case_study"]}
    blog_categories = [
        {"id": blog_cat_ids["kinh_nghiem"], "name": "Kinh Nghiệm",      "slug": "kinh-nghiem",      "description": "Bài học kinh nghiệm thực tế"},
        {"id": blog_cat_ids["cong_cu"],     "name": "Công Cụ & Phần Mềm", "slug": "cong-cu-phan-mem", "description": "Giới thiệu và hướng dẫn sử dụng công cụ"},
        {"id": blog_cat_ids["case_study"],  "name": "Case Study",        "slug": "case-study",       "description": "Phân tích chiến dịch thực tế"},
    ]

    for bc in blog_categories:
        session.execute(text("""
            INSERT INTO categories (id, name, slug, description, created_at, updated_at)
            VALUES (:id, :name, :slug, :description, NOW(), NOW())
            ON CONFLICT (slug) DO NOTHING
        """), bc)

    tag_ids = {k: str(uuid.uuid4()) for k in ["tiktok", "facebook", "seo", "video", "kinh_doanh"]}
    tags = [
        {"id": tag_ids["tiktok"],    "name": "TikTok",           "slug": "tiktok"},
        {"id": tag_ids["facebook"],  "name": "Facebook Ads",     "slug": "facebook-ads"},
        {"id": tag_ids["seo"],       "name": "SEO",              "slug": "seo"},
        {"id": tag_ids["video"],     "name": "Video Marketing",  "slug": "video-marketing"},
        {"id": tag_ids["kinh_doanh"], "name": "Kinh Doanh Online", "slug": "kinh-doanh-online"},
    ]

    for t in tags:
        session.execute(text("""
            INSERT INTO tags (id, name, slug, created_at, updated_at)
            VALUES (:id, :name, :slug, NOW(), NOW())
            ON CONFLICT (slug) DO NOTHING
        """), t)

    post_ids = [str(uuid.uuid4()) for _ in range(4)]
    posts = [
        {
            "id": post_ids[0],
            "category_id": blog_cat_ids["kinh_nghiem"],
            "author_id": admin_id,
            "title": "7 Bí Quyết Tạo Video TikTok Viral Từ Đầu",
            "slug": "7-bi-quyet-tao-video-tiktok-viral-tu-dau",
            "excerpt": "Khám phá 7 bí quyết để tạo video TikTok triệu view dù bạn là người mới bắt đầu hay đã có kinh nghiệm.",
            "content": '{"type":"doc","content":[{"type":"paragraph","content":[{"type":"text","text":"Để tạo video TikTok viral, bạn cần hiểu rõ algorithm và tâm lý người xem..."}]}]}',
            "content_html": "<p>Để tạo video TikTok viral, bạn cần hiểu rõ algorithm và tâm lý người xem...</p>",
            "status": "published",
            "reading_time": 8,
            "view_count": 12450,
            "featured_image_url": "https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?w=800",
            "meta_title": "7 Bí Quyết Tạo Video TikTok Viral | EduVietPro Blog",
            "meta_description": "Học 7 bí quyết tạo video TikTok viral được kiểm chứng từ hàng trăm học viên.",
            "published_at": dt(15),
            "created_at": dt(20),
            "updated_at": dt(3),
        },
        {
            "id": post_ids[1],
            "category_id": blog_cat_ids["cong_cu"],
            "author_id": admin_id,
            "title": "So Sánh CapCut vs DaVinci Resolve: Nên Chọn Phần Mềm Nào?",
            "slug": "so-sanh-capcut-vs-davinci-resolve",
            "excerpt": "Phân tích ưu nhược điểm của CapCut và DaVinci Resolve để giúp bạn chọn công cụ dựng phim phù hợp nhất.",
            "content": '{"type":"doc","content":[{"type":"paragraph","content":[{"type":"text","text":"CapCut và DaVinci Resolve đều là những phần mềm dựng phim tuyệt vời..."}]}]}',
            "content_html": "<p>CapCut và DaVinci Resolve đều là những phần mềm dựng phim tuyệt vời...</p>",
            "status": "published",
            "reading_time": 6,
            "view_count": 8920,
            "featured_image_url": "https://images.unsplash.com/photo-1574717024653-61fd2cf4d44d?w=800",
            "meta_title": "So Sánh CapCut vs DaVinci Resolve | EduVietPro Blog",
            "meta_description": "CapCut hay DaVinci Resolve? Phân tích chi tiết giúp bạn chọn đúng công cụ.",
            "published_at": dt(8),
            "created_at": dt(12),
            "updated_at": dt(2),
        },
        {
            "id": post_ids[2],
            "category_id": blog_cat_ids["case_study"],
            "author_id": admin_id,
            "title": "Case Study: Từ 0 Đến 500K Followers TikTok Trong 3 Tháng",
            "slug": "case-study-tu-0-den-500k-followers-tiktok-3-thang",
            "excerpt": "Hành trình thực tế của học viên Trần Thị Mai từ kênh 0 follower đến 500K chỉ trong 3 tháng áp dụng phương pháp của EduVietPro.",
            "content": '{"type":"doc","content":[{"type":"paragraph","content":[{"type":"text","text":"Đây là câu chuyện thật 100% của học viên Trần Thị Mai..."}]}]}',
            "content_html": "<p>Đây là câu chuyện thật 100% của học viên Trần Thị Mai...</p>",
            "status": "published",
            "reading_time": 12,
            "view_count": 24680,
            "featured_image_url": "https://images.unsplash.com/photo-1611162618071-b39a2ec055fb?w=800",
            "meta_title": "Case Study: 0 → 500K TikTok Followers | EduVietPro Blog",
            "meta_description": "Câu chuyện thật từ học viên đạt 500K followers TikTok chỉ trong 3 tháng.",
            "published_at": dt(5),
            "created_at": dt(7),
            "updated_at": dt(1),
        },
        {
            "id": post_ids[3],
            "category_id": blog_cat_ids["kinh_nghiem"],
            "author_id": admin_id,
            "title": "Hướng Dẫn Xây Dựng Chiến Lược Content Marketing 2026",
            "slug": "huong-dan-xay-dung-chien-luoc-content-marketing-2026",
            "excerpt": "Cập nhật xu hướng content marketing mới nhất 2026 và cách xây dựng chiến lược phù hợp cho doanh nghiệp vừa và nhỏ tại Việt Nam.",
            "content": '{"type":"doc","content":[{"type":"paragraph","content":[{"type":"text","text":"Content marketing năm 2026 đã thay đổi rất nhiều so với những năm trước..."}]}]}',
            "content_html": "<p>Content marketing năm 2026 đã thay đổi rất nhiều so với những năm trước...</p>",
            "status": "draft",
            "reading_time": 10,
            "view_count": 0,
            "featured_image_url": None,
            "meta_title": None,
            "meta_description": None,
            "published_at": None,
            "created_at": dt(2),
            "updated_at": dt(1),
        },
    ]

    for p in posts:
        session.execute(text("""
            INSERT INTO posts (
                id, category_id, author_id, title, slug, excerpt, content, content_html,
                status, reading_time, view_count, featured_image_url,
                meta_title, meta_description, published_at, created_at, updated_at
            ) VALUES (
                :id, :category_id, :author_id, :title, :slug, :excerpt, :content::jsonb, :content_html,
                :status, :reading_time, :view_count, :featured_image_url,
                :meta_title, :meta_description, :published_at, :created_at, :updated_at
            ) ON CONFLICT (slug) DO NOTHING
        """), p)

    # Post tags
    post_tag_map = [
        (post_ids[0], tag_ids["tiktok"]),
        (post_ids[0], tag_ids["video"]),
        (post_ids[1], tag_ids["video"]),
        (post_ids[2], tag_ids["tiktok"]),
        (post_ids[2], tag_ids["kinh_doanh"]),
        (post_ids[3], tag_ids["kinh_doanh"]),
    ]
    for post_id, tag_id in post_tag_map:
        session.execute(text("""
            INSERT INTO post_tags (post_id, tag_id) VALUES (:post_id, :tag_id)
            ON CONFLICT DO NOTHING
        """), {"post_id": post_id, "tag_id": tag_id})

    # Post courses (CTA cuối bài)
    session.execute(text("""
        INSERT INTO post_courses (post_id, course_id, order_index)
        VALUES (:post_id, :course_id, 1)
        ON CONFLICT DO NOTHING
    """), {"post_id": post_ids[0], "course_id": course_ids["tiktok"]})

    session.execute(text("""
        INSERT INTO post_courses (post_id, course_id, order_index)
        VALUES (:post_id, :course_id, 1)
        ON CONFLICT DO NOTHING
    """), {"post_id": post_ids[1], "course_id": course_ids["quay_video"]})

    # ─── 14. LEADS ─────────────────────────────────────────────────────────────
    print("  → Leads")
    leads = [
        ("Nguyễn Thành Long", "thanh.long@gmail.com", "0901111222", "https://eduvietpro.vn", "facebook", "tiktok_cta", "tiktok_video_jul", None),
        ("Lê Thị Hương", "thi.huong@yahoo.com", "0902222333", "https://eduvietpro.vn/khoa-hoc/tiktok", "google", "organic_seo", None, None),
        ("Trần Văn Bình", "van.binh@gmail.com", "0903333444", "https://eduvietpro.vn", "tiktok", "tiktok_ads_jun", None, None),
        ("Phạm Thị Lan", "thi.lan@gmail.com", "0904444555", "https://eduvietpro.vn/blog", "facebook", "fb_retargeting", "summer_sale", student_ids[0]),
        ("Đỗ Minh Trí", "minh.tri@hotmail.com", "0905555666", "https://eduvietpro.vn", "google", "brand_search", None, None),
        ("Vũ Thị Ngọc", "thi.ngoc@gmail.com", "0906666777", "https://eduvietpro.vn/khoa-hoc", "direct", None, None, None),
        ("Hoàng Văn Phúc", "van.phuc@gmail.com", "0907777888", "https://eduvietpro.vn", "zalo", "zalo_ads_may", "tiktok30_lead", None),
        ("Nguyễn Thị Kim Anh", "kim.anh@gmail.com", "0908888999", "https://eduvietpro.vn/blog/tiktok", "facebook", "tiktok_cta", None, None),
    ]

    for name, email, phone, source_url, utm_source, utm_campaign, utm_content, user_id in leads:
        session.execute(text("""
            INSERT INTO leads (
                id, name, email, phone, source_url,
                utm_source, utm_campaign, utm_content,
                user_id, synced_to_sheet, created_at
            ) VALUES (
                gen_random_uuid(), :name, :email, :phone, :source_url,
                :utm_source, :utm_campaign, :utm_content,
                :user_id, FALSE, NOW() - INTERVAL '7 days'
            ) ON CONFLICT (email) DO NOTHING
        """), {
            "name": name, "email": email, "phone": phone,
            "source_url": source_url, "utm_source": utm_source,
            "utm_campaign": utm_campaign, "utm_content": utm_content,
            "user_id": user_id,
        })

    # ─── 15. ANALYTICS ─────────────────────────────────────────────────────────
    print("  → Analytics (video watch events, page views, checkout sessions)")

    # Video watch events
    for lesson_id in (lesson_ids_by_course.get(course_ids["quay_video"], []) or [])[:3]:
        for pct in [25, 50, 75, 100]:
            for user_id in student_ids[:3]:
                session.execute(text("""
                    INSERT INTO video_watch_events (
                        id, user_id, lesson_id, watch_percent, watch_seconds,
                        session_id, created_at
                    ) VALUES (
                        gen_random_uuid(), :user_id, :lesson_id, :pct, :secs,
                        gen_random_uuid()::text, NOW() - INTERVAL '10 days'
                    )
                """), {"user_id": user_id, "lesson_id": lesson_id, "pct": pct, "secs": pct * 6})

    # Video watch checkpoints (for heatmap)
    for lesson_id in (lesson_ids_by_course.get(course_ids["quay_video"], []) or [])[:2]:
        for pct in [0, 25, 50, 75, 100]:
            retention = max(30, 100 - pct * (pct // 30))
            session.execute(text("""
                INSERT INTO video_watch_checkpoints (
                    id, lesson_id, checkpoint_pct, viewer_count, total_views, retention_rate, updated_at
                ) VALUES (
                    gen_random_uuid(), :lesson_id, :pct, :viewers, 150, :retention, NOW()
                ) ON CONFLICT (lesson_id, checkpoint_pct) DO NOTHING
            """), {"lesson_id": lesson_id, "pct": pct, "viewers": int(150 * retention / 100), "retention": retention})

    # Page view events
    page_types = ["home", "course_list", "course_detail", "checkout"]
    for i, page_type in enumerate(page_types):
        for j in range(3):
            session.execute(text("""
                INSERT INTO page_view_events (
                    id, session_id, page_type, course_id, utm_source, created_at
                ) VALUES (
                    gen_random_uuid(), gen_random_uuid()::text, :page_type,
                    :course_id, 'facebook', NOW() - INTERVAL ':days days'
                )
            """), {
                "page_type": page_type,
                "course_id": course_ids["quay_video"] if page_type in ("course_detail", "checkout") else None,
                "days": str(i + j),
            })

    # Checkout sessions
    for i in range(5):
        outcome = "completed" if i < 3 else ("abandoned" if i == 3 else "expired")
        session.execute(text("""
            INSERT INTO checkout_sessions (
                id, session_id, course_id, outcome, created_at, updated_at
            ) VALUES (
                gen_random_uuid(), gen_random_uuid()::text, :course_id,
                :outcome, NOW() - INTERVAL ':days days', NOW()
            )
        """), {"course_id": course_ids["quay_video"], "outcome": outcome, "days": str(i * 3)})

    # ─── 16. SITE SETTINGS ─────────────────────────────────────────────────────
    print("  → Site settings")

    site_settings = [
        # Tổng quan
        ("general", "site_name",         "EduVietPro",                                           None,    False, "Tên website"),
        ("general", "site_tagline",      "Học Thực Chiến — Thành Công Thực Tế",                 None,    False, "Tagline ngắn"),
        ("general", "site_url",          "https://eduvietpro.vn",                                None,    False, "URL chính của website"),
        ("general", "contact_email",     "support@eduvietpro.vn",                                None,    False, "Email hỗ trợ"),
        ("general", "contact_phone",     "0901 234 567",                                          None,    False, "Số điện thoại liên hệ"),
        ("general", "facebook_url",      "https://facebook.com/eduvietpro",                       None,    False, "Facebook Fanpage"),
        ("general", "youtube_url",       "https://youtube.com/@eduvietpro",                       None,    False, "YouTube Channel"),
        ("general", "tiktok_url",        "https://tiktok.com/@eduvietpro",                        None,    False, "TikTok Profile"),
        # Thanh toán
        ("payment", "bank_name",         "Vietcombank",                                           None,    False, "Tên ngân hàng"),
        ("payment", "bank_account",      "0123456789",                                            None,    False, "Số tài khoản"),
        ("payment", "bank_holder",       "NGUYEN KHANH HUNG",                                    None,    False, "Tên chủ tài khoản"),
        ("payment", "sepay_webhook_key", "sep_wh_secret_key_here",                               None,    True,  "SePay webhook secret key"),
        ("payment", "order_expiry_mins", "30",                                                    None,    False, "Thời gian hết hạn đơn hàng (phút)"),
        # Email
        ("email",   "resend_api_key",    "re_live_key_here",                                     None,    True,  "Resend API key"),
        ("email",   "from_email",        "no-reply@eduvietpro.vn",                               None,    False, "Email gửi đi"),
        ("email",   "from_name",         "EduVietPro",                                            None,    False, "Tên hiển thị khi gửi email"),
        # Analytics
        ("analytics", "ga4_id",          "G-XXXXXXXXXX",                                         None,    False, "Google Analytics 4 Measurement ID"),
        ("analytics", "meta_pixel_id",   "XXXXXXXXXXXXXXXXX",                                    None,    False, "Meta Pixel ID"),
        ("analytics", "clarity_id",      "xxxxxxxxxx",                                           None,    False, "Microsoft Clarity Project ID"),
        # Affiliate
        ("affiliate", "commission_rate", "40",                                                    None,    False, "Tỷ lệ hoa hồng (%)"),
        ("affiliate", "cookie_days",     "30",                                                    None,    False, "Thời gian cookie (ngày)"),
        ("affiliate", "min_withdrawal",  "500000",                                               None,    False, "Số tiền rút tối thiểu (VND)"),
        # Lead magnet
        ("lead",    "popup_enabled",     "true",                                                  None,    False, "Bật/tắt popup lead magnet"),
        ("lead",    "popup_title",       "Học Miễn Phí 5 Ngày",                                  None,    False, "Tiêu đề popup"),
        ("lead",    "popup_subtitle",    "Webinar thực chiến về TikTok Marketing",               None,    False, "Phụ đề popup"),
        ("lead",    "popup_delay_secs",  "5",                                                    None,    False, "Thời gian delay trước khi hiện popup (giây)"),
        ("lead",    "webinar_zoom_link", "https://zoom.us/j/xxxxxxxxxx",                         None,    False, "Link Zoom webinar"),
        ("lead",    "sheets_doc_id",     "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms",       None,    True,  "Google Sheets Document ID"),
        # SEO
        ("seo",     "meta_title_suffix", "| EduVietPro",                                         None,    False, "Hậu tố title SEO"),
        ("seo",     "meta_description",  "EduVietPro — Nền tảng học marketing online thực chiến hàng đầu Việt Nam", None, False, "Meta description mặc định"),
        ("seo",     "og_image_url",      "https://eduvietpro.vn/og-image.jpg",                  None,    False, "Default Open Graph image"),
    ]

    for section, key, value, value_json, is_secret, description in site_settings:
        session.execute(text("""
            INSERT INTO site_settings (id, section, key, value, value_json, is_secret, description, created_at, updated_at)
            VALUES (gen_random_uuid(), :section, :key, :value, :value_json, :is_secret, :description, NOW(), NOW())
            ON CONFLICT (section, key) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW()
        """), {
            "section": section, "key": key, "value": value,
            "value_json": value_json, "is_secret": is_secret, "description": description,
        })

    session.commit()
    print("\n✅  Seed hoàn tất!")
    print("   Admin:   admin@eduvietpro.vn / Admin@123456")
    print("   Student: tuan.anh@gmail.com  / Password123")
    print("   Affiliate: hoai.thu@gmail.com / Password123")


if __name__ == "__main__":
    engine = get_engine()
    with Session(engine) as session:
        seed(session)
