#!/bin/bash

# Sports Stats Scraper - macOS Launcher Script
# Double-click this file to launch the web dashboard

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

echo "=========================================="
echo "  Sports Stats Scraper - Web Dashboard"
echo "=========================================="
echo ""
echo "Starting application..."
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed."
    echo "Please install Python 3.12 and try again."
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $PYTHON_VERSION"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "⚠️  Virtual environment not found."
    echo "Creating virtual environment..."
    python3 -m venv venv

    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment."
        read -p "Press Enter to exit..."
        exit 1
    fi

    echo "✓ Virtual environment created."
fi

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are installed
if [ ! -f "venv/lib/python*/site-packages/streamlit/__init__.py" ] && [ ! -f "venv/lib/python3*/site-packages/streamlit/__init__.py" ]; then
    echo ""
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt

    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies."
        read -p "Press Enter to exit..."
        exit 1
    fi

    echo "✓ Dependencies installed."
fi

echo ""
echo "🚀 Launching Sports Stats Scraper..."
echo ""
echo "The application will open in your default browser."
echo "To stop the application, close this terminal window or press Ctrl+C."
echo ""
echo "=========================================="
echo ""

# Launch Streamlit
streamlit run streamlit_app.py --server.port 8501 --server.headless false

# Keep terminal open if there's an error
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ An error occurred."
    echo ""
    read -p "Press Enter to exit..."
fi
