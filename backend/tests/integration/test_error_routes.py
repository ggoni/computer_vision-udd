"""Integration tests for error and edge cases using dependency overrides."""

from __future__ import annotations

from uuid import uuid4

from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from src.api.routes.images import get_image_service  # type: ignore
from src.main import app

client = TestClient(app)


class FakeImageServiceDuplicate:
    async def save_uploaded_image(
        self, *, file_bytes: bytes, filename: str, original_url: str | None = None
    ):  # type: ignore[override]
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Image with the same attributes already exists"
        )

    async def upload_image(
        self, *, image_content: bytes, original_filename: str, content_type: str
    ):
        """Also raise the same error for upload_image method."""
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Image with the same attributes already exists"
        )

    async def get_image(self, image_id):  # pragma: no cover - not used here
        return None

    async def delete_image(self, image_id):  # pragma: no cover - not used here
        return False


def test_upload_duplicate_returns_409(monkeypatch):
    # Override image service to simulate duplicate scenario
    app.dependency_overrides[get_image_service] = lambda: FakeImageServiceDuplicate()
    resp = client.post(
        "/api/v1/images/upload",
        files={"file": ("dup.jpg", b"data", "image/jpeg")},
    )
    assert resp.status_code == 409
    assert "already exists" in resp.json()["detail"]

    # Clean up override
    del app.dependency_overrides[get_image_service]


def test_analyze_nonexistent_image_returns_404(monkeypatch):
    """Test that analyzing an image that doesn't exist returns 404."""

    class FakeImageServiceEmpty:
        async def get_image(self, image_id):
            return None

    app.dependency_overrides[get_image_service] = lambda: FakeImageServiceEmpty()

    fake_uuid = uuid4()
    resp = client.post(f"/api/v1/images/{fake_uuid}/analyze")
    assert resp.status_code == 404

    # Clean up override
    del app.dependency_overrides[get_image_service]
