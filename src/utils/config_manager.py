"""Configuration management for the Sports Stats Scraper."""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """Manages application configuration from YAML file."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.

        Args:
            config_path: Path to the config file. If None, uses default location.
        """
        if config_path is None:
            # Default to config.yaml in project root
            self.config_path = Path(__file__).parent.parent.parent / "config.yaml"
        else:
            self.config_path = Path(config_path)

        self.config: Dict[str, Any] = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            if not self.config_path.exists():
                raise FileNotFoundError(f"Config file not found: {self.config_path}")

            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)

            return config if config else {}
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration if file cannot be loaded."""
        return {
            'scraping': {
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'request_delay': 3,
                'timeout': 30,
                'max_retries': 3,
                'retry_delay': 5
            },
            'cache': {
                'enabled': True,
                'directory': './cache',
                'current_season_ttl': 86400,
                'historical_ttl': 2592000,
                'playoff_ttl': 604800
            },
            'logging': {
                'enabled': True,
                'directory': './logs',
                'level': 'INFO',
                'max_file_size': 10485760,
                'backup_count': 5
            },
            'defaults': {
                'sport': 'NFL',
                'stat_type': 'season',
                'stat_category': 'basic',
                'export_format': 'csv'
            },
            'favorites': {
                'nfl': [],
                'mlb': []
            },
            'display': {
                'table_style': 'rich',
                'color_comparisons': True,
                'show_summary': True,
                'max_rows_display': 100
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.

        Args:
            key: Configuration key (e.g., 'scraping.user_agent')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation.

        Args:
            key: Configuration key (e.g., 'defaults.sport')
            value: Value to set
        """
        keys = key.split('.')
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def save(self) -> None:
        """Save current configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            print(f"Error saving config file: {e}")

    def add_favorite(self, sport: str, player_info: Dict[str, str]) -> None:
        """
        Add a player to favorites.

        Args:
            sport: 'nfl' or 'mlb'
            player_info: Dictionary with player information
        """
        sport_lower = sport.lower()
        if sport_lower not in self.config['favorites']:
            self.config['favorites'][sport_lower] = []

        # Check if player already in favorites
        for fav in self.config['favorites'][sport_lower]:
            if fav.get('name') == player_info.get('name'):
                return  # Already in favorites

        self.config['favorites'][sport_lower].append(player_info)
        self.save()

    def remove_favorite(self, sport: str, player_name: str) -> bool:
        """
        Remove a player from favorites.

        Args:
            sport: 'nfl' or 'mlb'
            player_name: Name of the player to remove

        Returns:
            True if removed, False if not found
        """
        sport_lower = sport.lower()
        if sport_lower not in self.config['favorites']:
            return False

        favorites = self.config['favorites'][sport_lower]
        original_length = len(favorites)

        self.config['favorites'][sport_lower] = [
            fav for fav in favorites if fav.get('name') != player_name
        ]

        if len(self.config['favorites'][sport_lower]) < original_length:
            self.save()
            return True

        return False

    def get_favorites(self, sport: str) -> list:
        """
        Get list of favorite players for a sport.

        Args:
            sport: 'nfl' or 'mlb'

        Returns:
            List of favorite players
        """
        sport_lower = sport.lower()
        return self.config.get('favorites', {}).get(sport_lower, [])
