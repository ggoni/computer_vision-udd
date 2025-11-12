# Computer Vision MVP - Task List

> **Instructions**: Complete tasks sequentially. Each task is atomic, testable, and follows SOLID principles. Test after each task before proceeding.

---

## Phase 1: Project Foundation & Setup

### 1.1 Backend Foundation

#### Task 1.1.1: Initialize Backend Project Structure
**Objective**: Create backend directory with uv project configuration

**Steps**:
1. Create `backend/` directory
2. Run `uv init` inside backend/
3. Verify `pyproject.toml` created with Python 3.12

**Test**: `uv --version` shows uv installed, `pyproject.toml` exists

**Acceptance**: Backend folder has valid uv project structure

---

#### Task 1.1.2: Configure Backend Dependencies
**Objective**: Add core backend dependencies using uv

**Steps**:
1. Add FastAPI: `uv add fastapi`
2. Add Uvicorn: `uv add uvicorn[standard]`
3. Add SQLAlchemy: `uv add sqlalchemy`
4. Add Alembic: `uv add alembic`
5. Add Pydantic Settings: `uv add pydantic-settings`
6. Add PostgreSQL driver: `uv add psycopg2-binary`
7. Add Redis client: `uv add redis`
8. Verify `uv.lock` generated

**Test**: `uv pip list` shows all dependencies, `uv sync` completes without errors

**Acceptance**: All dependencies locked in `uv.lock`

---

#### Task 1.1.3: Add ML/CV Dependencies
**Objective**: Install ML libraries for computer vision

**Steps**:
1. Add Transformers: `uv add transformers`
2. Add PyTorch: `uv add torch torchvision`
3. Add Pillow: `uv add pillow`
4. Add NumPy: `uv add numpy`
5. Add Python-multipart: `uv add python-multipart`

**Test**: `uv run python -c "import torch; import transformers; import PIL"` succeeds

**Acceptance**: All ML dependencies importable

---

#### Task 1.1.4: Add Testing & Development Dependencies
**Objective**: Install testing framework and dev tools

**Steps**:
1. Add pytest: `uv add --dev pytest`
2. Add pytest-asyncio: `uv add --dev pytest-asyncio`
3. Add pytest-cov: `uv add --dev pytest-cov`
4. Add httpx: `uv add --dev httpx`
5. Add black: `uv add --dev black`
6. Add ruff: `uv add --dev ruff`

**Test**: `uv run pytest --version` shows pytest installed

**Acceptance**: Dev dependencies in `[tool.uv.dev-dependencies]` section

---

#### Task 1.1.5: Create Backend Directory Structure
**Objective**: Set up clean architecture folder structure

**Steps**:
1. Create `backend/src/` directory
2. Create subdirectories: `api/`, `core/`, `db/`, `models/`, `schemas/`, `services/`, `utils/`
3. Create `api/routes/` subdirectory
4. Create `tests/unit/` and `tests/integration/` directories
5. Add `__init__.py` to all Python package directories
6. Create `backend/storage/uploads/` directory
7. Add `.gitkeep` to empty directories

**Test**: Directory structure matches architecture.md specification

**Acceptance**: All directories exist with proper `__init__.py` files

---

### 1.2 Configuration & Core Setup

#### Task 1.2.1: Create Core Configuration Module
**Objective**: Implement centralized configuration using Pydantic Settings

**File**: `backend/src/core/config.py`

**Steps**:
1. Create `Settings` class extending `BaseSettings`
2. Add fields: `APP_ENV`, `DEBUG`, `LOG_LEVEL`, `DATABASE_URL`, `REDIS_URL`
3. Add fields: `UPLOAD_DIR`, `MAX_UPLOAD_SIZE`, `MODEL_NAME`, `MODEL_CACHE_DIR`, `CONFIDENCE_THRESHOLD`
4. Configure `model_config` with `env_file=".env"`
5. Create `get_settings()` function with `@lru_cache` decorator
6. Add docstrings

**Test**: Create `tests/unit/test_config.py`:
```python
def test_settings_loads_defaults():
    settings = get_settings()
    assert settings.APP_ENV is not None
    assert settings.MAX_UPLOAD_SIZE > 0
```

**Acceptance**: Settings loadable, cached, and testable

---

#### Task 1.2.2: Create .env.example File
**Objective**: Document required environment variables

**File**: `backend/.env.example`

**Steps**:
1. List all config variables from Settings class
2. Provide example values (not secrets)
3. Add comments for each section
4. Add instructions at top

**Test**: Copy to `.env`, verify settings load without errors

**Acceptance**: Complete env template with documentation

---

#### Task 1.2.3: Implement Structured Logging
**Objective**: Set up JSON structured logging with correlation IDs

**File**: `backend/src/core/logging.py`

**Steps**:
1. Import `logging` and `json`
2. Create `JSONFormatter` class extending `logging.Formatter`
3. Implement `format()` method to output JSON
4. Create `setup_logging()` function that:
   - Reads `LOG_LEVEL` from settings
   - Configures root logger
   - Adds JSONFormatter
5. Add correlation ID context var (contextvars)

**Test**: Create `tests/unit/test_logging.py`:
```python
def test_json_formatter_outputs_valid_json():
    setup_logging()
    # Capture log output and verify JSON structure
```

**Acceptance**: Logs output valid JSON with timestamp, level, message

---

#### Task 1.2.4: Create Database Base Configuration
**Objective**: Set up SQLAlchemy declarative base and UUID mixin

**File**: `backend/src/db/base.py`

**Steps**:
1. Import SQLAlchemy components
2. Create `Base = declarative_base()`
3. Create `UUIDMixin` with `id = Column(UUID, primary_key=True, default=uuid4)`
4. Create `TimestampMixin` with `created_at` and `updated_at` fields
5. Configure `updated_at` with `onupdate=func.now()`

**Test**: Create `tests/unit/test_db_base.py`:
```python
def test_uuid_mixin_generates_uuid():
    class TestModel(Base, UUIDMixin):
        __tablename__ = "test"

    model = TestModel()
    assert model.id is not None
```

**Acceptance**: Mixins reusable across all models

---

#### Task 1.2.5: Implement Database Session Management
**Objective**: Create async session factory with connection pooling

**File**: `backend/src/db/session.py`

**Steps**:
1. Import `create_async_engine`, `async_sessionmaker`
2. Create `engine` with `DATABASE_URL` from settings
3. Configure pool: `pool_size=20`, `max_overflow=10`, `pool_pre_ping=True`
4. Create `AsyncSessionLocal` using `async_sessionmaker`
5. Implement `get_db()` async generator for dependency injection
6. Add proper cleanup with `finally`

**Test**: Create `tests/integration/test_db_session.py`:
```python
@pytest.mark.asyncio
async def test_get_db_yields_session():
    async for session in get_db():
        assert session is not None
        assert hasattr(session, 'execute')
```

**Acceptance**: Sessions properly created and closed

---

#### Task 1.2.6: Initialize Alembic for Migrations
**Objective**: Set up database migration system

**Steps**:
1. Run `uv run alembic init backend/src/db/migrations`
2. Edit `alembic.ini`: set `sqlalchemy.url` to use env var
3. Edit `env.py`: import `Base` and set `target_metadata = Base.metadata`
4. Configure async engine in `env.py`
5. Update `script_location` in `alembic.ini`

**Test**: `uv run alembic current` runs without error

**Acceptance**: Alembic configured and ready for migrations

---

