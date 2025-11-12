# Computer Vision Application - Architecture Document

## Overview

Production-ready web application for object detection using computer vision AI models. Designed for non-technical users to upload images and receive structured detection results through a modern web interface.

---

## Technology Stack

### Backend
- **Python 3.12+** with FastAPI
- **PostgreSQL 16** for data persistence
- **Redis** for caching and job queuing
- **Celery** for async task processing
- **uv** for dependency management

### Frontend
- **React 18** with TypeScript
- **Vite** as build tool
- **TanStack Query** for data fetching
- **TailwindCSS** for styling
- **Zustand** for state management

### ML/AI
- **Transformers** (Hugging Face)
- **PyTorch** for model inference
- **Pillow** for image processing

### Infrastructure
- **Docker** & **Docker Compose**
- **Nginx** as reverse proxy
- **PostgreSQL** containerized
- **Redis** containerized

---

## Project Structure

```
computer_vision-udd/
├── backend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── dependencies.py          # Dependency injection
│   │   │   ├── middleware.py            # CORS, logging, error handling
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       ├── health.py            # Health check endpoints
│   │   │       ├── images.py            # Image upload & management
│   │   │       └── detections.py        # Detection results & history
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py                # Settings (Pydantic BaseSettings)
│   │   │   ├── security.py              # Auth helpers (future)
│   │   │   └── logging.py               # Logging configuration
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                  # SQLAlchemy base
│   │   │   ├── session.py               # Database session management
│   │   │   └── migrations/              # Alembic migrations
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── image.py                 # Image ORM model
│   │   │   └── detection.py             # Detection ORM model
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── image.py                 # Image Pydantic schemas
│   │   │   └── detection.py             # Detection Pydantic schemas
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── cv_service.py            # Computer vision logic
│   │   │   ├── image_service.py         # Image storage & retrieval
│   │   │   └── detection_service.py     # Detection CRUD operations
│   │   ├── tasks/
│   │   │   ├── __init__.py
│   │   │   └── detection_tasks.py       # Celery async tasks
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── file_utils.py            # File validation & processing
│   │   │   └── model_loader.py          # Model loading & caching
│   │   └── main.py                      # FastAPI application entry
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── conftest.py
│   ├── storage/                         # Local file storage (volume mount)
│   │   └── uploads/
│   ├── pyproject.toml                   # uv project config
│   ├── uv.lock                          # Locked dependencies
│   ├── Dockerfile
│   └── .dockerignore
│
├── frontend/
│   ├── src/
│   │   ├── assets/                      # Static assets
│   │   ├── components/
│   │   │   ├── common/                  # Reusable UI components
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Spinner.tsx
│   │   │   │   └── ErrorBoundary.tsx
│   │   │   ├── layout/
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Footer.tsx
│   │   │   │   └── Layout.tsx
│   │   │   ├── upload/
│   │   │   │   ├── ImageUploader.tsx    # Drag & drop uploader
│   │   │   │   └── UploadProgress.tsx
│   │   │   └── results/
│   │   │       ├── DetectionResults.tsx # Results display
│   │   │       ├── BoundingBox.tsx      # Visual bounding boxes
│   │   │       └── DetectionList.tsx    # Table of detections
│   │   ├── hooks/
│   │   │   ├── useImageUpload.ts        # Upload logic
│   │   │   ├── useDetections.ts         # Fetch detections
│   │   │   └── usePolling.ts            # Poll for async results
│   │   ├── services/
│   │   │   └── api.ts                   # Axios client & endpoints
│   │   ├── store/
│   │   │   └── appStore.ts              # Zustand global state
│   │   ├── types/
│   │   │   ├── image.ts
│   │   │   └── detection.ts
│   │   ├── utils/
│   │   │   ├── formatters.ts            # Data formatting helpers
│   │   │   └── validators.ts            # Client-side validation
│   │   ├── pages/
│   │   │   ├── Home.tsx                 # Main upload page
│   │   │   ├── Results.tsx              # Results view page
│   │   │   └── History.tsx              # Analysis history
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── vite-env.d.ts
│   ├── public/
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── Dockerfile
│   └── .dockerignore
│
├── nginx/
│   ├── nginx.conf                       # Main nginx config
│   └── default.conf                     # Site config
│
├── docker-compose.yml
├── docker-compose.dev.yml               # Development overrides
├── .env.example
├── .gitignore
├── README.md
└── architecture.md                      # This file
```

