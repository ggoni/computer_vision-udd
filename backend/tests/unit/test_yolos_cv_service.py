"""Unit tests for YOLOSCVService."""

from __future__ import annotations

from unittest.mock import Mock

import pytest
from PIL import Image

from src.services.yolos_cv_service import YOLOSCVService


@pytest.fixture
def mock_model_loader():
    loader = Mock()
    loader.load_model.return_value = None
    loader.warmup.return_value = None
    return loader


def create_test_image(color: str = "white") -> Image.Image:
    return Image.new("RGB", (100, 100), color=color)


def test_load_model_invokes_loader_methods(mock_model_loader):
    service = YOLOSCVService(model_loader=mock_model_loader)

    service.load_model()

    mock_model_loader.load_model.assert_called_once()
    mock_model_loader.warmup.assert_called_once()


def test_detect_objects_returns_formatted_results(mock_model_loader):
    mock_model = Mock(
        return_value=[
            {
                "label": "cat",
                "score": 0.95,
                "box": {"xmin": 10, "ymin": 20, "xmax": 110, "ymax": 120},
            },
            {
                "label": "dog",
                "score": 0.80,
                "box": {"xmin": 5, "ymin": 15, "xmax": 85, "ymax": 95},
            },
        ]
    )
    mock_model_loader.get_model.return_value = mock_model

    service = YOLOSCVService(model_loader=mock_model_loader, confidence_threshold=0.5)

    image = create_test_image()
    results = service.detect_objects(image)

    assert len(results) == 2
    first = results[0]
    assert first["label"] == "gato"  # Translated from "cat" to Spanish
    assert first["confidence_score"] == pytest.approx(0.95)
    assert first["bbox"] == {"xmin": 10, "ymin": 20, "xmax": 110, "ymax": 120}


def test_detect_objects_filters_by_confidence(mock_model_loader):
    mock_model = Mock(
        return_value=[
            {
                "label": "bird",
                "score": 0.40,
                "box": {"xmin": 0, "ymin": 0, "xmax": 50, "ymax": 50},
            }
        ]
    )
    mock_model_loader.get_model.return_value = mock_model

    service = YOLOSCVService(model_loader=mock_model_loader, confidence_threshold=0.5)

    image = create_test_image()
    results = service.detect_objects(image)

    assert results == []


def test_detect_objects_converts_to_rgb(mock_model_loader):
    mock_model = Mock(return_value=[])
    mock_model_loader.get_model.return_value = mock_model

    service = YOLOSCVService(model_loader=mock_model_loader)

    image = Image.new("RGBA", (60, 60), color=(255, 0, 0, 128))
    service.detect_objects(image)

    mock_model.assert_called_once()
    called_image = mock_model.call_args.args[0]
    assert called_image.mode == "RGB"
