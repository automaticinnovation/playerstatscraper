"""Base scraper class with common functionality for all scrapers."""

import time
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any, List
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin, urlparse
import re

from ..utils.cache_manager import CacheManager
from ..utils.logger import Logger
from ..utils.config_manager import ConfigManager


class BaseScraper:
    """Base class for all sports scrapers with common functionality."""

    def __init__(self, config: ConfigManager, cache: CacheManager, logger: Logger):
        """
        Initialize the base scraper.

        Args:
            config: Configuration manager instance
            cache: Cache manager instance
            logger: Logger instance
        """
        self.config = config
        self.cache = cache
        self.logger = logger

        # Scraping settings
        self.user_agent = config.get('scraping.user_agent')
        self.request_delay = config.get('scraping.request_delay', 3)
        self.timeout = config.get('scraping.timeout', 30)
        self.max_retries = config.get('scraping.max_retries', 3)
        self.retry_delay = config.get('scraping.retry_delay', 5)

        # Track last request time for rate limiting
        self.last_request_time = 0

        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

        # Robots.txt parser
        self.robots_parser: Optional[RobotFileParser] = None

    def _check_robots_txt(self, url: str) -> bool:
        """
        Check if URL is allowed by robots.txt.

        Args:
            url: URL to check

        Returns:
            True if allowed, False otherwise
        """
        try:
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

            if self.robots_parser is None:
                self.robots_parser = RobotFileParser()
                robots_url = urljoin(base_url, '/robots.txt')
                self.robots_parser.set_url(robots_url)
                self.robots_parser.read()

            return self.robots_parser.can_fetch(self.user_agent, url)
        except Exception as e:
            self.logger.warning(f"Could not check robots.txt: {e}")
            return True  # If we can't check, assume it's allowed

    def _rate_limit(self) -> None:
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_delay:
            sleep_time = self.request_delay - elapsed
            self.logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)

    def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None,
                      use_cache: bool = True, cache_ttl: Optional[int] = None) -> Optional[str]:
        """
        Make an HTTP request with retry logic and caching.

        Args:
            url: URL to request
            params: Optional query parameters
            use_cache: Whether to use cache
            cache_ttl: Cache time-to-live in seconds

        Returns:
            Response text or None if failed
        """
        # Check cache first
        if use_cache:
            cached_data = self.cache.get(url, params, cache_ttl)
            if cached_data is not None:
                self.logger.log_request(url, cached=True)
                return cached_data

        # Check robots.txt
        if not self._check_robots_txt(url):
            self.logger.warning(f"URL disallowed by robots.txt: {url}")
            return None

        # Rate limiting
        self._rate_limit()

        # Make request with retries
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=self.timeout,
                    allow_redirects=True
                )

                self.last_request_time = time.time()
                self.logger.log_request(url, response.status_code)

                # Check if successful
                if response.status_code == 200:
                    # Cache the response
                    if use_cache:
                        self.cache.set(url, response.text, params)

                    return response.text

                elif response.status_code == 404:
                    self.logger.warning(f"URL not found (404): {url}")
                    return None

                elif response.status_code == 429:
                    # Too many requests - wait longer
                    wait_time = self.retry_delay * (attempt + 1) * 2
                    self.logger.warning(f"Rate limited (429). Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue

                else:
                    self.logger.warning(f"HTTP {response.status_code} for {url}")

            except requests.exceptions.Timeout:
                self.logger.warning(f"Request timeout (attempt {attempt + 1}/{self.max_retries}): {url}")

            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request error (attempt {attempt + 1}/{self.max_retries}): {e}")

            # Wait before retry
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay * (attempt + 1))

        self.logger.error(f"Failed to fetch {url} after {self.max_retries} attempts")
        return None

    def _parse_html(self, html: str) -> Optional[BeautifulSoup]:
        """
        Parse HTML content into BeautifulSoup object.

        Args:
            html: HTML content

        Returns:
            BeautifulSoup object or None if parsing failed
        """
        try:
            return BeautifulSoup(html, 'lxml')
        except Exception as e:
            self.logger.error(f"HTML parsing error: {e}")
            return None

    def _clean_text(self, text: Optional[str]) -> str:
        """
        Clean and normalize text.

        Args:
            text: Text to clean

        Returns:
            Cleaned text
        """
        if text is None:
            return ""

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        # Remove special characters that might cause issues
        text = text.replace('\xa0', ' ')  # Non-breaking space
        text = text.replace('\u200b', '')  # Zero-width space

        return text

    def _extract_number(self, text: str) -> Optional[float]:
        """
        Extract numeric value from text.

        Args:
            text: Text containing a number

        Returns:
            Numeric value or None if not found
        """
        try:
            # Remove common non-numeric characters
            cleaned = re.sub(r'[,$%]', '', text)
            cleaned = cleaned.strip()

            # Handle percentages
            if '%' in text:
                return float(cleaned) / 100

            return float(cleaned)
        except (ValueError, AttributeError):
            return None

    def _normalize_player_name(self, name: str) -> str:
        """
        Normalize player name for searching.

        Args:
            name: Player name

        Returns:
            Normalized name
        """
        # Convert to lowercase
        name = name.lower()

        # Remove special characters
        name = re.sub(r'[^a-z\s\-]', '', name)

        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name)

        return name.strip()

    def close(self) -> None:
        """Close the session and cleanup resources."""
        if hasattr(self, 'session'):
            self.session.close()
