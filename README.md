# Sports Stats Scraper

An interactive CLI tool for scraping NFL player stats from Pro Football Reference and MLB player stats from Baseball Reference.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ⚠️ Important Disclaimer

**This tool is for personal, educational use only.** Please review and respect the Terms of Service of both [Pro Football Reference](https://www.pro-football-reference.com/) and [Baseball Reference](https://www.baseball-reference.com/). This scraper:

- Implements polite scraping practices with rate limiting
- Checks and respects robots.txt files
- Uses caching to minimize redundant requests
- Should NOT be used for commercial purposes
- Should NOT be used to create derivative databases

Use responsibly and at your own risk.

## Features

### Core Functionality

- **Interactive Menu System**: User-friendly CLI with keyboard navigation
- **Multi-Sport Support**: NFL and MLB statistics
- **Player Search**: Fuzzy search with disambiguation for common names
- **Multiple Stat Types**:
  - Season stats (specific year or current season)
  - Career statistics
  - Game-by-game logs
  - Playoff stats (MLB)
- **Position-Aware Stats**: Automatically displays relevant stats based on player position
  - NFL: QB, RB, WR, TE, Defensive players, Kickers, Punters
  - MLB: Pitchers vs Hitters with position-specific metrics
- **Stat Categories**: Basic stats and advanced metrics
- **Player Comparison**: Side-by-side comparison of 2-5 players with highlighting
- **Export Options**: Save results to CSV or JSON
- **Favorites Management**: Save frequently searched players

### Technical Features

- **Smart Caching**: Local cache with configurable TTL (different for current vs historical data)
- **Rate Limiting**: Polite scraping with configurable delays between requests
- **Retry Logic**: Automatic retries with exponential backoff
- **Logging System**: Comprehensive logging for debugging and tracking
- **Robots.txt Compliance**: Checks and respects robots.txt before scraping
- **Beautiful Output**: Rich terminal formatting with tables and colors

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd playerstatscraper
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

## Usage

### Quick Start

1. Run the application:
   ```bash
   python main.py
   ```

2. Navigate the menu using arrow keys and Enter

3. Select "Search for player stats"

4. Choose your sport (NFL or MLB)

5. Enter a player name (e.g., "Patrick Mahomes", "Mike Trout")

6. Select from search results if multiple matches

7. Choose stat type (season, career, game logs, playoffs)

8. View beautifully formatted stats in your terminal!

### Example Workflows

#### Getting Season Stats

```
1. Select "Search for player stats"
2. Choose "NFL"
3. Enter "Josh Allen"
4. Select player from results
5. Choose "Season stats"
6. Enter year (e.g., "2023") or leave blank for current season
7. Select "Basic stats" or "Advanced metrics"
8. View stats and optionally export to CSV/JSON
```

#### Comparing Players

```
1. Select "Compare players"
2. Choose sport (NFL/MLB)
3. Enter number of players (2-5)
4. Enter each player's name and select from results
5. Enter season year or leave blank for career stats
6. Select stat category
7. View side-by-side comparison with highlighting
8. Optionally export comparison data
```

#### Getting Game Logs

```
1. Select "Search for player stats"
2. Choose sport
3. Search for player
4. Select "Game logs"
5. Enter season year
6. View game-by-game statistics
7. Export to CSV for further analysis
```

## Configuration

Edit `config.yaml` to customize settings:

### Scraping Settings

```yaml
scraping:
  user_agent: "Your custom user agent"
  request_delay: 3  # Seconds between requests (minimum 3 recommended)
  timeout: 30
  max_retries: 3
  retry_delay: 5
```

### Cache Settings

```yaml
cache:
  enabled: true
  directory: "./cache"
  current_season_ttl: 86400  # 24 hours
  historical_ttl: 2592000    # 30 days
  playoff_ttl: 604800        # 7 days
```

### Display Settings

```yaml
display:
  table_style: "rich"  # "rich" for colors or "simple"
  color_comparisons: true
  show_summary: true
  max_rows_display: 100
```

### Adding Favorites

```yaml
favorites:
  nfl:
    - name: "Patrick Mahomes"
      team: "Kansas City Chiefs"
      position: "QB"
  mlb:
    - name: "Mike Trout"
      team: "Los Angeles Angels"
      position: "OF"
```

## Project Structure

```
playerstatscraper/
├── main.py                 # Entry point
├── config.yaml            # Configuration file
├── requirements.txt       # Dependencies
├── README.md             # This file
│
├── src/
│   ├── cli/              # CLI interface
│   │   └── menu.py       # Interactive menu system
│   │
│   ├── scrapers/         # Scraping modules
│   │   ├── base_scraper.py    # Base scraper with common functionality
│   │   ├── nfl_scraper.py     # NFL-specific scraper
│   │   └── mlb_scraper.py     # MLB-specific scraper
│   │
│   └── utils/            # Utility modules
│       ├── cache_manager.py   # Caching system
│       ├── config_manager.py  # Configuration management
│       ├── logger.py          # Logging system
│       ├── display.py         # Terminal formatting
│       └── export.py          # CSV/JSON export
│
├── tests/                # Unit tests
│   └── test_base_scraper.py
│
├── cache/                # Cache directory (auto-created)
├── logs/                 # Log files (auto-created)
└── exports/              # Exported data (auto-created)
```

## NFL Stats

### Supported Positions

- **Quarterbacks (QB)**: Passing stats, rushing stats, passer rating, QBR
- **Running Backs (RB)**: Rushing stats, receiving stats, yards from scrimmage
- **Wide Receivers (WR)**: Receiving stats, targets, catch rate, yards after catch
- **Tight Ends (TE)**: Receiving stats, blocking stats
- **Defensive Players**: Tackles, sacks, interceptions, passes defended
- **Kickers (K)**: Field goals, extra points, accuracy
- **Punters (P)**: Punting stats, yards per punt

### Available Stats

**Basic Stats** (varies by position):
- Games played/started
- Passing: Completions, attempts, yards, TDs, INTs
- Rushing: Carries, yards, TDs, yards per carry
- Receiving: Receptions, yards, TDs, targets
- Defense: Tackles, sacks, interceptions, forced fumbles
- Kicking: FG made/attempted, XP made/attempted

**Advanced Metrics**:
- Passer rating, QBR
- Yards per attempt, completion percentage
- Yards after catch (YAC)
- Catch rate
- And more...

## MLB Stats

### Player Types

- **Pitchers**: Starters and relievers
- **Hitters**: All position players

### Available Stats

**Hitting Stats**:
- Basic: AVG, HR, RBI, Hits, Runs, SB, OBP, SLG, OPS
- Advanced: WAR, wOBA, wRC+, ISO

**Pitching Stats**:
- Basic: W-L, ERA, IP, K, BB, WHIP, Saves
- Advanced: FIP, xFIP, K%, BB%, SIERA

## Exporting Data

### Export Formats

1. **CSV**: Tabular format, great for Excel and data analysis
2. **JSON**: Structured format, great for programming and APIs

### Export Options

- Single player stats
- Player comparisons
- Game logs
- Custom filenames
- Automatic timestamping

### Export Location

All exports are saved to the `exports/` directory with descriptive filenames.

## Troubleshooting

### Common Issues

#### "No players found"

- Check spelling of player name
- Try first name or last name only
- Player might be too obscure or not in the database

#### "Could not fetch stats"

- Player might not have played in that year
- Network connection issues
- Website structure may have changed

#### Rate limiting errors (429)

- The tool automatically handles this with retries
- If persistent, increase `request_delay` in config.yaml

#### Website structure changes

If the scraper stops working due to website updates:

1. Check the logs in `logs/` directory
2. Update CSS selectors in scraper files:
   - `src/scrapers/nfl_scraper.py`
   - `src/scrapers/mlb_scraper.py`
3. Look for table IDs and data attributes in the HTML

### Updating Selectors

The scrapers use CSS selectors to find data. If websites change:

1. Visit the player's page in a browser
2. Right-click and "Inspect Element"
3. Find the table containing stats
4. Look for `id` attributes (e.g., `id="passing"`, `id="batting_standard"`)
5. Update the selectors in the appropriate scraper file

Example:
```python
# In nfl_scraper.py
table = soup.find('table', {'id': 'passing'})  # Update 'passing' if ID changes
```

## Running Tests

Run the test suite:

```bash
python -m pytest tests/

# Or using unittest
python -m unittest discover tests/
```

## Cache Management

### Viewing Cache Info

Use the "Manage cache" option in the main menu to:
- View cache size and file count
- Clear all cache
- Clear old cache (>30 days)

### Manual Cache Management

Cache files are stored in `cache/` directory as JSON files. You can:
- Manually delete files to clear specific cache
- Change TTL settings in config.yaml
- Disable caching entirely (not recommended)

## Logging

Logs are stored in `logs/` directory:
- Automatic rotation when files reach 10MB
- Keeps 5 backup files
- Configurable log level (DEBUG, INFO, WARNING, ERROR)

View logs:
```bash
# View latest log
tail -f logs/scraper_*.log

# Search for errors
grep ERROR logs/scraper_*.log
```

## Performance Tips

1. **Use caching**: Keep cache enabled for faster repeated queries
2. **Batch operations**: Use comparison mode instead of individual searches
3. **Historical data**: Cache TTL is longer for historical data
4. **Export frequently used data**: Save to CSV for offline analysis

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Legal & Ethics

### Terms of Service

This tool is for **personal, educational use only**. Commercial use or redistribution of scraped data may violate the Terms of Service of the source websites.

### Polite Scraping

This tool implements ethical scraping practices:
- ✅ Respects robots.txt
- ✅ Rate limiting (3-second default delay)
- ✅ Proper User-Agent headers
- ✅ Caching to minimize requests
- ✅ Error handling and retries
- ✅ No circumvention of access controls

### Your Responsibility

As a user, you are responsible for:
- Complying with the websites' Terms of Service
- Using reasonable rate limits
- Not using data for commercial purposes
- Respecting copyright and intellectual property

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Data sourced from [Pro Football Reference](https://www.pro-football-reference.com/) and [Baseball Reference](https://www.baseball-reference.com/)
- Built with Python, BeautifulSoup, Rich, and other amazing open-source libraries
- Inspired by the need for accessible sports statistics

## Support

For issues, questions, or feature requests:
1. Check the Troubleshooting section
2. Review existing issues on GitHub
3. Create a new issue with details

## Roadmap

Potential future features:
- [ ] NHL and NBA support
- [ ] Historical comparisons (player vs player across different eras)
- [ ] Team statistics
- [ ] Playoff bracket tracking
- [ ] Statistical analysis and visualizations
- [ ] API mode for programmatic access
- [ ] Web interface option

---

**Made with ❤️ for sports fans and data enthusiasts**
