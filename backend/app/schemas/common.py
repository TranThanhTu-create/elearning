"""
Schemas dùng chung: pagination, response wrapper, error.
"""

from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class PaginatedResponse(BaseModel, Generic[DataT]):
    items: List[DataT]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def build(cls, items: List, total: int, page: int, page_size: int):
        import math
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=max(1, math.ceil(total / page_size)) if page_size else 1,
        )


class MessageResponse(BaseModel):
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None


class StatsCard(BaseModel):
    """Dùng cho admin dashboard cards — số tiền định dạng VN."""
    label: str
    value: str           # đã format: "1.490.000 ₫" hoặc "312"
    value_raw: float     # số nguyên/thực để frontend tự format nếu cần
    change_text: Optional[str] = None   # "↑ 67 so với tháng trước"
    change_positive: Optional[bool] = None
