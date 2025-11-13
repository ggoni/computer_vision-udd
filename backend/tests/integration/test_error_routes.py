"""Integration tests for error and edge cases using dependency overrides."""

from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from src.api.routes.images import get_image_service  # type: ignore
from src.main import app

client = TestClient(app)


class FakeImageServiceDuplicate:
    async def save_uploaded_image(
        self, *, file_bytes: bytes, filename: str, original_url: str | None = None
    ):  # type: ignore[override]
        raise ValueError("Image with the same attributes already exists")

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
    app.dependency_overrides.pop(get_image_service, None)


def test_analyze_nonexistent_image_returns_404():
    # Generate an ID not present in DB (guard against extremely unlikely UUID collision)
    attempt = 0
    while attempt < 3:
        random_id = uuid4()
        meta = client.get(f"/api/v1/images/{random_id}")
        if meta.status_code == 404:
            break
        attempt += 1
    resp = client.post(f"/api/v1/images/{random_id}/analyze")
    assert resp.status_code == 404
