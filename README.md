# Computer Vision Detection API

![CI](https://github.com/ggoni/computer_vision-udd/actions/workflows/ci.yml/badge.svg)

FastAPI-based backend providing image upload, object detection analysis, and paginated listing of images and detections.

## Usage Instructions

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
   docker run --name cv-postgres -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=cv_db -p 5432:5432 -d postgres:15
   
   # Or install PostgreSQL locally and create database
   createdb cv_db
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
   
   # Start the server
   uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
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
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

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

### File Storage
- Images are stored in organized directory structure: `uploads/YYYY/MM/DD/`
- Filenames include content hash for deduplication: `abc123_original_name.jpg`
- Collision detection adds random suffix if needed
- File integrity verified via SHA256 hashing

### Model Information
- Uses **YOLO-tiny** model from Hugging Face (`hustvl/yolos-tiny`)
- First analysis may take longer due to model download (~100MB)
- Model is cached locally in `~/.cache/huggingface/`
- Supports 80+ object classes from COCO dataset
- Confidence threshold can be filtered in the UI (default shows all >0.1)

### Troubleshooting

#### Backend Issues
```bash
# Check database connection
uv run python -c "from src.db.session import check_db_connection; import asyncio; print(asyncio.run(check_db_connection()))"

# View logs with debug info
APP_ENV=development uv run uvicorn src.main:app --log-level debug

# Reset database schema
uv run python scripts/init_db.py
```

#### Frontend Issues
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check API connectivity
curl http://localhost:8000/api/v1/health

# Run tests for debugging
npm run test
```

#### Common Issues
- **Database connection failed**: Ensure PostgreSQL is running and credentials are correct
- **Model download slow**: First run downloads ~100MB model, subsequent runs are fast
- **File upload fails**: Check file size (<5MB) and format (jpg/png/webp)
- **CORS errors**: Ensure backend is running on port 8000 and frontend on 5173

## Architecture

### Backend Structure
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

### Frontend Structure
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

#### DevOps & Quality
- **GitHub Actions**: CI/CD pipeline
- **uv**: Python package management
- **Ruff**: Python linting and formatting
- **ESLint**: JavaScript/TypeScript linting
- **Coverage**: Test coverage reporting

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

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/unit/test_image_service.py -v

# Run integration tests only
uv run pytest tests/integration/ -v
```

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

# Check code style
uv run ruff check

# Auto-fix issues
uv run ruff check --fix

# Format code
uv run ruff format
```

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
- **File Size Limits**: Maximum 5MB per upload
- **Filename Sanitization**: Prevents path traversal attacks
- **SQL Injection Prevention**: Parameterized queries via SQLAlchemy

### Authentication Ready
- **JWT Token Support**: Auth context and header injection infrastructure
- **CORS Configuration**: Secure cross-origin request handling
- **Environment-based Config**: Sensitive data via environment variables

## Deployment

### Production Recommendations
```bash
# Backend production server
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4

# Frontend production build
cd frontend && npm run build

# Environment variables for production
export APP_ENV=production
export DATABASE_URL=postgresql+asyncpg://user:pass@prod-db:5432/cv_db
export UPLOAD_DIR=/var/uploads
```

### Docker Support (Future Enhancement)
The application is designed to be containerizable:
- Backend: Python 3.12 + uv + FastAPI
- Frontend: Node.js + Nginx for static serving
- Database: PostgreSQL official image
- Reverse Proxy: Nginx or Traefik

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
- **Tests**: Maintain >80% coverage, test both happy and error paths
- **Documentation**: Update README for new features

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

