"""Tests for base scraper functionality."""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.scrapers.base_scraper import BaseScraper
from src.utils.config_manager import ConfigManager
from src.utils.cache_manager import CacheManager
from src.utils.logger import Logger


class TestBaseScraper(unittest.TestCase):
    """Test cases for BaseScraper class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = ConfigManager()
        self.cache = CacheManager(enabled=False)  # Disable cache for tests
        self.logger = Logger(enabled=False)  # Disable logging for tests
        self.scraper = BaseScraper(self.config, self.cache, self.logger)

    def test_clean_text(self):
        """Test text cleaning functionality."""
        # Test whitespace removal
        self.assertEqual(self.scraper._clean_text("  hello  world  "), "hello world")

        # Test None handling
        self.assertEqual(self.scraper._clean_text(None), "")

        # Test special characters
        self.assertEqual(self.scraper._clean_text("hello\xa0world"), "hello world")

    def test_extract_number(self):
        """Test number extraction from text."""
        # Test basic number
        self.assertEqual(self.scraper._extract_number("123"), 123.0)

        # Test number with comma
        self.assertEqual(self.scraper._extract_number("1,234"), 1234.0)

        # Test number with dollar sign
        self.assertEqual(self.scraper._extract_number("$123"), 123.0)

        # Test invalid input
        self.assertIsNone(self.scraper._extract_number("abc"))

    def test_normalize_player_name(self):
        """Test player name normalization."""
        # Test basic normalization
        self.assertEqual(self.scraper._normalize_player_name("Patrick Mahomes"), "patrick mahomes")

        # Test special characters
        self.assertEqual(self.scraper._normalize_player_name("O'Neill Jr."), "oneill jr")

        # Test extra whitespace
        self.assertEqual(self.scraper._normalize_player_name("  Mike   Trout  "), "mike trout")

    def tearDown(self):
        """Clean up after tests."""
        self.scraper.close()


class TestCacheManager(unittest.TestCase):
    """Test cases for CacheManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.cache = CacheManager(cache_dir="./test_cache", enabled=True)

    def test_generate_key(self):
        """Test cache key generation."""
        key1 = self.cache._generate_key("http://example.com", {'param': 'value'})
        key2 = self.cache._generate_key("http://example.com", {'param': 'value'})
        key3 = self.cache._generate_key("http://example.com", {'param': 'other'})

        # Same inputs should generate same key
        self.assertEqual(key1, key2)

        # Different inputs should generate different keys
        self.assertNotEqual(key1, key3)

    def test_set_and_get(self):
        """Test setting and getting cache data."""
        url = "http://example.com"
        data = {"test": "data"}

        # Set cache
        self.cache.set(url, data)

        # Get cache (no TTL, should return data)
        cached_data = self.cache.get(url)
        self.assertEqual(cached_data, data)

    def test_cache_expiration(self):
        """Test cache expiration with TTL."""
        import time

        url = "http://example.com"
        data = {"test": "data"}

        # Set cache
        self.cache.set(url, data)

        # Get with very short TTL (should expire)
        time.sleep(0.1)
        cached_data = self.cache.get(url, ttl=0.01)  # 0.01 seconds
        self.assertIsNone(cached_data)

    def tearDown(self):
        """Clean up test cache."""
        self.cache.clear()
        import shutil
        if os.path.exists("./test_cache"):
            shutil.rmtree("./test_cache")


class TestConfigManager(unittest.TestCase):
    """Test cases for ConfigManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = ConfigManager()

    def test_get_nested_value(self):
        """Test getting nested configuration values."""
        # Test valid nested key
        user_agent = self.config.get('scraping.user_agent')
        self.assertIsNotNone(user_agent)
        self.assertIsInstance(user_agent, str)

        # Test default value for missing key
        missing = self.config.get('nonexistent.key', 'default')
        self.assertEqual(missing, 'default')

    def test_set_value(self):
        """Test setting configuration values."""
        self.config.set('test.value', 'test_data')
        self.assertEqual(self.config.get('test.value'), 'test_data')


if __name__ == '__main__':
    unittest.main()
