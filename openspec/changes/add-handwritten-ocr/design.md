# Design: Handwritten Text Recognition via OpenRouter

## Architecture

### Data Flow

```
POST /api/v1/images/upload (with file)
    │
    ├─→ Store image in storage
    ├─→ Create Image record in DB
    └─→ Return 202 Accepted + task_id
    
    │
    ▼ (Celery background task)
    
analyze_image_with_ocr(image_id):
    │
    ├─→ Load image from storage
    │
    ├─→ YOLOSCVService.detect_objects()
    │   └─→ Returns: List[{label, bbox, confidence}]
    │
    ├─→ OpenRouterOCRService.extract_text()
    │   └─→ POST to https://openrouter.ai/api/v1/chat/completions
    │   └─→ Returns: {text, confidence, error}
    │
    └─→ Combine + store result
    
GET /api/v1/results/{task_id}
    └─→ Returns combined response
```

### Service Interface

**OpenRouterOCRService** (new)
```python
class OpenRouterOCRService:
    """Extract handwritten text from images via OpenRouter."""
    
    async def extract_text(image: Image.Image) -> dict:
        """
        Args:
            image: PIL Image (RGB or converts)
        
        Returns:
            {
                "text": str | None,           # Extracted text or None if no handwriting
                "confidence": float,          # 0.0-1.0, fixed 0.85 for Claude
                "model": str,                 # "claude-3.5-sonnet"
                "error": str | None           # Error message if failed
            }
        """
```

### API Response Structure

**POST /api/v1/images/upload**
```json
{
  "task_id": "uuid",
  "status": "processing"
}
```

**GET /api/v1/results/{task_id}** (when complete)
```json
{
  "image_id": "uuid",
  "status": "success",
  "detections": [
    {
      "label": "person",
      "box": {"x": 100, "y": 200, "w": 50, "h": 100},
      "confidence": 0.94
    }
  ],
  "text_extraction": {
    "text": "Meeting notes:\n- Review Q2\n- Budget cut 10%",
    "confidence": 0.85,
    "model": "claude-3.5-sonnet",
    "error": null
  }
}
```

**If OCR fails but detection succeeds (partial)**
```json
{
  "image_id": "uuid",
  "status": "partial",
  "detections": [...],
  "text_extraction": {
    "text": null,
    "confidence": 0.0,
    "model": "claude-3.5-sonnet",
    "error": "OpenRouter API timeout"
  }
}
```

## Implementation Details

### Config (backend/src/core/config.py)

Add:
```python
OPENROUTER_API_KEY: str = Field(
    default="",
    validation_alias="OPENROUTER_API_KEY",
    description="OpenRouter API key for vision models"
)
```

### File Structure

```
backend/src/services/
├── cv_service_interface.py    (unchanged)
├── yolos_cv_service.py        (unchanged)
├── openrouter_ocr_service.py  (NEW)
├── detection_service.py       (unchanged)
└── ...

backend/src/tasks/
├── detection_tasks.py         (updated: new analyze_image_with_ocr task)
```

### Celery Task

In `backend/src/tasks/detection_tasks.py`, add:
```python
@shared_task(bind=True, max_retries=2)
async def analyze_image_with_ocr(self, image_id: str):
    """Run YOLO + OCR, return partial if OCR fails."""
    # Load image
    # Run YOLO detection
    # Run OCR (async)
    # Combine + store
    # Return result
```

### Error Handling Strategy

1. **YOLO fails** → Return 500 error (existing behavior)
2. **OCR fails** → Return 200 with status="partial", detections present, text_extraction.error set
3. **Both fail** → Return 500 error
4. **Timeout** → Retry once, then return partial if still fails

## Model Choice

**Claude 3.5 Sonnet** (via OpenRouter)
- Cost: $3/$15 per 1M tokens
- Handwriting accuracy: ~90-95% for clear text
- Speed: 1-3 seconds per image
- Fallback: If budget concern, can switch to GPT-4V ($0.01/image) or LLaVa ($0.24/1M tokens)

## Dependencies

**New package:**
- `httpx` - Async HTTP client for OpenRouter API

**No schema changes** - Use existing detection result storage.

## Testing Strategy

1. **Unit tests** - Mock OpenRouter responses
2. **Integration tests** - Real OpenRouter API with test image
3. **Behavior tests** - End-to-end with handwritten sample images
4. **Error tests** - Timeout, invalid key, network failure scenarios
