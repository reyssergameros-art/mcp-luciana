"""In-memory cache service for swagger specifications."""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from ....shared.config import settings


class CacheEntry:
    """Represents a cached specification with expiration."""
    
    def __init__(self, data: Dict[str, Any], ttl_seconds: int):
        """
        Initialize cache entry.
        
        Args:
            data: Specification data to cache
            ttl_seconds: Time-to-live in seconds
        """
        self.data = data
        self.created_at = datetime.now()
        self.expires_at = self.created_at + timedelta(seconds=ttl_seconds)
    
    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        return datetime.now() > self.expires_at
    
    def age_seconds(self) -> float:
        """Get the age of this cache entry in seconds."""
        return (datetime.now() - self.created_at).total_seconds()


class SpecificationCache:
    """
    In-memory cache for swagger specifications.
    
    Follows Single Responsibility Principle - only handles caching.
    """
    
    def __init__(self, ttl_seconds: Optional[int] = None):
        """
        Initialize cache.
        
        Args:
            ttl_seconds: Time-to-live for cache entries. Defaults to settings.cache_ttl_seconds
        """
        self.ttl_seconds = ttl_seconds or settings.cache_ttl_seconds
        self.enabled = settings.enable_cache
        self._cache: Dict[str, CacheEntry] = {}
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get specification from cache.
        
        Args:
            key: Cache key (typically the URL)
            
        Returns:
            Cached specification or None if not found/expired
        """
        if not self.enabled:
            return None
        
        entry = self._cache.get(key)
        
        if entry is None:
            return None
        
        if entry.is_expired():
            del self._cache[key]
            return None
        
        return entry.data
    
    def set(self, key: str, data: Dict[str, Any]) -> None:
        """
        Store specification in cache.
        
        Args:
            key: Cache key (typically the URL)
            data: Specification data to cache
        """
        if not self.enabled:
            return
        
        entry = CacheEntry(data, self.ttl_seconds)
        self._cache[key] = entry
    
    def invalidate(self, key: str) -> None:
        """
        Remove specific entry from cache.
        
        Args:
            key: Cache key to invalidate
        """
        if key in self._cache:
            del self._cache[key]
    
    def clear(self) -> None:
        """Clear all cache entries."""
        count = len(self._cache)
        self._cache.clear()
    
    def cleanup_expired(self) -> int:
        """
        Remove expired entries from cache.
        
        Returns:
            Number of entries removed
        """
        expired_keys = [
            key for key, entry in self._cache.items() 
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        total_entries = len(self._cache)
        expired_entries = sum(1 for entry in self._cache.values() if entry.is_expired())
        
        return {
            'enabled': self.enabled,
            'ttl_seconds': self.ttl_seconds,
            'total_entries': total_entries,
            'active_entries': total_entries - expired_entries,
            'expired_entries': expired_entries
        }