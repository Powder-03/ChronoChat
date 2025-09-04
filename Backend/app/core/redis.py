"""
Redis client configuration
"""
import redis.asyncio as aioredis
from app.core.config import settings


class RedisClient:
    """Redis client singleton"""
    
    def __init__(self):
        self._client = None
    
    async def get_client(self) -> aioredis.Redis:
        """Get Redis client instance"""
        if self._client is None:
            self._client = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
        return self._client
    
    async def close(self):
        """Close Redis connection"""
        if self._client:
            await self._client.close()


# Global Redis client instance
redis_client = RedisClient()