### 1.3 Basic FastAPI Application

#### Task 1.3.1: Create Minimal FastAPI App
**Objective**: Initialize FastAPI application instance

**File**: `backend/src/main.py`

**Steps**:
1. Import FastAPI, settings, setup_logging
2. Create `app = FastAPI(title="CV Detection API", version="0.1.0")`
3. Call `setup_logging()` on startup
4. Add root endpoint: `GET /` returning `{"status": "ok"}`
5. Configure CORS middleware (allow localhost origins)
6. Add startup event to log configuration

**Test**: Create `tests/integration/test_main.py`:
```python
def test_root_endpoint():
    from fastapi.testclient import TestClient
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

**Acceptance**: FastAPI app runs with `uv run uvicorn src.main:app`

---

#### Task 1.3.2: Implement Health Check Endpoints
**Objective**: Create health and readiness probes

**File**: `backend/src/api/routes/health.py`

**Steps**:
1. Create router: `router = APIRouter(prefix="/health", tags=["health"])`
2. Implement `GET /health` returning `{"status": "healthy"}`
3. Implement `GET /health/ready` that:
   - Tests DB connection with simple query
   - Returns 200 if healthy, 503 if not
   - Catches exceptions gracefully
4. Add router to main.py

**Test**: Create `tests/integration/test_health.py`:
```python
def test_health_endpoint_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200

def test_ready_endpoint_checks_database():
    # Mock DB connection
    response = client.get("/health/ready")
    assert response.status_code in [200, 503]
```

**Acceptance**: Both endpoints functional, ready checks DB

---

#### Task 1.3.3: Create API Error Handler Middleware
**Objective**: Centralized error handling with proper logging

**File**: `backend/src/api/middleware.py`

**Steps**:
1. Create `ErrorHandlerMiddleware` class
2. Catch all exceptions in middleware
3. Log errors with correlation ID
4. Return standardized error response:
   ```json
   {
     "error": "error_code",
     "message": "Human readable message",
     "detail": "Technical detail (dev mode only)"
   }
   ```
5. Handle specific exceptions: `RequestValidationError`, `HTTPException`
6. Add middleware to FastAPI app

**Test**: Create `tests/unit/test_middleware.py`:
```python
def test_error_middleware_catches_exceptions():
    # Trigger error and verify response format
```

**Acceptance**: All errors properly formatted and logged

---

#### Task 1.3.4: Create API Dependencies Module
**Objective**: Reusable dependency injection functions

**File**: `backend/src/api/dependencies.py`

**Steps**:
1. Create `get_settings()` dependency (already in config)
2. Create `get_db()` dependency (already in session)
3. Create `get_correlation_id()` from request headers or generate
4. Create `verify_upload_size()` dependency for file uploads
5. Add docstrings for each

**Test**: Create `tests/unit/test_dependencies.py`:
```python
def test_get_correlation_id_generates_uuid():
    correlation_id = get_correlation_id()
    assert len(correlation_id) > 0
```

**Acceptance**: Dependencies reusable across routes

---

## Phase 2: Database Models & Schemas

### 2.1 ORM Models

#### Task 2.1.1: Create Image ORM Model
**Objective**: Define database model for images table

**File**: `backend/src/models/image.py`

**Steps**:
1. Import Base, UUIDMixin, TimestampMixin
2. Create `Image` class extending Base, UUIDMixin, TimestampMixin
3. Define table: `__tablename__ = "images"`
4. Add columns:
   - `filename: str` (255 chars)
   - `original_url: str` (optional, nullable)
   - `storage_path: str` (500 chars)
   - `file_size: int`
   - `status: str` (50 chars, default="pending")
   - `upload_timestamp: datetime`
5. Add `__repr__` method
6. Add relationship to detections (one-to-many)

**Test**: Create `tests/unit/test_image_model.py`:
```python
def test_image_model_creation():
    image = Image(
        filename="test.jpg",
        storage_path="/uploads/test.jpg",
        file_size=1024,
        upload_timestamp=datetime.utcnow()
    )
    assert image.filename == "test.jpg"
    assert image.status == "pending"
```

**Acceptance**: Model compiles, has all fields, follows naming conventions

---

#### Task 2.1.2: Create Detection ORM Model
**Objective**: Define database model for detections table

**File**: `backend/src/models/detection.py`

**Steps**:
1. Import Base, UUIDMixin, TimestampMixin
2. Create `Detection` class
3. Define table: `__tablename__ = "detections"`
4. Add columns:
   - `image_id: UUID` (ForeignKey to images.id, with cascade delete)
   - `label: str` (100 chars)
   - `confidence_score: float`
   - `bbox_xmin: int`
   - `bbox_ymin: int`
   - `bbox_xmax: int`
   - `bbox_ymax: int`
5. Add relationship: `image = relationship("Image", back_populates="detections")`
6. Add `__repr__` method

**Test**: Create `tests/unit/test_detection_model.py`:
```python
def test_detection_model_has_bbox_coordinates():
    detection = Detection(
        label="cat",
        confidence_score=0.95,
        bbox_xmin=10, bbox_ymin=20,
        bbox_xmax=100, bbox_ymax=200
    )
    assert detection.label == "cat"
    assert detection.confidence_score == 0.95
```

**Acceptance**: Model has proper foreign key and bbox fields

---

#### Task 2.1.3: Create Initial Database Migration
**Objective**: Generate Alembic migration for tables

**Steps**:
1. Import models in `src/db/base.py` to register them
2. Run: `uv run alembic revision --autogenerate -m "Create images and detections tables"`
3. Review generated migration file
4. Verify up and down operations
5. Test migration: `uv run alembic upgrade head`
6. Verify tables created: `uv run alembic current`

**Test**:
- Check PostgreSQL tables exist
- Run `uv run alembic downgrade base` and verify tables dropped
- Run `uv run alembic upgrade head` again

**Acceptance**: Migration creates tables with all columns and constraints

---

### 2.2 Pydantic Schemas

#### Task 2.2.1: Create Image Base Schemas
**Objective**: Define Pydantic models for Image DTOs

**File**: `backend/src/schemas/image.py`

**Steps**:
1. Create `ImageBase` with common fields (filename, file_size)
2. Create `ImageCreate` extending ImageBase (fields for creation)
3. Create `ImageUpdate` with optional fields for updates
4. Create `ImageInDB` extending ImageBase with:
   - All DB fields (id, created_at, status, etc.)
   - Configure `from_attributes = True`
5. Create `ImageResponse` for API responses
6. Add validators for filename (no path traversal)

**Test**: Create `tests/unit/test_image_schema.py`:
```python
def test_image_schema_validates_filename():
    with pytest.raises(ValidationError):
        ImageCreate(filename="../etc/passwd", file_size=100)
```

**Acceptance**: Schemas validate input, convert from ORM

---

#### Task 2.2.2: Create Detection Base Schemas
**Objective**: Define Pydantic models for Detection DTOs

**File**: `backend/src/schemas/detection.py`

**Steps**:
1. Create `BoundingBox` model with xmin, ymin, xmax, ymax
2. Add validator: xmax > xmin and ymax > ymin
3. Create `DetectionBase` with label, confidence_score, bbox
4. Create `DetectionCreate` extending DetectionBase + image_id
5. Create `DetectionInDB` with id, created_at
6. Create `DetectionResponse` for API responses
7. Add validator: confidence_score between 0 and 1

**Test**: Create `tests/unit/test_detection_schema.py`:
```python
def test_bbox_validates_coordinates():
    with pytest.raises(ValidationError):
        BoundingBox(xmin=100, ymin=50, xmax=50, ymax=100)

