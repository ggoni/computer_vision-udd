"""Pydantic schemas for API requests and responses."""

from .image import ImageBase, ImageCreate, ImageUpdate, ImageInDB, ImageResponse
from .detection import (
    BoundingBox,
    DetectionBase,
    DetectionCreate,
    DetectionInDB,
    DetectionResponse,
    DetectionWithBBox,
)
from .common import PaginatedResponse

__all__ = [
    # Image schemas
    "ImageBase",
    "ImageCreate",
    "ImageUpdate",
    "ImageInDB",
    "ImageResponse",
    # Detection schemas
    "BoundingBox",
    "DetectionBase",
    "DetectionCreate",
    "DetectionInDB",
    "DetectionResponse",
    "DetectionWithBBox",
    # Common schemas
    "PaginatedResponse",
]
