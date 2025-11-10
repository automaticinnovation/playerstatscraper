"""Favorites management page for Streamlit dashboard."""

import streamlit as st


def show():
    """Display the Favorites page."""
    st.markdown('<div class="main-header">⭐ Favorites</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Manage your favorite players</div>', unsafe_allow_html=True)

    # Sport tabs
    tab1, tab2 = st.tabs(["🏈 NFL", "⚾ MLB"])

    with tab1:
        show_sport_favorites("NFL", "nfl")

    with tab2:
        show_sport_favorites("MLB", "mlb")


def show_sport_favorites(sport_name, sport_key):
    """Display favorites for a specific sport."""
    config = st.session_state.config
    favorites = config.get_favorites(sport_key)

    if not favorites:
        st.info(f"No {sport_name} favorites yet. Add players from the Player Search page!")
        return

    st.markdown(f"### {sport_name} Favorites ({len(favorites)})")

    # Display favorites as cards
    for i, fav in enumerate(favorites):
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

            with col1:
                st.markdown(f"**{fav.get('name', 'Unknown')}**")

            with col2:
                st.write(f"Position: {fav.get('position', 'N/A')}")

            with col3:
                st.write(f"Years: {fav.get('years', 'N/A')}")

            with col4:
                if st.button("🗑️", key=f"remove_fav_{sport_key}_{i}"):
                    config.remove_favorite(sport_key, fav['name'])
                    st.success(f"Removed {fav['name']} from favorites")
                    st.rerun()

            st.markdown("---")

    # Quick actions
    st.markdown("### Quick Actions")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Compare All Favorites", use_container_width=True):
            if len(favorites) >= 2:
                # Set up comparison with favorites
                st.session_state.comparison_players = favorites[:5]  # Max 5 players
                st.session_state.comparison_sport_type = sport_name
                st.session_state.current_page = "🔄 Compare Players"
                st.switch_page("streamlit_app.py")
            else:
                st.warning("Need at least 2 favorites to compare")

    with col2:
        if st.button("🗑️ Clear All Favorites", use_container_width=True):
            if st.checkbox("Are you sure? This cannot be undone.", key=f"confirm_clear_{sport_key}"):
                # Clear all favorites for this sport
                for fav in favorites[:]:  # Create a copy to iterate
                    config.remove_favorite(sport_key, fav['name'])
                st.success(f"Cleared all {sport_name} favorites")
                st.rerun()
