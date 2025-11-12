"""API routes package exports routers for inclusion in main app."""

from .health import router as health_router
from .images import router as images_router
from .detection import router as detection_router  # type: ignore[attr-defined]

__all__ = ["health_router", "images_router", "detection_router"]