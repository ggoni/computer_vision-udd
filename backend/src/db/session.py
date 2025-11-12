"""Database session management with async SQLAlchemy.

This module provides async database session configuration with
connection pooling and dependency injection for FastAPI.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from ..core.config import get_settings
from ..core.logging import get_logger

logger = get_logger(__name__)

# Global engine and session factory
_engine = None
_async_session_local = None


def get_engine():
    """Get or create the async SQLAlchemy engine."""
    global _engine
    
    if _engine is None:
        settings = get_settings()
        
        logger.info("Creating database engine", extra={"database_url": settings.DATABASE_URL.split("@")[-1]})
        
        _engine = create_async_engine(
            settings.DATABASE_URL,
            # Connection pool settings
            pool_size=20,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600,  # 1 hour
            # Use NullPool for testing environments
            poolclass=NullPool if settings.APP_ENV == "test" else None,
            # Echo SQL in debug mode
            echo=settings.DEBUG and settings.LOG_LEVEL.upper() == "DEBUG",
        )
        
        logger.info("Database engine created successfully")
    
    return _engine


def get_session_local():
    """Get or create the async session factory."""
    global _async_session_local
    
    if _async_session_local is None:
        engine = get_engine()
        _async_session_local = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=True,
            autocommit=False,
        )
        
        logger.info("Database session factory created")
    
    return _async_session_local


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides a database session.
    
    This function is used as a FastAPI dependency to inject
    database sessions into route handlers.
    
    Yields:
        AsyncSession: Database session
        
    Example:
        @app.get("/users/")
        async def get_users(db: AsyncSession = Depends(get_db)):
            # Use db session here
            pass
    """
    session_local = get_session_local()
    
    async with session_local() as session:
        try:
            logger.debug("Database session created")
            yield session
            await session.commit()
            logger.debug("Database session committed")
        except Exception as e:
            logger.error("Database session error, rolling back", extra={"error": str(e)})
            await session.rollback()
            raise
        finally:
            await session.close()
            logger.debug("Database session closed")


async def close_db():
    """Close database connections.
    
    This should be called during application shutdown
    to properly close all database connections.
    """
    global _engine
    
    if _engine:
        logger.info("Closing database connections")
        await _engine.dispose()
        _engine = None
        logger.info("Database connections closed")


# Health check function
async def check_db_connection() -> bool:
    """Check if database connection is healthy.
    
    Returns:
        bool: True if connection is healthy, False otherwise
    """
    try:
        session_local = get_session_local()
        async with session_local() as session:
            # Simple query to check connection
            result = await session.execute("SELECT 1")
            result.fetchone()
            logger.debug("Database health check passed")
            return True
    except Exception as e:
        logger.error("Database health check failed", extra={"error": str(e)})
        return False