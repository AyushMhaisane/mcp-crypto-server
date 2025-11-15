import redis.asyncio as redis
from app.config import settings

# Global Redis client instance
redis_client: redis.Redis = None

async def get_redis_client() -> redis.Redis:
    """
    Dependency injector for accessing the Redis client.
    """
    if redis_client is None:
        raise ConnectionError("Redis client is not initialized.")
    return redis_client

async def startup_redis():
    """
    Initializes the Redis client connection pool on application startup.
    """
    global redis_client
    print(f"Connecting to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
    try:
        redis_client = redis.from_url(
            settings.REDIS_URL, 
            encoding="utf-8", 
            decode_responses=True # Auto-decode responses to strings
        )
        await redis_client.ping()
        print("Redis connection successful.")
    except Exception as e:
        print(f"Error connecting to Redis: {e}")
        # In a production app, you might want to raise here or use a fallback.

async def shutdown_redis():
    """
    Closes the Redis connection pool on application shutdown.
    """
    global redis_client
    if redis_client:
        await redis_client.close()
        print("Redis connection closed.")