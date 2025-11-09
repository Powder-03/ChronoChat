"""
Database connection managers for PostgreSQL and MongoDB
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from motor.motor_asyncio import AsyncIOMotorClient
from typing import AsyncGenerator
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy Base for PostgreSQL
Base = declarative_base()

# PostgreSQL Engine and Session
engine = None
async_session_maker = None

# MongoDB Client
mongodb_client: AsyncIOMotorClient = None
mongodb_db = None


async def init_postgres():
    """Initialize PostgreSQL connection"""
    global engine, async_session_maker
    
    try:
        # Convert sync URL to async URL
        db_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        
        engine = create_async_engine(
            db_url,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )
        
        async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        logger.info("PostgreSQL connection initialized")
        
    except Exception as e:
        logger.error(f"Error initializing PostgreSQL: {str(e)}")
        raise


async def close_postgres():
    """Close PostgreSQL connection"""
    global engine
    if engine:
        await engine.dispose()
        logger.info("PostgreSQL connection closed")


async def get_postgres_session() -> AsyncGenerator[AsyncSession, None]:
    """Get PostgreSQL session"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_mongodb():
    """Initialize MongoDB connection"""
    global mongodb_client, mongodb_db
    
    try:
        mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
        mongodb_db = mongodb_client[settings.MONGODB_DB_NAME]
        
        # Test connection
        await mongodb_client.admin.command('ping')
        
        # Create indexes for better performance
        await mongodb_db.conversations.create_index("user_id")
        await mongodb_db.conversations.create_index("created_at")
        await mongodb_db.messages.create_index("conversation_id")
        await mongodb_db.messages.create_index("created_at")
        
        logger.info("MongoDB connection initialized")
        
    except Exception as e:
        logger.error(f"Error initializing MongoDB: {str(e)}")
        raise


async def close_mongodb():
    """Close MongoDB connection"""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        logger.info("MongoDB connection closed")


def get_mongodb():
    """Get MongoDB database instance"""
    return mongodb_db


async def init_databases():
    """Initialize all database connections"""
    await init_postgres()
    await init_mongodb()
    logger.info("All database connections initialized")


async def close_databases():
    """Close all database connections"""
    await close_postgres()
    await close_mongodb()
    logger.info("All database connections closed")
