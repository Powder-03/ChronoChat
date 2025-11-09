"""
ChronoChat - AI-powered chatbot with Clerk authentication
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.database import init_databases, close_databases
from app.api.routes import auth, chat, health, system

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting ChronoChat API...")
    logger.info(f"Environment: {'Development' if settings.DEBUG else 'Production'}")
    
    # Initialize database connections
    try:
        await init_databases()
        logger.info("Database connections established")
    except Exception as e:
        logger.error(f"Failed to initialize databases: {str(e)}")
        raise
    
    yield
    
    # Close database connections
    logger.info("Shutting down ChronoChat API...")
    await close_databases()


# Initialize FastAPI app
app = FastAPI(
    title="ChronoChat API",
    description="AI-powered chatbot with Clerk authentication",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(system.router, prefix="/api/system", tags=["system"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "ChronoChat API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/api/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
