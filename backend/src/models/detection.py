"""Detection ORM model for the computer vision application.

This module defines the Detection database table for storing object detection results.
"""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import BaseModel

if TYPE_CHECKING:
    from .image import Image


class Detection(BaseModel):
    """Detection model representing object detections in images.
    
    Stores information about detected objects including the label,
    confidence score, and bounding box coordinates.
    """
    
    __tablename__ = "detections"
    
    # Foreign key to the image
    image_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("images.id", ondelete="CASCADE"),
        nullable=False,
        doc="ID of the image this detection belongs to",
    )
    
    # Object detection information
    label: Mapped[str] = mapped_column(String(100), nullable=False, doc="Detected object label (e.g., 'cat', 'car', 'person')")
    
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, doc="Model confidence score (0.0 to 1.0)")
    
    # Bounding box coordinates (absolute pixel values)
    bbox_xmin: Mapped[int] = mapped_column(Integer, nullable=False, doc="Left edge of bounding box (x-coordinate)")
    
    bbox_ymin: Mapped[int] = mapped_column(Integer, nullable=False, doc="Top edge of bounding box (y-coordinate)")
    
    bbox_xmax: Mapped[int] = mapped_column(Integer, nullable=False, doc="Right edge of bounding box (x-coordinate)")
    
    bbox_ymax: Mapped[int] = mapped_column(Integer, nullable=False, doc="Bottom edge of bounding box (y-coordinate)")
    
    # Relationships
    image: Mapped["Image"] = relationship(
        "Image",
        back_populates="detections",
        lazy="selectin",
        doc="Image this detection belongs to"
    )
    
    def __repr__(self) -> str:
        """String representation of the Detection model."""
        return (
            f"<Detection("
            f"id={self.id}, "
            f"label='{self.label}', "
            f"confidence={self.confidence_score:.3f}, "
            f"bbox=({self.bbox_xmin},{self.bbox_ymin},{self.bbox_xmax},{self.bbox_ymax})"
            f")>"
        )
    
    @property
    def bbox_width(self) -> int:
        """Get bounding box width in pixels."""
        return self.bbox_xmax - self.bbox_xmin
    
    @property
    def bbox_height(self) -> int:
        """Get bounding box height in pixels."""
        return self.bbox_ymax - self.bbox_ymin
    
    @property
    def bbox_area(self) -> int:
        """Get bounding box area in square pixels."""
        return self.bbox_width * self.bbox_height
    
    @property
    def bbox_center(self) -> tuple[int, int]:
        """Get bounding box center coordinates (x, y)."""
        center_x = (self.bbox_xmin + self.bbox_xmax) // 2
        center_y = (self.bbox_ymin + self.bbox_ymax) // 2
        return (center_x, center_y)
    
    def confidence_percentage(self) -> float:
        """Get confidence score as percentage."""
        return self.confidence_score * 100