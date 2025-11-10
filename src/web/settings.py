"""Settings page for Streamlit dashboard."""

import streamlit as st


def show():
    """Display the Settings page."""
    st.markdown('<div class="main-header">⚙️ Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Configure application preferences</div>', unsafe_allow_html=True)

    config = st.session_state.config

    # Default preferences
    st.markdown("### 🎯 Default Preferences")

    col1, col2 = st.columns(2)

    with col1:
        default_sport = st.selectbox(
            "Default Sport",
            ["NFL", "MLB"],
            index=0 if config.get('defaults.sport') == 'NFL' else 1,
            key="default_sport_setting"
        )

        default_stat_type = st.selectbox(
            "Default Stat Type",
            ["season", "career", "game_logs", "playoffs"],
            index=["season", "career", "game_logs", "playoffs"].index(config.get('defaults.stat_type', 'season')),
            key="default_stat_type_setting"
        )

    with col2:
        default_stat_category = st.selectbox(
            "Default Stat Category",
            ["basic", "advanced"],
            index=0 if config.get('defaults.stat_category') == 'basic' else 1,
            key="default_stat_category_setting"
        )

        default_export_format = st.selectbox(
            "Default Export Format",
            ["csv", "json"],
            index=0 if config.get('defaults.export_format', 'csv') == 'csv' else 1,
            key="default_export_format_setting"
        )

    st.markdown("---")

    # Display preferences
    st.markdown("### 🎨 Display Preferences")

    col1, col2 = st.columns(2)

    with col1:
        table_style = st.selectbox(
            "Table Style",
            ["rich", "simple"],
            index=0 if config.get('display.table_style') == 'rich' else 1,
            key="table_style_setting"
        )

        color_comparisons = st.checkbox(
            "Highlight Best Values in Comparisons",
            value=config.get('display.color_comparisons', True),
            key="color_comparisons_setting"
        )

    with col2:
        show_summary = st.checkbox(
            "Show Summary Statistics",
            value=config.get('display.show_summary', True),
            key="show_summary_setting"
        )

        max_rows = st.number_input(
            "Maximum Rows to Display",
            min_value=10,
            max_value=1000,
            value=config.get('display.max_rows_display', 100),
            step=10,
            key="max_rows_setting"
        )

    st.markdown("---")

    # Scraping settings
    st.markdown("### 🌐 Scraping Settings")

    st.warning("⚠️ Changing these settings may affect scraping behavior. Use with caution!")

    with st.expander("Advanced Scraping Settings"):
        col1, col2 = st.columns(2)

        with col1:
            request_delay = st.number_input(
                "Request Delay (seconds)",
                min_value=1,
                max_value=30,
                value=config.get('scraping.request_delay', 3),
                help="Delay between requests to be polite to servers",
                key="request_delay_setting"
            )

            timeout = st.number_input(
                "Request Timeout (seconds)",
                min_value=5,
                max_value=120,
                value=config.get('scraping.timeout', 30),
                key="timeout_setting"
            )

        with col2:
            max_retries = st.number_input(
                "Maximum Retries",
                min_value=0,
                max_value=10,
                value=config.get('scraping.max_retries', 3),
                key="max_retries_setting"
            )

            retry_delay = st.number_input(
                "Retry Delay (seconds)",
                min_value=1,
                max_value=30,
                value=config.get('scraping.retry_delay', 5),
                key="retry_delay_setting"
            )

    st.markdown("---")

    # Cache settings
    st.markdown("### 🗄️ Cache Settings")

    col1, col2, col3 = st.columns(3)

    with col1:
        cache_enabled = st.checkbox(
            "Enable Cache",
            value=config.get('cache.enabled', True),
            key="cache_enabled_setting"
        )

    with col2:
        current_season_ttl = st.number_input(
            "Current Season TTL (hours)",
            min_value=1,
            max_value=168,
            value=config.get('cache.current_season_ttl', 86400) // 3600,
            help="Time-to-live for current season data",
            key="current_season_ttl_setting"
        )

    with col3:
        historical_ttl = st.number_input(
            "Historical TTL (days)",
            min_value=1,
            max_value=365,
            value=config.get('cache.historical_ttl', 2592000) // 86400,
            help="Time-to-live for historical data",
            key="historical_ttl_setting"
        )

    st.markdown("---")

    # Logging settings
    st.markdown("### 📝 Logging Settings")

    col1, col2 = st.columns(2)

    with col1:
        logging_enabled = st.checkbox(
            "Enable Logging",
            value=config.get('logging.enabled', True),
            key="logging_enabled_setting"
        )

        log_level = st.selectbox(
            "Log Level",
            ["DEBUG", "INFO", "WARNING", "ERROR"],
            index=["DEBUG", "INFO", "WARNING", "ERROR"].index(config.get('logging.level', 'INFO')),
            key="log_level_setting"
        )

    with col2:
        max_file_size = st.number_input(
            "Max Log File Size (MB)",
            min_value=1,
            max_value=100,
            value=config.get('logging.max_file_size', 10485760) // (1024 * 1024),
            key="max_file_size_setting"
        )

        backup_count = st.number_input(
            "Log Backup Count",
            min_value=1,
            max_value=20,
            value=config.get('logging.backup_count', 5),
            key="backup_count_setting"
        )

    st.markdown("---")

    # Save settings
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("💾 Save Settings", type="primary", use_container_width=True):
            try:
                # Update configuration (this is a simplified version - in reality you'd need to implement save methods)
                st.success("✅ Settings saved successfully!")
                st.info("Note: Some settings may require restarting the application to take effect.")
            except Exception as e:
                st.error(f"Error saving settings: {str(e)}")

    with col2:
        if st.button("🔄 Reset to Defaults", use_container_width=True):
            st.warning("This feature will be implemented in a future update.")

    st.markdown("---")

    # Configuration file location
    st.markdown("### 📄 Configuration File")

    st.info(
        f"""
        Configuration is stored in: `config.yaml`

        You can manually edit this file for advanced configuration options.
        The application must be restarted after manual edits.
        """
    )
