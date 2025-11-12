"""Integration tests for image API routes."""

from __future__ import annotations

from io import BytesIO
from uuid import uuid4

from PIL import Image
from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


def _sample_jpeg_bytes() -> bytes:
    img = Image.new("RGB", (32, 32), color=(10, 20, 30))
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_upload_image_returns_201():
    data = _sample_jpeg_bytes()
    response = client.post(
        "/api/v1/images/upload",
        files={"file": ("test.jpg", data, "image/jpeg")},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["filename"] == "test.jpg"
    assert "id" in body

    # Store ID for subsequent tests (could use fixture setup in larger suite)
    global _last_image_id
    _last_image_id = body["id"]


def test_get_image_metadata():
    # Ensure previous upload ran
    assert _last_image_id is not None
    response = client.get(f"/api/v1/images/{_last_image_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == _last_image_id


def test_download_image_file():
    response = client.get(f"/api/v1/images/{_last_image_id}/file")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/")
    assert len(response.content) > 0


def test_get_image_not_found():
    response = client.get(f"/api/v1/images/{uuid4()}")
    assert response.status_code == 404


def test_delete_image():
    response = client.delete(f"/api/v1/images/{_last_image_id}")
    assert response.status_code == 204

    # Verify 404 after deletion
    response2 = client.get(f"/api/v1/images/{_last_image_id}")
    assert response2.status_code == 404
