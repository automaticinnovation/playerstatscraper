"""Cache management page for Streamlit dashboard."""

import streamlit as st


def show():
    """Display the Cache Management page."""
    st.markdown('<div class="main-header">🗄️ Cache Management</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">View and manage cached data</div>', unsafe_allow_html=True)

    cache_manager = st.session_state.cache
    cache_info = cache_manager.get_cache_info()

    # Cache statistics
    st.markdown("### 📊 Cache Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Cache Status",
            "Enabled" if cache_info.get('enabled', False) else "Disabled",
            delta=None
        )

    with col2:
        st.metric(
            "Total Files",
            cache_info.get('file_count', 0),
            delta=None
        )

    with col3:
        st.metric(
            "Cache Size",
            f"{cache_info.get('total_size_mb', 0):.2f} MB",
            delta=None
        )

    with col4:
        directory = cache_info.get('directory', 'N/A')
        st.metric(
            "Directory",
            directory if len(directory) < 20 else "..." + directory[-17:],
            delta=None
        )

    st.markdown("---")

    # Cache information
    st.markdown("### ℹ️ Cache Information")

    st.info(
        """
        **How caching works:**
        - **Current season data** is cached for 24 hours
        - **Historical data** is cached for 30 days
        - **Playoff data** is cached for 7 days

        Caching reduces load on the sports reference websites and speeds up repeated queries.
        """
    )

    # Cache details
    with st.expander("📋 View Cache Details"):
        st.write(f"**Cache Directory:** `{cache_info.get('directory', 'N/A')}`")
        st.write(f"**Cache Enabled:** {cache_info.get('enabled', False)}")
        st.write(f"**Total Files:** {cache_info.get('file_count', 0)}")
        st.write(f"**Total Size:** {cache_info.get('total_size_mb', 0):.2f} MB")

        if cache_info.get('file_count', 0) > 0:
            st.write(f"**Average File Size:** {cache_info.get('total_size_mb', 0) / max(cache_info.get('file_count', 1), 1):.2f} MB")

    st.markdown("---")

    # Cache management actions
    st.markdown("### 🛠️ Cache Management Actions")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Clear Old Cache")
        st.write("Remove cache files older than 30 days")

        if st.button("🧹 Clear Old Cache (>30 days)", use_container_width=True):
            with st.spinner("Clearing old cache files..."):
                try:
                    count = cache_manager.clear(older_than=2592000)  # 30 days in seconds
                    st.success(f"✅ Cleared {count} old cache file(s)")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error clearing old cache: {str(e)}")

    with col2:
        st.markdown("#### Clear All Cache")
        st.write("Remove all cached data")

        clear_all = st.checkbox("I understand this will remove all cached data", key="confirm_clear_all")

        if st.button(
            "🗑️ Clear All Cache",
            use_container_width=True,
            disabled=not clear_all,
            type="primary" if clear_all else "secondary"
        ):
            with st.spinner("Clearing all cache files..."):
                try:
                    count = cache_manager.clear()
                    st.success(f"✅ Cleared {count} cache file(s)")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error clearing cache: {str(e)}")

    st.markdown("---")

    # Cache benefits
    st.markdown("### 💡 Benefits of Caching")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**⚡ Faster Queries**")
        st.write("Repeated searches are instant")

    with col2:
        st.markdown("**🌐 Reduced Load**")
        st.write("Fewer requests to sports websites")

    with col3:
        st.markdown("**📊 Better Performance**")
        st.write("Smoother user experience")

    # Refresh button
    st.markdown("---")
    if st.button("🔄 Refresh Cache Info", use_container_width=True):
        st.rerun()
