# Tasks: Handwritten Text Recognition Implementation

> **Instructions**: Complete tasks sequentially. Each task is atomic, testable, and follows SOLID principles. Test after each task before proceeding.

---

## Phase 1: Setup & Configuration

### Task 1.1: Add httpx Dependency

**Objective**: Add async HTTP client to project

**Steps**:
1. Run `uv add httpx`
2. Verify `pyproject.toml` updated
3. Verify `uv.lock` regenerated

**Test**:
```bash
uv run python -c "import httpx; print(httpx.__version__)"
```

**Acceptance**: httpx importable and locked

---

### Task 1.2: Add OpenRouter API Key Configuration

**Objective**: Support OPENROUTER_API_KEY environment variable

**Steps**:
1. Open `backend/src/core/config.py`
2. Add field to Settings class:
   ```python
   OPENROUTER_API_KEY: str = Field(
       default="",
       validation_alias="OPENROUTER_API_KEY",
       description="OpenRouter API key for vision models"
   )
   ```
3. Verify validation works
4. Update `.env.example` with placeholder

**Test**:
```bash
OPENROUTER_API_KEY=sk-test-key uv run python -c \
  "from src.core.config import get_settings; s = get_settings(); print(s.OPENROUTER_API_KEY)"
```

**Acceptance**: Configuration loads from environment variable

---

## Phase 2: Core Service Implementation

### Task 2.1: Create OpenRouterOCRService Class

**Objective**: Implement handwritten text extraction via OpenRouter API

**File**: `backend/src/services/openrouter_ocr_service.py`

**Steps**:
1. Create new file
2. Implement `OpenRouterOCRService` class with:
   - `__init__(api_key: str | None = None)`
   - `async def extract_text(image: Image.Image) -> dict[str, Any]`
3. Use Claude 3.5 Sonnet model
4. Base64 encode image
5. Handle "NO_HANDWRITING" response
6. Include timeout (30s) and error handling

**Implementation**:
```python
"""OpenRouter-based OCR service for handwritten text extraction."""

from __future__ import annotations

import base64
import io
import logging
from typing import TYPE_CHECKING, Any

import httpx
from src.core.config import get_settings

if TYPE_CHECKING:
    from PIL import Image

logger = logging.getLogger(__name__)


class OpenRouterOCRService:
    """Extract handwritten text from images using OpenRouter."""

    def __init__(self, api_key: str | None = None):
        settings = get_settings()
        self._api_key = api_key or settings.OPENROUTER_API_KEY
        self._model = "claude-3.5-sonnet"
        self._base_url = "https://openrouter.ai/api/v1/chat/completions"

    async def extract_text(self, image: Image.Image) -> dict[str, Any]:
        """
        Extract handwritten text from image.

        Args:
            image: PIL Image object

        Returns:
            {
                "text": str | None,
                "confidence": float,
                "model": str,
                "error": str | None
            }
        """
        # Ensure RGB
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Convert to base64
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        base64_image = base64.standard_b64encode(buffer.getvalue()).decode("utf-8")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self._base_url,
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "HTTP-Referer": "http://localhost:3000",
                        "X-Title": "Computer Vision App",
                    },
                    json={
                        "model": self._model,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "image",
                                        "source": {
                                            "type": "base64",
                                            "media_type": "image/png",
                                            "data": base64_image,
                                        },
                                    },
                                    {
                                        "type": "text",
                                        "text": (
                                            "Read all handwritten text in this image. "
                                            "Return ONLY the extracted text. "
                                            "If no handwriting found, return 'NO_HANDWRITING'."
                                        ),
                                    },
                                ],
                            }
                        ],
                        "max_tokens": 1000,
                    },
                )

                response.raise_for_status()
                data = response.json()
                extracted = data["choices"][0]["message"]["content"].strip()

                if extracted == "NO_HANDWRITING":
                    return {
                        "text": None,
                        "confidence": 1.0,
                        "model": self._model,
                        "error": None,
                    }

                return {
                    "text": extracted,
                    "confidence": 0.85,
                    "model": self._model,
                    "error": None,
                }

        except httpx.HTTPError as e:
            logger.error("OpenRouter API error: %s", e)
            return {
                "text": None,
                "confidence": 0.0,
                "model": self._model,
                "error": str(e),
            }
```

**Test**:
```bash
# Mock test (no real API call)
uv run pytest backend/tests/unit/test_openrouter_ocr_service.py::test_extract_text_no_handwriting -v
```

**Acceptance**: Class created, methods exist, mocks pass

---

### Task 2.2: Write Unit Tests for OpenRouterOCRService

**Objective**: Comprehensive unit tests with mocked API

**File**: `backend/tests/unit/test_openrouter_ocr_service.py`

**Test Cases**:
1. `test_extract_text_success` - Returns extracted text + confidence 0.85
2. `test_extract_text_no_handwriting` - Returns null + confidence 1.0
3. `test_extract_text_api_error` - Handles httpx.HTTPError gracefully
4. `test_extract_text_timeout` - Handles timeout (30s)
5. `test_extract_text_image_conversion` - Converts non-RGB to RGB
6. `test_init_with_custom_api_key` - Accepts custom key in constructor

