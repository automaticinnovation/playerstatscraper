"""MLB stats scraper for Baseball Reference."""

import re
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from datetime import datetime

from .base_scraper import BaseScraper


class MLBScraper(BaseScraper):
    """Scraper for MLB player statistics from Baseball Reference."""

    BASE_URL = "https://www.baseball-reference.com"

    # Position categories
    PITCHER_POSITIONS = {'P', 'SP', 'RP', 'CL'}
    HITTER_POSITIONS = {'C', '1B', '2B', '3B', 'SS', 'LF', 'CF', 'RF', 'OF', 'DH', 'PH'}

    def __init__(self, config, cache, logger):
        """Initialize MLB scraper."""
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
        self.logger.info(f"Searching for MLB player: {player_name}")

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
        canonical = soup.find('link', {'rel': 'canonical'})
        if canonical and '/players/' in canonical.get('href', ''):
            player_info = self._extract_player_from_page(soup)
            if player_info:
                return [player_info]

        # Parse search results
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
                player_id = url.split('/')[-1].replace('.shtml', '')

                # Extract metadata
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
                    'teams': teams[:3] if len(teams) > 3 else teams
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

            # Remove the span with additional info
            span = h1.find('span')
            if span:
                span.decompose()

            name = self._clean_text(h1.text)

            # Get URL
            canonical = soup.find('link', {'rel': 'canonical'})
            url = canonical.get('href', '') if canonical else ''
            player_id = url.split('/')[-1].replace('.shtml', '')

            # Get position
            position = ""
            meta_div = soup.find('div', {'id': 'meta'})
            if meta_div:
                for p in meta_div.find_all('p'):
                    text = self._clean_text(p.text)
                    if 'Position' in text:
                        pos_match = re.search(r'Position:\s*([A-Za-z]+)', text)
                        if pos_match:
                            position = pos_match.group(1).upper()
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
            player_id: Player ID (e.g., 'troutmi01')
            year: Season year (None for career stats)
            stat_category: 'basic' or 'advanced'

        Returns:
            Dictionary with player stats or None if not found
        """
        # Baseball Reference player URLs: /players/{first_letter}/{player_id}.shtml
        url = f"{self.BASE_URL}/players/{player_id[0]}/{player_id}.shtml"

        cache_ttl = self.config.get('cache.current_season_ttl') if year == self.current_year \
                    else self.config.get('cache.historical_ttl')

        html = self._make_request(url, use_cache=True, cache_ttl=cache_ttl)
        if not html:
            return None

        soup = self._parse_html(html)
        if not soup:
            return None

        # Determine if player is pitcher or hitter
        is_pitcher = self._is_pitcher(soup)

        if is_pitcher:
            return self._parse_pitching_stats(soup, year, stat_category)
        else:
            return self._parse_batting_stats(soup, year, stat_category)

    def _is_pitcher(self, soup: BeautifulSoup) -> bool:
        """Determine if player is primarily a pitcher."""
        # Check for pitching table
        pitching_table = soup.find('table', {'id': 'pitching_standard'})
        batting_table = soup.find('table', {'id': 'batting_standard'})

        # If both tables exist, check which has more rows (primary role)
        if pitching_table and batting_table:
            pitch_rows = len(pitching_table.find('tbody').find_all('tr')) if pitching_table.find('tbody') else 0
            bat_rows = len(batting_table.find('tbody').find_all('tr')) if batting_table.find('tbody') else 0
            return pitch_rows > bat_rows

        return pitching_table is not None

    def _parse_batting_stats(self, soup: BeautifulSoup, year: Optional[int],
                            stat_category: str) -> Optional[Dict[str, Any]]:
        """Parse batting statistics."""
        stats = {
            'player_type': 'hitter',
            'year': year,
            'stat_category': stat_category,
            'stats': {}
        }

        # Standard batting table
        if stat_category == 'basic':
            table = soup.find('table', {'id': 'batting_standard'})
        else:
            # Advanced stats
            table = soup.find('table', {'id': 'batting_value'}) or \
                   soup.find('table', {'id': 'batting_standard'})

        if not table:
            return None

        tbody = table.find('tbody')
        if not tbody:
            return stats

        rows = tbody.find_all('tr')

        if year:
            # Find specific year
            for row in rows:
                # Skip summary rows
                if row.get('class') and 'partial_table' in row.get('class'):
                    continue

                year_cell = row.find('th', {'data-stat': 'year_ID'})
                if year_cell and str(year) in year_cell.text:
                    stats['stats'] = self._extract_batting_row(row, stat_category)
                    break
        else:
            # Get career stats
            for row in rows:
                if row.get('id') and 'batting_standard.career' in row.get('id'):
                    stats['stats'] = self._extract_batting_row(row, stat_category)
                    break

        return stats if stats['stats'] else None

    def _extract_batting_row(self, row, stat_category: str) -> Dict[str, Any]:
        """Extract batting stats from a table row."""
        stats = {}

        # Basic batting stats
        basic_stat_map = {
            'games': 'G',
            'plate_appearances': 'PA',
            'at_bats': 'AB',
            'runs': 'R',
            'hits': 'H',
            'doubles': '2B',
            'triples': '3B',
            'home_runs': 'HR',
            'rbi': 'RBI',
            'stolen_bases': 'SB',
            'caught_stealing': 'CS',
            'walks': 'BB',
            'strikeouts': 'SO',
            'batting_avg': 'BA',
            'on_base_pct': 'OBP',
            'slugging_pct': 'SLG',
            'ops': 'OPS',
            'ops_plus': 'OPS+',
            'total_bases': 'TB',
            'gdp': 'GDP',
            'hbp': 'HBP',
            'sacrifice_hits': 'SH',
            'sacrifice_flies': 'SF',
            'intentional_walks': 'IBB'
        }

        # Advanced stats
        advanced_stat_map = {
            'war': 'WAR',
            'batting_runs': 'batting_runs',
            'baserunning_runs': 'baserunning_runs',
            'woba': 'woba',
            'wraa': 'wraa',
            'wrc_plus': 'wrc_plus'
        }

        stat_map = basic_stat_map if stat_category == 'basic' else {**basic_stat_map, **advanced_stat_map}

        for stat_name, data_stat in stat_map.items():
            cell = row.find('td', {'data-stat': data_stat})
            if cell:
                value = self._clean_text(cell.text)
                if value and value != '':
                    stats[stat_name] = value

        return stats

    def _parse_pitching_stats(self, soup: BeautifulSoup, year: Optional[int],
                             stat_category: str) -> Optional[Dict[str, Any]]:
        """Parse pitching statistics."""
        stats = {
            'player_type': 'pitcher',
            'year': year,
            'stat_category': stat_category,
            'stats': {}
        }

        # Standard pitching table
        if stat_category == 'basic':
            table = soup.find('table', {'id': 'pitching_standard'})
        else:
            # Advanced stats
            table = soup.find('table', {'id': 'pitching_value'}) or \
                   soup.find('table', {'id': 'pitching_standard'})

        if not table:
            return None

        tbody = table.find('tbody')
        if not tbody:
            return stats

        rows = tbody.find_all('tr')

        if year:
            # Find specific year
            for row in rows:
                # Skip summary rows
                if row.get('class') and 'partial_table' in row.get('class'):
                    continue

                year_cell = row.find('th', {'data-stat': 'year_ID'})
                if year_cell and str(year) in year_cell.text:
                    stats['stats'] = self._extract_pitching_row(row, stat_category)
                    break
        else:
            # Get career stats
            for row in rows:
                if row.get('id') and 'pitching_standard.career' in row.get('id'):
                    stats['stats'] = self._extract_pitching_row(row, stat_category)
                    break

        return stats if stats['stats'] else None

    def _extract_pitching_row(self, row, stat_category: str) -> Dict[str, Any]:
        """Extract pitching stats from a table row."""
        stats = {}

        # Basic pitching stats
        basic_stat_map = {
            'wins': 'W',
            'losses': 'L',
            'win_loss_pct': 'W-L%',
            'era': 'ERA',
            'games': 'G',
            'games_started': 'GS',
            'games_finished': 'GF',
            'complete_games': 'CG',
            'shutouts': 'SHO',
            'saves': 'SV',
            'innings_pitched': 'IP',
            'hits': 'H',
            'runs': 'R',
            'earned_runs': 'ER',
            'home_runs': 'HR',
            'walks': 'BB',
            'intentional_walks': 'IBB',
            'strikeouts': 'SO',
            'hbp': 'HBP',
            'balks': 'BK',
            'wild_pitches': 'WP',
            'batters_faced': 'BF',
            'era_plus': 'ERA+',
            'fip': 'FIP',
            'whip': 'WHIP',
            'hits_per_9': 'H9',
            'hr_per_9': 'HR9',
            'bb_per_9': 'BB9',
            'so_per_9': 'SO9',
            'so_bb_ratio': 'SO/W'
        }

        # Advanced stats
        advanced_stat_map = {
            'war': 'WAR',
            'pitching_runs': 'pitching_runs',
            'fip_minus': 'fip_minus',
            'whiff_pct': 'whiff_pct',
            'k_pct': 'k_pct',
            'bb_pct': 'bb_pct'
        }

        stat_map = basic_stat_map if stat_category == 'basic' else {**basic_stat_map, **advanced_stat_map}

        for stat_name, data_stat in stat_map.items():
            cell = row.find('td', {'data-stat': data_stat})
            if cell:
                value = self._clean_text(cell.text)
                if value and value != '':
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
        # Determine if pitcher or hitter to get the right game log
        player_url = f"{self.BASE_URL}/players/{player_id[0]}/{player_id}.shtml"
        html = self._make_request(player_url, use_cache=True)

        if not html:
            return None

        soup = self._parse_html(html)
        if not soup:
            return None

        is_pitcher = self._is_pitcher(soup)

        # Game log URLs
        if is_pitcher:
            gamelog_url = f"{self.BASE_URL}/players/gl.fcgi?id={player_id}&t=p&year={year}"
        else:
            gamelog_url = f"{self.BASE_URL}/players/gl.fcgi?id={player_id}&t=b&year={year}"

        cache_ttl = self.config.get('cache.current_season_ttl') if year == self.current_year \
                    else self.config.get('cache.historical_ttl')

        html = self._make_request(gamelog_url, use_cache=True, cache_ttl=cache_ttl)
        if not html:
            return None

        soup = self._parse_html(html)
        if not soup:
            return None

        # Find the stats table
        table = soup.find('table', {'id': 'pitching_gamelogs'}) if is_pitcher \
               else soup.find('table', {'id': 'batting_gamelogs'})

        if not table:
            return None

        game_logs = []
        tbody = table.find('tbody')
        if not tbody:
            return game_logs

        for row in tbody.find_all('tr'):
            # Skip header rows and summary rows
            if row.get('class') and ('thead' in row.get('class') or 'no_class' in row.get('class')):
                continue

            game_log = self._extract_game_log_row(row)
            if game_log:
                game_logs.append(game_log)

        return game_logs

    def _extract_game_log_row(self, row) -> Optional[Dict[str, Any]]:
        """Extract game log data from a row."""
        try:
            game_log = {}

            # Game number
            game_num_cell = row.find('th', {'data-stat': 'Rk'})
            if game_num_cell:
                game_log['game_num'] = self._clean_text(game_num_cell.text)

            # Date
            date_cell = row.find('td', {'data-stat': 'Date'})
            if date_cell:
                game_log['date'] = self._clean_text(date_cell.text)

            # Opponent
            opp_cell = row.find('td', {'data-stat': 'Opp'})
            if opp_cell:
                game_log['opponent'] = self._clean_text(opp_cell.text)

            # Result
            result_cell = row.find('td', {'data-stat': 'Rslt'})
            if result_cell:
                game_log['result'] = self._clean_text(result_cell.text)

            # Extract all other stats dynamically
            for cell in row.find_all('td'):
                data_stat = cell.get('data-stat', '')
                if data_stat and data_stat not in ['Date', 'Opp', 'Rslt']:
                    value = self._clean_text(cell.text)
                    if value and value != '':
                        game_log[data_stat] = value

            return game_log if len(game_log) > 2 else None

        except Exception as e:
            self.logger.warning(f"Error extracting game log row: {e}")
            return None

    def get_playoff_stats(self, player_id: str, stat_category: str = 'basic') -> Optional[Dict[str, Any]]:
        """
        Get playoff/postseason statistics for a player.

        Args:
            player_id: Player ID
            stat_category: 'basic' or 'advanced'

        Returns:
            Dictionary with playoff stats or None if not found
        """
        url = f"{self.BASE_URL}/players/{player_id[0]}/{player_id}.shtml"

        cache_ttl = self.config.get('cache.playoff_ttl')
        html = self._make_request(url, use_cache=True, cache_ttl=cache_ttl)

        if not html:
            return None

        soup = self._parse_html(html)
        if not soup:
            return None

        is_pitcher = self._is_pitcher(soup)

        stats = {
            'player_type': 'pitcher' if is_pitcher else 'hitter',
            'stat_type': 'playoffs',
            'stat_category': stat_category,
            'stats': {}
        }

        # Look for postseason tables
        if is_pitcher:
            table = soup.find('table', {'id': 'pitching_postseason'})
            if table:
                # Get career postseason row
                tbody = table.find('tbody')
                if tbody:
                    for row in tbody.find_all('tr'):
                        if row.get('id') and 'career' in row.get('id').lower():
                            stats['stats'] = self._extract_pitching_row(row, stat_category)
                            break
        else:
            table = soup.find('table', {'id': 'batting_postseason'})
            if table:
                # Get career postseason row
                tbody = table.find('tbody')
                if tbody:
                    for row in tbody.find_all('tr'):
                        if row.get('id') and 'career' in row.get('id').lower():
                            stats['stats'] = self._extract_batting_row(row, stat_category)
                            break

        return stats if stats['stats'] else None
