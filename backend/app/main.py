"""
Tú Marketing Backend — FastAPI Application Entry Point
======================================================
Múi giờ: Asia/Ho_Chi_Minh (UTC+7)
"""

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.utils.logger import get_logger, setup_root_logger, log_request, log_response

# ── Setup logger trước tiên ───────────────────────────────
setup_root_logger(debug=settings.DEBUG)
logger = get_logger(__name__)


# ── Lifespan (startup / shutdown) ─────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 60)
    logger.info(f"[START] Tu Marketing Backend dang khoi dong...")
    logger.info(f"   ENV         : {settings.APP_ENV}")
    logger.info(f"   DEBUG       : {settings.DEBUG}")
    logger.info(f"   TIMEZONE    : {settings.TZ}")
    logger.info(f"   DB          : {settings.DATABASE_URL[:40]}...")
    logger.info(f"   FRONTEND    : {settings.FRONTEND_URL}")
    logger.info("=" * 60)

    # Khởi tạo DB connection pool
    from app.database import async_engine
    async with async_engine.connect() as conn:
        logger.info("[OK] Database ket noi thanh cong")

    yield

    # Shutdown
    logger.info("[STOP] EduVietPro Backend dang tat...")
    await async_engine.dispose()
    logger.info("✅ Database pool đã đóng")


# ── FastAPI App ────────────────────────────────────────────
app = FastAPI(
    title="Tú Marketing API",
    description="Tú Marketing — AI Agent & Marketing Automation Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ── Middleware ─────────────────────────────────────────────

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing + logging
@app.middleware("http")
async def request_logger_middleware(request: Request, call_next):
    start = time.perf_counter()

    # Lấy IP thực (qua proxy)
    ip = request.headers.get("X-Forwarded-For",
         request.headers.get("X-Real-IP",
         request.client.host if request.client else "?"))

    # Log request đến
    log_request(
        method=request.method,
        path=request.url.path,
        ip=ip,
        params=dict(request.query_params) or None,
    )

    try:
        response: Response = await call_next(request)
    except Exception as exc:
        duration = (time.perf_counter() - start) * 1000
        logger.error(f"💥 Unhandled exception [{duration:.1f}ms]: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Lỗi hệ thống nội bộ. Vui lòng thử lại sau."},
        )

    duration = (time.perf_counter() - start) * 1000
    log_response(request.method, request.url.path, response.status_code, duration)

    # Thêm header debug timing
    response.headers["X-Process-Time-Ms"] = f"{duration:.1f}"
    return response


# ── Import & Register Routers ─────────────────────────────
from app.api import auth, courses, orders, blog, affiliate, leads, dashboard
from app.api.admin import (
    courses as admin_courses,
    blog as admin_blog,
    orders as admin_orders,
    users as admin_users,
    coupons as admin_coupons,
    leads as admin_leads,
    affiliate as admin_affiliate,
    analytics as admin_analytics,
    settings as admin_settings,
)

# Public / Auth
app.include_router(auth.router,       prefix="/api/auth",      tags=["Auth"])

# Public content
app.include_router(courses.router,    prefix="/api/courses",   tags=["Courses"])
app.include_router(blog.router,       prefix="/api/blog",      tags=["Blog"])
app.include_router(leads.router,      prefix="/api/leads",     tags=["Leads"])

# Authenticated student
app.include_router(orders.router,     prefix="/api/orders",    tags=["Orders"])
app.include_router(dashboard.router,  prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(affiliate.router,  prefix="/api/affiliate", tags=["Affiliate"])

# Admin
app.include_router(admin_courses.router,   prefix="/api/admin/courses",   tags=["Admin - Courses"])
app.include_router(admin_blog.router,      prefix="/api/admin/blog",      tags=["Admin - Blog"])
app.include_router(admin_orders.router,    prefix="/api/admin/orders",    tags=["Admin - Orders"])
app.include_router(admin_users.router,     prefix="/api/admin/users",     tags=["Admin - Users"])
app.include_router(admin_coupons.router,   prefix="/api/admin/coupons",   tags=["Admin - Coupons"])
app.include_router(admin_leads.router,     prefix="/api/admin/leads",     tags=["Admin - Leads"])
app.include_router(admin_affiliate.router, prefix="/api/admin/affiliate", tags=["Admin - Affiliate"])
app.include_router(admin_analytics.router, prefix="/api/admin/analytics", tags=["Admin - Analytics"])
app.include_router(admin_settings.router,  prefix="/api/admin/settings",  tags=["Admin - Settings"])


# ── Health Check ───────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health_check():
    from app.utils.timezone import now_vn, format_vn_datetime
    now = now_vn()
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "env": settings.APP_ENV,
        "timezone": settings.TZ,
        "server_time_vn": format_vn_datetime(now, "%d/%m/%Y %H:%M:%S"),
        "version": "1.0.0",
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "message": "Tu Marketing API v1.0.0",
        "docs": "/docs",
        "health": "/health",
    }
