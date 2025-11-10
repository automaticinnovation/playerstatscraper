"""Display utilities for formatting output in the terminal."""

from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from tabulate import tabulate


class StatsDisplay:
    """Handles formatting and displaying stats in the terminal."""

    def __init__(self, use_rich: bool = True):
        """
        Initialize the stats display.

        Args:
            use_rich: Whether to use rich library for formatting
        """
        self.use_rich = use_rich
        if use_rich:
            self.console = Console()

    def display_player_stats(self, player_name: str, stats_data: Dict[str, Any],
                            title: Optional[str] = None) -> None:
        """
        Display player statistics.

        Args:
            player_name: Name of the player
            stats_data: Dictionary containing stats
            title: Optional custom title
        """
        if not stats_data or 'stats' not in stats_data:
            self.print_error("No stats data available")
            return

        if title is None:
            year_str = f" ({stats_data.get('year', 'Career')})" if stats_data.get('year') else " (Career)"
            title = f"{player_name}{year_str}"

        stats = stats_data['stats']

        if self.use_rich:
            self._display_rich_stats(title, stats, stats_data)
        else:
            self._display_simple_stats(title, stats)

    def _display_rich_stats(self, title: str, stats: Dict[str, Any],
                           metadata: Dict[str, Any]) -> None:
        """Display stats using rich library."""
        # Create table
        table = Table(title=title, box=box.ROUNDED, show_header=True,
                     header_style="bold magenta")

        table.add_column("Stat", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")

        # Add metadata
        if 'position' in metadata:
            table.add_row("Position", str(metadata['position']))

        if 'player_type' in metadata:
            table.add_row("Player Type", str(metadata['player_type']).title())

        if metadata.get('stat_category'):
            table.add_row("Category", str(metadata['stat_category']).title())

        # Add separator
        if metadata:
            table.add_row("", "")

        # Add stats
        for stat_name, value in stats.items():
            # Format stat name (replace underscores, title case)
            formatted_name = stat_name.replace('_', ' ').title()
            table.add_row(formatted_name, str(value))

        self.console.print(table)

    def _display_simple_stats(self, title: str, stats: Dict[str, Any]) -> None:
        """Display stats using simple table format."""
        print(f"\n{title}")
        print("=" * len(title))

        # Convert to list for tabulate
        data = [[k.replace('_', ' ').title(), v] for k, v in stats.items()]

        print(tabulate(data, headers=["Stat", "Value"], tablefmt="simple"))
        print()

    def display_comparison(self, players_data: Dict[str, Dict[str, Any]],
                          highlight_better: bool = True) -> None:
        """
        Display comparison of multiple players.

        Args:
            players_data: Dictionary with player names as keys
            highlight_better: Whether to highlight better stats
        """
        if not players_data:
            self.print_error("No data to compare")
            return

        if self.use_rich:
            self._display_rich_comparison(players_data, highlight_better)
        else:
            self._display_simple_comparison(players_data)

    def _display_rich_comparison(self, players_data: Dict[str, Dict[str, Any]],
                                highlight_better: bool) -> None:
        """Display player comparison using rich library."""
        # Create table
        table = Table(title="Player Comparison", box=box.DOUBLE,
                     show_header=True, header_style="bold magenta")

        # Add columns
        table.add_column("Stat", style="cyan", no_wrap=True)

        player_names = list(players_data.keys())
        for name in player_names:
            table.add_column(name, style="white")

        # Collect all unique stats
        all_stats = set()
        for data in players_data.values():
            if 'stats' in data:
                all_stats.update(data['stats'].keys())

        # Add rows for each stat
        for stat in sorted(all_stats):
            values = []
            numeric_values = []

            # Collect values from each player
            for player_name in player_names:
                player_data = players_data[player_name]
                stats = player_data.get('stats', {})
                value = stats.get(stat, 'N/A')
                values.append(value)

                # Try to extract numeric value
                if value != 'N/A':
                    try:
                        # Remove common non-numeric characters
                        numeric = str(value).replace('%', '').replace(',', '')
                        numeric_values.append(float(numeric))
                    except (ValueError, AttributeError):
                        numeric_values.append(None)
                else:
                    numeric_values.append(None)

            # Determine best value if highlighting
            best_idx = None
            if highlight_better and numeric_values and any(v is not None for v in numeric_values):
                # Simple heuristic: higher is better (may not always be true)
                valid_values = [(i, v) for i, v in enumerate(numeric_values) if v is not None]
                if valid_values:
                    best_idx = max(valid_values, key=lambda x: x[1])[0]

            # Format stat name
            stat_name = stat.replace('_', ' ').title()

            # Build row with highlighting
            row = [stat_name]
            for i, value in enumerate(values):
                if highlight_better and i == best_idx:
                    row.append(f"[bold green]{value}[/bold green]")
                else:
                    row.append(str(value))

            table.add_row(*row)

        self.console.print(table)

    def _display_simple_comparison(self, players_data: Dict[str, Dict[str, Any]]) -> None:
        """Display player comparison using simple table format."""
        print("\nPlayer Comparison")
        print("=" * 50)

        # Collect all unique stats
        all_stats = set()
        for data in players_data.values():
            if 'stats' in data:
                all_stats.update(data['stats'].keys())

        # Prepare data for tabulate
        headers = ['Stat'] + list(players_data.keys())
        rows = []

        for stat in sorted(all_stats):
            row = [stat.replace('_', ' ').title()]

            for player_name in players_data.keys():
                player_data = players_data[player_name]
                stats = player_data.get('stats', {})
                value = stats.get(stat, 'N/A')
                row.append(str(value))

            rows.append(row)

        print(tabulate(rows, headers=headers, tablefmt="grid"))
        print()

    def display_game_logs(self, game_logs: List[Dict[str, Any]],
                         player_name: str, year: int,
                         max_games: Optional[int] = None) -> None:
        """
        Display game-by-game logs.

        Args:
            game_logs: List of game log dictionaries
            player_name: Player name
            year: Season year
            max_games: Maximum number of games to display
        """
        if not game_logs:
            self.print_error("No game logs available")
            return

        display_logs = game_logs[:max_games] if max_games else game_logs

        if self.use_rich:
            self._display_rich_game_logs(display_logs, player_name, year)
        else:
            self._display_simple_game_logs(display_logs, player_name, year)

        if max_games and len(game_logs) > max_games:
            self.print_info(f"Showing {max_games} of {len(game_logs)} games")

    def _display_rich_game_logs(self, game_logs: List[Dict[str, Any]],
                               player_name: str, year: int) -> None:
        """Display game logs using rich library."""
        title = f"{player_name} - {year} Game Logs"

        table = Table(title=title, box=box.ROUNDED, show_header=True,
                     header_style="bold magenta")

        # Get headers from first game
        if game_logs:
            headers = list(game_logs[0].keys())

            # Add columns
            for header in headers:
                style = "cyan" if header in ['week', 'date', 'game_num', 'opponent'] else "white"
                table.add_column(header.replace('_', ' ').title(), style=style)

            # Add rows
            for log in game_logs:
                row = [str(log.get(h, '')) for h in headers]
                table.add_row(*row)

        self.console.print(table)

    def _display_simple_game_logs(self, game_logs: List[Dict[str, Any]],
                                  player_name: str, year: int) -> None:
        """Display game logs using simple table format."""
        title = f"\n{player_name} - {year} Game Logs"
        print(title)
        print("=" * len(title))

        if not game_logs:
            return

        # Get headers
        headers = list(game_logs[0].keys())
        formatted_headers = [h.replace('_', ' ').title() for h in headers]

        # Prepare rows
        rows = []
        for log in game_logs:
            row = [str(log.get(h, '')) for h in headers]
            rows.append(row)

        print(tabulate(rows, headers=formatted_headers, tablefmt="grid"))
        print()

    def display_search_results(self, players: List[Dict[str, str]]) -> None:
        """
        Display player search results.

        Args:
            players: List of player dictionaries
        """
        if not players:
            self.print_warning("No players found")
            return

        if self.use_rich:
            self._display_rich_search_results(players)
        else:
            self._display_simple_search_results(players)

    def _display_rich_search_results(self, players: List[Dict[str, str]]) -> None:
        """Display search results using rich library."""
        table = Table(title="Search Results", box=box.ROUNDED,
                     show_header=True, header_style="bold magenta")

        table.add_column("#", style="cyan", width=4)
        table.add_column("Name", style="green")
        table.add_column("Position", style="yellow", width=8)
        table.add_column("Years", style="white", width=12)
        table.add_column("Teams", style="blue")

        for i, player in enumerate(players, 1):
            teams_str = ', '.join(player.get('teams', []))
            if len(teams_str) > 40:
                teams_str = teams_str[:37] + "..."

            table.add_row(
                str(i),
                player.get('name', 'Unknown'),
                player.get('position', 'N/A'),
                player.get('years', 'N/A'),
                teams_str or 'N/A'
            )

        self.console.print(table)

    def _display_simple_search_results(self, players: List[Dict[str, str]]) -> None:
        """Display search results using simple table format."""
        print("\nSearch Results:")
        print("=" * 50)

        rows = []
        for i, player in enumerate(players, 1):
            teams_str = ', '.join(player.get('teams', []))
            if len(teams_str) > 40:
                teams_str = teams_str[:37] + "..."

            rows.append([
                i,
                player.get('name', 'Unknown'),
                player.get('position', 'N/A'),
                player.get('years', 'N/A'),
                teams_str or 'N/A'
            ])

        print(tabulate(rows, headers=['#', 'Name', 'Position', 'Years', 'Teams'],
                      tablefmt="simple"))
        print()

    def print_info(self, message: str) -> None:
        """Print an info message."""
        if self.use_rich:
            self.console.print(f"[blue]ℹ {message}[/blue]")
        else:
            print(f"ℹ {message}")

    def print_success(self, message: str) -> None:
        """Print a success message."""
        if self.use_rich:
            self.console.print(f"[green]✓ {message}[/green]")
        else:
            print(f"✓ {message}")

    def print_warning(self, message: str) -> None:
        """Print a warning message."""
        if self.use_rich:
            self.console.print(f"[yellow]⚠ {message}[/yellow]")
        else:
            print(f"⚠ {message}")

    def print_error(self, message: str) -> None:
        """Print an error message."""
        if self.use_rich:
            self.console.print(f"[red]✗ {message}[/red]")
        else:
            print(f"✗ {message}")

    def show_banner(self) -> None:
        """Display application banner."""
        if self.use_rich:
            banner_text = Text("Sports Stats Scraper", style="bold blue")
            subtitle = Text("NFL & MLB Player Statistics Tool", style="italic")

            panel = Panel.fit(
                f"{banner_text}\n{subtitle}",
                border_style="blue"
            )
            self.console.print(panel)
        else:
            print("\n" + "=" * 50)
            print("       Sports Stats Scraper")
            print("   NFL & MLB Player Statistics Tool")
            print("=" * 50 + "\n")

    def show_progress(self, message: str) -> None:
        """Show a progress message."""
        if self.use_rich:
            self.console.print(f"[yellow]⏳ {message}...[/yellow]")
        else:
            print(f"⏳ {message}...")
