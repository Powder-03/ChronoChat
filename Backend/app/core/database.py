"""
Database configuration and connection management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

from app.core.config import settings

# Create sync engine for migrations
engine = create_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")
)

# Create async engine for application
async_engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Create base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """Create database tables"""
    async with async_engine.begin() as conn:
        # Import all models to ensure they are registered
        from app.models import user, chat  # noqa
        
        await conn.run_sync(Base.metadata.create_all)
