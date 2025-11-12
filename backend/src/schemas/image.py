"""Pydantic schemas for Image model."""

from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ImageBase(BaseModel):
    """Base schema for Image with shared attributes."""

    filename: str = Field(..., min_length=1, max_length=255)
    original_url: Optional[str] = Field(None, max_length=2048)

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, v: str) -> str:
        """Validate filename to prevent path traversal attacks."""
        if not v:
            raise ValueError("Filename cannot be empty")
        
        # Check for path traversal patterns
        dangerous_patterns = ["..", "/", "\\", "\0"]
        for pattern in dangerous_patterns:
            if pattern in v:
                raise ValueError(
                    f"Filename contains invalid character or pattern: {pattern}"
                )
        
        return v


class ImageCreate(ImageBase):
    """Schema for creating a new Image."""

    pass


class ImageUpdate(BaseModel):
    """Schema for updating an existing Image."""

    filename: Optional[str] = Field(None, min_length=1, max_length=255)
    original_url: Optional[str] = Field(None, max_length=2048)
    status: Optional[str] = Field(None, max_length=50)

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, v: Optional[str]) -> Optional[str]:
        """Validate filename to prevent path traversal attacks."""
        if v is None:
            return v
        
        if not v:
            raise ValueError("Filename cannot be empty")
        
        # Check for path traversal patterns
        dangerous_patterns = ["..", "/", "\\", "\0"]
        for pattern in dangerous_patterns:
            if pattern in v:
                raise ValueError(
                    f"Filename contains invalid character or pattern: {pattern}"
                )
        
        return v


class ImageInDB(ImageBase):
    """Schema for Image as stored in database."""

    id: UUID
    storage_path: str
    file_size: int
    status: str
    upload_timestamp: datetime
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ImageResponse(ImageInDB):
    """Schema for Image in API responses."""

    pass