---

## Component Responsibilities

### Backend Components

#### **API Layer** (`src/api/`)
- HTTP request handling
- Input validation via Pydantic
- Response serialization
- Error handling middleware
- CORS configuration

#### **Core** (`src/core/`)
- Application configuration (environment variables)
- Security utilities (API keys, rate limiting)
- Centralized logging setup

#### **Database** (`src/db/`)
- SQLAlchemy engine & session management
- Connection pooling
- Alembic migrations for schema versioning

#### **Models** (`src/models/`)
ORM models representing database tables:
- **Image**: id, filename, original_url, upload_timestamp, file_size, status
- **Detection**: id, image_id (FK), label, confidence_score, bbox_coordinates, created_at

#### **Schemas** (`src/schemas/`)
Pydantic models for request/response validation:
- Input validation (file uploads, filters)
- Output serialization (API responses)
- Data transfer objects (DTOs)

#### **Services** (`src/services/`)
Business logic layer:

- **cv_service.py**:
  - Load ML models (singleton pattern)
  - Run object detection inference
  - Post-process predictions (filtering, formatting)

- **image_service.py**:
  - Save uploaded images to storage
  - Generate thumbnails
  - Retrieve image metadata

- **detection_service.py**:
  - CRUD operations for detections
  - Query filtering & pagination
  - Data aggregation

#### **Tasks** (`src/tasks/`)
- Celery workers for async processing
- Offload heavy inference to background jobs
- Result callbacks to update DB

#### **Utils** (`src/utils/`)
- File validation (type, size, dimensions)
- Model lazy loading & caching
- Helper functions

---

### Frontend Components

#### **Components** (`src/components/`)
React component hierarchy:

