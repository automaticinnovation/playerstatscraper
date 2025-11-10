# Quick Start Guide

Get up and running with Sports Stats Scraper in under 5 minutes!

## Installation

### 1. Install Python

Make sure you have Python 3.8 or higher installed:

```bash
python --version
# or
python3 --version
```

If you don't have Python, download it from [python.org](https://www.python.org/downloads/)

### 2. Install Dependencies

```bash
# Navigate to the project directory
cd playerstatscraper

# Install required packages
pip install -r requirements.txt

# On some systems, use pip3
pip3 install -r requirements.txt
```

### 3. Run the Application

```bash
python main.py

# On some systems, use python3
python3 main.py
```

## First Steps

### Example 1: Get Patrick Mahomes' 2023 Season Stats

1. Run `python main.py`
2. Select: **"Search for player stats"**
3. Select: **"NFL"**
4. Enter: **"Patrick Mahomes"**
5. Press Enter to select the player
6. Select: **"Season stats"**
7. Enter: **"2023"**
8. Select: **"Basic stats"**
9. View the stats!

### Example 2: Compare Two Players

1. Run `python main.py`
2. Select: **"Compare players"**
3. Select: **"MLB"**
4. Enter: **"2"** (number of players)
5. Enter first player: **"Aaron Judge"**
6. Select player from results
7. Enter second player: **"Shohei Ohtani"**
8. Select player from results
9. Enter year: **"2023"** (or leave blank for career)
10. Select: **"Basic stats"**
11. View side-by-side comparison!

### Example 3: Get Game Logs

1. Run `python main.py`
2. Select: **"Search for player stats"**
3. Choose sport and find your player
4. Select: **"Game logs"**
5. Enter season year: **"2023"**
6. View game-by-game stats!
7. Optional: Export to CSV for analysis in Excel

## Tips

- **Search Tips**:
  - You can use partial names ("Mahomes", "Trout")
  - The search will find multiple matches for common names

- **Navigation**:
  - Use arrow keys to navigate menus
  - Press Enter to select
  - Ctrl+C to exit anytime

- **Export Data**:
  - Always offered after viewing stats
  - Choose CSV for Excel compatibility
  - Choose JSON for programming/API use

- **Favorites**:
  - Save frequently searched players
  - Quick access through "View favorites"

## Common Commands

```bash
# Run the application
python main.py

# Run tests
python -m pytest tests/

# View logs
tail -f logs/scraper_*.log

# Clear cache
# Use the "Manage cache" option in the menu
```

## Configuration

Edit `config.yaml` to customize:

- **Request delay**: Change `scraping.request_delay` (default: 3 seconds)
- **Cache duration**: Adjust TTL values
- **Display style**: Switch between "rich" and "simple"

## Getting Help

- Check the full [README.md](README.md) for detailed documentation
- Review [Troubleshooting](README.md#troubleshooting) section
- Check logs in `logs/` directory for errors

## Next Steps

1. ✅ Successfully run your first search
2. ✅ Try comparing players
3. ✅ Export data to CSV
4. ✅ Add players to favorites
5. ✅ Customize config.yaml to your preferences

Happy scraping! 🏈⚾
