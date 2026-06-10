"""Unit tests for DetectionResultSchema with OCR text_extraction field."""

import pytest
from pydantic import ValidationError

from src.schemas.detection import DetectionResultSchema, TextExtractionSchema


class TestTextExtractionSchema:
    """Tests for TextExtractionSchema."""

    def test_text_extraction_success(self):
        schema = TextExtractionSchema(
            text="Hello World",
            confidence=0.85,
            model="claude-3.5-sonnet",
            error=None,
        )
        assert schema.text == "Hello World"
        assert schema.confidence == 0.85
        assert schema.model == "claude-3.5-sonnet"
        assert schema.error is None

    def test_text_extraction_no_handwriting(self):
        schema = TextExtractionSchema(
            text=None,
            confidence=1.0,
            model="claude-3.5-sonnet",
            error=None,
        )
        assert schema.text is None
        assert schema.confidence == 1.0

    def test_text_extraction_error(self):
        schema = TextExtractionSchema(
            text=None,
            confidence=0.0,
            model="claude-3.5-sonnet",
            error="OpenRouter API timeout",
        )
        assert schema.text is None
        assert schema.error == "OpenRouter API timeout"

    def test_confidence_must_be_between_0_and_1(self):
        with pytest.raises(ValidationError):
            TextExtractionSchema(
                text=None,
                confidence=1.5,
                model="claude-3.5-sonnet",
                error=None,
            )


def test_detection_result_with_ocr():
    """DetectionResultSchema includes text_extraction field."""
    result = DetectionResultSchema(
        image_id="550e8400-e29b-41d4-a716-446655440000",
        status="success",
        detections=[],
        text_extraction=TextExtractionSchema(
            text="Meeting notes",
            confidence=0.85,
            model="claude-3.5-sonnet",
            error=None,
        ),
    )
    assert result.text_extraction is not None
    assert result.text_extraction.text == "Meeting notes"
    assert result.status == "success"


def test_detection_result_partial_status():
    """DetectionResultSchema accepts partial status when OCR fails."""
    result = DetectionResultSchema(
        image_id="550e8400-e29b-41d4-a716-446655440000",
        status="partial",
        detections=[],
        text_extraction=TextExtractionSchema(
            text=None,
            confidence=0.0,
            model="claude-3.5-sonnet",
            error="API timeout",
        ),
    )
    assert result.status == "partial"
    assert result.text_extraction.error == "API timeout"


def test_detection_result_without_ocr():
    """text_extraction field is optional (None by default)."""
    result = DetectionResultSchema(
        image_id="550e8400-e29b-41d4-a716-446655440000",
        status="success",
        detections=[],
    )
    assert result.text_extraction is None


def test_detection_result_invalid_status():
    """Status must be 'success' or 'partial'."""
    with pytest.raises(ValidationError):
        DetectionResultSchema(
            image_id="550e8400-e29b-41d4-a716-446655440000",
            status="invalid",
            detections=[],
        )
