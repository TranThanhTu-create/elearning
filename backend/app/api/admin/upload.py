"""
Admin Upload API — Upload ảnh lên Cloudflare R2.
Endpoint: POST /api/admin/upload/image
"""

import io
import uuid
import mimetypes
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from PIL import Image

from app.config import settings
from app.utils.deps import require_admin
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SIZE_MB = 10
MAX_DIMENSION = 2048   # resize nếu lớn hơn


def _get_r2_client():
    """Tạo boto3 S3 client trỏ vào Cloudflare R2."""
    if not all([settings.R2_ACCOUNT_ID, settings.R2_ACCESS_KEY_ID, settings.R2_SECRET_ACCESS_KEY]):
        return None
    try:
        import boto3
        return boto3.client(
            "s3",
            endpoint_url=f"https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
            aws_access_key_id=settings.R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
            region_name="auto",
        )
    except Exception as e:
        logger.error(f"R2 client error: {e}")
        return None


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    _admin=Depends(require_admin),
):
    """Upload ảnh lên Cloudflare R2, trả về public URL."""

    # ── Kiểm tra cấu hình R2 ──
    client = _get_r2_client()
    if not client:
        raise HTTPException(
            status_code=503,
            detail=(
                "Chưa cấu hình Cloudflare R2. "
                "Vui lòng thêm R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, "
                "R2_SECRET_ACCESS_KEY, R2_PUBLIC_URL vào biến môi trường trên Render."
            ),
        )
    if not settings.R2_PUBLIC_URL:
        raise HTTPException(status_code=503, detail="Thiếu R2_PUBLIC_URL trong biến môi trường.")

    # ── Kiểm tra định dạng ──
    content_type = file.content_type or ""
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"Chỉ chấp nhận ảnh JPG, PNG, WebP, GIF. Bạn upload: {content_type}")

    # ── Đọc file ──
    data = await file.read()
    if len(data) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File quá lớn. Tối đa {MAX_SIZE_MB}MB.")

    # ── Resize nếu cần (dùng Pillow) ──
    try:
        img = Image.open(io.BytesIO(data))
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")

        # Resize nếu chiều nào vượt MAX_DIMENSION
        if max(img.size) > MAX_DIMENSION:
            img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.LANCZOS)

        buf = io.BytesIO()
        fmt = "JPEG" if content_type == "image/jpeg" else ("PNG" if content_type == "image/png" else "WEBP")
        img.save(buf, format=fmt, quality=85, optimize=True)
        buf.seek(0)
        data = buf.read()
    except Exception as e:
        logger.warning(f"Pillow resize error: {e} — dùng file gốc")
        buf = io.BytesIO(data)

    # ── Tạo key (path) trong bucket ──
    ext = mimetypes.guess_extension(content_type) or ".jpg"
    if ext == ".jpe":
        ext = ".jpg"
    month = datetime.now().strftime("%Y/%m")
    key = f"uploads/{month}/{uuid.uuid4().hex}{ext}"

    # ── Upload lên R2 ──
    try:
        client.put_object(
            Bucket=settings.R2_BUCKET_NAME,
            Key=key,
            Body=data,
            ContentType=content_type,
            CacheControl="public, max-age=31536000",
        )
    except Exception as e:
        logger.error(f"R2 upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi upload lên R2: {str(e)}")

    public_url = f"{settings.R2_PUBLIC_URL.rstrip('/')}/{key}"
    logger.info(f"✅ Upload ảnh thành công: {public_url}")

    return {"url": public_url, "key": key, "size": len(data)}
