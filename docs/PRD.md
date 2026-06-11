# PRD — Website Bán Khóa Học Online

> **Phiên bản:** 1.0 | **Ngày:** 29/05/2026 | **Trạng thái:** Draft

---

## Mục Lục

1. [Tổng Quan Sản Phẩm](#1-tổng-quan-sản-phẩm)
2. [Tech Stack](#2-tech-stack)
3. [Người Dùng & Phân Quyền](#3-người-dùng--phân-quyền)
4. [Danh Sách Tính Năng](#4-danh-sách-tính-năng)
5. [Landing Page Từng Khóa Học](#5-landing-page-từng-khóa-học)
6. [Flow Thanh Toán SePay](#6-flow-thanh-toán-sepay)
7. [Popup Lead Magnet](#7-popup-lead-magnet)
8. [Hệ Thống Affiliate](#8-hệ-thống-affiliate)
9. [Database Schema](#9-database-schema)
10. [API Endpoints](#10-api-endpoints)
11. [UX & Thiết Kế](#11-ux--thiết-kế)
12. [Định Dạng Việt Nam](#12-định-dạng-việt-nam)
13. [Yêu Cầu Phi Chức Năng](#13-yêu-cầu-phi-chức-năng)
14. [Roadmap](#14-roadmap)

---

## 1. Tổng Quan Sản Phẩm

### 1.1 Mô Tả

Website bán khóa học online là nền tảng e-learning cho phép người dùng mua nhiều khóa học riêng lẻ, xem video (YouTube embed được bảo vệ bởi backend), theo dõi tiến độ học tập, và nhận chứng chỉ hoàn thành. Hệ thống tích hợp thanh toán tự động qua SePay, chương trình affiliate 40% hoa hồng, blog chuyên môn, và analytics toàn diện. Toàn bộ giao diện, nội dung, định dạng số và múi giờ theo chuẩn Việt Nam.

### 1.2 Quyết Định Cốt Lõi Đã Chốt

| Hạng mục | Quyết định |
|---|---|
| Thanh toán | Mua từng khóa riêng lẻ (không cần giỏ hàng) |
| Quyền truy cập | Lifetime — mua 1 lần dùng mãi mãi |
| Instructor | Chỉ 1 người (chủ sở hữu) |
| Giá | Mỗi khóa có giá riêng |
| Video | YouTube IFrame API (bảo vệ videoId bằng backend) |
| Thanh toán | SePay — QR + chuyển khoản tự động |
| Affiliate | 40% cố định, rút tiền thủ công |
| Ngôn ngữ | Tiếng Việt duy nhất |
| Múi giờ | UTC+7 (Asia/Ho_Chi_Minh) toàn hệ thống |
| Lead magnet | Webinar miễn phí 5 ngày qua Zoom |
| Lưu leads | Google Sheet + DB nội bộ |
| Blog | 1 tác giả, không comment |

### 1.3 Mục Tiêu Kinh Doanh

- Tăng doanh thu từ bán khóa học trực tuyến
- Xây dựng nền tảng học tập chuyên nghiệp, dễ sử dụng
- Thu thập leads qua popup webinar miễn phí
- Phát triển mạng lưới affiliate tự động hóa hoa hồng
- Đo lường hiệu quả marketing qua GA4, Meta Pixel, UTM

---

## 2. Tech Stack

### 2.1 Tổng Quan

```
┌─────────────────────────────────────────────────────────┐
│              FRONTEND (Next.js 14)                      │
│  Landing | Courses | Blog | Checkout | Dashboard | Admin │
└────────────────────┬────────────────────────────────────┘
                     │ REST API / JSON
┌────────────────────▼────────────────────────────────────┐
│              BACKEND (FastAPI / Python)                  │
│  Auth | Courses | Payments | Blog | Analytics | Affiliate│
└──────┬─────────────┬──────────────┬──────────────────────┘
       │             │              │
┌──────▼──────┐ ┌────▼────┐ ┌──────▼──────────────────────┐
│ PostgreSQL  │ │  Redis  │ │  Cloudflare R2              │
│ (Supabase)  │ │(Upstash)│ │  Ảnh, PDF, Avatar           │
└─────────────┘ └─────────┘ └─────────────────────────────┘

External Services:
  SePay (Thanh toán)  │  Google Sheets API (Leads)
  Resend.com (Email)  │  YouTube IFrame API (Video)
  GA4 + Meta Pixel    │  Microsoft Clarity (Heatmap)
```

### 2.2 Chi Tiết Tech Stack

| Thành phần | Công nghệ | Lý do chọn |
|---|---|---|
| **Backend** | FastAPI (Python 3.12) | Async, nhanh, nhẹ, tự sinh Swagger docs |
| **Frontend** | Next.js 14 (App Router) + TypeScript | SSR/SSG cho SEO, React ecosystem |
| **Styling** | Tailwind CSS | Nhanh, responsive, không cần CSS riêng |
| **Database** | PostgreSQL (Supabase) | Production-ready, free tier, realtime |
| **ORM** | SQLAlchemy 2.0 + Alembic | Type-safe, migration dễ |
| **Cache** | Redis (Upstash free) | Session, rate limiting, idempotency |
| **File storage** | Cloudflare R2 | Rẻ hơn S3, CDN toàn cầu, 10GB free |
| **Video** | YouTube IFrame API | Miễn phí, CDN toàn cầu |
| **Email** | Resend.com | 3.000 email/tháng free, DX tốt |
| **Thanh toán** | SePay | QR tự động, webhook Việt Nam |
| **Blog editor** | TipTap (React) | Rich text mạnh nhất cho Next.js |
| **Auth** | JWT + Google OAuth (NextAuth) | Đơn giản, bảo mật |
| **Analytics** | GA4 + Meta Pixel + tự build | Tracking toàn diện |
| **Heatmap** | Microsoft Clarity | Miễn phí hoàn toàn |
| **Deploy FE** | Vercel | CI/CD tự động, free |
| **Deploy BE** | Railway | Free tier, dễ scale |
| **Múi giờ** | `pytz` / `pendulum` (Python), `date-fns-tz` (JS) | UTC+7 toàn hệ thống |

### 2.3 Cấu Trúc Thư Mục Dự Án

```
project/
├── backend/                    # FastAPI
│   ├── app/
│   │   ├── api/               # Route handlers
│   │   │   ├── auth.py
│   │   │   ├── courses.py
│   │   │   ├── orders.py
│   │   │   ├── blog.py
│   │   │   ├── affiliate.py
│   │   │   ├── leads.py
│   │   │   ├── analytics.py
│   │   │   └── admin/
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   ├── utils/
│   │   │   ├── timezone.py    # Xử lý UTC+7
│   │   │   ├── formatters.py  # Định dạng tiền VND
│   │   │   └── sepay.py       # SePay webhook verify
│   │   └── main.py
│   ├── alembic/               # DB migrations
│   └── requirements.txt
│
├── frontend/                   # Next.js 14
│   ├── app/
│   │   ├── (public)/
│   │   │   ├── page.tsx       # Trang chủ
│   │   │   ├── courses/
│   │   │   │   ├── page.tsx   # Danh sách khóa
│   │   │   │   └── [slug]/
│   │   │   │       └── page.tsx  # Landing page khóa
│   │   │   └── blog/
│   │   │       ├── page.tsx
│   │   │       └── [slug]/page.tsx
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   └── register/
│   │   ├── (dashboard)/
│   │   │   ├── dashboard/     # Học viên
│   │   │   └── learn/[slug]/[lessonId]/
│   │   └── (admin)/
│   │       └── admin/
│   ├── components/
│   │   ├── ui/                # Shadcn/UI components
│   │   ├── video/             # YouTube player + watermark
│   │   ├── checkout/          # QR SePay
│   │   └── popup/             # Lead magnet
│   └── lib/
│       ├── format.ts          # Định dạng VND, ngày giờ
│       └── api.ts             # API client
│
└── PRD.md
```

---

## 3. Người Dùng & Phân Quyền

### 3.1 Các Vai Trò

| Vai trò | Mô tả | Quyền hạn |
|---|---|---|
| **Admin** | Chủ sở hữu | Toàn quyền hệ thống |
| **Student** | Học viên | Xem, mua khóa, học, affiliate |
| **Visitor** | Khách chưa đăng nhập | Xem public pages |

### 3.2 User Stories

#### Khách (Visitor)
- Tôi muốn xem danh sách khóa học để chọn khóa phù hợp
- Tôi muốn xem landing page từng khóa để quyết định mua
- Tôi muốn xem bài viết blog miễn phí để đánh giá chất lượng
- Tôi muốn đăng ký nhận webinar miễn phí 5 ngày qua Zoom
- Tôi muốn xem thử video miễn phí trước khi mua

#### Học Viên (Student)
- Tôi muốn đăng ký tài khoản bằng email hoặc Google
- Tôi muốn mua khóa học và thanh toán bằng QR SePay
- Tôi muốn xem video, tua, chỉnh tốc độ phát (0.75x–2x)
- Tôi muốn theo dõi tiến độ học của mình theo %
- Tôi muốn tạo link affiliate để giới thiệu cho bạn bè
- Tôi muốn xem lịch sử giao dịch và khóa đã mua
- Tôi muốn tự xóa tài khoản nếu muốn
- Tôi muốn tải tài liệu đính kèm (PDF) của từng bài học

#### Admin
- Tôi muốn thêm/sửa/xóa khóa học, chương, bài học
- Tôi muốn set bài học nào là free, bài nào cần mua
- Tôi muốn viết bài blog bằng rich text editor
- Tôi muốn xem dashboard doanh thu theo ngày/tuần/tháng
- Tôi muốn quản lý đơn hàng và học viên
- Tôi muốn phê duyệt yêu cầu rút hoa hồng affiliate
- Tôi muốn tạo và quản lý mã giảm giá

---

## 4. Danh Sách Tính Năng

> **Ký hiệu:** 🔴 MVP (Phase 1) | 🟡 Phase 2 | 🟢 Phase 3

### 4.1 Xác Thực & Quản Lý Tài Khoản

| # | Phase | Tính năng | Ghi chú kỹ thuật |
|---|---|---|---|
| 1 | 🔴 | Đăng ký bằng email + mật khẩu | Xác thực email sau đăng ký |
| 2 | 🔴 | Đăng nhập Google OAuth | NextAuth.js provider |
| 3 | 🔴 | Quên mật khẩu — reset qua email | Token hết hạn sau 1 giờ |
| 4 | 🔴 | Xác thực email sau đăng ký | Resend.com gửi mail |
| 5 | 🔴 | Phân quyền Admin / Student | Middleware bảo vệ route |
| 6 | 🔴 | Tự xóa tài khoản | Soft delete, giữ lịch sử giao dịch |
| 7 | 🔴 | Cập nhật hồ sơ: họ tên, avatar | Upload ảnh lên Cloudflare R2 |
| 8 | 🔴 | Đổi mật khẩu | Xác nhận mật khẩu cũ trước |
| 9 | 🟡 | Lịch sử đăng nhập (thiết bị, IP, thời gian) | Bảo mật tài khoản |
| 10 | 🟡 | Chặn tài khoản vi phạm (admin) | is_active = false |
| 11 | 🟢 | Giới hạn thiết bị đăng nhập (tối đa 2) | Chống chia sẻ tài khoản |

### 4.2 Khóa Học

| # | Phase | Tính năng | Ghi chú kỹ thuật |
|---|---|---|---|
| 12 | 🔴 | Trang danh sách khóa học `/courses` | Filter, sort, search |
| 13 | 🔴 | Landing page từng khóa `/courses/[slug]` | Sales page đầy đủ |
| 14 | 🔴 | Cấu trúc: Khóa → Chương → Bài học | Nested, order_index |
| 15 | 🔴 | Admin tự set bài nào free, bài nào locked | Toggle từng bài |
| 16 | 🔴 | Video YouTube embed (backend bảo vệ) | Chỉ trả videoId khi đã mua |
| 17 | 🔴 | Tua video, chỉnh tốc độ (0.75x–2x) | YouTube IFrame API |
| 18 | 🔴 | Đánh dấu bài học hoàn thành | POST `/progress` |
| 19 | 🔴 | Tiến độ % hoàn thành mỗi khóa | Hiển thị thanh tiến trình |
| 20 | 🔴 | Trailer video giới thiệu khóa | YouTube embed public |
| 21 | 🔴 | Danh sách chương/bài (syllabus) trên landing | Hiển thị free/locked icon |
| 22 | 🔴 | Tải tài liệu đính kèm (PDF) mỗi bài | Cloudflare R2 signed URL |
| 23 | 🔴 | Watermark email học viên trên video | Canvas overlay |
| 24 | 🔴 | Tiếp tục học — bài đang dở | Lưu lesson_id cuối cùng xem |
| 25 | 🟡 | Badge: Bestseller, Mới, Sale | Admin gán nhãn |
| 26 | 🟡 | Combo/Bundle nhiều khóa | Giá riêng cho gói |
| 27 | 🟡 | Ghi chú (notes) trong khi xem video | Lưu theo timestamp |
| 28 | 🟢 | Quiz cuối chương | Trắc nghiệm đơn giản |
| 29 | 🟢 | Certificate hoàn thành | PDF có tên, ngày |
| 30 | 🟢 | Phụ đề / transcript | SRT file upload |

### 4.3 Thanh Toán SePay

| # | Phase | Tính năng | Ghi chú kỹ thuật |
|---|---|---|---|
| 31 | 🔴 | Trang checkout từng khóa | Hiển thị giá định dạng VND |
| 32 | 🔴 | Tạo QR SePay động + STK ngân hàng | Mã đơn hàng duy nhất |
| 33 | 🔴 | Webhook tự động mở khóa khi nhận tiền | Verify HMAC signature |
| 34 | 🔴 | Order hết hạn sau 30 phút chưa thanh toán | Cron job tự expire |
| 35 | 🔴 | Email xác nhận sau thanh toán thành công | Gửi ngay qua Resend |
| 36 | 🔴 | Lịch sử giao dịch (admin + user) | Lọc theo ngày, trạng thái |
| 37 | 🔴 | Mã giảm giá / coupon (% hoặc số tiền) | Giới hạn lượt sử dụng |
| 38 | 🟡 | Flash sale — giá ưu đãi có thời hạn | Countdown timer |
| 39 | 🟡 | Invoice PDF gửi email | Sau mỗi giao dịch |
| 40 | 🟡 | Upsell: "Học viên mua khóa này cũng mua..." | Cross-sell trên checkout |
| 41 | 🟢 | Hoàn tiền (refund) thủ công qua admin | Ghi log |

### 4.4 Blog

| # | Phase | Tính năng | Ghi chú kỹ thuật |
|---|---|---|---|
| 42 | 🔴 | Danh sách bài viết + category + tag | Slug tùy chỉnh |
| 43 | 🔴 | Trang chi tiết bài viết | SEO meta, OG image |
| 44 | 🔴 | Admin viết bài bằng TipTap editor | Upload ảnh nội bộ |
| 45 | 🔴 | Draft / Published / Archived | Trạng thái bài viết |
| 46 | 🔴 | Lên lịch đăng bài (schedule) | `published_at` tương lai |
| 47 | 🔴 | SEO fields: meta title, meta desc, slug | Tự động tạo nếu bỏ trống |
| 48 | 🔴 | Reading time tự động tính | Hiển thị trên đầu bài |
| 49 | 🔴 | View count hiển thị | Tăng mỗi khi load trang |
| 50 | 🔴 | CTA khóa học liên quan cuối bài | Admin gắn khi viết |
| 51 | 🟡 | Related posts (bài viết liên quan) | Cùng category/tag |
| 52 | 🟡 | Table of contents tự động (TOC) | Trích xuất heading |
| 53 | 🟡 | Share lên Facebook / Zalo | OG meta đầy đủ |
| 54 | 🟡 | Newsletter subscribe cuối bài | Thu email độc giả |
| 55 | 🟡 | RSS Feed | Auto generate |
| 56 | 🟢 | Reaction (like/heart) bài viết | Không cần đăng nhập |

### 4.5 Dashboard Học Viên

| # | Phase | Tính năng | Ghi chú kỹ thuật |
|---|---|---|---|
| 57 | 🔴 | Danh sách khóa đã mua | Thumbnail + tên + % tiến độ |
| 58 | 🔴 | Tiếp tục học — bài đang dở | Bài cuối cùng xem |
| 59 | 🔴 | Tiến độ % mỗi khóa (thanh tiến trình) | Cập nhật real-time |
| 60 | 🔴 | Lịch sử giao dịch cá nhân | Ngày (UTC+7), số tiền VND |
| 61 | 🔴 | Thông tin cá nhân + đổi mật khẩu | Cập nhật avatar |
| 62 | 🔴 | Tự xóa tài khoản | Xác nhận 2 bước |
| 63 | 🟡 | Thống kê affiliate (click, doanh số, hoa hồng) | Biểu đồ đơn giản |
| 64 | 🟡 | Yêu cầu rút hoa hồng | Nhập STK, admin duyệt |

### 4.6 Affiliate System

| # | Phase | Tính năng | Ghi chú kỹ thuật |
|---|---|---|---|
| 65 | 🟡 | Mỗi học viên có link affiliate riêng | Mã duy nhất mỗi người |
| 66 | 🟡 | Hoa hồng 40% cố định trên giá bán | Tính sau webhook SePay OK |
| 67 | 🟡 | Cookie duration 30 ngày | Click link → mua trong 30 ngày |
| 68 | 🟡 | Dashboard: click, đơn hàng, hoa hồng | Theo tháng, biểu đồ |
| 69 | 🟡 | Yêu cầu rút tiền (nhập STK ngân hàng) | Admin xử lý thủ công |
| 70 | 🟡 | Admin phê duyệt / từ chối yêu cầu rút | Lịch sử rút tiền |
| 71 | 🟡 | Email thông báo khi có hoa hồng mới | Real-time notify |
| 72 | 🟢 | Báo cáo affiliate tổng hợp cho admin | Export Excel |

### 4.7 Lead Magnet & Marketing

| # | Phase | Tính năng | Ghi chú kỹ thuật |
|---|---|---|---|
| 73 | 🔴 | Popup thu email + SĐT → tặng webinar 5 ngày | Hiện sau 30s hoặc scroll 50% |
| 74 | 🔴 | Lưu leads vào Google Sheet tự động | Google Sheets API |
| 75 | 🔴 | Lưu leads vào DB nội bộ (backup) | Bảng `leads` |
| 76 | 🔴 | Email xác nhận + thông tin Zoom sau đăng ký | Gửi ngay sau submit |
| 77 | 🔴 | Cookie ẩn popup 7 ngày | Không hiện lại nếu đã submit/đóng |
| 78 | 🟡 | Testimonial / review từng khóa | Học viên đánh giá sao + nhận xét |
| 79 | 🟡 | Waiting list khi khóa chưa mở bán | Email khi mở bán |
| 80 | 🟡 | Countdown timer flash sale trên landing | Deadline tự động tắt |
| 81 | 🟢 | Leaderboard học viên tích cực | Dựa trên % hoàn thành |
| 82 | 🟢 | Zalo OA thông báo | Tích hợp Zalo API |

### 4.8 Email Automation

| # | Phase | Tính năng | Ghi chú kỹ thuật |
|---|---|---|---|
| 83 | 🔴 | Email chào mừng sau đăng ký tài khoản | Gửi ngay lập tức |
| 84 | 🔴 | Email xác nhận thanh toán + link vào học | Sau webhook SePay OK |
| 85 | 🔴 | Email xác nhận đăng ký webinar + Zoom link | Sau submit popup |
| 86 | 🟡 | Email nhắc học (3 ngày không vào hệ thống) | Cron job hàng ngày |
| 87 | 🟡 | Email thông báo khóa học mới ra mắt | Gửi cho tất cả học viên |
| 88 | 🟡 | Email chúc mừng hoàn thành khóa học | Kèm link tải chứng chỉ |
| 89 | 🟢 | Email upsell sau khi hoàn thành khóa | 7 ngày sau khi xong |

### 4.9 Analytics & Báo Cáo

| # | Phase | Tính năng | Ghi chú kỹ thuật |
|---|---|---|---|
| 90 | 🔴 | Google Analytics 4 | Events: page_view, purchase, lead |
| 91 | 🔴 | Meta Pixel (Facebook/Instagram Ads) | Purchase, Lead, ViewContent |
| 92 | 🔴 | UTM tracking | Lưu vào DB với mỗi đơn hàng |
| 93 | 🟡 | Video analytics: lượt xem, % hoàn thành | Theo từng bài học |
| 94 | 🟡 | Funnel report: Xem trang → Checkout → Mua | Tỷ lệ chuyển đổi |
| 95 | 🟡 | Dashboard admin: doanh thu ngày/tuần/tháng | Biểu đồ đường |
| 96 | 🟡 | Top khóa học theo doanh thu, lượt mua | Bảng xếp hạng |
| 97 | 🟡 | Microsoft Clarity (heatmap miễn phí) | Script embed |
| 98 | 🟡 | Báo cáo học viên: đăng ký, tỷ lệ hoàn thành | Theo khóa |
| 99 | 🟡 | Export báo cáo Excel / CSV | Admin download |
| 100 | 🟢 | Cohort analysis | Phân tích xa hơn |
| 101 | 🟢 | Alert doanh thu bất thường | Email cho admin |

### 4.10 Admin Panel

| # | Phase | Tính năng | Ghi chú kỹ thuật |
|---|---|---|---|
| 102 | 🔴 | Dashboard tổng quan (doanh thu, học viên, đơn hàng) | So sánh hôm qua |
| 103 | 🔴 | CRUD khóa học + chương + bài học | Drag-drop sắp xếp thứ tự |
| 104 | 🔴 | Set bài free/locked, nhập YouTube videoId | Toggle từng bài |
| 105 | 🔴 | CRUD bài blog + TipTap editor | Upload ảnh, SEO fields |
| 106 | 🔴 | Quản lý học viên (xem, khóa, cấp quyền) | Tìm kiếm theo email |
| 107 | 🔴 | Quản lý đơn hàng + trạng thái | Lọc theo ngày, khóa |
| 108 | 🔴 | Quản lý coupon (tạo, vô hiệu hóa) | Số lần sử dụng còn lại |
| 109 | 🟡 | Quản lý affiliate (phê duyệt rút tiền) | Lịch sử rút tiền |
| 110 | 🟡 | Quản lý leads (xem, export) | Đồng bộ Google Sheet |
| 111 | 🟡 | Cài đặt website (logo, màu sắc, thông tin) | Config toàn cục |
| 112 | 🟡 | Audit log (ai làm gì lúc mấy giờ UTC+7) | Ghi log mọi action |
| 113 | 🟢 | Quản lý trang tĩnh (About, Contact, Terms) | CMS đơn giản |

---

## 5. Landing Page Từng Khóa Học

**URL:** `/courses/[slug]` — Sales page dài, đầy đủ thông tin để quyết định mua.

### Cấu Trúc Sections

| Section | Nội dung |
|---|---|
| **Hero** | Tiêu đề khóa, mô tả ngắn, giá (định dạng VND), nút "Mua ngay", thumbnail/trailer |
| **Bạn sẽ học được gì** | 4–8 điểm chính, icon, lấy ý từ USP khóa học |
| **Nội dung chi tiết (Syllabus)** | Danh sách chương → bài học, thời lượng, icon free/locked |
| **Thông tin giảng viên** | Ảnh, tên, kinh nghiệm, thành tích |
| **Testimonial / Review** | Đánh giá sao + nhận xét của học viên cũ |
| **FAQ** | 5–8 câu hỏi thường gặp, accordion UI |
| **Giá & CTA** | Giá gốc, giá sale (nếu có), countdown, nút "Mua ngay" |
| **Khóa học liên quan** | Gợi ý 2–3 khóa khác |

### Yêu Cầu Kỹ Thuật

- **SEO:** `generateMetadata()` Next.js → title, description, OG image động
- **Schema.org:** JSON-LD `Course` để hiển thị rich result trên Google
- **Tốc độ:** Ảnh thumbnail lazy load, above-the-fold tối ưu, LCP < 2.5s
- **Mobile:** Nút "Mua ngay" cố định ở cuối màn hình mobile (sticky CTA)
- **Đã mua:** Ẩn nút "Mua ngay", hiện nút "Vào học ngay"

---

## 6. Flow Thanh Toán SePay

### 6.1 Happy Path

```
User click "Mua ngay"
  │
  ▼
Tạo order (status: pending)
  │ order_id, amount, course_id, user_id, expires_at (+30 phút)
  ▼
Hiển thị trang Checkout
  │ QR SePay động
  │ STK: 0123456789 - Ngân hàng XYZ
  │ Số tiền: 1.490.000 ₫
  │ Nội dung: DH[order_id]
  │ Đếm ngược: 29:59
  ▼
User chuyển khoản
  │
  ▼
SePay nhận tiền → bắn webhook đến /webhook/sepay
  │
  ▼
Server verify HMAC signature
  │ ✅ Hợp lệ
  ▼
Cập nhật order status: completed
  │
  ├── Tạo enrollment (user_id, course_id, enrolled_at)
  ├── Gửi email xác nhận (Resend.com)
  ├── Tính hoa hồng affiliate (nếu có ref_code)
  ├── Ghi UTM source vào order
  └── Redirect → /learn/[slug]/bai-dau-tien
```

### 6.2 Edge Cases

| Trường hợp | Xử lý |
|---|---|
| Order quá 30 phút chưa thanh toán | Cron job tự chuyển `status: expired` |
| Webhook đến nhưng order không tồn tại | Trả 400, ghi log |
| Webhook trùng lặp (duplicate) | Idempotency check theo `transaction_id` (Redis) |
| User đã mua khóa | Ẩn nút "Mua ngay", hiện "Vào học ngay" |
| Coupon hết hạn / hết lượt | Thông báo lỗi rõ ràng trước khi checkout |
| Mất kết nối giữa chừng | Polling `/orders/:id/status` mỗi 3 giây từ frontend |

### 6.3 Trang Checkout UX

```
┌─────────────────────────────────────────────┐
│  Thanh toán khóa học                        │
│                                             │
│  [Thumbnail]  Tên Khóa Học                  │
│               1.490.000 ₫                   │
│                                             │
│  ┌─────────────────────┐                    │
│  │  [QR CODE SEPAY]    │   STK: 0123...     │
│  │                     │   NH: Vietcombank  │
│  │                     │   Số tiền:         │
│  └─────────────────────┘   1.490.000 ₫      │
│                             Nội dung:        │
│  ⏱ Hết hạn sau: 29:45      DH20260529001   │
│                                             │
│  ✅ Đã thanh toán? Hệ thống sẽ tự xác nhận │
│                                             │
│  [Nhập mã giảm giá]  [Áp dụng]             │
└─────────────────────────────────────────────┘
```

---

## 7. Popup Lead Magnet

### 7.1 Thông Tin

| Hạng mục | Chi tiết |
|---|---|
| **Tiêu đề** | "Tham gia Webinar Miễn Phí 5 Ngày" |
| **Mô tả** | Học [chủ đề chính] trong 5 buổi trực tiếp qua Zoom |
| **Thu thập** | Họ tên + Email + Số điện thoại |
| **Khi nào hiện** | Sau 30 giây HOẶC khi scroll 50% trang |
| **Xuất hiện ở đâu** | Trang chủ, Landing page khóa, Blog |
| **Không hiện** | `/learn/*`, `/dashboard`, `/admin/*` |
| **Cookie ẩn** | 7 ngày nếu đã đóng hoặc đã submit |
| **Sau khi submit** | Thông báo cảm ơn + gửi email xác nhận + Zoom link |

### 7.2 Flow Xử Lý Lead

```
User submit form
  │
  ├── Validate: email hợp lệ, SĐT 10 số bắt đầu 0
  ├── Lưu vào bảng leads (PostgreSQL)
  ├── Gọi Google Sheets API → append row
  ├── Gửi email xác nhận (Resend.com)
  └── Set cookie 7 ngày → ẩn popup
```

### 7.3 Định Dạng Google Sheet

| Cột | Nội dung |
|---|---|
| A | Thời gian đăng ký (DD/MM/YYYY HH:mm — UTC+7) |
| B | Họ tên |
| C | Email |
| D | Số điện thoại |
| E | Trang nguồn (URL đăng ký) |
| F | UTM Source (nếu có) |
| G | UTM Medium (nếu có) |
| H | UTM Campaign (nếu có) |

---

## 8. Hệ Thống Affiliate

### 8.1 Quy Tắc

| Quy tắc | Chi tiết |
|---|---|
| Hoa hồng | 40% cố định trên giá bán (sau khi trừ coupon) |
| Cookie | 30 ngày kể từ khi click link affiliate |
| Điều kiện tính | Đơn hàng webhook SePay thành công |
| Rút tiền | Thủ công: học viên nhập STK, admin chuyển khoản |
| Tối thiểu rút | 500.000 ₫ |
| Thời gian xử lý | 3–7 ngày làm việc sau khi admin phê duyệt |

### 8.2 Link Affiliate

```
https://yourdomain.com/courses/ten-khoa-hoc?ref=ABC123
                                                └── Mã duy nhất mỗi người
```

### 8.3 Dashboard Affiliate (Học Viên)

```
┌──────────────────────────────────────────────────────┐
│  Chương trình Affiliate của tôi                      │
│                                                      │
│  Link của tôi: [https://...?ref=ABC123]  [📋 Sao chép]│
│                                                      │
│  Tháng 5/2026          Tháng này  │  Tổng cộng       │
│  ─────────────────────────────────────────────────   │
│  Lượt click                  142  │        1.893      │
│  Đơn hàng thành công          12  │          187      │
│  Hoa hồng                     ...│  28.340.000 ₫     │
│                                                      │
│  Hoa hồng chưa rút: 3.560.000 ₫                     │
│  [Yêu cầu rút tiền]                                  │
│                                                      │
│  Lịch sử hoa hồng:                                   │
│  29/05/2026  Khóa A  1.490.000₫  → +596.000₫         │
│  28/05/2026  Khóa B  990.000₫   → +396.000₫          │
└──────────────────────────────────────────────────────┘
```

---

## 9. Database Schema

### 9.1 Tổng Quan Quan Hệ

```
users ──────────────── enrollments ──── courses
  │                                       │
  ├── orders ──── order_items             ├── chapters
  │      │                               │      └── lessons
  │      └── coupons                     │             └── lesson_attachments
  │                                      │
  ├── lesson_progress                    ├── post_courses ── posts
  │                                      │                    ├── categories
  ├── affiliates ── commissions          │                    └── post_tags ── tags
  │      └── withdrawal_requests         │
  │                                      └── leads
  └── video_watch_events
```

### 9.2 Chi Tiết Các Bảng

#### `users`
```sql
CREATE TABLE users (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email         VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255),           -- NULL nếu đăng nhập Google
  name          VARCHAR(255) NOT NULL,
  avatar_url    TEXT,
  role          VARCHAR(20) DEFAULT 'student',  -- 'admin' | 'student'
  is_active     BOOLEAN DEFAULT true,
  google_id     VARCHAR(255),
  last_login_at TIMESTAMPTZ,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);
```

#### `courses`
```sql
CREATE TABLE courses (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title            VARCHAR(500) NOT NULL,
  slug             VARCHAR(500) UNIQUE NOT NULL,
  description      TEXT,
  short_desc       VARCHAR(500),
  thumbnail_url    TEXT,
  trailer_video_id VARCHAR(50),        -- YouTube videoId (public)
  price            BIGINT NOT NULL,    -- Đơn vị: đồng VND
  original_price   BIGINT,            -- Giá gốc (nếu đang sale)
  is_published     BOOLEAN DEFAULT false,
  badge            VARCHAR(50),        -- 'bestseller' | 'new' | 'sale'
  order_index      INT DEFAULT 0,
  meta_title       VARCHAR(255),
  meta_desc        VARCHAR(500),
  created_at       TIMESTAMPTZ DEFAULT NOW()
);
```

#### `chapters`
```sql
CREATE TABLE chapters (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  course_id   UUID REFERENCES courses(id) ON DELETE CASCADE,
  title       VARCHAR(500) NOT NULL,
  order_index INT DEFAULT 0
);
```

#### `lessons`
```sql
CREATE TABLE lessons (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  chapter_id       UUID REFERENCES chapters(id) ON DELETE CASCADE,
  title            VARCHAR(500) NOT NULL,
  youtube_video_id VARCHAR(50),        -- Chỉ admin và backend thấy
  is_free          BOOLEAN DEFAULT false,
  duration_seconds INT DEFAULT 0,
  order_index      INT DEFAULT 0
);
```

#### `lesson_attachments`
```sql
CREATE TABLE lesson_attachments (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lesson_id  UUID REFERENCES lessons(id) ON DELETE CASCADE,
  file_name  VARCHAR(500),
  file_url   TEXT,                     -- Cloudflare R2 URL
  file_size  BIGINT
);
```

#### `enrollments`
```sql
CREATE TABLE enrollments (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID REFERENCES users(id),
  course_id   UUID REFERENCES courses(id),
  enrolled_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, course_id)           -- Không mua trùng
);
```

#### `lesson_progress`
```sql
CREATE TABLE lesson_progress (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID REFERENCES users(id),
  lesson_id     UUID REFERENCES lessons(id),
  is_completed  BOOLEAN DEFAULT false,
  watch_seconds INT DEFAULT 0,
  completed_at  TIMESTAMPTZ,
  UNIQUE(user_id, lesson_id)
);
```

#### `orders`
```sql
CREATE TABLE orders (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID REFERENCES users(id),
  course_id       UUID REFERENCES courses(id),
  amount          BIGINT NOT NULL,     -- Số tiền thực tế (sau coupon), đơn vị: đồng
  original_amount BIGINT NOT NULL,     -- Giá gốc
  coupon_id       UUID REFERENCES coupons(id),
  affiliate_code  VARCHAR(50),         -- ref code affiliate
  utm_source      VARCHAR(100),
  utm_medium      VARCHAR(100),
  utm_campaign    VARCHAR(100),
  sepay_txn_id    VARCHAR(255),        -- Transaction ID từ SePay
  status          VARCHAR(20) DEFAULT 'pending',  -- pending|completed|expired|refunded
  expires_at      TIMESTAMPTZ,         -- Hết hạn sau 30 phút
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  completed_at    TIMESTAMPTZ
);
```

#### `coupons`
```sql
CREATE TABLE coupons (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code           VARCHAR(50) UNIQUE NOT NULL,
  discount_type  VARCHAR(10) NOT NULL,  -- 'percent' | 'fixed'
  discount_value BIGINT NOT NULL,       -- % hoặc số tiền (đồng)
  max_uses       INT,                   -- NULL = không giới hạn
  used_count     INT DEFAULT 0,
  expires_at     TIMESTAMPTZ,
  is_active      BOOLEAN DEFAULT true,
  created_at     TIMESTAMPTZ DEFAULT NOW()
);
```

#### `posts` (Blog)
```sql
CREATE TABLE posts (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title        VARCHAR(500) NOT NULL,
  slug         VARCHAR(500) UNIQUE NOT NULL,
  content      JSONB,                   -- TipTap JSON format
  content_html TEXT,                    -- Rendered HTML
  excerpt      VARCHAR(500),
  thumbnail_url TEXT,
  category_id  UUID REFERENCES categories(id),
  status       VARCHAR(20) DEFAULT 'draft',  -- draft|published|archived
  published_at TIMESTAMPTZ,
  view_count   INT DEFAULT 0,
  reading_time INT DEFAULT 0,           -- Phút
  meta_title   VARCHAR(255),
  meta_desc    VARCHAR(500),
  created_at   TIMESTAMPTZ DEFAULT NOW()
);
```

#### `categories` & `tags`
```sql
CREATE TABLE categories (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        VARCHAR(255) NOT NULL,
  slug        VARCHAR(255) UNIQUE NOT NULL,
  description TEXT
);

CREATE TABLE tags (
  id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,
  slug VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE post_tags (
  post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
  tag_id  UUID REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (post_id, tag_id)
);

CREATE TABLE post_courses (
  post_id   UUID REFERENCES posts(id) ON DELETE CASCADE,
  course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
  PRIMARY KEY (post_id, course_id)
);
```

#### `leads`
```sql
CREATE TABLE leads (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name       VARCHAR(255),
  email      VARCHAR(255) NOT NULL,
  phone      VARCHAR(20),
  source_url TEXT,
  utm_source VARCHAR(100),
  utm_medium VARCHAR(100),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### `affiliates` & `commissions`
```sql
CREATE TABLE affiliates (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id             UUID REFERENCES users(id) UNIQUE,
  ref_code            VARCHAR(20) UNIQUE NOT NULL,
  total_clicks        INT DEFAULT 0,
  total_earnings      BIGINT DEFAULT 0,  -- Đồng VND
  pending_withdrawal  BIGINT DEFAULT 0,
  created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE commissions (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  affiliate_id UUID REFERENCES affiliates(id),
  order_id     UUID REFERENCES orders(id),
  amount       BIGINT NOT NULL,           -- Đồng VND
  status       VARCHAR(20) DEFAULT 'pending',  -- pending|approved|paid
  created_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE withdrawal_requests (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  affiliate_id   UUID REFERENCES affiliates(id),
  amount         BIGINT NOT NULL,
  bank_name      VARCHAR(100),
  account_number VARCHAR(50),
  account_name   VARCHAR(255),
  status         VARCHAR(20) DEFAULT 'pending',  -- pending|approved|rejected
  note           TEXT,
  created_at     TIMESTAMPTZ DEFAULT NOW(),
  processed_at   TIMESTAMPTZ
);
```

#### `video_watch_events`
```sql
CREATE TABLE video_watch_events (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID REFERENCES users(id),
  lesson_id     UUID REFERENCES lessons(id),
  watch_percent INT,                    -- 0–100
  watch_seconds INT,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 10. API Endpoints

### 10.1 Auth

| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/auth/register` | Đăng ký tài khoản mới |
| POST | `/auth/login` | Đăng nhập, trả JWT |
| POST | `/auth/google` | Đăng nhập Google OAuth |
| POST | `/auth/refresh` | Làm mới access token |
| POST | `/auth/forgot-password` | Gửi email reset |
| POST | `/auth/reset-password` | Đổi mật khẩu bằng token |
| DELETE | `/auth/account` | Học viên tự xóa tài khoản |

### 10.2 Khóa Học & Video

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/courses` | Danh sách (filter, sort, search, page) |
| GET | `/courses/:slug` | Chi tiết khóa + syllabus |
| GET | `/courses/:slug/video/:lessonId` | Trả videoId (kiểm tra quyền truy cập) |
| POST | `/courses/:id/progress` | Cập nhật tiến độ bài học |
| GET | `/courses/:id/progress` | Lấy tiến độ tất cả bài |
| POST | `/video-events` | Gửi sự kiện xem video (watch_percent) |

### 10.3 Thanh Toán

| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/orders` | Tạo đơn hàng, trả QR info |
| GET | `/orders/:id/status` | Kiểm tra trạng thái (polling 3s) |
| POST | `/webhook/sepay` | Nhận webhook từ SePay (public) |
| POST | `/coupons/validate` | Kiểm tra mã giảm giá |
| GET | `/orders/history` | Lịch sử giao dịch của user |

### 10.4 Blog

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/posts` | Danh sách bài viết (public) |
| GET | `/posts/:slug` | Chi tiết bài viết (tăng view_count) |
| GET | `/categories` | Danh sách category |
| GET | `/tags` | Danh sách tag |

### 10.5 Affiliate & Leads

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/affiliate/stats` | Thống kê affiliate cá nhân |
| GET | `/affiliate/commissions` | Lịch sử hoa hồng |
| POST | `/affiliate/withdrawal` | Yêu cầu rút tiền |
| POST | `/leads` | Submit form lead magnet |

### 10.6 Admin (prefix `/admin`)

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/admin/dashboard` | Tổng quan doanh thu, học viên |
| CRUD | `/admin/courses` | Quản lý khóa học |
| CRUD | `/admin/chapters` | Quản lý chương |
| CRUD | `/admin/lessons` | Quản lý bài học |
| CRUD | `/admin/posts` | Quản lý blog |
| CRUD | `/admin/coupons` | Quản lý coupon |
| GET | `/admin/orders` | Danh sách đơn hàng |
| GET | `/admin/users` | Danh sách học viên |
| PATCH | `/admin/users/:id` | Khóa/mở tài khoản |
| GET | `/admin/leads` | Danh sách leads |
| GET | `/admin/affiliates` | Quản lý affiliate |
| PATCH | `/admin/withdrawals/:id` | Phê duyệt rút tiền |
| GET | `/admin/analytics` | Báo cáo analytics |

---

## 11. UX & Thiết Kế

### 11.1 Nguyên Tắc UX Cốt Lõi

1. **Đơn giản trước tiên** — Mỗi trang chỉ có 1 hành động chính (CTA rõ ràng)
2. **Phản hồi ngay lập tức** — Loading state, success/error message cho mọi action
3. **Không bao giờ mất dữ liệu** — Tự lưu draft blog, tự lưu tiến độ học
4. **Mobile first** — Thiết kế cho màn hình 375px trước, rồi mới lên desktop
5. **Tốc độ** — Skeleton loading thay vì spinner, prefetch trang quan trọng

### 11.2 Design System

| Element | Giá trị |
|---|---|
| **Font chính** | Inter (Google Fonts) — đọc tốt trên màn hình |
| **Màu primary** | `#1E3A5F` (navy) |
| **Màu accent** | `#2E86AB` (teal) |
| **Màu success** | `#27AE60` |
| **Màu danger** | `#E74C3C` |
| **Border radius** | `8px` card, `4px` input, `100px` button pill |
| **Shadow card** | `0 2px 8px rgba(0,0,0,0.08)` |
| **Breakpoints** | sm:640, md:768, lg:1024, xl:1280 |

### 11.3 UX Từng Trang

#### Trang chủ
- Hero rõ ràng: "Học gì — Ai dạy — Giá bao nhiêu"
- Hiển thị 3–4 khóa nổi bật
- Social proof: số học viên, số khóa học
- Popup lead magnet sau 30 giây

#### Danh sách khóa học
- Card khóa: thumbnail, tên, giá VND, số học viên, badge
- Filter nhanh theo danh mục (tab bar, không cần reload)
- Skeleton loading khi fetch data
- Infinite scroll hoặc pagination (6 khóa/trang)

#### Trang học (Video player)
- Sidebar trái: danh sách chương/bài, checkbox hoàn thành
- Vùng chính: YouTube player (tối màu nền)
- Watermark: email học viên nhỏ, bán trong suốt, góc phải
- Nút: Bài trước | Đánh dấu hoàn thành | Bài tiếp theo
- Auto chuyển bài tiếp theo sau 5 giây khi xong (có thể tắt)

#### Dashboard học viên
- Card mỗi khóa: thumbnail, tên, thanh % tiến độ, nút "Tiếp tục học"
- Tab: Khóa của tôi | Giao dịch | Affiliate | Cài đặt
- Empty state thân thiện khi chưa mua khóa nào

#### Checkout
- 1 cột, đơn giản nhất có thể
- QR lớn, dễ quét
- Đếm ngược rõ ràng
- Trạng thái "Đang chờ thanh toán..." → "✅ Thanh toán thành công!"

#### Admin Dashboard
- Sidebar trái: điều hướng rõ ràng
- Card metrics: doanh thu hôm nay, tuần này, tháng này
- Biểu đồ đường: 30 ngày gần nhất
- Bảng đơn hàng mới nhất (real-time)

### 11.4 Responsive Breakpoints

| Trang | Mobile (< 768px) | Desktop |
|---|---|---|
| Landing page khóa | 1 cột, CTA sticky bottom | 2 cột (content + sidebar giá) |
| Trang học | Sidebar ẩn (drawer) | Sidebar + video 2 cột |
| Blog | 1 cột | 2 cột (bài + sidebar) |
| Admin | Collapse sidebar | Full sidebar |

---

## 12. Định Dạng Việt Nam

> Toàn hệ thống phải hiển thị đúng chuẩn Việt Nam — không dùng format quốc tế.

### 12.1 Múi Giờ (UTC+7)

```typescript
// frontend/lib/format.ts
import { formatInTimeZone } from 'date-fns-tz';
import { vi } from 'date-fns/locale';

const VN_TIMEZONE = 'Asia/Ho_Chi_Minh';

export function formatDateTime(date: Date | string): string {
  return formatInTimeZone(date, VN_TIMEZONE, 'HH:mm - dd/MM/yyyy', { locale: vi });
  // Kết quả: "14:30 - 29/05/2026"
}

export function formatDate(date: Date | string): string {
  return formatInTimeZone(date, VN_TIMEZONE, 'dd/MM/yyyy', { locale: vi });
  // Kết quả: "29/05/2026"
}

export function formatDateLong(date: Date | string): string {
  return formatInTimeZone(date, VN_TIMEZONE, "EEEE, dd 'tháng' MM 'năm' yyyy", { locale: vi });
  // Kết quả: "Thứ Năm, 29 tháng 05 năm 2026"
}
```

```python
# backend/app/utils/timezone.py
from datetime import datetime
import pytz

VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')

def now_vn() -> datetime:
    """Lấy thời gian hiện tại theo múi giờ Việt Nam."""
    return datetime.now(VN_TZ)

def to_vn_time(dt: datetime) -> datetime:
    """Chuyển datetime UTC sang UTC+7."""
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    return dt.astimezone(VN_TZ)

def format_vn_datetime(dt: datetime) -> str:
    """Định dạng: HH:mm - DD/MM/YYYY"""
    return to_vn_time(dt).strftime('%H:%M - %d/%m/%Y')
```

### 12.2 Định Dạng Tiền Tệ VND

```typescript
// frontend/lib/format.ts

export function formatVND(amount: number): string {
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
    minimumFractionDigits: 0,
  }).format(amount);
  // Kết quả: "1.490.000 ₫"
}

export function formatVNDShort(amount: number): string {
  if (amount >= 1_000_000_000) {
    return `${(amount / 1_000_000_000).toFixed(1)} tỷ ₫`;
  }
  if (amount >= 1_000_000) {
    return `${(amount / 1_000_000).toFixed(0)} triệu ₫`;
  }
  return formatVND(amount);
  // Kết quả: "1.5 tỷ ₫" | "490 triệu ₫" | "990.000 ₫"
}

// Ví dụ sử dụng:
// formatVND(1490000)   → "1.490.000 ₫"
// formatVND(990000)    → "990.000 ₫"
// formatVND(199000)    → "199.000 ₫"
// formatVNDShort(1500000000) → "1.5 tỷ ₫"
// formatVNDShort(490000000)  → "490 triệu ₫"
```

```python
# backend/app/utils/formatters.py

def format_vnd(amount: int) -> str:
    """Định dạng tiền VND: 1.490.000 ₫"""
    return f"{amount:,.0f} ₫".replace(",", ".")

def format_vnd_short(amount: int) -> str:
    """Rút gọn: 1.5 tỷ ₫ | 490 triệu ₫ | 990.000 ₫"""
    if amount >= 1_000_000_000:
        return f"{amount / 1_000_000_000:.1f} tỷ ₫"
    if amount >= 1_000_000:
        return f"{amount / 1_000_000:.0f} triệu ₫"
    return format_vnd(amount)
```

### 12.3 Định Dạng Số Điện Thoại Việt Nam

```typescript
export function formatPhone(phone: string): string {
  const digits = phone.replace(/\D/g, '');
  if (digits.length === 10) {
    return `${digits.slice(0,4)} ${digits.slice(4,7)} ${digits.slice(7)}`;
    // Kết quả: "0901 234 567"
  }
  return phone;
}

export function validatePhone(phone: string): boolean {
  return /^(0[3-9][0-9]{8})$/.test(phone.replace(/\s/g, ''));
  // 10 số, bắt đầu bằng 03x, 05x, 07x, 08x, 09x
}
```

### 12.4 Hiển Thị Trong UI

| Trường hợp | Hiển thị đúng |
|---|---|
| Giá khóa học | `1.490.000 ₫` |
| Giá gốc (gạch ngang) | ~~`1.990.000 ₫`~~ |
| Hoa hồng affiliate | `+596.000 ₫` |
| Doanh thu admin | `124.350.000 ₫` |
| Thời gian đơn hàng | `14:32 - 29/05/2026` |
| Ngày đăng ký | `29/05/2026` |
| Số điện thoại | `0901 234 567` |
| Thời lượng video | `12 phút 30 giây` |
| Tiến độ | `45%` hoặc `9/20 bài` |
| Ngày phát hành blog | `29 tháng 05, 2026` |

---

## 13. Yêu Cầu Phi Chức Năng

### 13.1 Hiệu Suất

| Chỉ số | Mục tiêu |
|---|---|
| LCP (Largest Contentful Paint) | < 2.5 giây |
| FID (First Input Delay) | < 100ms |
| CLS (Cumulative Layout Shift) | < 0.1 |
| API response thông thường | < 500ms |
| Video bắt đầu phát | < 2 giây |
| Dashboard admin load | < 5 giây |

### 13.2 Bảo Mật

- **HTTPS** bắt buộc toàn bộ trang
- **JWT** access token hết hạn sau 7 ngày, refresh token 30 ngày
- **Rate limiting:** 5 lần đăng nhập sai → khóa 15 phút (Redis)
- **SePay webhook:** Verify HMAC signature trước khi xử lý
- **YouTube videoId:** Chỉ trả về sau khi xác nhận quyền truy cập trên server
- **SQL injection:** SQLAlchemy ORM parameterized query
- **XSS:** Sanitize nội dung TipTap (DOMPurify) trước khi lưu
- **CORS:** Chỉ cho phép domain frontend
- **Env vars:** Không commit `.env` lên git

### 13.3 SEO

- Mỗi trang có unique `title` + `meta description`
- Open Graph image động cho mỗi khóa học + bài blog
- `sitemap.xml` tự động cập nhật khi có khóa/bài mới
- Schema.org JSON-LD cho `Course` và `BlogPosting`
- URL thân thiện: `/courses/ten-khoa-hoc`, `/blog/ten-bai-viet`
- `robots.txt` đúng cấu hình
- `canonical URL` cho mọi trang

### 13.4 Accessibility

- Responsive 100% trên mobile (375px+)
- Nút mua cố định ở cuối màn hình mobile
- Ảnh có `alt text`
- Contrast ratio tối thiểu 4.5:1
- Keyboard navigation cho form, modal, dropdown
- `aria-label` cho icon button

### 13.5 Backup & Reliability

- Supabase tự động backup PostgreSQL hàng ngày
- Upstash Redis: persistent storage
- Vercel: tự động rollback nếu deploy lỗi
- Railway: restart tự động nếu crash
- Webhook SePay: retry 3 lần nếu server trả lỗi

---

## 14. Roadmap

### Phase 1 — MVP (Tuần 1–6)

**Tuần 1–2: Nền tảng**
- [ ] Setup project: FastAPI + Next.js + PostgreSQL + Redis
- [ ] Auth: đăng ký, đăng nhập, Google OAuth, reset password
- [ ] Database migrations (Alembic)
- [ ] Deploy cơ bản lên Vercel + Railway

**Tuần 3–4: Core Features**
- [ ] CRUD khóa học, chương, bài học (admin)
- [ ] Video player: YouTube embed + bảo vệ videoId + watermark
- [ ] Trang danh sách + landing page từng khóa
- [ ] Tiến độ học, đánh dấu hoàn thành

**Tuần 5–6: Thanh Toán & Launch**
- [ ] Tích hợp SePay: tạo order, hiển thị QR, webhook
- [ ] Coupon / mã giảm giá
- [ ] Popup lead magnet → Google Sheet
- [ ] Blog: TipTap editor, danh sách, chi tiết
- [ ] Email: chào mừng, xác nhận thanh toán, webinar
- [ ] GA4 + Meta Pixel tracking cơ bản

### Phase 2 — Growth (Tuần 7–12)

- [ ] Affiliate system: link, dashboard, commissions, rút tiền
- [ ] Video analytics: watch_percent, watch_seconds
- [ ] Admin dashboard: biểu đồ doanh thu, báo cáo
- [ ] Testimonial / review từng khóa
- [ ] Email automation: nhắc học, thông báo khóa mới
- [ ] Microsoft Clarity (heatmap)
- [ ] Flash sale + countdown timer
- [ ] Export báo cáo Excel
- [ ] Audit log admin

### Phase 3 — Scale (Tháng 4+)

- [ ] Certificate hoàn thành (PDF)
- [ ] Quiz cuối chương
- [ ] PWA (Progressive Web App)
- [ ] Zalo OA thông báo
- [ ] Cohort analysis
- [ ] Combo/Bundle nhiều khóa
- [ ] Giới hạn thiết bị đăng nhập

### Checklist Trước Khi Ra Mắt (MVP)

- [ ] Toàn bộ luồng thanh toán SePay hoạt động end-to-end (test sandbox)
- [ ] Video YouTube chỉ hiển thị với người đã mua hoặc bài free
- [ ] Watermark email học viên trên video
- [ ] Popup lead magnet → lưu Google Sheet thành công
- [ ] Email xác nhận gửi được (test Resend)
- [ ] Admin có thể thêm/sửa khóa học và bài học
- [ ] Admin có thể viết và đăng bài blog
- [ ] GA4 + Meta Pixel tracking mua hàng
- [ ] SSL certificate hợp lệ
- [ ] Test trên mobile (iOS + Android Chrome)
- [ ] Định dạng VND đúng trên toàn bộ UI
- [ ] Múi giờ UTC+7 đúng trên log, email, dashboard
- [ ] Số điện thoại validate đúng format Việt Nam

---

*PRD v1.0 — Website Bán Khóa Học Online — 29/05/2026*