def test_confidence_score_range():
    with pytest.raises(ValidationError):
        DetectionBase(label="cat", confidence_score=1.5, bbox=...)
```

**Acceptance**: Schemas validate bbox and confidence ranges

---

#### Task 2.2.3: Create Paginated Response Schema
**Objective**: Generic pagination wrapper for list endpoints

**File**: `backend/src/schemas/common.py`

**Steps**:
1. Create generic `PaginatedResponse[T]` using TypeVar
2. Add fields: `items: List[T]`, `total: int`, `page: int`, `page_size: int`, `pages: int`
3. Add computed property `has_next` and `has_previous`
4. Add example documentation

**Test**: Create `tests/unit/test_common_schema.py`:
```python
def test_paginated_response_calculates_pages():
    response = PaginatedResponse(
        items=[1, 2, 3],
        total=10,
        page=1,
        page_size=3
    )
    assert response.pages == 4
    assert response.has_next is True
```

**Acceptance**: Generic pagination schema reusable

---

## Phase 3: Utility Functions

### 3.1 File Handling Utilities

#### Task 3.1.1: Implement File Validation Utility
**Objective**: Validate uploaded files (type, size, safety)

**File**: `backend/src/utils/file_utils.py`

**Steps**:
1. Create `ALLOWED_EXTENSIONS` constant: {".jpg", ".jpeg", ".png", ".webp"}
2. Create `validate_file_extension(filename: str) -> bool`
3. Create `validate_file_size(size: int, max_size: int) -> bool`
4. Create `sanitize_filename(filename: str) -> str`:
   - Remove path components
   - Replace special characters
   - Limit length to 255 chars
5. Create `get_file_hash(file_bytes: bytes) -> str` (SHA256)
6. Add docstrings and type hints

**Test**: Create `tests/unit/test_file_utils.py`:
```python
def test_sanitize_filename_removes_path():
    result = sanitize_filename("../../etc/passwd")
    assert "/" not in result
    assert ".." not in result

def test_validate_extension_allows_jpg():
    assert validate_file_extension("image.jpg") is True
    assert validate_file_extension("file.exe") is False

def test_file_hash_is_consistent():
    data = b"test content"
    hash1 = get_file_hash(data)
    hash2 = get_file_hash(data)
    assert hash1 == hash2
```

**Acceptance**: All validations work, filenames sanitized safely

---

#### Task 3.1.2: Implement File Storage Service
**Objective**: Save and retrieve files from storage

**File**: `backend/src/utils/file_storage.py`

**Steps**:
1. Create `FileStorage` class with `upload_dir` from settings
2. Implement `save_file(file_bytes: bytes, filename: str) -> str`:
   - Create timestamped subdirectory (YYYY/MM/DD)
   - Generate unique filename (hash + original name)
   - Save file to disk
   - Return storage path
3. Implement `get_file_path(storage_path: str) -> Path`
4. Implement `delete_file(storage_path: str) -> bool`
5. Implement `file_exists(storage_path: str) -> bool`
6. Handle errors gracefully (disk full, permissions, etc.)

**Test**: Create `tests/unit/test_file_storage.py`:
```python
def test_save_file_creates_directory_structure(tmp_path):
    storage = FileStorage(upload_dir=tmp_path)
    file_bytes = b"test image data"
    path = storage.save_file(file_bytes, "test.jpg")

    assert storage.file_exists(path)
    saved_file = storage.get_file_path(path)
    assert saved_file.read_bytes() == file_bytes

def test_delete_file_removes_file(tmp_path):
    storage = FileStorage(upload_dir=tmp_path)
    path = storage.save_file(b"data", "test.jpg")
    assert storage.delete_file(path) is True
    assert storage.file_exists(path) is False
```

**Acceptance**: Files saved/retrieved/deleted correctly, errors handled

---

### 3.2 ML Model Utilities

#### Task 3.2.1: Implement Model Loader Singleton
**Objective**: Load ML model once and cache in memory

**File**: `backend/src/utils/model_loader.py`

**Steps**:
1. Create `ModelLoader` class with Singleton pattern
2. Add `__new__` to enforce single instance
3. Implement `load_model()` method:
   - Check if model already loaded
   - Load from Hugging Face using `pipeline`
   - Cache in instance variable
   - Log loading time
4. Implement `get_model()` that returns cached model
5. Add model warmup method (run dummy inference)
6. Handle loading errors gracefully

**Test**: Create `tests/unit/test_model_loader.py`:
```python
def test_model_loader_is_singleton():
    loader1 = ModelLoader()
    loader2 = ModelLoader()
    assert loader1 is loader2

def test_model_loads_once():
    loader = ModelLoader()
    model1 = loader.get_model()
    model2 = loader.get_model()
    assert model1 is model2  # Same object reference

@pytest.mark.slow
def test_model_warmup_runs_inference():
    loader = ModelLoader()
    loader.load_model()
    # Verify model can run inference
```

**Acceptance**: Model loaded once, subsequent calls return cached instance

---

#### Task 3.2.2: Create Image Preprocessing Utility
**Objective**: Prepare images for model inference

**File**: `backend/src/utils/image_processing.py`

**Steps**:
1. Create `preprocess_image(image_bytes: bytes) -> Image`:
   - Open with PIL
   - Validate image format
   - Check dimensions (min/max)
   - Convert to RGB if needed
2. Create `resize_image(image: Image, max_size: tuple) -> Image`:
   - Maintain aspect ratio
   - Use high-quality resampling
3. Create `image_to_bytes(image: Image, format: str) -> bytes`
4. Add error handling for corrupt images

**Test**: Create `tests/unit/test_image_processing.py`:
```python
def test_preprocess_converts_to_rgb():
    # Create test RGBA image
    image_bytes = create_test_image_rgba()
    processed = preprocess_image(image_bytes)
    assert processed.mode == "RGB"

def test_resize_maintains_aspect_ratio():
    image = create_test_image(1000, 2000)
    resized = resize_image(image, max_size=(500, 500))
    assert resized.width == 250
    assert resized.height == 500
```

**Acceptance**: Images preprocessed correctly, errors handled

---

## Phase 4: Services Layer

### 4.1 Computer Vision Service

#### Task 4.1.1: Create CV Service Interface
**Objective**: Define abstract interface for CV operations (Interface Segregation Principle)

**File**: `backend/src/services/cv_service_interface.py`

**Steps**:
1. Create `CVServiceInterface` abstract base class
2. Define abstract method: `detect_objects(image: Image) -> List[Dict]`
3. Define abstract method: `load_model() -> None`
4. Add docstrings explaining contract

**Test**: Not directly testable (interface only)

**Acceptance**: Clean interface following ISP

---

#### Task 4.1.2: Implement YOLOS Detection Service
**Objective**: Concrete implementation of CV service using YOLOS model

**File**: `backend/src/services/yolos_cv_service.py`

**Steps**:
1. Create `YOLOSCVService` implementing `CVServiceInterface`
2. Inject `ModelLoader` and `Settings` via constructor (Dependency Injection)
3. Implement `load_model()`:
   - Use ModelLoader to get model
   - Perform warmup inference
4. Implement `detect_objects(image: Image) -> List[Dict]`:
   - Run model inference
   - Filter results by confidence threshold
   - Format output: label, score, bbox dict
   - Sort by confidence descending
5. Add logging for inference time

**Test**: Create `tests/unit/test_yolos_cv_service.py`:
```python
def test_detect_objects_returns_formatted_results(mocker):
    # Mock model loader
    mock_model = mocker.Mock()
    mock_model.return_value = [
        {"label": "cat", "score": 0.95, "box": {...}}
    ]

    service = YOLOSCVService(model_loader=mock_loader)
    results = service.detect_objects(test_image)

    assert len(results) > 0
    assert "label" in results[0]
    assert "confidence_score" in results[0]

