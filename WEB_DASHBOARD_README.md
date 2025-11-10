# Sports Stats Scraper - Web Dashboard 🏈⚾

## Welcome to Your New User-Friendly Interface!

This is a beautiful, modern web-based interface for the Sports Stats Scraper. No more terminal commands - just click, search, and analyze!

---

## 🚀 Quick Start (macOS)

### Option 1: Double-Click Launch (Easiest!)

1. **Double-click** the `launch_dashboard.command` file in this folder
2. The first time you run it:
   - It will create a virtual environment (if needed)
   - Install all dependencies automatically
   - This may take 2-3 minutes
3. Your browser will automatically open to the dashboard
4. Start searching for players!

**Note:** The first time you double-click, macOS may show a security warning. If this happens:
- Right-click the `launch_dashboard.command` file
- Select "Open"
- Click "Open" in the security dialog
- Future launches will work with a double-click

### Option 2: Terminal Launch

```bash
# Navigate to the project folder
cd /path/to/playerstatscraper

# Make the launcher executable (one-time only)
chmod +x launch_dashboard.command

# Run the launcher
./launch_dashboard.command
```

### Option 3: Direct Streamlit Command

```bash
# Install dependencies (one-time only)
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py
```

---

## 🎯 Features Overview

### 🏈 Player Search
- Search for any NFL or MLB player by name
- View comprehensive statistics:
  - Season stats for any year
  - Career totals
  - Game-by-game logs
  - Playoff statistics (MLB)
- **Visual charts** showing performance breakdowns
- **Export** data to CSV or JSON
- **Add players to favorites** for quick access

### 🔄 Player Comparison
- Compare 2-5 players side-by-side
- **Interactive visualizations:**
  - Radar charts showing multi-dimensional comparison
  - Bar charts for specific stats
  - Automatic highlighting of best values
- Compare by season or career stats
- Export comparisons for external analysis

### ⭐ Favorites Management
- Save your favorite players
- Separate lists for NFL and MLB
- Quick comparison of all favorites
- Easy add/remove functionality

### 🗄️ Cache Management
- View cache statistics
- Clear old cache files (>30 days)
- Clear all cache to free up space
- See how caching improves performance

### ⚙️ Settings
- Customize default preferences
- Adjust display options
- Configure scraping behavior
- Manage cache settings

---

## 📖 How to Use

### Searching for a Player

1. Click **"🏈 Player Search"** in the sidebar
2. Select your sport (NFL or MLB)
3. Enter the player's name (e.g., "Patrick Mahomes", "Mike Trout")
4. Click **"🔍 Search Player"**
5. Select the player from the results
6. Choose stat type (Season, Career, Game Logs, or Playoffs)
7. Select the year (if applicable) and category (Basic or Advanced)
8. Click **"📥 Fetch Stats"**
9. View beautiful tables and charts!
10. Optionally export or add to favorites

### Comparing Players

1. Click **"🔄 Compare Players"** in the sidebar
2. Select your sport
3. Search for each player you want to compare:
   - Enter name and click **"🔍 Search"**
   - Click **"➕ Add"** next to the correct player
   - Repeat for 2-5 players
4. Select comparison settings:
   - Season Stats or Career Stats
   - Year (if season)
   - Basic or Advanced category
5. Click **"📊 Compare Players"**
6. Explore the comparison table and visualizations
7. Export if desired

### Managing Favorites

1. Add players to favorites from the Player Search page
2. View favorites: Click **"⭐ Favorites"** in the sidebar
3. Choose NFL or MLB tab
4. Quick actions:
   - Remove individual players with the 🗑️ button
   - Compare all favorites at once
   - Clear all favorites

### Cache Management

1. Click **"🗄️ Cache Management"** in the sidebar
2. View statistics about your cache
3. Actions:
   - **Clear Old Cache**: Removes files older than 30 days
   - **Clear All Cache**: Removes all cached data (use if seeing stale data)

---

## 💡 Tips & Tricks

### For Best Results

1. **Use Full Names**: Search with complete names like "Patrick Mahomes" instead of just "Mahomes"

2. **Check Years Carefully**: Make sure the year you select matches when the player was active

3. **Compare Similar Positions**: Comparisons are most meaningful between players at the same position

4. **Use Advanced Stats**: Switch to "Advanced" category for deeper analysis (WAR, PER, etc.)

5. **Export for Excel**: CSV exports work great in Excel for further analysis

6. **Cache Management**: If data seems outdated, clear old cache files

7. **Add to Favorites**: Save players you search frequently for quick access

8. **Visualizations**: The radar charts are great for seeing strengths/weaknesses at a glance

---

## 🔧 Troubleshooting

### Application Won't Start

**Problem:** Double-clicking launcher does nothing
- **Solution:** Right-click → Open → Click "Open" in security dialog (first time only)

