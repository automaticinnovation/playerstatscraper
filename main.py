#!/usr/bin/env python3
"""
Sports Stats Scraper - Main Entry Point

Interactive CLI tool for scraping NFL and MLB player statistics.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.cli.menu import CLIMenu


def main():
    """Main entry point for the application."""
    try:
        cli = CLIMenu()
        cli.run()
    except KeyboardInterrupt:
        print("\n\nExiting... Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