def test_filters_low_confidence_detections():
    service = YOLOSCVService(confidence_threshold=0.8)
    # Mock returns 0.5 confidence detection
    results = service.detect_objects(test_image)
    assert len(results) == 0
```

**Acceptance**: Service returns filtered, formatted detections

---

### 4.2 Image Service

#### Task 4.2.1: Create Image Repository Interface
**Objective**: Define data access interface (Repository Pattern)

**File**: `backend/src/services/image_repository.py`

**Steps**:
1. Create `ImageRepositoryInterface` ABC
2. Define abstract methods:
   - `create(image_data: dict) -> Image`
   - `get_by_id(image_id: UUID) -> Optional[Image]`
   - `update_status(image_id: UUID, status: str) -> Image`
   - `delete(image_id: UUID) -> bool`
3. Add docstrings

**Test**: Not directly testable (interface)

**Acceptance**: Clean repository interface

---

#### Task 4.2.2: Implement SQLAlchemy Image Repository
**Objective**: Concrete repository implementation

**File**: `backend/src/services/image_repository_impl.py`

**Steps**:
1. Create `ImageRepository` implementing interface
2. Inject `AsyncSession` via constructor
3. Implement `create()`:
   - Create Image ORM instance
   - Add to session
   - Commit and refresh
   - Handle unique constraint violations
4. Implement `get_by_id()` with async query
5. Implement `update_status()` with optimistic locking
6. Implement `delete()` with CASCADE handling
7. Add error handling and logging

**Test**: Create `tests/integration/test_image_repository.py`:
```python
@pytest.mark.asyncio
async def test_create_image(db_session):
    repo = ImageRepository(db_session)
    image_data = {
        "filename": "test.jpg",
        "storage_path": "/uploads/test.jpg",
        "file_size": 1024,
        "upload_timestamp": datetime.utcnow()
    }

    image = await repo.create(image_data)
    assert image.id is not None
    assert image.filename == "test.jpg"

@pytest.mark.asyncio
async def test_get_by_id_returns_none_if_not_found(db_session):
    repo = ImageRepository(db_session)
    result = await repo.get_by_id(uuid4())
    assert result is None
```

**Acceptance**: Repository performs all CRUD operations correctly

---

#### Task 4.2.3: Create Image Service
**Objective**: Business logic for image operations (Service Layer)

**File**: `backend/src/services/image_service.py`

**Steps**:
1. Create `ImageService` class
2. Inject `ImageRepository` and `FileStorage` via constructor
3. Implement `save_uploaded_image(file_bytes, filename, original_url)`:
   - Validate file
   - Save to storage via FileStorage
   - Create DB record via repository
   - Return ImageInDB schema
4. Implement `get_image(image_id: UUID) -> Optional[ImageInDB]`
5. Implement `delete_image(image_id: UUID)`:
   - Delete from storage
   - Delete from DB
   - Transaction handling
6. Add comprehensive error handling

**Test**: Create `tests/unit/test_image_service.py`:
```python
@pytest.mark.asyncio
async def test_save_uploaded_image_validates_file(mocker):
    mock_storage = mocker.Mock()
    mock_repo = mocker.Mock()
    service = ImageService(mock_repo, mock_storage)

    with pytest.raises(ValueError):
        await service.save_uploaded_image(
            file_bytes=b"data",
            filename="invalid.exe",
            original_url=None
        )

@pytest.mark.asyncio
async def test_delete_image_removes_file_and_record(mocker):
    service = ImageService(mock_repo, mock_storage)
    mock_storage.delete_file.return_value = True
    mock_repo.delete.return_value = True

    result = await service.delete_image(uuid4())
    assert result is True
```

**Acceptance**: Service orchestrates storage + repository correctly

---

### 4.3 Detection Service

#### Task 4.3.1: Create Detection Repository
**Objective**: Data access for detections

**File**: `backend/src/services/detection_repository.py`

**Steps**:
1. Create `DetectionRepository` class
2. Inject `AsyncSession`
3. Implement `create_many(detections: List[dict]) -> List[Detection]`:
   - Bulk insert
   - Return created records
4. Implement `get_by_image_id(image_id: UUID) -> List[Detection]`:
   - Query with filters
   - Order by confidence descending
5. Implement `get_paginated(page, page_size, filters) -> tuple`:
   - Return (items, total_count)
   - Support filtering by label, min_confidence
6. Implement `delete_by_image_id(image_id: UUID)`

**Test**: Create `tests/integration/test_detection_repository.py`:
```python
@pytest.mark.asyncio
async def test_create_many_inserts_all_detections(db_session):
    repo = DetectionRepository(db_session)
    detections = [
        {"label": "cat", "confidence_score": 0.95, ...},
        {"label": "dog", "confidence_score": 0.88, ...}
    ]

    result = await repo.create_many(detections)
    assert len(result) == 2

@pytest.mark.asyncio
async def test_get_by_image_id_filters_correctly(db_session):
    repo = DetectionRepository(db_session)
    # Create test data
    results = await repo.get_by_image_id(test_image_id)
    assert all(d.image_id == test_image_id for d in results)
```

**Acceptance**: Repository handles bulk operations and filtering

---

#### Task 4.3.2: Create Detection Service
**Objective**: Business logic for detection operations

**File**: `backend/src/services/detection_service.py`

**Steps**:
1. Create `DetectionService` class
2. Inject `DetectionRepository`, `CVServiceInterface`, `ImageRepository`
3. Implement `analyze_image(image_id: UUID) -> List[DetectionResponse]`:
   - Get image from DB
   - Get file from storage
   - Preprocess image
   - Run CV service
   - Save detections to DB
   - Update image status to "completed"
   - Return detection schemas
4. Implement `get_detections(image_id) -> List[DetectionResponse]`
5. Implement `get_all_paginated(page, size, filters) -> PaginatedResponse`
6. Add transaction handling and rollback on errors

**Test**: Create `tests/unit/test_detection_service.py`:
```python
@pytest.mark.asyncio
async def test_analyze_image_orchestrates_workflow(mocker):
    mock_cv = mocker.Mock()
    mock_cv.detect_objects.return_value = [
        {"label": "cat", "score": 0.95, "box": {...}}
    ]

    service = DetectionService(
        detection_repo=mock_det_repo,
        cv_service=mock_cv,
        image_repo=mock_img_repo
    )

    results = await service.analyze_image(test_image_id)

    assert len(results) > 0
    mock_img_repo.update_status.assert_called_with(
        test_image_id, "completed"
    )