**Problem:** "Python 3 is not installed" error
- **Solution:** Install Python 3.12 from https://www.python.org/downloads/

**Problem:** Dependencies fail to install
- **Solution:** Ensure you're using Python 3.12 (not 3.13) and have internet connection

### During Usage

**Problem:** Player not found in search
- **Solution:**
  - Try different spelling variations
  - Check the player's exact name on Pro Football Reference or Baseball Reference
  - Ensure the player is in the database (very recent players may not be available yet)

**Problem:** Stats not loading
- **Solution:**
  - Check your internet connection
  - Clear cache and try again
  - The reference websites may be temporarily unavailable

**Problem:** Comparison charts not showing
- **Solution:**
  - Ensure all players have compatible stats
  - Try comparing players from the same position/type
  - Some stats may not be available for all players

**Problem:** Export fails
- **Solution:**
  - Check that the `exports/` directory exists
  - Ensure you have write permissions in the project folder

**Problem:** Browser doesn't open automatically
- **Solution:**
  - Manually open your browser and go to: `http://localhost:8501`
  - The terminal will show the exact URL

---

## 📁 Project Structure

```
playerstatscraper/
├── streamlit_app.py           # Main web dashboard entry point
├── launch_dashboard.command   # macOS launcher script
├── main.py                     # Original CLI entry point (still works!)
├── requirements.txt            # Python dependencies
├── config.yaml                 # Configuration file
├── src/
│   ├── web/                    # Web dashboard pages
│   │   ├── player_search.py
│   │   ├── player_comparison.py
│   │   ├── favorites.py
│   │   ├── cache_management.py
│   │   ├── settings.py
│   │   └── about.py
│   ├── scrapers/               # Data scrapers
│   ├── utils/                  # Utility modules
│   └── cli/                    # Original CLI (still available)
├── cache/                      # Cached data (auto-created)
├── exports/                    # Exported files (auto-created)
└── logs/                       # Log files (auto-created)
```

---

## 🆚 CLI vs Web Dashboard

**Both interfaces are available!**

### Web Dashboard (NEW) - Recommended
- ✅ User-friendly visual interface
- ✅ Interactive charts and visualizations
- ✅ Point-and-click navigation
- ✅ Beautiful modern design
- ✅ Easy player comparison
- ✅ No terminal knowledge needed

### Original CLI
- ✅ Lightweight and fast
- ✅ Works over SSH
- ✅ Scriptable and automatable
- ✅ Lower resource usage
- ✅ Run with: `python main.py`

---

## 🔐 Privacy & Ethics

This tool operates ethically:
- ✅ Respects robots.txt rules
- ✅ Rate limiting (3-second delays between requests)
- ✅ Caching to minimize requests
- ✅ Proper User-Agent headers
- ✅ Public data only

**For personal, educational, and non-commercial use only.**

---

## 🐛 Known Issues

1. **First Launch Delay**: The first time you run the app, it may take 2-3 minutes to install dependencies
2. **Python 3.13 Compatibility**: Some dependencies have issues with Python 3.13. Use Python 3.12 instead.
3. **Browser Auto-Open**: Sometimes the browser doesn't auto-open. Just navigate to `http://localhost:8501` manually.

---

## 💾 Data Export Locations

Exported files are saved to:
```
playerstatscraper/exports/
```

File naming format:
- Player stats: `player_name_season_2024.csv`
- Comparisons: `comparison_2024.csv`
- Game logs: `player_name_gamelogs_2024.csv`

---

## 🎓 Learning Resources

### Understanding Statistics

**NFL:**
- QB: Pass yards, completion %, passer rating, TDs, INTs
- RB: Rush yards, yards/carry, TDs, receptions
- WR/TE: Receptions, yards, yards/catch, TDs
- Defense: Tackles, sacks, INTs, forced fumbles

**MLB:**
- Batting: AVG, OBP, SLG, OPS, HR, RBI
- Pitching: ERA, WHIP, K/9, BB/9, W-L

### Advanced Metrics

- **WAR** (Wins Above Replacement): Overall player value
- **OPS** (On-Base Plus Slugging): Offensive production (MLB)
- **Passer Rating**: QB effectiveness (NFL)
- **wOBA** (Weighted On-Base Average): True offensive value (MLB)

---

## 🆘 Need Help?

1. **Check the About page** in the web dashboard (ℹ️ About in sidebar)
2. **Review this README** for common issues
3. **Check logs** in the `logs/` directory for detailed error messages
4. **Clear cache** if you see stale or missing data

---

## 🎉 Enjoy!

You now have a powerful, beautiful tool for analyzing sports statistics!

**Tips to get started:**
1. Double-click `launch_dashboard.command`
2. Search for your favorite player
3. Add them to favorites
4. Compare them with other great players
5. Export data for deeper analysis

**Happy analyzing! 🏈⚾📊**
