"""
ChronoChat FastAPI Backend
Main application entry point with authentication and chat functionality
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import create_tables
from app.api.routes import auth, chat, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await create_tables()
    print("🚀 ChronoChat Backend Started!")
    yield
    # Shutdown
    print("👋 ChronoChat Backend Shutting Down!")


# Create FastAPI app
app = FastAPI(
    title="ChronoChat API",
    description="A modern chat application with AI assistance and tool integration",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ChronoChat API is running!",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ChronoChat Backend"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