- **common/**: Reusable UI primitives (buttons, spinners, modals)
- **layout/**: Page structure components
- **upload/**: Image upload interface with drag-and-drop
- **results/**: Detection visualization (canvas overlay, table view)

#### **Hooks** (`src/hooks/`)
Custom React hooks for logic reuse:
- Data fetching with TanStack Query
- File upload with progress tracking
- Polling for async job completion

#### **Services** (`src/services/`)
- Axios HTTP client configuration
- API endpoint definitions
- Request/response interceptors

#### **Store** (`src/store/`)
Zustand state management:
- Current image state
- Detection results cache
- UI state (loading, errors)

#### **Types** (`src/types/`)
TypeScript type definitions matching backend schemas

---

## State Management

### Backend State

#### **Database (PostgreSQL)**
- **Persistent storage** for:
  - Image metadata
  - Detection results
  - Analysis history

- **Schema**:
  ```sql
  images (
    id UUID PRIMARY KEY,
    filename VARCHAR(255),
    original_url TEXT,
    storage_path VARCHAR(500),
    upload_timestamp TIMESTAMP,
    file_size INTEGER,
    status VARCHAR(50), -- 'pending', 'processing', 'completed', 'failed'
    created_at TIMESTAMP,
    updated_at TIMESTAMP
  )

  detections (
    id UUID PRIMARY KEY,
    image_id UUID REFERENCES images(id) ON DELETE CASCADE,
    label VARCHAR(100),
    confidence_score FLOAT,
    bbox_xmin INTEGER,
    bbox_ymin INTEGER,
    bbox_xmax INTEGER,
    bbox_ymax INTEGER,
    created_at TIMESTAMP
  )
  ```

#### **Redis**
- **Model cache**: Loaded ML models (avoid reloading)
- **Job queue**: Celery task queue for async processing
- **Result backend**: Store task results temporarily
- **Session storage**: (Future) User session data

#### **Application Memory**
- ML model singleton (loaded once per worker)
- Configuration settings (loaded at startup)

### Frontend State

#### **Zustand Store** (Global)
```typescript
interface AppState {
    currentImage: Image | null
    detections: Detection[]
    isLoading: boolean
    error: string | null
    uploadProgress: number
}
```

#### **TanStack Query Cache**
- Server state synchronization
- Automatic background refetching
- Optimistic updates

#### **Component State** (Local)
- Form inputs
- UI toggles (modals, dropdowns)
- Transient UI state

---

## Service Communication Flow

### Synchronous Flow (Quick Results)
```
User → Frontend → Nginx → Backend API → CV Service → ML Model
                                      ↓
                                   Database
                                      ↓
User ← Frontend ← Nginx ← JSON Response
```

### Asynchronous Flow (Heavy Processing)
```
1. Upload:
   User → Frontend → Backend API → Save Image → Database
                                 → Queue Task → Redis (Celery)
                                 → Return Job ID

2. Processing:
   Celery Worker → Redis → Fetch Task → CV Service → ML Model
                                      → Save Results → Database

3. Polling:
   Frontend → Backend API (poll job status) → Database → Return results
```

---

## Docker Architecture

### Container Services

#### **1. Backend API Container**
- Base: `python:3.12-slim`
- Optimizations:
  - Multi-stage build (build deps → runtime)
  - uv for fast dependency resolution
  - Non-root user
  - Health checks
- Exposed: Port 8000 (internal)

**Dockerfile highlights:**
```dockerfile
FROM python:3.12-slim AS builder
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

FROM python:3.12-slim
COPY --from=builder /app/.venv /app/.venv
# ... copy application code
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0"]
```

#### **2. Celery Worker Container**
- Same base as backend
- Runs Celery worker process
- Shares codebase with API container
- Mounts model cache volume

#### **3. Frontend Container**
- Base: `node:20-alpine`
- Multi-stage: build → serve with nginx
- Optimizations:
  - Bun or pnpm for faster installs (optional)
  - Production build minification
  - Static file caching headers

**Dockerfile highlights:**
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

#### **4. PostgreSQL Container**
- Image: `postgres:16-alpine`
- Persistent volume for data
- Initialization scripts for schema

#### **5. Redis Container**
- Image: `redis:7-alpine`
- Persistent volume (optional, for durability)

#### **6. Nginx Reverse Proxy**
- Image: `nginx:alpine`
- Routes:
  - `/api/*` → Backend API
  - `/` → Frontend SPA
  - `/static/*` → Static files
- SSL termination (production)
- Rate limiting

---

## Environment Configuration

### Backend (.env)
```bash
# Application
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://user:pass@db:5432/cvision
DB_POOL_SIZE=20

# Redis
REDIS_URL=redis://redis:6379/0

# Storage
UPLOAD_DIR=/app/storage/uploads
MAX_UPLOAD_SIZE=10485760  # 10MB

# ML Models
MODEL_NAME=huggingface/yolos-tiny
MODEL_CACHE_DIR=/app/models
CONFIDENCE_THRESHOLD=0.5

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
```

### Frontend (.env)
```bash
VITE_API_URL=http://localhost/api
VITE_MAX_FILE_SIZE=10485760
VITE_POLL_INTERVAL=2000
```

---

## Docker Compose Configuration

### docker-compose.yml
```yaml
version: '3.9'

services:
    db:
        image: postgres:16-alpine
        environment:
            POSTGRES_USER: cvision
            POSTGRES_PASSWORD: ${DB_PASSWORD}
            POSTGRES_DB: cvision
        volumes:
            - postgres_data:/var/lib/postgresql/data
        healthcheck:
            test: ["CMD-SHELL", "pg_isready -U cvision"]
            interval: 10s
            timeout: 5s
            retries: 5

    redis:
        image: redis:7-alpine
        volumes:
            - redis_data:/data
        healthcheck:
            test: ["CMD", "redis-cli", "ping"]
            interval: 10s

    backend:
        build:
            context: ./backend
            dockerfile: Dockerfile
        environment:
            DATABASE_URL: postgresql://cvision:${DB_PASSWORD}@db:5432/cvision
            REDIS_URL: redis://redis:6379/0
        volumes:
            - ./backend/storage:/app/storage
            - model_cache:/app/models
        depends_on:
            db:
                condition: service_healthy
            redis:
                condition: service_healthy
        healthcheck:
            test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
            interval: 30s

    celery:
        build:
            context: ./backend
            dockerfile: Dockerfile
        command: celery -A src.tasks worker --loglevel=info
        environment:
            DATABASE_URL: postgresql://cvision:${DB_PASSWORD}@db:5432/cvision
            REDIS_URL: redis://redis:6379/0
        volumes:
            - ./backend/storage:/app/storage
            - model_cache:/app/models
        depends_on:
            - redis
            - db

    frontend:
        build:
            context: ./frontend
            dockerfile: Dockerfile
        depends_on:
            - backend

    nginx:
        image: nginx:alpine
        ports:
            - "80:80"
            - "443:443"
        volumes:
            - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
            - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
        depends_on:
            - backend
            - frontend

volumes:
    postgres_data:
    redis_data:
    model_cache:
```

---

## API Endpoints

### Image Management
- `POST /api/v1/images/upload` - Upload image (multipart/form-data)
- `GET /api/v1/images/{id}` - Retrieve image metadata
- `GET /api/v1/images/{id}/file` - Download original image
- `DELETE /api/v1/images/{id}` - Delete image & detections

### Detection
- `POST /api/v1/detections/analyze/{image_id}` - Trigger analysis (async)
- `GET /api/v1/detections/job/{job_id}` - Check job status
- `GET /api/v1/detections/{image_id}` - Get detection results
- `GET /api/v1/detections` - List all detections (paginated)

### Health
- `GET /api/health` - Service health check
- `GET /api/health/ready` - Readiness probe (DB + Redis)

---

## Security Considerations

### Current Implementation
- Input validation (file type, size)
- SQL injection prevention (ORM)
- CORS configuration
- Rate limiting (nginx)

### Future Enhancements
- Authentication (JWT)
- API key management
- File scanning (malware detection)
- HTTPS enforcement
- CSP headers

---

## Performance Optimizations

### Backend
1. **Model Loading**: Singleton pattern, load once per worker
2. **Connection Pooling**: PostgreSQL pool (20 connections)
3. **Caching**: Redis for frequent queries
4. **Async Processing**: Celery for heavy inference
5. **Image Optimization**: Resize large uploads before processing

### Frontend
1. **Code Splitting**: Lazy load routes
2. **Image Optimization**: Compress uploads client-side
3. **Caching**: TanStack Query deduplication
4. **Debouncing**: Limit polling frequency

### Database
1. **Indexes**: image_id, created_at, status
2. **Partitioning**: (Future) Partition detections by date
3. **Archival**: Move old data to cold storage

---

## Monitoring & Observability

### Logging
- **Structured logging** (JSON format)
- **Log levels**: DEBUG, INFO, WARNING, ERROR
- **Correlation IDs**: Track requests across services

### Metrics (Future)
- Prometheus exporters
- Grafana dashboards
- Key metrics:
  - Request latency (p50, p95, p99)
  - Inference time
  - Queue depth
  - Error rates

### Tracing (Future)
- OpenTelemetry instrumentation
- Distributed tracing across services

---

## Deployment Strategy

### Development
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```
- Hot reload enabled
- Debug mode on
- Local volumes mounted

### Production
```bash
docker-compose up -d
```
- Optimized builds
- Health checks enabled
- Auto-restart policies
- Resource limits

### CI/CD Pipeline
1. **Build**: `docker build` for each service
2. **Test**: Run unit & integration tests
3. **Scan**: Trivy for vulnerability scanning
4. **Push**: Push images to registry
5. **Deploy**: Update running containers

---

## Scaling Strategy

### Horizontal Scaling
- **Backend API**: Scale via replicas (load balancer)
- **Celery Workers**: Add workers for parallel processing
- **Database**: Read replicas for heavy read loads

### Vertical Scaling
- Increase worker memory for larger models
- GPU support for faster inference (CUDA)

---

## Migration Path from Prototype

1. **Phase 1**: Set up backend API with FastAPI
2. **Phase 2**: Migrate CV logic to service layer
3. **Phase 3**: Add database persistence
4. **Phase 4**: Build frontend UI
5. **Phase 5**: Implement async processing with Celery
6. **Phase 6**: Containerize all services
7. **Phase 7**: Production hardening (security, monitoring)

---

## Development Workflow

### Backend Setup
```bash
cd backend
uv venv
uv sync
uv run alembic upgrade head
uv run uvicorn src.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Full Stack (Docker)
```bash
docker-compose up --build
```

---

## Testing Strategy

### Backend
- **Unit**: pytest for services, models
- **Integration**: TestClient for API routes
- **E2E**: Test full inference pipeline

### Frontend
- **Unit**: Vitest for components
- **Integration**: React Testing Library
- **E2E**: Playwright for user flows

---

## Conclusion

This architecture provides:
- **Scalability**: Horizontal scaling via containers
- **Maintainability**: Clean separation of concerns
- **Performance**: Async processing, caching, optimized Docker images
- **Developer Experience**: Modern tooling (uv, Vite, Docker Compose)
- **Production-Ready**: Health checks, logging, error handling

The system transforms the educational prototype into an enterprise-grade application suitable for real-world deployment.
