"""Request validation models for API endpoints.

This module provides Pydantic models for validating API requests,
ensuring proper input sanitization and type checking.
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field, validator


class ImageListParams(BaseModel):
    """Query parameters for listing images with validation."""
    
    page: int = Field(
        default=1,
        ge=1,
        le=1000,
        description="Page number for pagination (1-based)"
    )
    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of items per page (max 100)"
    )
    status: Optional[Literal["pending", "completed", "failed"]] = Field(
        default=None,
        description="Filter by image processing status"
    )
    filename_substr: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Search for files containing this substring"
    )
    
    @validator('filename_substr')
    def validate_filename_substr(cls, v):
        """Sanitize filename substring input."""
        if v is not None:
            # Remove potentially dangerous characters
            v = v.strip()
            if len(v) < 1:
                return None
            # Basic sanitization - allow alphanumeric, spaces, dots, hyphens, underscores
            import re
            if not re.match(r'^[a-zA-Z0-9\s.\-_]+$', v):
                raise ValueError("Filename search contains invalid characters")
        return v


class DetectionListParams(BaseModel):
    """Query parameters for listing detections with validation."""
    
    page: int = Field(
        default=1,
        ge=1,
        le=1000,
        description="Page number for pagination (1-based)"
    )
    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of items per page (max 100)"
    )
    label: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Filter by detection label"
    )
    min_confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Minimum confidence score (0.0-1.0)"
    )
    
    @validator('label')
    def validate_label(cls, v):
        """Sanitize label input."""
        if v is not None:
            v = v.strip()
            if len(v) < 1:
                return None
            # Allow alphanumeric characters, spaces, and common punctuation
            import re
            if not re.match(r'^[a-zA-Z0-9\s\-_]+$', v):
                raise ValueError("Label contains invalid characters")
        return v


class ErrorResponse(BaseModel):
    """Standard error response format."""
    
    error: str = Field(description="Error type identifier")
    message: str = Field(description="Human-readable error message")
    details: Optional[dict] = Field(default=None, description="Additional error details")


class SuccessResponse(BaseModel):
    """Standard success response format."""
    
    success: bool = Field(default=True, description="Operation success status")
    message: str = Field(description="Success message")
    data: Optional[dict] = Field(default=None, description="Response data")