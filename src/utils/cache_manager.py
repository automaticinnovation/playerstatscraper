"""Cache management for storing scraped data."""

import os
import json
import hashlib
import time
from pathlib import Path
from typing import Optional, Any, Dict
from datetime import datetime


class CacheManager:
    """Manages caching of scraped data to reduce redundant requests."""

    def __init__(self, cache_dir: str = "./cache", enabled: bool = True):
        """
        Initialize the cache manager.

        Args:
            cache_dir: Directory to store cache files
            enabled: Whether caching is enabled
        """
        self.cache_dir = Path(cache_dir)
        self.enabled = enabled

        if self.enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _generate_key(self, url: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a unique cache key from URL and parameters.

        Args:
            url: The URL being cached
            params: Optional parameters

        Returns:
            MD5 hash of the URL and parameters
        """
        cache_string = url
        if params:
            cache_string += str(sorted(params.items()))

        return hashlib.md5(cache_string.encode()).hexdigest()

    def _get_cache_path(self, key: str) -> Path:
        """Get the file path for a cache key."""
        return self.cache_dir / f"{key}.json"

    def get(self, url: str, params: Optional[Dict[str, Any]] = None,
            ttl: Optional[int] = None) -> Optional[Any]:
        """
        Retrieve data from cache if available and not expired.

        Args:
            url: The URL to check cache for
            params: Optional parameters used in the request
            ttl: Time to live in seconds (None = no expiration)

        Returns:
            Cached data if available and valid, None otherwise
        """
        if not self.enabled:
            return None

        key = self._generate_key(url, params)
        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)

            # Check if cache has expired
            if ttl is not None:
                cached_time = cache_data.get('timestamp', 0)
                if time.time() - cached_time > ttl:
                    # Cache expired, remove it
                    cache_path.unlink()
                    return None

            return cache_data.get('data')

        except (json.JSONDecodeError, KeyError, IOError):
            # Invalid cache file, remove it
            if cache_path.exists():
                cache_path.unlink()
            return None

    def set(self, url: str, data: Any, params: Optional[Dict[str, Any]] = None,
            metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Store data in cache.

        Args:
            url: The URL being cached
            data: The data to cache
            params: Optional parameters used in the request
            metadata: Optional metadata to store with the cache
        """
        if not self.enabled:
            return

        key = self._generate_key(url, params)
        cache_path = self._get_cache_path(key)

        cache_data = {
            'url': url,
            'params': params,
            'timestamp': time.time(),
            'cached_at': datetime.now().isoformat(),
            'data': data,
            'metadata': metadata or {}
        }

        try:
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except (IOError, TypeError) as e:
            print(f"Warning: Could not write to cache: {e}")

    def clear(self, older_than: Optional[int] = None) -> int:
        """
        Clear cache files.

        Args:
            older_than: Only clear files older than this many seconds (None = clear all)

        Returns:
            Number of files deleted
        """
        if not self.enabled:
            return 0

        count = 0
        current_time = time.time()

        for cache_file in self.cache_dir.glob("*.json"):
            try:
                if older_than is not None:
                    # Check file modification time
                    file_mtime = cache_file.stat().st_mtime
                    if current_time - file_mtime < older_than:
                        continue

                cache_file.unlink()
                count += 1
            except (IOError, OSError):
                continue

        return count

    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get information about the cache.

        Returns:
            Dictionary with cache statistics
        """
        if not self.enabled or not self.cache_dir.exists():
            return {
                'enabled': False,
                'file_count': 0,
                'total_size': 0
            }

        cache_files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files)

        return {
            'enabled': True,
            'directory': str(self.cache_dir),
            'file_count': len(cache_files),
            'total_size': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        }

    def invalidate(self, url: str, params: Optional[Dict[str, Any]] = None) -> bool:
        """
        Invalidate (remove) a specific cache entry.

        Args:
            url: The URL to invalidate
            params: Optional parameters

        Returns:
            True if cache was removed, False if not found
        """
        if not self.enabled:
            return False

        key = self._generate_key(url, params)
        cache_path = self._get_cache_path(key)

        if cache_path.exists():
            try:
                cache_path.unlink()
                return True
            except IOError:
                return False

        return False
