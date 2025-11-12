"""Pydantic schemas for Detection model."""

from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class BoundingBox(BaseModel):
    """Schema for bounding box coordinates."""

    xmin: int = Field(..., ge=0, description="Left x coordinate")
    ymin: int = Field(..., ge=0, description="Top y coordinate")
    xmax: int = Field(..., gt=0, description="Right x coordinate")
    ymax: int = Field(..., gt=0, description="Bottom y coordinate")

    @model_validator(mode="after")
    def validate_bbox(self) -> "BoundingBox":
        """Validate that bbox coordinates form a valid box."""
        if self.xmax <= self.xmin:
            raise ValueError("xmax must be greater than xmin")
        if self.ymax <= self.ymin:
            raise ValueError("ymax must be greater than ymin")
        return self


class DetectionBase(BaseModel):
    """Base schema for Detection with shared attributes."""

    label: str = Field(..., min_length=1, max_length=255)
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    bbox_xmin: int = Field(..., ge=0)
    bbox_ymin: int = Field(..., ge=0)
    bbox_xmax: int = Field(..., gt=0)
    bbox_ymax: int = Field(..., gt=0)

    @model_validator(mode="after")
    def validate_bbox_coordinates(self) -> "DetectionBase":
        """Validate that bbox coordinates form a valid box."""
        if self.bbox_xmax <= self.bbox_xmin:
            raise ValueError("bbox_xmax must be greater than bbox_xmin")
        if self.bbox_ymax <= self.bbox_ymin:
            raise ValueError("bbox_ymax must be greater than bbox_ymin")
        return self


class DetectionCreate(DetectionBase):
    """Schema for creating a new Detection."""

    image_id: UUID


class DetectionInDB(DetectionBase):
    """Schema for Detection as stored in database."""

    id: UUID
    image_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DetectionResponse(DetectionInDB):
    """Schema for Detection in API responses."""

    pass


class DetectionWithBBox(BaseModel):
    """Alternative schema using nested BoundingBox."""

    id: UUID
    image_id: UUID
    label: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    bbox: BoundingBox
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
