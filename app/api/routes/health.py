"""
Health check endpoints
"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "chronochat-api"
    }


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    # Add checks for database, redis, etc. here
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat()
    }
