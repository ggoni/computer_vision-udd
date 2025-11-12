"""ORM models package.

This package contains all SQLAlchemy ORM models for the computer vision application.
Models are imported here to ensure they are registered with the declarative base.
"""

from .image import Image
from .detection import Detection

__all__ = ["Image", "Detection"]