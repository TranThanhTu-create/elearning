# Hướng dẫn Deploy Tú Marketing lên Production

## Kiến trúc đề xuất

```
Frontend → Vercel.com (miễn phí)
Backend  → Render.com (miễn phí)
Database → Supabase.com (miễn phí 500MB)
Domain   → Mua tại Hostinger, trỏ DNS về Vercel/Render
```

---

## BƯỚC 1: Tạo Database (Supabase)

1. Vào https://supabase.com → Đăng ký miễn phí
2. Tạo project mới → Chọn region **Singapore**
3. Vào **Settings → Database → Connection string**
4. Chọn **Transaction pooler** → Copy URI
5. Thay `[YOUR-PASSWORD]` bằng mật khẩu đã đặt
6. Lưu lại 2 connection string (asyncpg và psycopg2)

---

## BƯỚC 2: Deploy Backend (Render.com)

1. Vào https://render.com → Đăng ký miễn phí
2. **New → Web Service** → Connect GitHub (push code lên GitHub trước)
3. Chọn thư mục `backend/`
4. Điền:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Vào **Environment** → thêm tất cả biến từ file `.env.production.example`
6. Deploy xong → Copy URL dạng `https://xxx.onrender.com`

**Chạy migration sau khi deploy:**
Vào Render Dashboard → Shell → chạy:
```bash
alembic upgrade head
```

---

## BƯỚC 3: Deploy Frontend (Vercel)

1. Vào https://vercel.com → Đăng ký miễn phí (dùng GitHub)
2. **Add New Project** → Import repo → Chọn thư mục `frontend/`
3. Vào **Environment Variables** → Thêm:
   - `NEXT_PUBLIC_API_URL` = URL Render từ bước 2
   - `NEXT_PUBLIC_SITE_URL` = domain của bạn (vd: https://tumarketing.vn)
4. Deploy

---

## BƯỚC 4: Trỏ Domain từ Hostinger

1. Vào Hostinger → DNS Zone → Xóa record A mặc định
2. Thêm CNAME: `@` → `cname.vercel-dns.com`
3. Trong Vercel → Settings → Domains → Thêm domain của bạn
4. Chờ 5-30 phút để DNS lan truyền

---

## BƯỚC 5: Cấu hình SePay Webhook

Sau khi backend live, vào SePay dashboard:
- Webhook URL: `https://YOUR-RENDER-URL.onrender.com/api/orders/webhook/sepay`
- Điền SEPAY_WEBHOOK_SECRET trùng với `.env`

---

## Thông tin cần cung cấp cho Tú Marketing

Trước khi deploy, bạn cần có:

| Thông tin | Lấy ở đâu |
|-----------|-----------|
| Resend API Key | resend.com → API Keys |
| SePay API Key + Webhook Secret | sepay.vn → Tài khoản |
| Số tài khoản ngân hàng | Ngân hàng của bạn |
| Link nhóm Zalo thật | Tạo nhóm Zalo → Lấy link mời |
| Domain website | Đã mua ở Hostinger |
