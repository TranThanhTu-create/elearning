# ============================================================
# EduVietPro — Khởi động toàn bộ hệ thống
# ============================================================
Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "   EduVietPro — Khởi động hệ thống" -ForegroundColor Cyan
Write-Host "=====================================`n" -ForegroundColor Cyan

$ROOT = $PSScriptRoot
$BACKEND = "$ROOT\backend"
$FRONTEND = "$ROOT\frontend"

# ── 1. Khởi động PostgreSQL qua Docker ──────────────────────
Write-Host "[1/5] Khởi động PostgreSQL (Docker)..." -ForegroundColor Yellow
Set-Location $ROOT
docker compose up -d postgres 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Lỗi khởi động Docker. Hãy mở Docker Desktop trước." -ForegroundColor Red
    exit 1
}

# Chờ PostgreSQL healthy
Write-Host "      Chờ PostgreSQL sẵn sàng..." -ForegroundColor Gray
$t = 0
while ($t -lt 30) {
    Start-Sleep -Seconds 2; $t += 2
    $health = docker inspect --format='{{.State.Health.Status}}' eduvietpro_db 2>&1
    if ($health -eq "healthy") { Write-Host "      PostgreSQL OK!" -ForegroundColor Green; break }
    Write-Host "      [$t s] chưa ready ($health)..." -ForegroundColor Gray
}

# ── 2. Chạy Alembic migration ────────────────────────────────
Write-Host "`n[2/5] Chạy database migration..." -ForegroundColor Yellow
Set-Location $BACKEND
$env:PYTHONPATH = $BACKEND
alembic upgrade head
if ($LASTEXITCODE -ne 0) {
    Write-Host "Migration thất bại! Kiểm tra lại DB connection." -ForegroundColor Red
    exit 1
}
Write-Host "      Migration OK!" -ForegroundColor Green

# ── 3. Tạo admin user ────────────────────────────────────────
Write-Host "`n[3/5] Tạo tài khoản admin..." -ForegroundColor Yellow
python -c @"
import asyncio, sys
sys.path.insert(0, r'$BACKEND')

async def create_admin():
    from app.database import AsyncSessionLocal
    from app.models.user import User
    from app.models.affiliate import Affiliate
    from app.utils.security import hash_password
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        exist = await db.execute(select(User).where(User.email == 'admin@eduvietpro.vn'))
        if exist.scalar_one_or_none():
            print('Admin da ton tai, bo qua.')
            return

        admin = User(
            email='admin@eduvietpro.vn',
            name='Admin',
            password_hash=hash_password('admin123'),
            role='admin',
            is_active=True,
            is_email_verified=True,
            ref_code='ADMIN001',
        )
        db.add(admin)
        await db.flush()
        db.add(Affiliate(user_id=admin.id, status='active'))
        await db.commit()
        print('Admin tao thanh cong: admin@eduvietpro.vn / admin123')

asyncio.run(create_admin())
"@
Write-Host "      Admin OK!" -ForegroundColor Green

# ── 4. Chạy Backend ──────────────────────────────────────────
Write-Host "`n[4/5] Khởi động Backend (port 8000)..." -ForegroundColor Yellow
Set-Location $BACKEND
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$BACKEND'; `$env:PYTHONPATH='$BACKEND'; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -WindowStyle Normal

Start-Sleep -Seconds 3

# ── 5. Chạy Frontend ─────────────────────────────────────────
Write-Host "[5/5] Khởi động Frontend (port 3000)..." -ForegroundColor Yellow
Set-Location $FRONTEND
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$FRONTEND'; npm run dev" -WindowStyle Normal

Start-Sleep -Seconds 2

# ── Done ─────────────────────────────────────────────────────
Write-Host "`n=====================================" -ForegroundColor Green
Write-Host "   HE THONG DA KHOI DONG XONG!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Website    : http://localhost:3000" -ForegroundColor Cyan
Write-Host "  Admin      : http://localhost:3000/admin" -ForegroundColor Cyan
Write-Host "  API Docs   : http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Tai khoan Admin:" -ForegroundColor White
Write-Host "    Email    : admin@eduvietpro.vn" -ForegroundColor White
Write-Host "    Password : admin123" -ForegroundColor White
Write-Host ""
