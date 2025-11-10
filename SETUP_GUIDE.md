# Setup Guide - Sports Stats Scraper Web Dashboard

## Quick Setup for macOS (M-Series Mac)

### Prerequisites

✅ **Python 3.12** (Required - Python 3.13 has compatibility issues)
✅ **macOS** (M1, M2, or M3 Mac)
✅ **Internet connection**

### Installation Steps

#### Step 1: Install Python 3.12 (if not already installed)

1. Download Python 3.12 from: https://www.python.org/downloads/
2. Run the installer
3. Verify installation:
   ```bash
   python3 --version
   # Should show Python 3.12.x
   ```

#### Step 2: Navigate to Project Folder

Open Terminal and navigate to the project:
```bash
cd /path/to/playerstatscraper
```

Or simply drag the folder to Terminal after typing `cd `.

#### Step 3: Install Dependencies

**Option A: Using the Launcher (Automatic)**
```bash
# Make launcher executable
chmod +x launch_dashboard.command

# Run it - dependencies will be installed automatically
./launch_dashboard.command
```

**Option B: Manual Installation**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 4: Launch the Application

**Easy Way (Double-Click):**
- Double-click `launch_dashboard.command` in Finder
- First time: Right-click → Open → Click "Open" in security dialog
- Browser will open automatically

**Terminal Way:**
```bash
# If not already activated
source venv/bin/activate

# Launch app
streamlit run streamlit_app.py
```

#### Step 5: Start Using!

The application will open in your browser at: `http://localhost:8501`

If browser doesn't open automatically, just visit that URL manually.

---

## Troubleshooting Common Setup Issues

### Issue: "python3: command not found"

**Solution:** Python is not installed or not in PATH
```bash
# Check if Python exists
which python3

# If not found, install from python.org
```

### Issue: "permission denied" when running launcher

**Solution:** Make the script executable
```bash
chmod +x launch_dashboard.command
```

### Issue: Can't open launcher (macOS security)

**Solution:**
1. Right-click `launch_dashboard.command`
2. Select "Open"
3. Click "Open" in the security dialog
4. Future launches will work normally

### Issue: Dependencies fail to install

**Solutions:**
```bash
# Update pip first
pip install --upgrade pip

# Try installing again
pip install -r requirements.txt

# If specific package fails, try:
pip install --upgrade setuptools wheel
pip install -r requirements.txt
```

### Issue: "No module named 'streamlit'"

**Solution:** Dependencies not installed
```bash
# Activate virtual environment first
source venv/bin/activate

# Then install
pip install -r requirements.txt
```

### Issue: Using Python 3.13

**Solution:** Some packages aren't compatible with 3.13 yet
```bash
# Uninstall Python 3.13
# Install Python 3.12 from python.org
# Recreate virtual environment:
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Directory Structure After Setup

```
playerstatscraper/
├── venv/                       # Virtual environment (created during setup)
├── cache/                      # Cache directory (auto-created)
├── exports/                    # Export directory (auto-created)
├── logs/                       # Logs directory (auto-created)
├── streamlit_app.py            # Main web app
├── launch_dashboard.command    # Easy launcher
├── requirements.txt            # Dependencies
├── config.yaml                 # Configuration
├── WEB_DASHBOARD_README.md     # Usage guide
└── SETUP_GUIDE.md             # This file
```

---

## Verifying Installation

Run these commands to verify everything is set up correctly:

```bash
# Activate virtual environment
source venv/bin/activate

# Check Python version
python --version
# Should show Python 3.12.x

# Check if streamlit is installed
python -c "import streamlit; print('✓ Streamlit installed:', streamlit.__version__)"

# Check if all dependencies are installed
python -c "import pandas, plotly, requests, beautifulsoup4; print('✓ All dependencies installed')"

# Test syntax of web app
python -m py_compile streamlit_app.py
echo "✓ Web app syntax is valid"
```

If all checks pass, you're ready to go!

---

## Uninstallation

To completely remove the application:

```bash
# 1. Delete the project folder
cd ..
rm -rf playerstatscraper

# 2. (Optional) Uninstall Python 3.12 if not needed for other projects
```

To just reset the application:

```bash
# Remove virtual environment and caches
rm -rf venv cache exports logs

# Then re-run setup
./launch_dashboard.command
```

---

## Next Steps

1. ✅ Setup complete? Read `WEB_DASHBOARD_README.md` for usage instructions
2. ✅ Launch the app: Double-click `launch_dashboard.command`
3. ✅ Start searching for your favorite players!

---

## Need Help?

- **Setup Issues:** Review this guide
- **Usage Questions:** See `WEB_DASHBOARD_README.md`
- **Error Messages:** Check `logs/` directory
- **Python Issues:** Verify Python 3.12 is installed: `python3 --version`

---

## Tips

💡 **Create a Desktop Shortcut:**
- Drag `launch_dashboard.command` to your Desktop
- Double-click anytime to launch the app

💡 **Bookmark the App:**
- Launch the app
- Bookmark `http://localhost:8501` in your browser
- Access it easily (app must be running)

💡 **Auto-start on Login:**
- System Preferences → Users & Groups → Login Items
- Add `launch_dashboard.command`
- App will start automatically when you log in

---

**You're all set! Enjoy the Sports Stats Scraper! 🏈⚾**
