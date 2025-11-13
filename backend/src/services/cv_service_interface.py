"""Abstract interface for computer vision services."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from PIL import Image


class CVServiceInterface(ABC):
    """Contract for all computer vision services."""

    @abstractmethod
    def load_model(self) -> None:
        """Load and prepare the underlying ML model for inference."""

    @abstractmethod
    def detect_objects(self, image: Image.Image) -> list[dict[str, Any]]:
        """Run object detection on a PIL image and return formatted results."""
