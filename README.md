# Computer Vision Detection API

FastAPI-based backend providing image upload, object detection analysis, and paginated listing of images and detections.

## Endpoints Overview

### Images
- `POST /api/v1/images/upload` — Upload an image file. Returns metadata (201). Errors: 415 unsupported type, 409 duplicate (simulated duplicate scenario).
- `GET /api/v1/images/{image_id}` — Fetch image metadata (200 / 404).
- `GET /api/v1/images/{image_id}/file` — Download stored file (200 / 404 missing image or file).
- `DELETE /api/v1/images/{image_id}` — Delete image and its file (204 / 404).
- `GET /api/v1/images` — Paginated list of images. Query params: `page`, `page_size`, `status`, `filename_substr`.

### Detections
- `POST /api/v1/images/{image_id}/analyze` — Run CV model and persist detections (201 list of detections / 404 if image not found).
- `GET /api/v1/images/{image_id}/detections` — List detections for an image (200 empty list if none).
- `GET /api/v1/detections` — Paginated global detections. Query params: `page`, `page_size`, `label`, `min_confidence`.

## Pagination Response Shape
```
{
	"items": [ ... ],
	"total": 42,
	"page": 1,
	"page_size": 20,
	"pages": 3,
	"has_next": true,
	"has_previous": false
}
```

## Development
Run tests:
```
uv run pytest -q
```

## Notes
- Timezone-aware timestamps (`datetime.now(timezone.utc)`) used throughout.
- File storage paths include hash prefix + original stem; collision resolution adds random suffix.
- Detection service can be overridden in tests for faster runs (fake service).
- Duplicate upload 409 is triggered via dependency override simulation; real implementation permits re-upload with unique path.

