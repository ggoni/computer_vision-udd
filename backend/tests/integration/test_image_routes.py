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


def _upload_image(filename: str = "test.jpg") -> str:
    data = _sample_jpeg_bytes()
    response = client.post(
        "/api/v1/images/upload",
        files={"file": (filename, data, "image/jpeg")},
    )
    assert response.status_code == 201
    body = response.json()
    return body["id"]


def test_upload_and_metadata_and_download_and_delete_flow():
    """End-to-end flow test without relying on global state, ensuring isolation."""
    image_id = _upload_image()

    # Metadata
    meta_resp = client.get(f"/api/v1/images/{image_id}")
    assert meta_resp.status_code == 200
    assert meta_resp.json()["id"] == image_id

    # Download
    file_resp = client.get(f"/api/v1/images/{image_id}/file")
    assert file_resp.status_code == 200
    assert file_resp.headers["content-type"].startswith("image/")
    assert len(file_resp.content) > 0

    # Delete
    del_resp = client.delete(f"/api/v1/images/{image_id}")
    assert del_resp.status_code == 204

    # Confirm 404 after deletion
    not_found_resp = client.get(f"/api/v1/images/{image_id}")
    assert not_found_resp.status_code == 404


def test_get_image_not_found():
    response = client.get(f"/api/v1/images/{uuid4()}")
    assert response.status_code == 404
