"""Logging utilities for the Sports Stats Scraper."""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional
from datetime import datetime


class Logger:
    """Custom logger with file and console output."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Singleton pattern to ensure only one logger instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, log_dir: str = "./logs", level: str = "INFO",
                 max_bytes: int = 10485760, backup_count: int = 5,
                 enabled: bool = True):
        """
        Initialize the logger.

        Args:
            log_dir: Directory to store log files
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            max_bytes: Maximum size of log file before rotation
            backup_count: Number of backup files to keep
            enabled: Whether logging is enabled
        """
        # Only initialize once
        if hasattr(self, '_initialized'):
            return

        self._initialized = True
        self.enabled = enabled
        self.log_dir = Path(log_dir)

        if self.enabled:
            self.log_dir.mkdir(parents=True, exist_ok=True)

        # Create logger
        self.logger = logging.getLogger('SportsStatsScraper')
        self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))

        # Remove any existing handlers
        self.logger.handlers.clear()

        if self.enabled:
            # File handler with rotation
            log_file = self.log_dir / f"scraper_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count
            )
            file_handler.setLevel(getattr(logging, level.upper(), logging.INFO))

            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.WARNING)  # Only warnings and above to console

            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            # Add handlers
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def debug(self, message: str) -> None:
        """Log debug message."""
        if self.enabled:
            self.logger.debug(message)

    def info(self, message: str) -> None:
        """Log info message."""
        if self.enabled:
            self.logger.info(message)

    def warning(self, message: str) -> None:
        """Log warning message."""
        if self.enabled:
            self.logger.warning(message)

    def error(self, message: str, exc_info: bool = False) -> None:
        """
        Log error message.

        Args:
            message: Error message
            exc_info: Include exception information
        """
        if self.enabled:
            self.logger.error(message, exc_info=exc_info)

    def critical(self, message: str, exc_info: bool = False) -> None:
        """
        Log critical message.

        Args:
            message: Critical message
            exc_info: Include exception information
        """
        if self.enabled:
            self.logger.critical(message, exc_info=exc_info)

    def log_scrape(self, sport: str, player: str, stat_type: str,
                   success: bool, message: Optional[str] = None) -> None:
        """
        Log a scraping operation.

        Args:
            sport: Sport being scraped (NFL/MLB)
            player: Player name
            stat_type: Type of stats being scraped
            success: Whether the scrape was successful
            message: Optional message
        """
        status = "SUCCESS" if success else "FAILED"
        log_msg = f"[{sport}] {status} - Player: {player}, Type: {stat_type}"

        if message:
            log_msg += f" - {message}"

        if success:
            self.info(log_msg)
        else:
            self.error(log_msg)

    def log_request(self, url: str, status_code: Optional[int] = None,
                    cached: bool = False) -> None:
        """
        Log an HTTP request.

        Args:
            url: URL being requested
            status_code: HTTP status code
            cached: Whether the response was cached
        """
        cache_msg = " (cached)" if cached else ""
        if status_code:
            self.debug(f"Request to {url} - Status: {status_code}{cache_msg}")
        else:
            self.debug(f"Request to {url}{cache_msg}")

    def get_log_files(self) -> list:
        """
        Get list of log files.

        Returns:
            List of log file paths
        """
        if not self.enabled or not self.log_dir.exists():
            return []

        return sorted(self.log_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
