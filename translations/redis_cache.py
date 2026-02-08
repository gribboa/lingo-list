"""Redis hot cache layer for translations."""

import logging
import threading
import time

import redis
from django.conf import settings

logger = logging.getLogger(__name__)

# Module-level Redis client (singleton pattern with connection pooling)
_redis_client = None
_redis_lock = threading.Lock()
_last_connection_attempt = 0
_connection_retry_delay = 60  # Retry after 60 seconds


def get_redis_client():
    """Get a Redis client instance with connection pooling.
    
    Returns None if Redis is not available or not configured.
    Uses a singleton pattern with thread-safe initialization.
    Implements retry logic for temporary connection failures.
    """
    global _redis_client, _last_connection_attempt
    
    # Return existing client if available
    if _redis_client is not None:
        return _redis_client
    
    # Check if we should retry connection
    current_time = time.time()
    if current_time - _last_connection_attempt < _connection_retry_delay:
        return None
    
    # Thread-safe client creation
    with _redis_lock:
        # Double-check after acquiring lock
        if _redis_client is not None:
            return _redis_client
        
        _last_connection_attempt = current_time
        
        # Check if REDIS_URL is configured
        redis_url = getattr(settings, 'REDIS_URL', None)
        if not redis_url:
            logger.info("REDIS_URL not configured, hot cache disabled")
            return None
        
        # Create new client
        try:
            client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            # Test connection
            client.ping()
            _redis_client = client
            logger.info("Redis connection established")
            return _redis_client
        except (redis.ConnectionError, redis.TimeoutError) as e:
            logger.warning("Redis connection failed: %s. Will retry in %d seconds", 
                         e, _connection_retry_delay)
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
        ttl = getattr(settings, 'REDIS_CACHE_TTL', 2592000)  # Default: 30 days
        client.setex(key, ttl, translated_text)
        logger.debug("Redis cache set: %s (TTL: %ds)", key, ttl)
        return True
    except redis.RedisError:
        logger.exception("Error writing to Redis cache")
        return False
