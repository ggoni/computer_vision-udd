# Computer Vision Detection API

![CI](https://github.com/ggoni/computer_vision-udd/actions/workflows/ci.yml/badge.svg)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)
[![Tests](https://img.shields.io/badge/tests-106%20passing-success.svg)](#running-tests)
[![Coverage](https://img.shields.io/badge/coverage-72%25-yellow.svg)](#running-tests)

FastAPI-based backend providing image upload, object detection analysis, and persistent storage for computer vision applications.

## Quick Start

### Docker Deployment (Recommended)
```bash
# Clone the repository
git clone https://github.com/ggoni/computer_vision-udd.git
cd computer_vision-udd

# Start all services
docker compose up -d

# Wait for services to start (30-60 seconds)
# Then access the application
```

**🌐 Access Points:**
- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health
- **PostgreSQL**: localhost:5432 (cvuser/cvpass123)

### What Gets Started
- ✅ **Frontend**: React application for image upload and visualization
- ✅ **Backend**: FastAPI server with YOLO object detection  
- ✅ **Database**: PostgreSQL for metadata storage
- ✅ **Persistent Storage**: Local bind mount for uploaded images

### Quick Commands
```bash
# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Stop services
docker compose down

# Check running services
docker compose ps

# Test the API
curl http://localhost:8000/health/
curl http://localhost:8000/api/v1/images/
```

### Upload an Image
```bash
# Via API
curl -F "file=@/path/to/image.jpg" http://localhost:8000/api/v1/images/upload

# Via Frontend
# Open http://localhost:3000 in your browser
```

### Data Persistence
- **Images**: Stored in `./storage/uploads/` (persists between container restarts)
- **Database**: PostgreSQL data in Docker volume `postgres_data`
- **ML Models**: Cached in Docker volume `model_cache`

---

## Alternative Setup Methods

### Development Setup (For Contributors)

### Prerequisites
- Python 3.12+ with [uv](https://github.com/astral-sh/uv) installed
- Node.js 18+ with npm
- PostgreSQL 15+ running locally or via Docker

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/ggoni/computer_vision-udd.git
   cd computer_vision-udd
   ```

2. **Set up the database**
   ```bash
   # Using Docker (recommended)
   docker run --name cv-postgres -e POSTGRES_USER=cvuser -e POSTGRES_PASSWORD=cvpass123 -e POSTGRES_DB=computer_vision_db -p 5432:5432 -d postgres:16-alpine
   
   # Or install PostgreSQL locally and create database
   createdb computer_vision_db
   ```

3. **Start the backend**
   ```bash
   cd backend
   
   # Install dependencies
   uv sync --group dev
   
   # Set environment variables
   export DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/cv_db"
   export APP_ENV="development"
   
   # Initialize database schema
   uv run python scripts/init_db.py
   
   # Start the server (set PYTHONPATH to include current directory)
   PYTHONPATH=. uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Start the frontend** (in a new terminal)
   ```bash
   cd frontend
   
   # Install dependencies
   npm install
   
   # Start development server
   npm run dev
   ```

5. **Open the application**
   - Frontend: http://localhost:5173 (development server)
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Management Commands

#### Docker Commands
```bash
# Start all services
docker-compose up -d

# Stop all services  
docker-compose down

# View service status
docker-compose ps

# View logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild after code changes
docker-compose up -d --build

# Remove everything (including data)
docker-compose down -v
```

#### Advanced Management (Optional)
```bash
# Use the management script for advanced features
./scripts/mlops.sh start-prod    # Alternative Docker setup
./scripts/mlops.sh health        # Health checks
./scripts/mlops.sh logs api      # Detailed logging
./scripts/test-integration.sh    # Run integration tests
```

---

## Simple Docker Deployment

For a basic containerized deployment without the full MLOps stack:

```bash
# Start basic services
docker-compose -f docker-compose.production.yml up -d

# Check services
docker-compose -f docker-compose.production.yml ps

# Stop services
docker-compose -f docker-compose.production.yml down
```

This provides the core application (API + Frontend + Database) without monitoring services.

---

## Usage Guide

### Using the Web Interface

#### 1. Upload Images
- Navigate to the **Upload** page (default home page)
- Click "Choose file" and select an image (JPEG, PNG, WebP supported)
- Click "Upload Image" to upload
- The image metadata will be displayed after successful upload

#### 2. Browse Images
- Go to the **Images** page to see all uploaded images
- Use filters to search by filename or status
- Navigate between pages using pagination controls
- Click on any image ID to view details

#### 3. Image Analysis
- From the **Image Detail** page, click "Analyze Image"
- The system will run YOLO object detection
- Detected objects will be overlaid on the image with bounding boxes
- Toggle the overlay on/off with the "Toggle Overlay" button
- Each detection shows label and confidence score

#### 4. Browse All Detections
- Visit the **Detections** page for a global view of all detections
- Filter by object label (e.g., "person", "car", "dog")
- Filter by minimum confidence score
- See which image each detection belongs to

### Using the API Directly

#### Upload an Image
```bash
curl -X POST "http://localhost:8000/api/v1/images/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_image.jpg"
```

#### Analyze Image for Objects
```bash
# Replace {image_id} with actual ID from upload response
curl -X POST "http://localhost:8000/api/v1/images/{image_id}/analyze" \
  -H "accept: application/json"
```

#### Get All Images (Paginated)
```bash
curl "http://localhost:8000/api/v1/images?page=1&page_size=10"
```

#### Get Detections with Filters
```bash
# Get all detections for "person" with confidence > 80%
curl "http://localhost:8000/api/v1/detections?label=person&min_confidence=0.8"
```

#### Download Image File
```bash
curl "http://localhost:8000/api/v1/images/{image_id}/file" --output downloaded_image.jpg
```

### Configuration

#### Backend Environment Variables
```bash
# Required
DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/cv_db"

# Optional (with defaults)
APP_ENV="development"                    # development, production, test
UPLOAD_DIR="./uploads"                   # File storage directory
MAX_FILE_SIZE=5242880                    # 5MB in bytes
ALLOWED_EXTENSIONS="jpg,jpeg,png,webp"   # Comma-separated
MODEL_NAME="hustvl/yolos-tiny"          # Hugging Face model
```

#### Frontend Configuration
Create `frontend/.env` for custom API URL:
```bash
VITE_API_BASE_URL=http://localhost:8000
```

---

## MLOps Configuration

### Environment Variables (.env)
Copy `.env.template` to `.env` and customize:

#### Essential Settings
```bash
# Database
DATABASE_URL=postgresql+asyncpg://cvuser:cvpass123@postgres:5432/computer_vision_db

# ML Model  
MODEL_NAME=hustvl/yolos-tiny
CONFIDENCE_THRESHOLD=0.5

# Security
SECRET_KEY=your-secret-key-here

# Monitoring
PROMETHEUS_METRICS=true
GRAFANA_ADMIN_PASSWORD=grafana123
```

#### Optional Cloud Storage (Production)
```bash
# AWS S3
AWS_REGION=us-west-2
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret

# Google Cloud Storage
GOOGLE_CLOUD_PROJECT=your-project-id
GCS_BUCKET=cv-production-bucket

# MinIO (Default for local/development)
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minio123456
```

### Monitoring Dashboards

#### Grafana Dashboards (localhost:3001)
- **MLOps Dashboard**: API metrics, model performance, inference time
- **Infrastructure Dashboard**: Resource usage, service health, database metrics

#### Custom Metrics Available
- `http_requests_total`: API request counts by endpoint
- `model_inference_duration_seconds`: Model inference latency  
- `model_prediction_confidence`: Model confidence score distribution
- `detected_objects_total`: Object detection counts by class
- `image_uploads_total`: Image upload rate

#### Alerting Rules
- High API latency (>2s 95th percentile)
- High error rate (>10% 5xx responses)  
- Low model confidence (<0.3 median)
- Resource exhaustion (>80% memory/CPU)
- Database slow queries (>1s average)

### Backup & Maintenance
```bash
# Backup all data
./scripts/mlops.sh backup

# Update containers
./scripts/mlops.sh update

# Clean unused resources  
./scripts/mlops.sh cleanup

# View service status
./scripts/mlops.sh status
```

---

## File Storage & Model Information
### File Storage
- **Development**: Images stored in `uploads/YYYY/MM/DD/` directory structure  
- **Production**: MinIO object storage with S3-compatible API
- **Security**: Filenames include content hash for deduplication: `abc123_original_name.jpg`
- **Integrity**: File verification via SHA256 hashing
- **Collision**: Automatic suffix addition if filename conflicts occur

### Model Information
- Uses **YOLO-tiny** model from Hugging Face (`hustvl/yolos-tiny`)
- **Performance**: First analysis may take longer due to model download (~100MB)
- **Caching**: Model cached locally in `~/.cache/huggingface/` or Docker volumes
- **Classes**: Supports 80+ object classes from COCO dataset
- **Filtering**: Confidence threshold configurable (UI default shows >0.1)
- **Alternative Models**: Easily switch to `hustvl/yolos-small` or `hustvl/yolos-base`

---

## Troubleshooting

### Troubleshooting

#### Quick Fixes
```bash
# If services won't start
docker-compose down
docker-compose up -d

# If you see permission errors
sudo chown -R $USER:$USER ./storage

# If frontend shows connection errors
# Wait 60 seconds for backend to download the ML model on first run

# Check service health
curl http://localhost:8000/health
```

#### Common Issues
- **Services won't start**: Check Docker has enough memory (4GB+ recommended)
- **Model download slow**: First run downloads ~100MB YOLO model, subsequent runs are fast
- **Can't access frontend**: Wait for all services to be healthy (`docker-compose ps`)
- **Database errors**: Ensure no other PostgreSQL is running on port 5432

## Architecture

### Development Structure

#### Backend
```
backend/
├── src/
│   ├── api/routes/          # FastAPI route handlers
│   ├── core/                # Configuration and logging
│   ├── db/                  # Database models and session management
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic request/response models
│   ├── services/            # Business logic layer
│   └── utils/               # File storage, image processing, model loading
├── tests/
│   ├── integration/         # API endpoint tests
│   └── unit/               # Service and utility tests
└── scripts/                # Database initialization
```

#### Frontend
```
frontend/
├── src/
│   ├── api/                # API client and type definitions
│   ├── auth/               # Authentication context
│   ├── components/         # Reusable UI components
│   ├── pages/              # Route components
│   └── __tests__/          # Component and page tests
├── public/                 # Static assets
└── dist/                   # Build output
```

### MLOps Platform Structure

#### Infrastructure Services
- **API Service**: FastAPI with Prometheus metrics
- **Frontend**: Production React build with Nginx  
- **Database**: PostgreSQL with performance tuning
- **Storage**: MinIO S3-compatible object storage
- **Cache**: Redis for caching and job queuing
- **Reverse Proxy**: Nginx with rate limiting

#### MLOps Services  
- **Training Service**: PyTorch + MLflow + Optuna
- **EDA Service**: Jupyter Lab for data analysis
- **Monitoring**: Prometheus + Grafana observability
- **Logging**: Loki + Promtail log aggregation

#### Container Architecture
```
docker/
├── api/Dockerfile          # Production API container
├── training/Dockerfile     # ML training environment
├── eda/Dockerfile         # Jupyter data science setup
├── frontend/Dockerfile    # Production React build
├── prometheus/            # Metrics collection config
├── grafana/              # Dashboard configurations
├── nginx/nginx.conf      # Reverse proxy config
└── postgres/init.sql     # Database initialization
```

### Technology Stack

#### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: ORM with async support for database operations
- **PostgreSQL**: Primary database for storing image and detection metadata
- **Hugging Face Transformers**: YOLO model for object detection
- **Pillow**: Image processing and manipulation
- **Pytest**: Testing framework with async support

#### Frontend
- **React 18**: Component-based UI library
- **Vite**: Fast build tool and development server
- **TypeScript**: Type-safe JavaScript development
- **React Router**: Client-side routing
- **TanStack Query**: Data fetching and caching
- **Vitest**: Testing framework for frontend components

#### DevOps & MLOps
- **GitHub Actions**: CI/CD pipeline with security scanning
- **Docker**: Multi-stage builds with security hardening
- **Prometheus + Grafana**: Comprehensive monitoring and alerting
- **MinIO**: S3-compatible object storage for production
- **Nginx**: Production-grade reverse proxy and load balancer
- **uv**: Python package management
- **Ruff**: Python linting and formatting
- **ESLint**: JavaScript/TypeScript linting

---

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

## Development & Testing

### Running Tests

#### Backend Tests
```bash
cd backend

# Run all tests (106 tests, 72% coverage)
uv run pytest

# Run with coverage report
uv run pytest --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/unit/test_image_service.py -v

# Run integration tests only
uv run pytest tests/integration/ -v
```

**Test Suite Coverage:**
- ✅ 106 total tests passing
- ✅ 72% code coverage (866/1198 lines)
- ✅ Unit tests for services, repositories, and utilities
- ✅ Integration tests for API routes and database operations
- ✅ Test isolation with automatic rollback fixtures

#### Frontend Tests
```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm run coverage

# Run tests in watch mode
npm run test:watch

# Run specific test file
npx vitest run src/__tests__/uploadPage.spec.tsx
```

### Code Quality

#### Backend Linting & Formatting
```bash
cd backend

# Check code style (Ruff v0.8.4)
uv run ruff check

# Auto-fix issues
uv run ruff check --fix

# Format code
uv run ruff format
```

**Linting Standards:**
- ✅ Modern Python 3.12+ syntax (PEP 604 union types, PEP 695 generics)
- ✅ Import organization and sorting (isort-compatible)
- ✅ Type-checking imports with TYPE_CHECKING blocks
- ✅ No trailing whitespace or unnecessary f-strings
- ✅ All lint rules passing in CI/CD pipeline

#### Frontend Linting
```bash
cd frontend

# Check code style
npm run lint

# Auto-fix issues
npm run lint:fix
```

### Development Setup
```bash
# Install backend dependencies with dev extras
cd backend && uv sync --group dev

# Install frontend dependencies
cd frontend && npm install

# Run database migrations (if needed)
cd backend && uv run alembic upgrade head
```

## Notes
- Timezone-aware timestamps (`datetime.now(timezone.utc)`) used throughout.
- File storage paths include hash prefix + original stem; collision resolution adds random suffix.
- Detection service can be overridden in tests for faster runs (fake service).
- Duplicate upload 409 is triggered via dependency override simulation; real implementation permits re-upload with unique path.
- Modern Python 3.12+ features: Union types (X | None), Generic class syntax (class Name[T]), TYPE_CHECKING blocks
- Test isolation: Database fixtures with automatic rollback, independent test execution
- UUID-based identifiers: Consistent type safety across API routes and database operations

## Performance Considerations

### Backend Optimizations
- **Model Caching**: YOLO model loaded once and kept in memory
- **Connection Pooling**: Async database connections with SQLAlchemy
- **File Hashing**: SHA256 for deduplication and integrity verification
- **Pagination**: Efficient database queries with limit/offset

### Frontend Optimizations
- **React Query Caching**: Intelligent data fetching and caching (30s stale time)
- **Code Splitting**: Vite handles automatic code splitting
- **Error Boundaries**: Graceful error handling without full page crashes
- **Lazy Loading**: Images and components loaded on demand

## Security Features

### Input Validation
- **File Type Validation**: Only allowed image formats (JPEG, PNG, WebP)
- **File Extension Validation**: Pre-upload extension check to prevent invalid files
- **File Size Limits**: Maximum 5MB per upload
- **Filename Sanitization**: Prevents path traversal attacks
- **SQL Injection Prevention**: Parameterized queries via SQLAlchemy
- **Type Safety**: UUID-based identifiers for database consistency

### Authentication Ready
- **JWT Token Support**: Auth context and header injection infrastructure
- **CORS Configuration**: Secure cross-origin request handling
- **Environment-based Config**: Sensitive data via environment variables

## Deployment

### Production Deployment

#### Simple Production (Recommended)
```bash
# Start the full application stack
docker-compose up -d

# For production, consider:
export POSTGRES_PASSWORD=your-secure-password
export MINIO_ROOT_PASSWORD=your-secure-minio-password
docker-compose up -d
```

#### Advanced MLOps Deployment (Optional)
```bash
# Full MLOps platform with additional services
./scripts/mlops.sh start-mlops

# Custom environment configuration
cp .env.template .env
# Edit .env with your settings
./scripts/mlops.sh start-prod
```

## Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and add tests
4. Run test suite: `uv run pytest && npm test`
5. Run linting: `uv run ruff check --fix && npm run lint:fix`
6. Commit with conventional commits: `git commit -m "feat: add amazing feature"`
7. Push and create a Pull Request

### Code Standards
- **Backend**: Follow PEP 8, use type hints, add docstrings
- **Frontend**: Use TypeScript, follow React best practices
- **Tests**: Maintain >70% coverage, test both happy and error paths
- **Documentation**: Update README for new features
- **Commits**: Use conventional commit format (feat, fix, docs, style, refactor, test, chore)

### Continuous Integration
- **GitHub Actions**: Automated testing and linting on every push
- **Code Quality**: Ruff for Python, ESLint for TypeScript
- **Test Coverage**: pytest with coverage reporting
- **Security**: Dependency scanning and vulnerability checks

### Issue Reporting
Please include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python/Node versions)
- Relevant logs or error messages

## License

This project is part of the Computer Vision course at Universidad del Desarrollo (UDD).

**Educational Use License**: This project is intended for educational purposes. Students and educators are free to use, modify, and learn from this codebase. Commercial use requires permission from the course instructors.

## Acknowledgments

- **Hugging Face**: For providing the YOLO model and transformers library
- **FastAPI Team**: For the excellent async web framework
- **React Team**: For the component-based UI library
- **Universidad del Desarrollo**: For supporting this educational project

---

**Built with ❤️ for computer vision education at UDD**

Available as both a development environment and a production-ready MLOps platform.

