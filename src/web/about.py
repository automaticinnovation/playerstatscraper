"""About page for Streamlit dashboard."""

import streamlit as st
from datetime import datetime


def show():
    """Display the About page."""
    st.markdown('<div class="main-header">ℹ️ About</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Sports Stats Scraper - Player Statistics Tool</div>', unsafe_allow_html=True)

    # Application overview
    st.markdown("### 📊 Application Overview")

    st.markdown("""
    **Sports Stats Scraper** is a comprehensive tool for fetching and analyzing professional sports player statistics.
    This web dashboard provides an intuitive interface for searching, comparing, and exporting player data from
    NFL and MLB reference websites.
    """)

    st.markdown("---")

    # Key features
    st.markdown("### ✨ Key Features")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **🔍 Player Search**
        - Search NFL and MLB players
        - View season, career, and game logs
        - Access basic and advanced statistics

        **🔄 Player Comparison**
        - Compare 2-5 players side-by-side
        - Visual radar and bar charts
        - Highlight best performers

        **⭐ Favorites Management**
        - Save favorite players
        - Quick access to favorites
        - Compare all favorites at once
        """)

    with col2:
        st.markdown("""
        **📤 Data Export**
        - Export to CSV format
        - Export to JSON format
        - Timestamped filenames

        **🗄️ Smart Caching**
        - Faster repeated queries
        - Configurable TTL
        - Reduces server load

        **🎨 User-Friendly Interface**
        - Clean, modern design
        - Interactive visualizations
        - Easy navigation
        """)

    st.markdown("---")

    # Supported sports
    st.markdown("### 🏈 Supported Sports")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **NFL (National Football League)**
        - Source: Pro Football Reference
        - All positions supported
        - Season stats, career stats, game logs
        - Offensive, defensive, and special teams stats
        """)

    with col2:
        st.markdown("""
        **MLB (Major League Baseball)**
        - Source: Baseball Reference
        - Batting and pitching stats
        - Season stats, career stats, game logs
        - Playoff statistics
        """)

    st.markdown("---")

    # Data sources
    st.markdown("### 🌐 Data Sources")

    st.info("""
    This application scrapes data from publicly available sports reference websites:
    - **Pro Football Reference** (https://www.pro-football-reference.com)
    - **Baseball Reference** (https://www.baseball-reference.com)

    All scraping is done ethically with:
    - Respect for robots.txt
    - Rate limiting (3-second delay between requests)
    - Proper User-Agent headers
    - Intelligent caching to minimize requests
    """)

    st.markdown("---")

    # Technical details
    st.markdown("### 🛠️ Technical Details")

    with st.expander("View Technical Information"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **Technologies Used:**
            - Python 3.8+
            - Streamlit (Web Framework)
            - BeautifulSoup4 (Web Scraping)
            - Pandas (Data Processing)
            - Plotly (Visualizations)
            - Requests (HTTP)
            """)

        with col2:
            st.markdown("""
            **Architecture:**
            - Modular scraper design
            - Configurable caching system
            - Rotating file logging
            - YAML-based configuration
            - Export to multiple formats
            """)

    st.markdown("---")

    # Usage tips
    st.markdown("### 💡 Usage Tips")

    with st.expander("How to Get the Most Out of This Tool"):
        st.markdown("""
        **For Best Results:**

        1. **Use Specific Player Names**: The search works best with full names (e.g., "Patrick Mahomes" instead of just "Mahomes")

        2. **Compare Similar Positions**: When comparing players, choose players from the same position for meaningful comparisons

        3. **Check Cache Regularly**: If you see outdated data, clear old cache files from the Cache Management page

        4. **Export Data**: Use the export features to save data for offline analysis in Excel or other tools

        5. **Add Favorites**: Save frequently searched players to your favorites for quick access

        6. **Use Advanced Stats**: For deeper analysis, switch to "Advanced" statistics in the Category dropdown
        """)

    st.markdown("---")

    # Version and copyright
    st.markdown("### 📝 Version Information")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Version", "2.0.0")

    with col2:
        st.metric("Release", "Web Dashboard")

    with col3:
        st.metric("Year", datetime.now().year)

    st.markdown("---")

    # Disclaimer
    st.markdown("### ⚠️ Disclaimer")

    st.warning("""
    **Important Notice:**

    This tool is for personal, educational, and non-commercial use only. All data is sourced from publicly
    available sports reference websites. Please respect the terms of service of these websites.

    - Data accuracy depends on the source websites
    - Historical data may have gaps or inconsistencies
    - Real-time data may have delays
    - Use this tool responsibly and ethically
    """)

    st.markdown("---")

    # Footer
    st.markdown("### 📬 Support")

    st.markdown("""
    For questions, issues, or feedback, please refer to the project documentation or contact the developer.

    **Happy stats hunting! 🏈⚾**
    """)

    # Additional info
    st.markdown("---")

    with st.expander("🔧 Troubleshooting"):
        st.markdown("""
        **Common Issues and Solutions:**

        **Problem:** Player not found in search
        - **Solution:** Try alternative spellings or check the exact name on the sports reference website

        **Problem:** Stats not loading
        - **Solution:** Check your internet connection and try clearing the cache

        **Problem:** Export fails
        - **Solution:** Ensure the exports directory exists and you have write permissions

        **Problem:** Comparison chart not showing
        - **Solution:** Ensure players have compatible stats (same position/type)

        **Problem:** Application feels slow
        - **Solution:** Clear old cache files and ensure cache is enabled in settings
        """)
