"""Image ORM model for the computer vision application.

This module defines the Image database table for storing uploaded image metadata.
"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import BaseModel

if TYPE_CHECKING:
    from .detection import Detection


class Image(BaseModel):
    """Image model representing uploaded images in the database.

    Stores metadata about uploaded images including filename, storage location,
    file size, processing status, and upload timestamp.
    """

    __tablename__ = "images"

    # Core image information
    filename: Mapped[str] = mapped_column(
        String(255), nullable=False, doc="Original filename of the uploaded image"
    )

    original_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="Original URL if image was downloaded from web (optional)",
    )

    storage_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        unique=True,
        doc="Relative path to stored image file",
    )

    file_size: Mapped[int] = mapped_column(
        Integer, nullable=False, doc="File size in bytes"
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
        doc="Processing status: pending, processing, completed, failed",
    )

    # Use timezone-aware UTC now for default to avoid deprecation warnings and ensure consistent timestamps
    upload_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        doc="When the image was uploaded",
    )

    # Relationships
    detections: Mapped[list["Detection"]] = relationship(
        "Detection",
        back_populates="image",
        cascade="all, delete-orphan",
        lazy="selectin",
        doc="Object detections found in this image",
    )

    def __repr__(self) -> str:
        """String representation of the Image model."""
        return (
            f"<Image("
            f"id={self.id}, "
            f"filename='{self.filename}', "
            f"status='{self.status}', "
            f"file_size={self.file_size}, "
            f"detections_count={len(self.detections) if self.detections else 0}"
            f")>"
        )

    @property
    def file_size_mb(self) -> float:
        """Get file size in megabytes."""
        return self.file_size / (1024 * 1024)

    @property
    def is_processed(self) -> bool:
        """Check if image processing is complete."""
        return self.status == "completed"

    @property
    def detection_count(self) -> int:
        """Get number of detections found in this image."""
        return len(self.detections) if self.detections else 0