```

**Acceptance**: Service coordinates CV analysis and persistence

---

## Phase 5: API Routes

### 5.1 Image Routes

#### Task 5.1.1: Create Image Upload Endpoint
**Objective**: POST endpoint to upload images

**File**: `backend/src/api/routes/images.py`

**Steps**:
1. Create router: `APIRouter(prefix="/api/v1/images", tags=["images"])`
2. Implement `POST /upload`:
   - Accept `UploadFile` (multipart/form-data)
   - Optional `original_url` query param
   - Inject `ImageService` dependency
   - Read file bytes
   - Call service.save_uploaded_image()
   - Return `ImageResponse` with 201 status
   - Handle file too large (413)
   - Handle invalid file type (415)
3. Add OpenAPI documentation
4. Add request validation

**Test**: Create `tests/integration/test_image_routes.py`:
```python
def test_upload_image_returns_201(client, test_image_file):
    response = client.post(
        "/api/v1/images/upload",
        files={"file": ("test.jpg", test_image_file, "image/jpeg")}
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["filename"] == "test.jpg"

def test_upload_rejects_invalid_extension(client):
    response = client.post(
        "/api/v1/images/upload",
        files={"file": ("test.exe", b"data", "application/x-executable")}
    )
    assert response.status_code == 415
```

**Acceptance**: Endpoint uploads files, validates input, returns proper errors

---

#### Task 5.1.2: Create Get Image Metadata Endpoint
**Objective**: GET endpoint to retrieve image info

**File**: `backend/src/api/routes/images.py`

**Steps**:
1. Implement `GET /{image_id}`:
   - Accept UUID path parameter
   - Inject ImageService
   - Call service.get_image()
   - Return ImageResponse or 404
2. Add OpenAPI docs
3. Validate UUID format

**Test**: Create test in `tests/integration/test_image_routes.py`:
```python
def test_get_image_returns_metadata(client, sample_image_id):
    response = client.get(f"/api/v1/images/{sample_image_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(sample_image_id)

def test_get_image_returns_404_if_not_found(client):
    response = client.get(f"/api/v1/images/{uuid4()}")
    assert response.status_code == 404
```

**Acceptance**: Endpoint retrieves image metadata correctly

---

#### Task 5.1.3: Create Download Image File Endpoint
**Objective**: GET endpoint to download original image

**File**: `backend/src/api/routes/images.py`

**Steps**:
1. Implement `GET /{image_id}/file`:
   - Get image metadata from DB
   - Retrieve file from storage
   - Return `FileResponse` with proper content-type
   - Set content-disposition header
   - Handle missing file (404)
2. Add streaming for large files

**Test**: Create test in `tests/integration/test_image_routes.py`:
```python
def test_download_image_file(client, sample_image_id):
    response = client.get(f"/api/v1/images/{sample_image_id}/file")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/")
    assert len(response.content) > 0
```

**Acceptance**: Endpoint streams file with correct headers

---

#### Task 5.1.4: Create Delete Image Endpoint
**Objective**: DELETE endpoint to remove image

**File**: `backend/src/api/routes/images.py`

**Steps**:
1. Implement `DELETE /{image_id}`:
   - Inject ImageService
   - Call service.delete_image()
   - Return 204 No Content
   - Return 404 if not found
2. Verify cascade deletes detections

**Test**: Create test in `tests/integration/test_image_routes.py`:
```python
def test_delete_image_removes_file_and_db_record(client, sample_image_id):
    response = client.delete(f"/api/v1/images/{sample_image_id}")
    assert response.status_code == 204

    # Verify deleted
    get_response = client.get(f"/api/v1/images/{sample_image_id}")
    assert get_response.status_code == 404
```

**Acceptance**: Endpoint deletes image and cascades to detections

---

### 5.2 Detection Routes

#### Task 5.2.1: Create Analyze Image Endpoint
**Objective**: POST endpoint to trigger CV analysis (synchronous MVP version)

**File**: `backend/src/api/routes/detections.py`

**Steps**:
1. Create router: `APIRouter(prefix="/api/v1/detections", tags=["detections"])`
2. Implement `POST /analyze/{image_id}`:
   - Accept image_id path param
   - Inject DetectionService
   - Call service.analyze_image()
   - Return List[DetectionResponse] with 200
   - Handle image not found (404)
   - Handle analysis errors (500)
   - Add timeout handling (30s)
3. Add OpenAPI documentation

**Test**: Create `tests/integration/test_detection_routes.py`:
```python
@pytest.mark.slow
def test_analyze_image_returns_detections(client, sample_image_id):
    response = client.post(f"/api/v1/detections/analyze/{sample_image_id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "label" in data[0]
        assert "confidence_score" in data[0]

def test_analyze_returns_404_for_invalid_image(client):
    response = client.post(f"/api/v1/detections/analyze/{uuid4()}")
    assert response.status_code == 404
```

**Acceptance**: Endpoint triggers analysis and returns results

---

#### Task 5.2.2: Create Get Detections by Image Endpoint
**Objective**: GET endpoint to retrieve detections for an image

**File**: `backend/src/api/routes/detections.py`

**Steps**:
1. Implement `GET /{image_id}`:
   - Accept image_id path param
   - Inject DetectionService
   - Call service.get_detections()
   - Return List[DetectionResponse]
   - Return empty list if no detections
2. Add OpenAPI docs

**Test**: Create test in `tests/integration/test_detection_routes.py`:
```python
def test_get_detections_returns_list(client, image_with_detections_id):
    response = client.get(f"/api/v1/detections/{image_with_detections_id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
```

**Acceptance**: Endpoint retrieves detections for specific image

---

#### Task 5.2.3: Create List All Detections Endpoint
**Objective**: GET endpoint with pagination and filtering

**File**: `backend/src/api/routes/detections.py`

**Steps**:
1. Implement `GET /`:
   - Query params: page (default 1), page_size (default 20)
   - Optional filters: label, min_confidence
   - Inject DetectionService
   - Call service.get_all_paginated()
   - Return PaginatedResponse[DetectionResponse]
2. Validate page and page_size ranges
3. Add OpenAPI docs with examples

**Test**: Create test in `tests/integration/test_detection_routes.py`:
```python
def test_list_detections_returns_paginated(client):
    response = client.get("/api/v1/detections?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data

def test_list_detections_filters_by_label(client):
    response = client.get("/api/v1/detections?label=cat")
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["label"] == "cat"
```

**Acceptance**: Endpoint returns paginated, filterable results

---

## Phase 6: Integration & End-to-End Testing

#### Task 6.1: Create E2E Test Fixtures
**Objective**: Set up test database and sample data

**File**: `backend/tests/conftest.py`

**Steps**:
1. Create `test_db` fixture with test database URL
2. Create `db_session` fixture that:
   - Creates tables before tests
   - Provides clean session
   - Rolls back after tests
3. Create `client` fixture (TestClient)
4. Create `sample_image` fixture with test JPEG
5. Create `sample_image_id` fixture (uploaded test image)
6. Add cleanup fixtures

**Test**: Run `uv run pytest tests/ -v` to verify fixtures work

**Acceptance**: All fixtures reusable across test files

---

#### Task 6.2: Write E2E Upload-Analyze-Retrieve Flow Test
**Objective**: Test complete user workflow

**File**: `backend/tests/integration/test_e2e_workflow.py`

**Steps**:
1. Test uploads image
2. Verifies image metadata returned
3. Triggers analysis
4. Verifies detections returned
5. Retrieves detections again via GET
6. Downloads image file
7. Deletes image
8. Verifies cascade deletion of detections

**Test**: The test itself is the deliverable

**Acceptance**: Complete workflow executes successfully

---

#### Task 6.3: Write Performance Test for Analysis
**Objective**: Ensure analysis completes within acceptable time

**File**: `backend/tests/integration/test_performance.py`

**Steps**:
1. Create test with large image (max allowed size)
2. Measure analysis time
3. Assert completes within 10 seconds
4. Test concurrent requests (3 simultaneous analyses)
5. Verify no race conditions

**Test**: The test itself is the deliverable

**Acceptance**: Analysis meets performance SLA

---

## Phase 7: Docker Configuration

### 7.1 Backend Docker Setup

#### Task 7.1.1: Create Backend Dockerfile
**Objective**: Multi-stage Docker build for backend

**File**: `backend/Dockerfile`

**Steps**:
1. **Stage 1: Builder**
   - Base: `python:3.12-slim`
   - Install uv: `pip install uv`
   - Copy `pyproject.toml` and `uv.lock`
   - Run `uv sync --frozen --no-dev`
2. **Stage 2: Runtime**
   - Base: `python:3.12-slim`
   - Install curl (for healthcheck)
   - Create non-root user `appuser`
   - Copy .venv from builder
   - Copy application code
   - Set working directory `/app`
   - Expose port 8000
   - Set environment: `PYTHONUNBUFFERED=1`
   - CMD: `["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]`
3. Add HEALTHCHECK instruction

**Test**: Build image: `docker build -t cv-backend:test ./backend`

**Acceptance**: Image builds successfully, size < 800MB

---

#### Task 7.1.2: Create Backend .dockerignore
**Objective**: Exclude unnecessary files from image

**File**: `backend/.dockerignore`

**Steps**:
1. Add: `__pycache__`, `*.pyc`, `.pytest_cache`, `.coverage`
2. Add: `tests/`, `*.md`, `.env`
3. Add: `storage/` (volume mounted)
4. Add: `.git/`, `.vscode/`

**Test**: Rebuild image, verify smaller size

**Acceptance**: Image excludes dev files

---

#### Task 7.1.3: Create Development Docker Compose Override
**Objective**: Hot reload for development

**File**: `docker-compose.dev.yml`

**Steps**:
1. Override backend service:
   - Mount `./backend/src:/app/src` (code reload)
   - Add environment: `DEBUG=true`
   - Command with `--reload` flag
2. Add volumes for tests
3. Expose additional ports for debugging

**Test**: `docker-compose -f docker-compose.yml -f docker-compose.dev.yml up backend`

**Acceptance**: Code changes trigger reload

---

### 7.2 Database & Redis Setup

#### Task 7.2.1: Create PostgreSQL Service in Docker Compose
**Objective**: Containerized database

**File**: `docker-compose.yml`

**Steps**:
1. Add `db` service:
   - Image: `postgres:16-alpine`
   - Environment: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
   - Volume: `postgres_data:/var/lib/postgresql/data`
   - Healthcheck: `pg_isready -U cvision`
   - Networks: internal

**Test**: `docker-compose up db`, verify accessible

**Acceptance**: Database starts and passes healthcheck

---

#### Task 7.2.2: Create Redis Service in Docker Compose
**Objective**: Containerized cache/queue

**File**: `docker-compose.yml`

**Steps**:
1. Add `redis` service:
   - Image: `redis:7-alpine`
   - Volume: `redis_data:/data` (optional persistence)
   - Healthcheck: `redis-cli ping`
   - Command: `redis-server --appendonly yes`

**Test**: `docker-compose up redis`, verify accessible

**Acceptance**: Redis starts and responds to PING

---

#### Task 7.2.3: Wire Backend to Database and Redis
**Objective**: Connect services via Docker network

**File**: `docker-compose.yml`

**Steps**:
1. Update backend service:
   - `depends_on`: db (with condition: service_healthy), redis
   - Environment: `DATABASE_URL=postgresql://cvision:${DB_PASSWORD}@db:5432/cvision`
   - Environment: `REDIS_URL=redis://redis:6379/0`
   - Volumes: `./backend/storage:/app/storage`, `model_cache:/app/models`
2. Add healthcheck for backend
3. Define named volumes

**Test**: `docker-compose up`, verify backend connects to DB

**Acceptance**: Backend starts successfully, migrations run

---

### 7.3 Frontend Setup (Minimal for MVP)

#### Task 7.3.1: Initialize Frontend Project
**Objective**: Create React + Vite project

**Steps**:
1. Create `frontend/` directory
2. Run: `npm create vite@latest . -- --template react-ts`
3. Install dependencies: `npm install`
4. Add TailwindCSS: `npm install -D tailwindcss postcss autoprefixer`
5. Init Tailwind: `npx tailwindcss init -p`
6. Configure `tailwind.config.js` with content paths
7. Add Tailwind directives to `src/index.css`

**Test**: `npm run dev` starts dev server

**Acceptance**: Frontend runs on localhost:5173

---

#### Task 7.3.2: Add Frontend Dependencies
**Objective**: Install required libraries

**Steps**:
1. Add Axios: `npm install axios`
2. Add TanStack Query: `npm install @tanstack/react-query`
3. Add React Router: `npm install react-router-dom`
4. Add Zustand: `npm install zustand`
5. Add React Dropzone: `npm install react-dropzone`

**Test**: Verify imports work

**Acceptance**: All dependencies installed

---

#### Task 7.3.3: Create Frontend Dockerfile
**Objective**: Multi-stage build for production

**File**: `frontend/Dockerfile`

**Steps**:
1. **Stage 1: Builder**
   - Base: `node:20-alpine`
   - Copy `package*.json`
   - Run `npm ci`
   - Copy source code
   - Run `npm run build`
2. **Stage 2: Nginx**
   - Base: `nginx:alpine`
   - Copy build output: `COPY --from=builder /app/dist /usr/share/nginx/html`
   - Copy nginx config
   - Expose 80

**Test**: Build image: `docker build -t cv-frontend:test ./frontend`

**Acceptance**: Image builds, size < 50MB

---

#### Task 7.3.4: Create Nginx Configuration
**Objective**: Serve SPA with proper routing

**File**: `frontend/nginx.conf`

**Steps**:
1. Configure server block:
   - Listen on port 80
   - Root: `/usr/share/nginx/html`
   - Index: `index.html`
2. Add location for SPA routing:
   ```nginx
   location / {
       try_files $uri $uri/ /index.html;
   }
   ```
3. Add cache headers for static assets
4. Gzip compression

**Test**: Deploy frontend container, test routing

**Acceptance**: SPA routes work correctly

---

### 7.4 Nginx Reverse Proxy

#### Task 7.4.1: Create Nginx Reverse Proxy Configuration
**Objective**: Route traffic to backend and frontend

**File**: `nginx/default.conf`

**Steps**:
1. Create upstream for backend: `upstream backend { server backend:8000; }`
2. Create upstream for frontend: `upstream frontend { server frontend:80; }`
3. Configure server block:
   - Listen 80
   - Location `/api/`: proxy to backend
   - Location `/`: proxy to frontend
4. Add proxy headers: Host, X-Real-IP, X-Forwarded-For
5. Add CORS headers
6. Add rate limiting

**Test**: Access via `http://localhost`, verify routing

**Acceptance**: Requests routed correctly to services

---

#### Task 7.4.2: Add Nginx Service to Docker Compose
**Objective**: Integrate reverse proxy

**File**: `docker-compose.yml`

**Steps**:
1. Add `nginx` service:
   - Image: `nginx:alpine`
   - Ports: `80:80`, `443:443`
   - Volumes: mount config files
   - Depends on: backend, frontend
2. Configure networks

**Test**: `docker-compose up`, access `http://localhost`

**Acceptance**: All services accessible via nginx

---

## Phase 8: Frontend Implementation (MVP Features)

### 8.1 Core Setup

#### Task 8.1.1: Create API Client Service
**Objective**: Centralized API communication

**File**: `frontend/src/services/api.ts`

**Steps**:
1. Create Axios instance with baseURL from env
2. Add request interceptor (correlation ID)
3. Add response interceptor (error handling)
4. Define API methods:
   - `uploadImage(file: File, originalUrl?: string)`
   - `getImage(imageId: string)`
   - `analyzeImage(imageId: string)`
   - `getDetections(imageId: string)`
   - `deleteImage(imageId: string)`
5. Add TypeScript types

**Test**: Create `src/services/api.test.ts` with mocked Axios

**Acceptance**: API client reusable, typed

---

#### Task 8.1.2: Create TypeScript Types
**Objective**: Type definitions matching backend schemas

**File**: `frontend/src/types/image.ts` and `frontend/src/types/detection.ts`

**Steps**:
1. Define `Image` interface
2. Define `Detection` interface
3. Define `BoundingBox` interface
4. Define `ApiError` interface
5. Export all types

**Test**: TypeScript compiles without errors

**Acceptance**: Types match backend schemas

---

#### Task 8.1.3: Create Zustand Store
**Objective**: Global state management

**File**: `frontend/src/store/appStore.ts`

**Steps**:
1. Define `AppState` interface
2. Create store with zustand:
   - State: currentImage, detections, isLoading, error, uploadProgress
   - Actions: setCurrentImage, setDetections, setLoading, setError, setUploadProgress, reset
3. Add persistence (optional)

**Test**: Create component that uses store, verify state updates

**Acceptance**: Store accessible across components

---

#### Task 8.1.4: Setup TanStack Query
**Objective**: Configure query client

**File**: `frontend/src/main.tsx`

**Steps**:
1. Import `QueryClient`, `QueryClientProvider`
2. Create client with config:
   - Stale time: 5 minutes
   - Retry: 3 times
   - Error handling
3. Wrap `<App>` with provider

**Test**: App renders without errors

**Acceptance**: Query client available

---

### 8.2 Common Components

#### Task 8.2.1: Create Button Component
**Objective**: Reusable button with variants

**File**: `frontend/src/components/common/Button.tsx`

**Steps**:
1. Create `Button` component with props: variant, size, disabled, loading, onClick
2. Style variants: primary, secondary, danger
3. Add loading spinner state
4. Add disabled styles
5. TypeScript props interface

**Test**: Storybook or visual test

**Acceptance**: Button renders all variants

---

#### Task 8.2.2: Create Spinner Component
**Objective**: Loading indicator

**File**: `frontend/src/components/common/Spinner.tsx`

**Steps**:
1. Create animated spinner with Tailwind
2. Props: size, color
3. Accessible (aria-label)

**Test**: Visual test

**Acceptance**: Spinner animates smoothly

---

#### Task 8.2.3: Create Error Boundary Component
**Objective**: Catch React errors gracefully

**File**: `frontend/src/components/common/ErrorBoundary.tsx`

**Steps**:
1. Create class component extending `React.Component`
2. Implement `componentDidCatch()` to log errors
3. Implement `getDerivedStateFromError()` to update state
4. Render fallback UI on error
5. Add reset button

**Test**: Trigger error in child component, verify boundary catches

**Acceptance**: App doesn't crash on errors

---

#### Task 8.2.4: Create Layout Components
**Objective**: Page structure components

**Files**: `frontend/src/components/layout/Header.tsx`, `Footer.tsx`, `Layout.tsx`

**Steps**:
1. Create `Header` with logo and title
2. Create `Footer` with credits
3. Create `Layout` that wraps pages with header/footer
4. Style with Tailwind
5. Make responsive

**Test**: Visual test

**Acceptance**: Layout renders correctly

---

### 8.3 Upload Feature

#### Task 8.3.1: Create Image Upload Hook
**Objective**: Encapsulate upload logic

**File**: `frontend/src/hooks/useImageUpload.ts`

**Steps**:
1. Use `useMutation` from TanStack Query
2. Call `uploadImage` API method
3. Track upload progress
4. Update Zustand store on success
5. Handle errors
6. Return: `upload` function, `isUploading`, `progress`, `error`

**Test**: Create test with mocked API

**Acceptance**: Hook manages upload state

---

#### Task 8.3.2: Create Image Uploader Component
**Objective**: Drag-and-drop upload UI

**File**: `frontend/src/components/upload/ImageUploader.tsx`

**Steps**:
1. Use `react-dropzone` for drag-and-drop
2. Accept only image files
3. Validate file size (max 10MB)
4. Show preview thumbnail
5. Display upload progress bar
6. Show error messages
7. Call `useImageUpload` hook
8. Redirect to results on success

**Test**: Integration test with mocked upload

**Acceptance**: User can upload images via drag-and-drop

---

#### Task 8.3.3: Create Upload Progress Component
**Objective**: Visual progress indicator

**File**: `frontend/src/components/upload/UploadProgress.tsx`

**Steps**:
1. Accept `progress` prop (0-100)
2. Render progress bar
3. Show percentage
4. Animate smoothly
5. Style with Tailwind

**Test**: Visual test with different progress values

**Acceptance**: Progress bar updates smoothly

---

### 8.4 Results Display

#### Task 8.4.1: Create Detection Results Component
**Objective**: Display detections list and image

**File**: `frontend/src/components/results/DetectionResults.tsx`

**Steps**:
1. Accept `imageId` prop
2. Fetch detections using TanStack Query
3. Display image with canvas overlay
4. Render bounding boxes on canvas
5. Show list of detections below
6. Handle loading and error states
7. Add "Analyze" button if not analyzed yet

**Test**: Render with mock data

**Acceptance**: Component displays detections correctly

---

#### Task 8.4.2: Create Bounding Box Canvas Component
**Objective**: Draw boxes on image

**File**: `frontend/src/components/results/BoundingBox.tsx`

**Steps**:
1. Use HTML5 canvas
2. Accept `image` and `detections` props
3. Draw image on canvas
4. Draw colored rectangles for each detection
5. Add labels with confidence scores
6. Make boxes color-coded by confidence
7. Handle responsive sizing

**Test**: Visual test with sample detections

**Acceptance**: Boxes drawn accurately on image

---

#### Task 8.4.3: Create Detection List Component
**Objective**: Table view of detections

**File**: `frontend/src/components/results/DetectionList.tsx`

**Steps**:
1. Accept `detections` prop
2. Render table with columns: Label, Confidence, Coordinates
3. Sort by confidence (desc)
4. Format confidence as percentage
5. Style with Tailwind
6. Make responsive (cards on mobile)

**Test**: Render with various detection lists

**Acceptance**: Table displays all detection data

---

### 8.5 Pages

#### Task 8.5.1: Create Home Page
**Objective**: Landing page with upload

**File**: `frontend/src/pages/Home.tsx`

**Steps**:
1. Import Layout and ImageUploader
2. Add title and instructions
3. Center uploader
4. Add example images section (optional)
5. Style with Tailwind

**Test**: Visual and interaction test

**Acceptance**: User can upload from home page

---

#### Task 8.5.2: Create Results Page
**Objective**: Display analysis results

**File**: `frontend/src/pages/Results.tsx`

**Steps**:
1. Get `imageId` from URL params
2. Import DetectionResults component
3. Add back button to home
4. Add delete button
5. Handle image not found
6. Add loading state while analyzing

**Test**: Navigation test

**Acceptance**: Results display after upload

---

#### Task 8.5.3: Setup React Router
**Objective**: Configure routing

**File**: `frontend/src/App.tsx`

**Steps**:
1. Import `BrowserRouter`, `Routes`, `Route`
2. Define routes:
   - `/` → Home
   - `/results/:imageId` → Results
3. Wrap with ErrorBoundary
4. Add 404 page

**Test**: Navigate between routes

**Acceptance**: Routing works correctly

---

#### Task 8.5.4: Create Analyze Hook with Polling
**Objective**: Trigger analysis and wait for results (for future async implementation)

**File**: `frontend/src/hooks/useAnalyze.ts`

**Steps**:
1. Use `useMutation` for analyze call
2. Use `useQuery` with `refetchInterval` for polling
3. Stop polling when status is "completed"
4. Handle errors and timeouts
5. Return: `analyze` function, `isAnalyzing`, `detections`, `error`

**Test**: Mock async analysis

**Acceptance**: Hook handles async analysis flow

---

## Phase 9: Integration & Testing

#### Task 9.1: Test Full Stack Locally with Docker
**Objective**: Verify all services work together

**Steps**:
1. Run `docker-compose up --build`
2. Access frontend at `http://localhost`
3. Upload an image
4. Verify analysis runs
5. Check detections display
6. Delete image
7. Check logs for errors

**Test**: Manual E2E test

**Acceptance**: Complete workflow functions

---

#### Task 9.2: Write Frontend E2E Tests
**Objective**: Automated user flow tests

**File**: `frontend/tests/e2e/upload-flow.spec.ts`

**Steps**:
1. Setup Playwright
2. Test: Navigate to home
3. Test: Upload image
4. Test: Wait for analysis
5. Test: Verify detections shown
6. Test: Delete image

**Test**: `npm run test:e2e`

**Acceptance**: E2E tests pass

---

#### Task 9.3: Performance Test Full Stack
**Objective**: Verify system meets performance requirements

**Steps**:
1. Upload 10 images concurrently
2. Measure response times
3. Check memory usage (backend < 1GB)
4. Verify no crashes
5. Check database connections don't leak

**Test**: Load testing script

**Acceptance**: System handles concurrent requests

---

## Phase 10: Documentation & Deployment Prep

#### Task 10.1: Update README with Setup Instructions
**Objective**: Document how to run the project

**File**: `README.md`

**Steps**:
1. Add prerequisites section
2. Add setup instructions (uv, Docker)
3. Add development commands
4. Add production deployment steps
5. Add API documentation link
6. Add troubleshooting section

**Test**: Fresh clone, follow README

**Acceptance**: New dev can set up project

---

#### Task 10.2: Create Environment Variables Documentation
**Objective**: Document all configuration options

**File**: `docs/environment-variables.md`

**Steps**:
1. List all backend variables with descriptions
2. List all frontend variables
3. Provide example values
4. Note which are required vs optional
5. Document defaults

**Test**: Review accuracy

**Acceptance**: All variables documented

---

#### Task 10.3: Generate API Documentation
**Objective**: Auto-generate OpenAPI docs

**Steps**:
1. Ensure all endpoints have docstrings
2. Add response models to decorators
3. Add example responses
4. Access Swagger UI at `/docs`
5. Export OpenAPI JSON

**Test**: Visit `/docs`, verify completeness

**Acceptance**: API fully documented

---

#### Task 10.4: Create Docker Compose Production Config
**Objective**: Production-ready compose file

**File**: `docker-compose.prod.yml`

**Steps**:
1. Remove volume mounts for code
2. Add resource limits (memory, CPU)
3. Add restart policies: `always`
4. Configure logging drivers
5. Add healthchecks to all services
6. Use secrets for passwords
7. Add nginx SSL configuration

**Test**: Deploy to staging environment

**Acceptance**: Production config ready

---

#### Task 10.5: Create Backup Script for Database
**Objective**: Automate database backups

**File**: `scripts/backup-db.sh`

**Steps**:
1. Use `pg_dump` to export database
2. Compress with gzip
3. Add timestamp to filename
4. Upload to backup location (S3, etc.)
5. Retain last 7 backups
6. Add cron job instructions

**Test**: Run script, verify backup created

**Acceptance**: Backups automated

---

## Phase 11: Optional Enhancements (Post-MVP)

#### Task 11.1: Implement Celery for Async Processing
**Objective**: Offload analysis to background workers

**Steps**:
1. Add Celery dependencies: `uv add celery`
2. Create `src/tasks/celery_app.py` with Celery config
3. Create task: `analyze_image_task(image_id)`
4. Update DetectionService to queue task
5. Return job ID to frontend
6. Implement job status endpoint
7. Update frontend to poll for status

**Test**: Queue multiple analyses, verify parallel processing

**Acceptance**: Analysis runs asynchronously

---

#### Task 11.2: Add Image Thumbnail Generation
**Objective**: Generate thumbnails for faster loading

**Steps**:
1. Add thumbnail generation to ImageService
2. Store thumbnail path in database
3. Add endpoint to serve thumbnails
4. Update frontend to show thumbnails in lists
5. Lazy load full images

**Test**: Verify thumbnails generated

**Acceptance**: Page loads faster

---

#### Task 11.3: Implement Redis Caching for Detections
**Objective**: Cache frequent queries

**Steps**:
1. Add caching layer to DetectionRepository
2. Cache detection results by image_id
3. Set TTL: 1 hour
4. Invalidate on update/delete
5. Add cache hit metrics

**Test**: Measure cache hit rate

**Acceptance**: Reduced DB load

---

#### Task 11.4: Add User Authentication (JWT)
**Objective**: Secure API with user accounts

**Steps**:
1. Create User model
2. Add password hashing
3. Implement JWT token generation
4. Add auth middleware
5. Protect endpoints
6. Update frontend with login flow

**Test**: Verify unauthorized access blocked

**Acceptance**: API secured

---

#### Task 11.5: Implement Model Hot-Swapping
**Objective**: Switch detection models without restart

**Steps**:
1. Add model name to analysis request
2. Update ModelLoader to support multiple models
3. Load models on-demand
4. Add model management endpoints
5. Update frontend with model selector

**Test**: Switch models and verify results differ

**Acceptance**: Multiple models supported

---

## Summary

**Total Tasks**: 110+ granular, testable tasks

**Estimated Timeline**:
- Phase 1-3 (Setup & Core): 1 week
- Phase 4-5 (Services & API): 1 week
- Phase 6-7 (Testing & Docker): 3-4 days
- Phase 8 (Frontend): 1 week
- Phase 9-10 (Integration & Docs): 2-3 days
- **Total MVP**: ~3-4 weeks for solo developer

**Key Principles Applied**:
- Single Responsibility (each task has one concern)
- Dependency Injection (services receive dependencies)
- Repository Pattern (data access abstraction)
- Interface Segregation (service interfaces)
- Test-Driven Development (test after each task)
- Clean Architecture (layered separation)

**Testing Strategy**:
- Unit tests for utils, services, schemas
- Integration tests for repositories, routes
- E2E tests for complete workflows
- Performance tests for scalability

**Deliverables**:
- Production-ready backend API
- Modern React frontend
- Dockerized deployment
- Complete test coverage
- Full documentation
