"""Integration tests for detection API routes using dependency overrides to avoid heavy model load."""

from __future__ import annotations

from typing import List
from uuid import uuid4

from fastapi.testclient import TestClient

from src.main import app
from src.services.detection_service import DetectionService
from src.schemas.detection import DetectionResponse


class FakeDetectionService(DetectionService):  # type: ignore[misc]
    """Lightweight fake for routing tests; bypass actual CV model."""

    async def analyze_image(self, image_id):  # type: ignore[override]
        # Return deterministic fake detections
        return [
            DetectionResponse(
                id=uuid4(),
                image_id=image_id,
                label="cat",
                confidence_score=0.9,
                bbox_xmin=10,
                bbox_ymin=20,
                bbox_xmax=100,
                bbox_ymax=150,
                created_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
                updated_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
            )
        ]

    async def get_detections(self, image_id):  # type: ignore[override]
        return await self.analyze_image(image_id)

    async def get_all_paginated(self, *, page: int, page_size: int, label=None, min_confidence=None):  # type: ignore[override]
        items = await self.analyze_image(uuid4())
        from src.schemas.common import PaginatedResponse
        return PaginatedResponse[DetectionResponse](items=items, total=1, page=1, page_size=page_size)


client = TestClient(app)

# Override dependency
from src.api.routes.detection import get_detection_service  # type: ignore

app.dependency_overrides[get_detection_service] = lambda: FakeDetectionService(  # type: ignore
    detection_repo=None, cv_service=None, image_repo=None, storage=None
)


def test_analyze_image_and_list_detections(monkeypatch):
    # First, upload an image to obtain ID
    img_bytes = b"fake image bytes"  # The image validation is elsewhere; minimal placeholder
    response = client.post(
        "/api/v1/images/upload",
        files={"file": ("sample.jpg", img_bytes, "image/jpeg")},
    )
    assert response.status_code == 201
    image_id = response.json()["id"]

    # Analyze
    analyze_resp = client.post(f"/api/v1/images/{image_id}/analyze")
    assert analyze_resp.status_code == 201
    detections = analyze_resp.json()
    assert len(detections) == 1
    assert detections[0]["label"] == "cat"

    # List per-image
    list_resp = client.get(f"/api/v1/images/{image_id}/detections")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1


def test_list_global_detections():
    resp = client.get("/api/v1/detections?page=1&page_size=5")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 1
    assert body["page"] == 1
    assert body["page_size"] == 5
