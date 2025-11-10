"""NFL stats scraper for Pro Football Reference."""

import re
from typing import Dict, List, Optional, Any, Tuple
from bs4 import BeautifulSoup
from datetime import datetime

from .base_scraper import BaseScraper


class NFLScraper(BaseScraper):
    """Scraper for NFL player statistics from Pro Football Reference."""

    BASE_URL = "https://www.pro-football-reference.com"

    # Position mappings
    OFFENSIVE_POSITIONS = {'QB', 'RB', 'WR', 'TE', 'FB'}
    DEFENSIVE_POSITIONS = {'DE', 'DT', 'NT', 'LB', 'MLB', 'OLB', 'ILB', 'CB', 'S', 'SS', 'FS', 'DB'}
    SPECIAL_TEAMS = {'K', 'P', 'LS'}

    def __init__(self, config, cache, logger):
        """Initialize NFL scraper."""
        super().__init__(config, cache, logger)
        self.current_year = datetime.now().year

    def search_player(self, player_name: str) -> List[Dict[str, str]]:
        """
        Search for a player and return possible matches.

        Args:
            player_name: Name of the player to search

        Returns:
            List of player matches with metadata
        """
        self.logger.info(f"Searching for NFL player: {player_name}")

        # Pro Football Reference uses player IDs in format: LastFiXXNN
        # where XX are first 2 letters of first name, NN is sequential number
        # We'll search using their search page

        search_url = f"{self.BASE_URL}/search/search.fcgi"
        params = {'search': player_name}

        html = self._make_request(search_url, params=params)
        if not html:
            return []

        soup = self._parse_html(html)
        if not soup:
            return []

        players = []

        # Check if we were redirected directly to a player page
        if '/players/' in soup.find('link', {'rel': 'canonical'}).get('href', ''):
            player_info = self._extract_player_from_page(soup)
            if player_info:
                return [player_info]

        # Otherwise, parse search results
        search_results = soup.find('div', {'id': 'search_results'})
        if not search_results:
            return []

        # Find player results
        player_section = search_results.find('div', {'id': 'players'})
        if not player_section:
            return []

        items = player_section.find_all('div', class_='search-item')

        for item in items:
            try:
                link = item.find('div', class_='search-item-name').find('a')
                if not link:
                    continue

                name = self._clean_text(link.text)
                url = link.get('href', '')
                player_id = url.split('/')[-1].replace('.htm', '')

                # Extract metadata from the description
                desc = item.find('div', class_='search-item-desc')
                position = ""
                years = ""
                teams = []

                if desc:
                    desc_text = self._clean_text(desc.text)

                    # Extract position
                    pos_match = re.search(r'\(([A-Z]{1,3})\)', desc_text)
                    if pos_match:
                        position = pos_match.group(1)

                    # Extract years
                    years_match = re.search(r'(\d{4})-(\d{4}|\w+)', desc_text)
                    if years_match:
                        years = f"{years_match.group(1)}-{years_match.group(2)}"

                    # Extract teams
                    team_section = re.search(r'with (.+)', desc_text)
                    if team_section:
                        teams = [t.strip() for t in team_section.group(1).split(',')]

                players.append({
                    'name': name,
                    'player_id': player_id,
                    'url': self.BASE_URL + url if not url.startswith('http') else url,
                    'position': position,
                    'years': years,
                    'teams': teams[:3] if len(teams) > 3 else teams  # Limit to 3 teams
                })

            except Exception as e:
                self.logger.warning(f"Error parsing search item: {e}")
                continue

        return players

    def _extract_player_from_page(self, soup: BeautifulSoup) -> Optional[Dict[str, str]]:
        """Extract player information from their main page."""
        try:
            # Get player name
            h1 = soup.find('h1')
            if not h1:
                return None

            name = self._clean_text(h1.text.replace('\\n', ''))

            # Get URL
            url = soup.find('link', {'rel': 'canonical'}).get('href', '')
            player_id = url.split('/')[-1].replace('.htm', '')

            # Get position from the info box
            position = ""
            info_div = soup.find('div', {'id': 'meta'})
            if info_div:
                for p in info_div.find_all('p'):
                    if 'Position' in p.text:
                        pos_text = self._clean_text(p.text)
                        pos_match = re.search(r'Position:\s*([A-Z]{1,3})', pos_text)
                        if pos_match:
                            position = pos_match.group(1)
                        break

            return {
                'name': name,
                'player_id': player_id,
                'url': url,
                'position': position,
                'years': '',
                'teams': []
            }

        except Exception as e:
            self.logger.warning(f"Error extracting player from page: {e}")
            return None

    def get_season_stats(self, player_id: str, year: Optional[int] = None,
                        stat_category: str = 'basic') -> Optional[Dict[str, Any]]:
        """
        Get season statistics for a player.

        Args:
            player_id: Player ID (e.g., 'MahoPa00')
            year: Season year (None for career stats)
            stat_category: 'basic' or 'advanced'

        Returns:
            Dictionary with player stats or None if not found
        """
        url = f"{self.BASE_URL}/players/{player_id[0]}/{player_id}.htm"

        cache_ttl = self.config.get('cache.current_season_ttl') if year == self.current_year \
                    else self.config.get('cache.historical_ttl')

        html = self._make_request(url, use_cache=True, cache_ttl=cache_ttl)
        if not html:
            return None

        soup = self._parse_html(html)
        if not soup:
            return None

        # Determine player position
        position = self._get_player_position(soup)

        # Get appropriate stats based on position
        if position in self.OFFENSIVE_POSITIONS:
            return self._parse_offensive_stats(soup, position, year, stat_category)
        elif position in self.DEFENSIVE_POSITIONS:
            return self._parse_defensive_stats(soup, position, year, stat_category)
        elif position in self.SPECIAL_TEAMS:
            return self._parse_special_teams_stats(soup, position, year, stat_category)
        else:
            self.logger.warning(f"Unknown position: {position}")
            return None

    def _get_player_position(self, soup: BeautifulSoup) -> str:
        """Extract player position from page."""
        meta_div = soup.find('div', {'id': 'meta'})
        if not meta_div:
            return ""

        for p in meta_div.find_all('p'):
            if 'Position' in p.text:
                pos_text = self._clean_text(p.text)
                pos_match = re.search(r'Position:\s*([A-Z]{1,3})', pos_text)
                if pos_match:
                    return pos_match.group(1)

        return ""

    def _parse_offensive_stats(self, soup: BeautifulSoup, position: str,
                               year: Optional[int], stat_category: str) -> Optional[Dict[str, Any]]:
        """Parse offensive player statistics."""
        stats = {
            'position': position,
            'year': year,
            'stat_category': stat_category,
            'stats': {}
        }

        # Main stats table
        if position == 'QB':
            table = soup.find('table', {'id': 'passing'})
            if table:
                stats['stats'] = self._parse_passing_stats(table, year, stat_category)

        elif position in ['RB', 'FB']:
            # Rushing and receiving
            rushing_table = soup.find('table', {'id': 'rushing_and_receiving'})
            if rushing_table:
                stats['stats'] = self._parse_rushing_stats(rushing_table, year, stat_category)

        elif position in ['WR', 'TE']:
            # Receiving
            receiving_table = soup.find('table', {'id': 'receiving_and_rushing'})
            if receiving_table:
                stats['stats'] = self._parse_receiving_stats(receiving_table, year, stat_category)

        if not stats['stats']:
            return None

        return stats

    def _parse_passing_stats(self, table, year: Optional[int], stat_category: str) -> Dict[str, Any]:
        """Parse QB passing statistics."""
        stats = {}

        tbody = table.find('tbody')
        if not tbody:
            return stats

        # Find the row for the specified year (or sum all years)
        rows = tbody.find_all('tr')

        if year:
            # Find specific year
            for row in rows:
                year_cell = row.find('th', {'data-stat': 'year_id'})
                if year_cell and str(year) in year_cell.text:
                    stats = self._extract_passing_row(row, stat_category)
                    break
        else:
            # Get career stats (usually last row with "Career" text)
            for row in rows:
                year_cell = row.find('th')
                if year_cell and 'Career' in year_cell.text:
                    stats = self._extract_passing_row(row, stat_category)
                    break

        return stats

    def _extract_passing_row(self, row, stat_category: str) -> Dict[str, Any]:
        """Extract passing stats from a table row."""
        stats = {}

        # Basic stats
        stat_map = {
            'games_played': 'g',
            'games_started': 'gs',
            'completions': 'pass_cmp',
            'attempts': 'pass_att',
            'completion_pct': 'pass_cmp_pct',
            'yards': 'pass_yds',
            'touchdowns': 'pass_td',
            'td_pct': 'pass_td_pct',
            'interceptions': 'pass_int',
            'int_pct': 'pass_int_pct',
            'first_downs': 'pass_first_down',
            'yards_per_attempt': 'pass_yds_per_att',
            'adjusted_yards_per_attempt': 'pass_adj_yds_per_att',
            'yards_per_completion': 'pass_yds_per_cmp',
            'yards_per_game': 'pass_yds_per_g',
            'passer_rating': 'pass_rating',
            'sacks': 'pass_sacked',
            'sack_yards': 'pass_sacked_yds'
        }

        for stat_name, data_stat in stat_map.items():
            cell = row.find('td', {'data-stat': data_stat})
            if cell:
                value = self._clean_text(cell.text)
                if value:
                    stats[stat_name] = value

        return stats

    def _parse_rushing_stats(self, table, year: Optional[int], stat_category: str) -> Dict[str, Any]:
        """Parse rushing statistics."""
        stats = {}

        tbody = table.find('tbody')
        if not tbody:
            return stats

        rows = tbody.find_all('tr')

        if year:
            for row in rows:
                year_cell = row.find('th', {'data-stat': 'year_id'})
                if year_cell and str(year) in year_cell.text:
                    stats = self._extract_rushing_row(row, stat_category)
                    break
        else:
            for row in rows:
                year_cell = row.find('th')
                if year_cell and 'Career' in year_cell.text:
                    stats = self._extract_rushing_row(row, stat_category)
                    break

        return stats

    def _extract_rushing_row(self, row, stat_category: str) -> Dict[str, Any]:
        """Extract rushing stats from a table row."""
        stats = {}

        stat_map = {
            'games_played': 'g',
            'games_started': 'gs',
            'rushing_attempts': 'rush_att',
            'rushing_yards': 'rush_yds',
            'rushing_tds': 'rush_td',
            'rushing_first_downs': 'rush_first_down',
            'yards_per_carry': 'rush_yds_per_att',
            'yards_per_game': 'rush_yds_per_g',
            'fumbles': 'fumbles',
            'receptions': 'rec',
            'receiving_yards': 'rec_yds',
            'receiving_tds': 'rec_td',
            'targets': 'targets'
        }

        for stat_name, data_stat in stat_map.items():
            cell = row.find('td', {'data-stat': data_stat})
            if cell:
                value = self._clean_text(cell.text)
                if value:
                    stats[stat_name] = value

        return stats

    def _parse_receiving_stats(self, table, year: Optional[int], stat_category: str) -> Dict[str, Any]:
        """Parse receiving statistics."""
        # Similar to rushing stats but focused on receiving
        return self._parse_rushing_stats(table, year, stat_category)

    def _parse_defensive_stats(self, soup: BeautifulSoup, position: str,
                               year: Optional[int], stat_category: str) -> Optional[Dict[str, Any]]:
        """Parse defensive player statistics."""
        stats = {
            'position': position,
            'year': year,
            'stat_category': stat_category,
            'stats': {}
        }

        # Defense table
        table = soup.find('table', {'id': 'defense'})
        if not table:
            return None

        tbody = table.find('tbody')
        if not tbody:
            return stats

        rows = tbody.find_all('tr')

        if year:
            for row in rows:
                year_cell = row.find('th', {'data-stat': 'year_id'})
                if year_cell and str(year) in year_cell.text:
                    stats['stats'] = self._extract_defensive_row(row, stat_category)
                    break
        else:
            for row in rows:
                year_cell = row.find('th')
                if year_cell and 'Career' in year_cell.text:
                    stats['stats'] = self._extract_defensive_row(row, stat_category)
                    break

        return stats if stats['stats'] else None

    def _extract_defensive_row(self, row, stat_category: str) -> Dict[str, Any]:
        """Extract defensive stats from a table row."""
        stats = {}

        stat_map = {
            'games_played': 'g',
            'games_started': 'gs',
            'tackles': 'tackles_combined',
            'solo_tackles': 'tackles_solo',
            'assists': 'tackles_assists',
            'tackles_for_loss': 'tackles_loss',
            'sacks': 'sacks',
            'qb_hits': 'qb_hits',
            'interceptions': 'def_int',
            'int_yards': 'def_int_yds',
            'int_tds': 'def_int_td',
            'passes_defended': 'pass_defended',
            'forced_fumbles': 'fumbles_forced',
            'fumble_recoveries': 'fumbles_rec',
            'fumble_rec_tds': 'fumbles_rec_td'
        }

        for stat_name, data_stat in stat_map.items():
            cell = row.find('td', {'data-stat': data_stat})
            if cell:
                value = self._clean_text(cell.text)
                if value:
                    stats[stat_name] = value

        return stats

    def _parse_special_teams_stats(self, soup: BeautifulSoup, position: str,
                                   year: Optional[int], stat_category: str) -> Optional[Dict[str, Any]]:
        """Parse special teams (K, P) statistics."""
        stats = {
            'position': position,
            'year': year,
            'stat_category': stat_category,
            'stats': {}
        }

        if position == 'K':
            table = soup.find('table', {'id': 'kicking'})
        elif position == 'P':
            table = soup.find('table', {'id': 'punting'})
        else:
            return None

        if not table:
            return None

        tbody = table.find('tbody')
        if not tbody:
            return stats

        rows = tbody.find_all('tr')

        if year:
            for row in rows:
                year_cell = row.find('th', {'data-stat': 'year_id'})
                if year_cell and str(year) in year_cell.text:
                    stats['stats'] = self._extract_kicking_row(row, position) if position == 'K' \
                                   else self._extract_punting_row(row)
                    break
        else:
            for row in rows:
                year_cell = row.find('th')
                if year_cell and 'Career' in year_cell.text:
                    stats['stats'] = self._extract_kicking_row(row, position) if position == 'K' \
                                   else self._extract_punting_row(row)
                    break

        return stats if stats['stats'] else None

    def _extract_kicking_row(self, row, position: str) -> Dict[str, Any]:
        """Extract kicking stats from a table row."""
        stats = {}

        stat_map = {
            'games_played': 'g',
            'fg_made': 'fgm',
            'fg_attempts': 'fga',
            'fg_pct': 'fg_pct',
            'xp_made': 'xpm',
            'xp_attempts': 'xpa',
            'xp_pct': 'xp_pct',
            'points': 'scoring'
        }

        for stat_name, data_stat in stat_map.items():
            cell = row.find('td', {'data-stat': data_stat})
            if cell:
                value = self._clean_text(cell.text)
                if value:
                    stats[stat_name] = value

        return stats

    def _extract_punting_row(self, row) -> Dict[str, Any]:
        """Extract punting stats from a table row."""
        stats = {}

        stat_map = {
            'games_played': 'g',
            'punts': 'punt',
            'punt_yards': 'punt_yds',
            'yards_per_punt': 'punt_yds_per_punt',
            'punts_blocked': 'punt_blocked'
        }

        for stat_name, data_stat in stat_map.items():
            cell = row.find('td', {'data-stat': data_stat})
            if cell:
                value = self._clean_text(cell.text)
                if value:
                    stats[stat_name] = value

        return stats

    def get_game_logs(self, player_id: str, year: int) -> Optional[List[Dict[str, Any]]]:
        """
        Get game-by-game logs for a player in a specific season.

        Args:
            player_id: Player ID
            year: Season year

        Returns:
            List of game logs or None if not found
        """
        url = f"{self.BASE_URL}/players/{player_id[0]}/{player_id}/gamelog/{year}/"

        cache_ttl = self.config.get('cache.current_season_ttl') if year == self.current_year \
                    else self.config.get('cache.historical_ttl')

        html = self._make_request(url, use_cache=True, cache_ttl=cache_ttl)
        if not html:
            return None

        soup = self._parse_html(html)
        if not soup:
            return None

        # Find the stats table
        table = soup.find('table', {'id': 'stats'})
        if not table:
            return None

        game_logs = []
        tbody = table.find('tbody')
        if not tbody:
            return game_logs

        for row in tbody.find_all('tr'):
            # Skip header rows
            if row.get('class') and 'thead' in row.get('class'):
                continue

            game_log = self._extract_game_log_row(row)
            if game_log:
                game_logs.append(game_log)

        return game_logs

    def _extract_game_log_row(self, row) -> Optional[Dict[str, Any]]:
        """Extract game log data from a row."""
        try:
            game_log = {}

            # Week/Game number
            week_cell = row.find('th', {'data-stat': 'week_num'})
            if week_cell:
                game_log['week'] = self._clean_text(week_cell.text)

            # Date
            date_cell = row.find('td', {'data-stat': 'game_date'})
            if date_cell:
                game_log['date'] = self._clean_text(date_cell.text)

            # Opponent
            opp_cell = row.find('td', {'data-stat': 'opp'})
            if opp_cell:
                game_log['opponent'] = self._clean_text(opp_cell.text)

            # Game result
            result_cell = row.find('td', {'data-stat': 'game_result'})
            if result_cell:
                game_log['result'] = self._clean_text(result_cell.text)

            # Extract all other stats dynamically
            for cell in row.find_all('td'):
                data_stat = cell.get('data-stat', '')
                if data_stat and data_stat not in ['game_date', 'opp', 'game_result']:
                    value = self._clean_text(cell.text)
                    if value:
                        game_log[data_stat] = value

            return game_log if len(game_log) > 2 else None

        except Exception as e:
            self.logger.warning(f"Error extracting game log row: {e}")
            return None
