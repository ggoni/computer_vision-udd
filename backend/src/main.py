"""FastAPI application entry point.

This module creates and configures the FastAPI application with
middleware, CORS, logging, and route registration.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.middleware import ErrorHandlerMiddleware
from .api.routes.health import router as health_router
from .api.routes.images import router as images_router
from .core.config import get_settings
from .core.logging import get_logger, setup_logging
from .db.session import close_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager.
    
    Handles startup and shutdown events for the FastAPI application.
    """
    # Startup
    setup_logging()
    logger = get_logger(__name__)
    logger.info("Starting Computer Vision API server")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Computer Vision API server")
    await close_db()


def create_app() -> FastAPI:
    """Create and configure FastAPI application.
    
    Returns:
        FastAPI: Configured application instance
    """
    settings = get_settings()
    
    # Create FastAPI app with lifespan
    app = FastAPI(
        title="Computer Vision Detection API",
        description="Object detection API using computer vision AI models",
        version="0.1.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    
    # Add error handling middleware
    app.add_middleware(ErrorHandlerMiddleware)
    
    # Include routers
    app.include_router(health_router)
    app.include_router(images_router)
    
    return app


# Create app instance
app = create_app()


@app.get("/")
async def root():
    """Root endpoint returning API status.
    
    Returns:
        dict: API status and information
    """
    settings = get_settings()
    
    return {
        "status": "ok",
        "message": "Computer Vision Detection API",
        "version": "0.1.0",
        "environment": settings.APP_ENV,
        "docs_url": "/docs" if settings.DEBUG else "disabled"
    }