"""Database session management with async SQLAlchemy.

This module provides async database session configuration with
connection pooling and dependency injection for FastAPI.
"""

from collections.abc import AsyncGenerator

from sqlalchemy import text
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

        logger.info(
            "Creating database engine",
            extra={"database_url": settings.DATABASE_URL.split("@")[-1]},
        )

        engine_kwargs = {
            "pool_pre_ping": True,
            "pool_recycle": 3600,  # Recycle connections every hour
            "echo": settings.DEBUG and settings.LOG_LEVEL.upper() == "DEBUG",
            # AsyncPG-specific optimizations
            "connect_args": {
                "command_timeout": 30,  # Query timeout from asyncpg docs
                "server_settings": {
                    "timezone": "UTC",  # Consistent timezone setting
                    "application_name": "cv_backend",  # Connection identification
                }
            }
        }

        if settings.APP_ENV == "test":
            engine_kwargs["poolclass"] = NullPool
        else:
            engine_kwargs.update(
                {
                    "pool_size": 20,
                    "max_overflow": 10,
                }
            )

        _engine = create_async_engine(
            settings.DATABASE_URL,
            **engine_kwargs,
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
    database sessions into route handlers with timeout handling.

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
            # Set session-level timeout
            await session.execute(text("SET statement_timeout = 30000"))  # 30 seconds
            yield session
            await session.commit()
            logger.debug("Database session committed")
        except Exception as e:
            logger.error(
                "Database session error, rolling back", 
                extra={"error": str(e), "error_type": type(e).__name__}
            )
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
            result = await session.execute(text("SELECT 1"))
            result.fetchone()
            logger.debug("Database health check passed")
            return True
    except Exception as e:
        logger.error("Database health check failed", extra={"error": str(e)})
        return False


# AsyncPG-style transaction context manager following best practices
class DatabaseQueryMonitor:
    """Database query monitoring context manager following asyncpg patterns."""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
    
    async def __aenter__(self):
        import time
        self.start_time = time.time()
        logger.debug(f"Starting database operation: {self.operation_name}")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        import time
        duration = time.time() - self.start_time
        
        if exc_type:
            logger.error(
                f"Database operation failed: {self.operation_name}",
                extra={"duration": duration, "error": str(exc_val)}
            )
        else:
            logger.debug(
                f"Database operation completed: {self.operation_name}",
                extra={"duration": duration}
            )
