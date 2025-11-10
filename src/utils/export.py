"""Export utilities for saving stats to CSV and JSON formats."""

import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class DataExporter:
    """Handles exporting player stats to various formats."""

    def __init__(self, output_dir: str = "./exports"):
        """
        Initialize the data exporter.

        Args:
            output_dir: Directory to save exported files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_to_json(self, data: Any, filename: Optional[str] = None,
                       pretty: bool = True) -> str:
        """
        Export data to JSON format.

        Args:
            data: Data to export
            filename: Custom filename (None for auto-generated)
            pretty: Whether to format JSON with indentation

        Returns:
            Path to the exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"stats_export_{timestamp}.json"

        if not filename.endswith('.json'):
            filename += '.json'

        filepath = self.output_dir / filename

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                if pretty:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(data, f, ensure_ascii=False)

            return str(filepath)

        except Exception as e:
            raise Exception(f"Error exporting to JSON: {e}")

    def export_to_csv(self, data: Any, filename: Optional[str] = None) -> str:
        """
        Export data to CSV format.

        Args:
            data: Data to export (dict, list of dicts, or dict with stats)
            filename: Custom filename (None for auto-generated)

        Returns:
            Path to the exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"stats_export_{timestamp}.csv"

        if not filename.endswith('.csv'):
            filename += '.csv'

        filepath = self.output_dir / filename

        try:
            # Convert data to list of dicts format
            rows = self._prepare_csv_data(data)

            if not rows:
                raise ValueError("No data to export")

            # Get all unique keys for headers
            headers = []
            for row in rows:
                for key in row.keys():
                    if key not in headers:
                        headers.append(key)

            # Write CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(rows)

            return str(filepath)

        except Exception as e:
            raise Exception(f"Error exporting to CSV: {e}")

    def _prepare_csv_data(self, data: Any) -> List[Dict[str, Any]]:
        """
        Prepare data for CSV export by converting to list of dicts.

        Args:
            data: Input data in various formats

        Returns:
            List of dictionaries ready for CSV export
        """
        # If already a list of dicts, return as is
        if isinstance(data, list) and all(isinstance(item, dict) for item in data):
            return self._flatten_dicts(data)

        # If a single dict, check if it has nested stats
        if isinstance(data, dict):
            # Check for common stat structures
            if 'stats' in data and isinstance(data['stats'], dict):
                # Single player stats
                flattened = {**data}
                flattened.update(flattened.pop('stats'))
                return [flattened]

            # Check if it's a dict of player stats
            if all(isinstance(v, dict) for v in data.values()):
                # Multiple players or comparison
                rows = []
                for player_name, player_data in data.items():
                    if isinstance(player_data, dict):
                        if 'stats' in player_data:
                            row = {'player': player_name}
                            row.update(player_data.get('stats', {}))
                            rows.append(row)
                        else:
                            row = {'player': player_name}
                            row.update(player_data)
                            rows.append(row)
                return rows

            # Single flat dict
            return [data]

        return []

    def _flatten_dicts(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Flatten nested dictionaries for CSV export."""
        flattened = []

        for item in data:
            flat_item = {}
            for key, value in item.items():
                if isinstance(value, dict):
                    # Flatten nested dict
                    for nested_key, nested_value in value.items():
                        flat_item[f"{key}_{nested_key}"] = nested_value
                elif isinstance(value, list):
                    # Convert list to string
                    flat_item[key] = ', '.join(str(v) for v in value)
                else:
                    flat_item[key] = value

            flattened.append(flat_item)

        return flattened

    def export_comparison(self, players_data: Dict[str, Any], filename: Optional[str] = None,
                         format: str = 'csv') -> str:
        """
        Export comparison data for multiple players.

        Args:
            players_data: Dictionary with player names as keys
            filename: Custom filename
            format: 'csv' or 'json'

        Returns:
            Path to the exported file
        """
        if format.lower() == 'json':
            return self.export_to_json(players_data, filename)
        else:
            # Convert to comparable CSV format
            rows = []
            for player_name, player_data in players_data.items():
                row = {'player_name': player_name}

                if isinstance(player_data, dict):
                    # Add metadata
                    for key in ['position', 'year', 'stat_category', 'player_type']:
                        if key in player_data:
                            row[key] = player_data[key]

                    # Add stats
                    if 'stats' in player_data and isinstance(player_data['stats'], dict):
                        row.update(player_data['stats'])

                rows.append(row)

            return self.export_to_csv(rows, filename)

    def export_game_logs(self, game_logs: List[Dict[str, Any]], player_name: str,
                        year: int, filename: Optional[str] = None,
                        format: str = 'csv') -> str:
        """
        Export game logs for a player.

        Args:
            game_logs: List of game log dictionaries
            player_name: Name of the player
            year: Season year
            filename: Custom filename
            format: 'csv' or 'json'

        Returns:
            Path to the exported file
        """
        if filename is None:
            safe_name = player_name.replace(' ', '_').lower()
            filename = f"{safe_name}_gamelogs_{year}"

        # Columns to exclude from export (case-insensitive matching)
        excluded_columns = [
            'player_game_num',
            'game_num',
            'rk',  # Rank/game number
            'team_game',
            'game_location',
            'game_location_indicator',
            'snap_counts_defense',
            'snap_counts_def_pct',
            'snap_counts_special_teams',
            'snap_counts_st_pct',
            'snap_counts_offense',
            'snap_counts_off_pct',
            'def_snaps',
            'def_snap_pct',
            'st_snaps',
            'st_snap_pct'
        ]

        # Add metadata to each game log and filter out unwanted columns
        enriched_logs = []
        for log in game_logs:
            enriched_log = {
                'player': player_name,
                'season': year
            }
            # Add log data, excluding unwanted columns
            for key, value in log.items():
                # Normalize key for comparison (lowercase, no spaces/underscores)
                normalized_key = key.lower().replace(' ', '').replace('_', '')
                # Check if key should be excluded
                should_exclude = any(
                    excl.lower().replace('_', '') in normalized_key
                    for excl in excluded_columns
                )
                if not should_exclude:
                    enriched_log[key] = value

            enriched_logs.append(enriched_log)

        if format.lower() == 'json':
            return self.export_to_json(enriched_logs, filename)
        else:
            return self.export_to_csv(enriched_logs, filename)

    def get_export_info(self) -> Dict[str, Any]:
        """
        Get information about exported files.

        Returns:
            Dictionary with export directory info
        """
        if not self.output_dir.exists():
            return {
                'directory': str(self.output_dir),
                'exists': False,
                'file_count': 0,
                'files': []
            }

        files = list(self.output_dir.glob("*"))
        file_info = []

        for f in files:
            file_info.append({
                'name': f.name,
                'size': f.stat().st_size,
                'modified': datetime.fromtimestamp(f.stat().st_mtime).isoformat()
            })

        return {
            'directory': str(self.output_dir),
            'exists': True,
            'file_count': len(files),
            'files': sorted(file_info, key=lambda x: x['modified'], reverse=True)
        }