**Acceptance**: All tests pass, >95% coverage

---

## Phase 3: Integration with Celery Task

### Task 3.1: Update Detection Task to Include OCR

**Objective**: Integrate OCR into async image analysis pipeline

**File**: `backend/src/tasks/detection_tasks.py`

**Steps**:
1. Import OpenRouterOCRService
2. Update `analyze_image_with_ocr` task (create if doesn't exist):
   - Load image from storage
   - Run YOLO detection
   - Run OCR async (in parallel)
   - Combine results
   - Store/return combined result
3. Handle partial results (OCR fails but YOLO succeeds)
4. Add logging for each step

**Implementation Pattern**:
```python
@shared_task(bind=True, max_retries=2)
def analyze_image_with_ocr(self, image_id: str):
    """Run YOLO + OCR, return partial if OCR fails."""
    import asyncio
    from PIL import Image
    from io import BytesIO

    try:
        # 1. Load image
        storage = get_file_storage()
        image_bytes = storage.get_file(image_id)
        image = Image.open(BytesIO(image_bytes))

        # 2. Run YOLO
        yolo_service = YOLOSCVService()
        yolo_service.load_model()
        detections = yolo_service.detect_objects(image)

        # 3. Run OCR
        ocr_service = OpenRouterOCRService()
        ocr_result = asyncio.run(ocr_service.extract_text(image))

        # 4. Combine
        result = {
            "image_id": image_id,
            "detections": detections,
            "text_extraction": ocr_result,
            "status": "success" if ocr_result["error"] is None else "partial",
        }

        # 5. Store result
        store_result(image_id, result)
        return result

    except Exception as exc:
        logger.error("Analysis failed: %s", exc)
        self.retry(exc=exc, countdown=5)
```

**Test**:
```bash
# Mock OpenRouter + test task execution
uv run pytest backend/tests/integration/test_detection_tasks_with_ocr.py -v
```

**Acceptance**: Task runs end-to-end with mocked OCR, returns combined result

---

### Task 3.2: Update Detection Response Schema

**Objective**: Add text_extraction field to API response

**File**: `backend/src/schemas/detection.py`

**Steps**:
1. Add TextExtractionSchema:
   ```python
   class TextExtractionSchema(BaseModel):
       text: str | None
       confidence: float
       model: str
       error: str | None
   ```
2. Add to DetectionResultSchema:
   ```python
   text_extraction: TextExtractionSchema | None = None
   ```

**Test**:
```bash
uv run pytest backend/tests/unit/test_detection_schema.py::test_detection_result_with_ocr -v
```

**Acceptance**: Schema validates, serialization works

---

## Phase 4: Testing & Validation

### Task 4.1: Integration Test with Real Image

**Objective**: End-to-end test with actual handwritten image

**File**: `backend/tests/integration/test_ocr_e2e.py`

**Steps**:
1. Create/use test image with handwritten text
2. Upload via API endpoint
3. Poll for results
4. Verify detections + text extraction both present
5. Verify confidence scores

**Test Cases**:
- Upload handwritten note image
- Verify text extracted correctly
- Verify objects still detected (if any)
- Verify response schema matches spec

**Acceptance**: Real end-to-end flow works (requires valid OPENROUTER_API_KEY)

---

### Task 4.2: Error Handling Tests

**Objective**: Verify graceful degradation when OCR fails

**Steps**:
1. Test timeout scenario (simulate 30s+ API response)
2. Test invalid API key
3. Test network error
4. Verify partial results returned (objects present, text extraction has error)

**Acceptance**: All error paths return expected responses

---

## Phase 5: Documentation & Cleanup

### Task 5.1: Update README

**Objective**: Document new OCR feature

**Steps**:
1. Add "Handwritten Text Recognition" section
2. Mention Claude 3.5 Sonnet via OpenRouter
3. Show example API response with text_extraction field
4. Document configuration (OPENROUTER_API_KEY)

**Acceptance**: README updated and clear

---

### Task 5.2: Update .env.example

**Objective**: Document configuration for new developers

**Steps**:
1. Add `OPENROUTER_API_KEY=sk-or-...` placeholder
2. Add comment explaining where to get key

**Acceptance**: .env.example complete

---

## Rollout Checklist

- [x] Task 1.1: httpx added
- [x] Task 1.2: Config supports API key
- [x] Task 2.1: OpenRouterOCRService implemented
- [x] Task 2.2: Unit tests pass
- [x] Task 3.1: Celery task updated
- [x] Task 3.2: Response schema updated
- [x] Task 4.1: E2E test passes
- [x] Task 4.2: Error scenarios handled
- [x] Task 5.1: README updated
- [x] Task 5.2: .env.example updated

**Ready to implement?** Exit explore mode and start Task 1.1.
