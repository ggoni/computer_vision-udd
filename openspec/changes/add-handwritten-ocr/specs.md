# Specs: Handwritten Text Recognition

## Requirements

### Functional Requirements

#### FR1: OpenRouter API Integration
- System shall call OpenRouter Claude 3.5 Sonnet vision API
- API key shall be read from environment variable `OPENROUTER_API_KEY`
- Requests shall include HTTP-Referer and X-Title headers for rate limit fairness
- Timeout shall be 30 seconds per request
- Max tokens per response: 1000

#### FR2: Text Extraction
- System shall extract handwritten text from uploaded images
- If no handwriting detected, return `text: null` with `confidence: 1.0`
- If handwriting found, return extracted text with `confidence: 0.85`
- Confidence score shall be fixed (Claude doesn't provide extraction confidence)

#### FR3: Async Processing
- Image analysis shall run asynchronously via Celery
- YOLO detection and OCR shall run in parallel (not sequentially)
- Results shall be combined before storage
- API shall return 202 Accepted immediately on upload

#### FR4: Error Handling
- If OCR fails, return partial results (objects only, no error thrown)
- If YOLO fails, return 500 error (existing behavior)
- If both fail, return 500 error
- Retry failed OCR tasks up to 2 times with 5-second backoff

#### FR5: API Response Structure
- Detection endpoint shall include `text_extraction` field with:
  - `text` (string | null)
  - `confidence` (float: 0.0-1.0)
  - `model` (string: "claude-3.5-sonnet")
  - `error` (string | null)

### Non-Functional Requirements

#### NFR1: Performance
- OCR latency: <3 seconds for typical image
- Total analysis time (YOLO + OCR parallel): <5 seconds
- No impact on YOLO detection performance (runs in parallel)

#### NFR2: Security
- API key never committed to repository
- API key stored only in `.env` file (gitignored)
- Configuration uses Pydantic `Field` with validation_alias
- No API key in logs, error messages, or responses

#### NFR3: Reliability
- Handle network timeouts gracefully
- Return meaningful error messages for debugging
- Partial results preferred over complete failure

#### NFR4: Compatibility
- Support image formats: JPEG, PNG, GIF, WebP
- Work with existing database schema (no migrations needed)
- Async-compatible with current Celery setup

### Constraints

- OpenRouter API charges per token
- Model selection limited to Claude 3.5 Sonnet (no customization)
- No local OCR fallback (OpenRouter-only)
- Handwriting accuracy depends on image quality and penmanship

## Acceptance Criteria

### Core Feature
- [ ] OpenRouterOCRService class exists and is testable
- [ ] Can extract text from image with handwriting
- [ ] Returns null for images without handwriting
- [ ] Integrates with Celery task pipeline
- [ ] Returns partial results if OCR fails

### Configuration
- [ ] OPENROUTER_API_KEY environment variable supported
- [ ] Configuration validated at startup
- [ ] Clear error if API key missing

### API Integration
- [ ] POST /api/v1/images/upload returns 202 with task_id
- [ ] GET /api/v1/results/{task_id} returns combined results
- [ ] Response includes text_extraction field
- [ ] Error scenarios handled gracefully

### Testing
- [ ] Unit tests mock OpenRouter (no real API calls)
- [ ] Integration tests use test image with handwriting
- [ ] Timeout handling tested (simulate 30s+ response)
- [ ] Network error handling tested
- [ ] Partial result handling tested

### Documentation
- [ ] Design doc updated (DONE)
- [ ] README includes OCR feature in feature list
- [ ] Example response in API docs
- [ ] Configuration documented in .env.example

## Open Questions / Decisions Needed

1. **Image resizing** - Should we resize large images before sending to OpenRouter? (Cost optimization)
   - Current: No, send as-is. Claude handles well.
   - Tradeoff: 4MB image = higher token cost but better accuracy

2. **Language support** - Should we detect language or just extract?
   - Current: Extract whatever is written (any language)
   - Note: Claude supports 90+ languages

3. **Confidence threshold** - Should we filter low-confidence extractions?
   - Current: Return all extracted text regardless of quality
   - Future: Add configurable threshold

4. **Batch processing** - If user uploads multiple images, run OCR in parallel?
   - Current: One image = one task. No batching yet.
   - Future: Implement if performance becomes issue.

## Implementation Checklist

- [ ] Add httpx to pyproject.toml
- [ ] Add OPENROUTER_API_KEY to config.py
- [ ] Create openrouter_ocr_service.py
- [ ] Update detection_tasks.py with OCR integration
- [ ] Update response schema to include text_extraction
- [ ] Write unit tests for OpenRouterOCRService
- [ ] Write integration tests with test image
- [ ] Update .env.example with OPENROUTER_API_KEY
- [ ] Update README with feature mention
- [ ] Manual end-to-end test with real image
