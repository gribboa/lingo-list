"""Redis hot cache layer for translations."""

import logging

import redis
from django.conf import settings

logger = logging.getLogger(__name__)


def get_redis_client():
    """Get a Redis client instance.
    
    Returns None if Redis is not available or not configured.
    """
    try:
        client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        # Test connection
        client.ping()
        return client
    except (redis.ConnectionError, redis.TimeoutError, AttributeError):
        logger.warning("Redis connection failed, hot cache disabled")
        return None


def get_cache_key(item_id: int, target_language: str) -> str:
    """Generate a Redis cache key for a translation.
    
    Args:
        item_id: The ListItem ID
        target_language: The target language code
        
    Returns:
        Cache key string
    """
    return f"translation:{item_id}:{target_language}"


def get_cached_translation(item_id: int, target_language: str) -> str | None:
    """Retrieve a cached translation from Redis.
    
    Args:
        item_id: The ListItem ID
        target_language: The target language code
        
    Returns:
        Translated text if found in cache, None otherwise
    """
    client = get_redis_client()
    if client is None:
        return None
    
    try:
        key = get_cache_key(item_id, target_language)
        value = client.get(key)
        if value:
            logger.debug("Redis cache hit: %s", key)
        return value
    except redis.RedisError:
        logger.exception("Error reading from Redis cache")
        return None


def set_cached_translation(
    item_id: int, target_language: str, translated_text: str
) -> bool:
    """Store a translation in Redis with TTL.
    
    Args:
        item_id: The ListItem ID
        target_language: The target language code
        translated_text: The translated text to cache
        
    Returns:
        True if successfully cached, False otherwise
    """
    client = get_redis_client()
    if client is None:
        return False
    
    try:
        key = get_cache_key(item_id, target_language)
        ttl = settings.REDIS_CACHE_TTL
        client.setex(key, ttl, translated_text)
        logger.debug("Redis cache set: %s (TTL: %ds)", key, ttl)
        return True
    except redis.RedisError:
        logger.exception("Error writing to Redis cache")
        return False
