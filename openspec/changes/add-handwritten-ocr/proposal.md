# Proposal: Add Handwritten Text Recognition

## Problem

Currently, the CV app detects objects in images (YOLO) but cannot extract handwritten text. Users who upload images containing notes, labels, or handwritten annotations lose that textual information.

## Solution

Add **handwritten text extraction (OCR)** using OpenRouter's Claude 3.5 Sonnet vision API. Extract text from handwritten content in parallel with YOLO object detection, returning combined results.

## Scope

### In
- Add OpenRouterOCRService (mirrors CVServiceInterface pattern)
- Integrate with existing Celery async pipeline
- Return extracted text + confidence scores in detection results
- Handle case where no handwriting exists (return null)
- Return partial results if OCR fails (object detection still works)

### Out
- Handwriting confidence scoring algorithm (use fixed 0.85 for Claude)
- User verification UI for extracted text
- Fine-tuning or custom models
- Real-time streaming of results

## Impact

| Dimension | Impact |
|-----------|--------|
| User Value | Users can now capture handwritten notes alongside object detection |
| Architecture | +1 service class, minimal coupling via Celery task |
| Dependencies | +httpx (async HTTP client) |
| Infrastructure | OpenRouter API key required (no new services) |
| Database | No schema changes (store text in existing detection result) |
| Performance | ~500ms-1s added latency per image (OCR call) |

## Success Criteria

1. ✓ Can extract handwritten text from images
2. ✓ Returns null when no handwriting detected
3. ✓ Returns partial results (objects) if OCR fails
4. ✓ Async processing via Celery
5. ✓ API key secured in .env
6. ✓ Integration tests pass
7. ✓ Example image with handwriting works end-to-end

## Risks

| Risk | Mitigation |
|------|-----------|
| OpenRouter API latency/failure | Implement timeout (30s), return partial results |
| High API costs (per-image billing) | Monitor usage, implement rate limiting if needed |
| Messy/illegible handwriting → poor extraction | Set confidence threshold, document limitations |
| API key exposure | Store in .env, never commit, use environment variable |
