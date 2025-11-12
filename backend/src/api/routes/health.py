"""Health check endpoints for monitoring and readiness probes."""

from fastapi import APIRouter, HTTPException, status

from ...core.logging import get_logger
from ...db.session import check_db_connection

logger = get_logger(__name__)
router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check():
    """Basic health check endpoint.
    
    Returns:
        dict: Health status
    """
    return {
        "status": "healthy",
        "service": "computer-vision-api",
        "timestamp": "2025-11-12T18:00:00Z"
    }


@router.get("/ready")
async def readiness_check():
    """Readiness probe that checks external dependencies.
    
    Returns:
        dict: Readiness status with dependency checks
        
    Raises:
        HTTPException: 503 if any dependency is unhealthy
    """
    checks = {
        "database": False,
        "overall": False
    }
    
    # Check database connection
    try:
        checks["database"] = await check_db_connection()
        logger.debug("Database health check completed", extra={"healthy": checks["database"]})
    except Exception as e:
        logger.error("Database health check failed", extra={"error": str(e)})
        checks["database"] = False
    
    # Overall readiness
    checks["overall"] = checks["database"]
    
    if not checks["overall"]:
        logger.warning("Readiness check failed", extra=checks)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not_ready", "checks": checks}
        )
    
    logger.info("Readiness check passed", extra=checks)
    return {
        "status": "ready",
        "checks": checks
    }