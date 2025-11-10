"""Interactive CLI menu system."""

import sys
import inquirer
from typing import Optional, List, Dict, Any
from thefuzz import fuzz

from ..utils.config_manager import ConfigManager
from ..utils.cache_manager import CacheManager
from ..utils.logger import Logger
from ..utils.display import StatsDisplay
from ..utils.export import DataExporter
from ..scrapers.nfl_scraper import NFLScraper
from ..scrapers.mlb_scraper import MLBScraper


class CLIMenu:
    """Interactive CLI menu for the Sports Stats Scraper."""

    def __init__(self):
        """Initialize the CLI menu."""
        # Initialize utilities
        self.config = ConfigManager()
        self.cache = CacheManager(
            cache_dir=self.config.get('cache.directory'),
            enabled=self.config.get('cache.enabled')
        )
        self.logger = Logger(
            log_dir=self.config.get('logging.directory'),
            level=self.config.get('logging.level'),
            max_bytes=self.config.get('logging.max_file_size'),
            backup_count=self.config.get('logging.backup_count'),
            enabled=self.config.get('logging.enabled')
        )
        self.display = StatsDisplay(
            use_rich=self.config.get('display.table_style') == 'rich'
        )
        self.exporter = DataExporter()

        # Initialize scrapers
        self.nfl_scraper = NFLScraper(self.config, self.cache, self.logger)
        self.mlb_scraper = MLBScraper(self.config, self.cache, self.logger)

        # Current session data
        self.current_sport = None
        self.current_scraper = None

    def run(self) -> None:
        """Run the main menu loop."""
        try:
            self.display.show_banner()
            self.main_menu()
        except KeyboardInterrupt:
            self.display.print_info("\nExiting... Goodbye!")
            sys.exit(0)
        except Exception as e:
            self.display.print_error(f"Unexpected error: {e}")
            self.logger.error(f"Unexpected error in main menu: {e}", exc_info=True)
            sys.exit(1)
        finally:
            # Cleanup
            if hasattr(self, 'nfl_scraper'):
                self.nfl_scraper.close()
            if hasattr(self, 'mlb_scraper'):
                self.mlb_scraper.close()

    def main_menu(self) -> None:
        """Display and handle the main menu."""
        while True:
            questions = [
                inquirer.List(
                    'action',
                    message="What would you like to do?",
                    choices=[
                        ('Search for player stats', 'search'),
                        ('Compare players', 'compare'),
                        ('View favorites', 'favorites'),
                        ('Manage cache', 'cache'),
                        ('Settings', 'settings'),
                        ('Exit', 'exit')
                    ]
                )
            ]

            answers = inquirer.prompt(questions)
            if not answers:
                continue

            action = answers['action']

            if action == 'search':
                self.search_player_flow()
            elif action == 'compare':
                self.compare_players_flow()
            elif action == 'favorites':
                self.favorites_menu()
            elif action == 'cache':
                self.cache_menu()
            elif action == 'settings':
                self.settings_menu()
            elif action == 'exit':
                self.display.print_info("Goodbye!")
                sys.exit(0)

    def search_player_flow(self) -> None:
        """Handle the player search workflow."""
        # Select sport
        sport = self._select_sport()
        if not sport:
            return

        self.current_sport = sport
        self.current_scraper = self.nfl_scraper if sport == 'NFL' else self.mlb_scraper

        # Get player name
        questions = [
            inquirer.Text(
                'player_name',
                message=f"Enter {sport} player name"
            )
        ]

        answers = inquirer.prompt(questions)
        if not answers or not answers['player_name']:
            return

        player_name = answers['player_name'].strip()

        # Search for player
        self.display.show_progress(f"Searching for {player_name}")
        players = self.current_scraper.search_player(player_name)

        if not players:
            self.display.print_warning(f"No players found matching '{player_name}'")
            return

        # Display search results
        self.display.display_search_results(players)

        # Let user select a player
        player = self._select_player(players)
        if not player:
            return

        # Get stat preferences
        stat_type = self._select_stat_type()
        if not stat_type:
            return

        # Handle different stat types
        if stat_type == 'season':
            self._get_season_stats(player)
        elif stat_type == 'career':
            self._get_career_stats(player)
        elif stat_type == 'game_logs':
            self._get_game_logs(player)
        elif stat_type == 'playoffs':
            self._get_playoff_stats(player)

    def _select_sport(self) -> Optional[str]:
        """Let user select a sport."""
        default_sport = self.config.get('defaults.sport', 'NFL')

        questions = [
            inquirer.List(
                'sport',
                message="Select sport",
                choices=['NFL', 'MLB'],
                default=default_sport
            )
        ]

        answers = inquirer.prompt(questions)
        return answers['sport'] if answers else None

    def _select_player(self, players: List[Dict[str, str]]) -> Optional[Dict[str, str]]:
        """Let user select a player from search results."""
        if len(players) == 1:
            # Auto-select if only one result
            return players[0]

        # Create choices with full player info
        choices = []
        for i, player in enumerate(players, 1):
            label = f"{i}. {player['name']}"
            if player.get('position'):
                label += f" ({player['position']})"
            if player.get('years'):
                label += f" - {player['years']}"

            choices.append((label, player))

        choices.append(('Cancel', None))

        questions = [
            inquirer.List(
                'player',
                message="Select a player",
                choices=choices
            )
        ]

        answers = inquirer.prompt(questions)
        return answers['player'] if answers else None

    def _select_stat_type(self) -> Optional[str]:
        """Let user select stat type."""
        questions = [
            inquirer.List(
                'stat_type',
                message="Select stat type",
                choices=[
                    ('Season stats', 'season'),
                    ('Career stats', 'career'),
                    ('Game logs', 'game_logs'),
                    ('Playoff stats', 'playoffs'),
                    ('Cancel', None)
                ],
                default=self.config.get('defaults.stat_type', 'season')
            )
        ]

        answers = inquirer.prompt(questions)
        return answers['stat_type'] if answers else None

    def _select_stat_category(self) -> Optional[str]:
        """Let user select stat category (basic/advanced)."""
        questions = [
            inquirer.List(
                'category',
                message="Select stat category",
                choices=[
                    ('Basic stats', 'basic'),
                    ('Advanced metrics', 'advanced')
                ],
                default=self.config.get('defaults.stat_category', 'basic')
            )
        ]

        answers = inquirer.prompt(questions)
        return answers['category'] if answers else None

    def _get_season_stats(self, player: Dict[str, str]) -> None:
        """Get season stats for a player."""
        # Ask for year
        questions = [
            inquirer.Text(
                'year',
                message="Enter season year (or leave blank for current season)",
                validate=lambda _, x: x == '' or (x.isdigit() and 1900 <= int(x) <= 2100)
            )
        ]

        answers = inquirer.prompt(questions)
        if not answers:
            return

        year = int(answers['year']) if answers['year'] else None

        # Select stat category
        category = self._select_stat_category()
        if not category:
            return

        # Fetch stats
        self.display.show_progress(f"Fetching stats for {player['name']}")

        stats_data = self.current_scraper.get_season_stats(
            player['player_id'],
            year=year,
            stat_category=category
        )

        if not stats_data:
            self.display.print_error("Could not fetch stats")
            self.logger.log_scrape(
                self.current_sport,
                player['name'],
                f"season_{year or 'current'}",
                False,
                "No data returned"
            )
            return

        # Display stats
        self.display.display_player_stats(player['name'], stats_data)

        # Log success
        self.logger.log_scrape(
            self.current_sport,
            player['name'],
            f"season_{year or 'current'}",
            True
        )

        # Ask if user wants to export
        self._offer_export({player['name']: stats_data}, f"{player['name']}_season_{year or 'current'}")

        # Ask if user wants to add to favorites
        self._offer_add_favorite(player)

    def _get_career_stats(self, player: Dict[str, str]) -> None:
        """Get career stats for a player."""
        # Select stat category
        category = self._select_stat_category()
        if not category:
            return

        # Fetch stats
        self.display.show_progress(f"Fetching career stats for {player['name']}")

        stats_data = self.current_scraper.get_season_stats(
            player['player_id'],
            year=None,  # None for career stats
            stat_category=category
        )

        if not stats_data:
            self.display.print_error("Could not fetch career stats")
            self.logger.log_scrape(
                self.current_sport,
                player['name'],
                "career",
                False,
                "No data returned"
            )
            return

        # Display stats
        self.display.display_player_stats(player['name'], stats_data, f"{player['name']} - Career Stats")

        # Log success
        self.logger.log_scrape(
            self.current_sport,
            player['name'],
            "career",
            True
        )

        # Offer export
        self._offer_export({player['name']: stats_data}, f"{player['name']}_career")

        # Offer to add to favorites
        self._offer_add_favorite(player)

    def _get_game_logs(self, player: Dict[str, str]) -> None:
        """Get game logs for a player."""
        # Ask for year
        questions = [
            inquirer.Text(
                'year',
                message="Enter season year",
                validate=lambda _, x: x.isdigit() and 1900 <= int(x) <= 2100
            )
        ]

        answers = inquirer.prompt(questions)
        if not answers or not answers['year']:
            return

        year = int(answers['year'])

        # Fetch game logs
        self.display.show_progress(f"Fetching game logs for {player['name']}")

        game_logs = self.current_scraper.get_game_logs(player['player_id'], year)

        if not game_logs:
            self.display.print_error("Could not fetch game logs")
            self.logger.log_scrape(
                self.current_sport,
                player['name'],
                f"game_logs_{year}",
                False,
                "No data returned"
            )
            return

        # Display game logs
        max_display = self.config.get('display.max_rows_display', 100)
        self.display.display_game_logs(game_logs, player['name'], year, max_display)

        # Log success
        self.logger.log_scrape(
            self.current_sport,
            player['name'],
            f"game_logs_{year}",
            True,
            f"{len(game_logs)} games"
        )

        # Offer export
        questions = [
            inquirer.Confirm(
                'export',
                message="Would you like to export these game logs?",
                default=False
            )
        ]

        answers = inquirer.prompt(questions)
        if answers and answers['export']:
            self._export_game_logs(game_logs, player['name'], year)

    def _get_playoff_stats(self, player: Dict[str, str]) -> None:
        """Get playoff stats for a player (MLB only for now)."""
        if self.current_sport != 'MLB':
            self.display.print_warning("Playoff stats are currently only available for MLB")
            return

        # Select stat category
        category = self._select_stat_category()
        if not category:
            return

        # Fetch stats
        self.display.show_progress(f"Fetching playoff stats for {player['name']}")

        stats_data = self.mlb_scraper.get_playoff_stats(
            player['player_id'],
            stat_category=category
        )

        if not stats_data:
            self.display.print_error("Could not fetch playoff stats (player may not have playoff experience)")
            return

        # Display stats
        self.display.display_player_stats(player['name'], stats_data, f"{player['name']} - Playoff Stats")

        # Offer export
        self._offer_export({player['name']: stats_data}, f"{player['name']}_playoffs")

    def compare_players_flow(self) -> None:
        """Handle player comparison workflow."""
        # Select sport
        sport = self._select_sport()
        if not sport:
            return

        self.current_sport = sport
        self.current_scraper = self.nfl_scraper if sport == 'NFL' else self.mlb_scraper

        # Get number of players to compare
        questions = [
            inquirer.Text(
                'num_players',
                message="How many players to compare?",
                validate=lambda _, x: x.isdigit() and 2 <= int(x) <= 5,
                default='2'
            )
        ]

        answers = inquirer.prompt(questions)
        if not answers:
            return

        num_players = int(answers['num_players'])

        # Collect players
        players = []
        for i in range(num_players):
            self.display.print_info(f"\nPlayer {i+1} of {num_players}")

            questions = [
                inquirer.Text(
                    'player_name',
                    message=f"Enter player {i+1} name"
                )
            ]

            answers = inquirer.prompt(questions)
            if not answers or not answers['player_name']:
                return

            player_name = answers['player_name'].strip()

            # Search for player
            self.display.show_progress(f"Searching for {player_name}")
            search_results = self.current_scraper.search_player(player_name)

            if not search_results:
                self.display.print_warning(f"No players found matching '{player_name}'")
                continue

            if len(search_results) > 1:
                self.display.display_search_results(search_results)
                player = self._select_player(search_results)
            else:
                player = search_results[0]

            if player:
                players.append(player)

        if len(players) < 2:
            self.display.print_error("Need at least 2 players to compare")
            return

        # Get stat preferences
        questions = [
            inquirer.Text(
                'year',
                message="Enter season year (or leave blank for career stats)",
                validate=lambda _, x: x == '' or (x.isdigit() and 1900 <= int(x) <= 2100)
            )
        ]

        answers = inquirer.prompt(questions)
        if not answers:
            return

        year = int(answers['year']) if answers['year'] else None

        category = self._select_stat_category()
        if not category:
            return

        # Fetch stats for all players
        comparison_data = {}

        for player in players:
            self.display.show_progress(f"Fetching stats for {player['name']}")

            stats_data = self.current_scraper.get_season_stats(
                player['player_id'],
                year=year,
                stat_category=category
            )

            if stats_data:
                comparison_data[player['name']] = stats_data
            else:
                self.display.print_warning(f"Could not fetch stats for {player['name']}")

        if len(comparison_data) < 2:
            self.display.print_error("Could not fetch stats for enough players")
            return

        # Display comparison
        self.display.display_comparison(
            comparison_data,
            highlight_better=self.config.get('display.color_comparisons', True)
        )

        # Offer export
        self._offer_export(comparison_data, f"comparison_{year or 'career'}")

    def _offer_export(self, data: Dict[str, Any], default_filename: str) -> None:
        """Offer to export data."""
        questions = [
            inquirer.Confirm(
                'export',
                message="Would you like to export this data?",
                default=False
            )
        ]

        answers = inquirer.prompt(questions)
        if not answers or not answers['export']:
            return

        # Select format
        questions = [
            inquirer.List(
                'format',
                message="Select export format",
                choices=['CSV', 'JSON'],
                default=self.config.get('defaults.export_format', 'csv').upper()
            ),
            inquirer.Text(
                'filename',
                message="Enter filename (without extension)",
                default=default_filename.replace(' ', '_').lower()
            )
        ]

        answers = inquirer.prompt(questions)
        if not answers:
            return

        try:
            filepath = self.exporter.export_comparison(
                data,
                filename=answers['filename'],
                format=answers['format'].lower()
            )

            self.display.print_success(f"Data exported to: {filepath}")

        except Exception as e:
            self.display.print_error(f"Export failed: {e}")
            self.logger.error(f"Export error: {e}", exc_info=True)

    def _export_game_logs(self, game_logs: List[Dict[str, Any]], player_name: str, year: int) -> None:
        """Export game logs."""
        questions = [
            inquirer.List(
                'format',
                message="Select export format",
                choices=['CSV', 'JSON'],
                default='CSV'
            )
        ]

        answers = inquirer.prompt(questions)
        if not answers:
            return

        try:
            filepath = self.exporter.export_game_logs(
                game_logs,
                player_name,
                year,
                format=answers['format'].lower()
            )

            self.display.print_success(f"Game logs exported to: {filepath}")

        except Exception as e:
            self.display.print_error(f"Export failed: {e}")
            self.logger.error(f"Export error: {e}", exc_info=True)

    def _offer_add_favorite(self, player: Dict[str, str]) -> None:
        """Offer to add player to favorites."""
        questions = [
            inquirer.Confirm(
                'add_favorite',
                message=f"Add {player['name']} to favorites?",
                default=False
            )
        ]

        answers = inquirer.prompt(questions)
        if answers and answers['add_favorite']:
            self.config.add_favorite(self.current_sport.lower(), player)
            self.display.print_success(f"{player['name']} added to favorites!")

    def favorites_menu(self) -> None:
        """Display and manage favorites."""
        # Select sport
        sport = self._select_sport()
        if not sport:
            return

        favorites = self.config.get_favorites(sport)

        if not favorites:
            self.display.print_info(f"No {sport} favorites saved yet")
            return

        # Display favorites
        self.display.print_info(f"\n{sport} Favorites:")
        for i, fav in enumerate(favorites, 1):
            print(f"{i}. {fav['name']} ({fav.get('position', 'N/A')})")

        # Menu options
        questions = [
            inquirer.List(
                'action',
                message="What would you like to do?",
                choices=[
                    ('View stats for a favorite', 'view'),
                    ('Remove a favorite', 'remove'),
                    ('Back to main menu', 'back')
                ]
            )
        ]

        answers = inquirer.prompt(questions)
        if not answers or answers['action'] == 'back':
            return

        if answers['action'] == 'remove':
            # Select favorite to remove
            choices = [(f"{fav['name']}", fav) for fav in favorites]
            questions = [
                inquirer.List('favorite', message="Select favorite to remove", choices=choices)
            ]
            answers = inquirer.prompt(questions)
            if answers:
                self.config.remove_favorite(sport.lower(), answers['favorite']['name'])
                self.display.print_success(f"{answers['favorite']['name']} removed from favorites")

    def cache_menu(self) -> None:
        """Display cache management menu."""
        cache_info = self.cache.get_cache_info()

        self.display.print_info("\nCache Information:")
        print(f"  Directory: {cache_info.get('directory')}")
        print(f"  Enabled: {cache_info.get('enabled')}")
        print(f"  Files: {cache_info.get('file_count')}")
        print(f"  Size: {cache_info.get('total_size_mb')} MB")

        questions = [
            inquirer.List(
                'action',
                message="What would you like to do?",
                choices=[
                    ('Clear all cache', 'clear_all'),
                    ('Clear old cache (>30 days)', 'clear_old'),
                    ('Back to main menu', 'back')
                ]
            )
        ]

        answers = inquirer.prompt(questions)
        if not answers or answers['action'] == 'back':
            return

        if answers['action'] == 'clear_all':
            confirm = inquirer.prompt([
                inquirer.Confirm('confirm', message="Are you sure?", default=False)
            ])
            if confirm and confirm['confirm']:
                count = self.cache.clear()
                self.display.print_success(f"Cleared {count} cache files")

        elif answers['action'] == 'clear_old':
            count = self.cache.clear(older_than=2592000)  # 30 days
            self.display.print_success(f"Cleared {count} old cache files")

    def settings_menu(self) -> None:
        """Display settings menu."""
        self.display.print_info("\nSettings menu - Coming soon!")
        self.display.print_info("Current settings are in config.yaml")
