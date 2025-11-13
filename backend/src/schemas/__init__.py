"""Pydantic schemas for API requests and responses."""

from .common import PaginatedResponse
from .detection import (
    BoundingBox,
    DetectionBase,
    DetectionCreate,
    DetectionInDB,
    DetectionResponse,
    DetectionWithBBox,
)
from .image import ImageBase, ImageCreate, ImageInDB, ImageResponse, ImageUpdate

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
