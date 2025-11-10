#!/usr/bin/env python3
"""
Sports Stats Scraper - Streamlit Web Dashboard

A user-friendly web interface for scraping NFL and MLB player statistics.
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.utils.config_manager import ConfigManager
from src.utils.cache_manager import CacheManager
from src.utils.logger import Logger
from src.utils.export import DataExporter
from src.scrapers.nfl_scraper import NFLScraper
from src.scrapers.mlb_scraper import MLBScraper


# Page configuration
st.set_page_config(
    page_title="Sports Stats Scraper",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stat-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stButton>button {
        width: 100%;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
def init_session_state():
    """Initialize session state variables."""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.config = ConfigManager()
        st.session_state.cache = CacheManager(
            cache_dir=st.session_state.config.get('cache.directory'),
            enabled=st.session_state.config.get('cache.enabled')
        )
        st.session_state.logger = Logger(
            log_dir=st.session_state.config.get('logging.directory'),
            level=st.session_state.config.get('logging.level'),
            max_bytes=st.session_state.config.get('logging.max_file_size'),
            backup_count=st.session_state.config.get('logging.backup_count'),
            enabled=st.session_state.config.get('logging.enabled')
        )
        st.session_state.exporter = DataExporter()
        st.session_state.nfl_scraper = NFLScraper(
            st.session_state.config,
            st.session_state.cache,
            st.session_state.logger
        )
        st.session_state.mlb_scraper = MLBScraper(
            st.session_state.config,
            st.session_state.cache,
            st.session_state.logger
        )

        # UI state
        st.session_state.current_page = "🏈 Player Search"
        st.session_state.search_results = None
        st.session_state.current_stats = None
        st.session_state.comparison_data = None


def main():
    """Main application entry point."""
    init_session_state()

    # Sidebar navigation
    st.sidebar.markdown("### 🏈 Sports Stats Scraper")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigation",
        [
            "🏈 Player Search",
            "🔄 Compare Players",
            "⭐ Favorites",
            "🗄️ Cache Management",
            "⚙️ Settings",
            "ℹ️ About"
        ],
        key="navigation"
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Quick Stats**")
    cache_info = st.session_state.cache.get_cache_info()
    st.sidebar.metric("Cached Files", cache_info.get('file_count', 0))
    st.sidebar.metric("Cache Size", f"{cache_info.get('total_size_mb', 0):.1f} MB")

    # Page routing
    if page == "🏈 Player Search":
        from src.web import player_search
        player_search.show()
    elif page == "🔄 Compare Players":
        from src.web import player_comparison
        player_comparison.show()
    elif page == "⭐ Favorites":
        from src.web import favorites
        favorites.show()
    elif page == "🗄️ Cache Management":
        from src.web import cache_management
        cache_management.show()
    elif page == "⚙️ Settings":
        from src.web import settings
        settings.show()
    elif page == "ℹ️ About":
        from src.web import about
        about.show()


if __name__ == "__main__":
    main()
