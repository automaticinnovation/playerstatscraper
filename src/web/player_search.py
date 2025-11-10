"""Player Search page for Streamlit dashboard."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime


def show():
    """Display the Player Search page."""
    st.markdown('<div class="main-header">🏈 Player Search</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Search for NFL and MLB player statistics</div>', unsafe_allow_html=True)

    # Sport selection
    col1, col2 = st.columns([1, 3])

    with col1:
        sport = st.selectbox(
            "Select Sport",
            ["NFL", "MLB"],
            key="search_sport",
            index=0 if st.session_state.config.get('defaults.sport') == 'NFL' else 1
        )

    with col2:
        player_name = st.text_input(
            "Enter Player Name",
            placeholder="e.g., Patrick Mahomes, Mike Trout",
            key="player_name_input"
        )

    # Search button
    if st.button("🔍 Search Player", type="primary", use_container_width=True):
        if not player_name:
            st.error("Please enter a player name")
        else:
            with st.spinner(f"Searching for {player_name}..."):
                scraper = st.session_state.nfl_scraper if sport == "NFL" else st.session_state.mlb_scraper
                results = scraper.search_player(player_name)

                if not results:
                    st.warning(f"No players found matching '{player_name}'")
                    st.session_state.search_results = None
                else:
                    st.session_state.search_results = results
                    st.session_state.selected_sport = sport
                    st.success(f"Found {len(results)} player(s)")

    # Display search results
    if st.session_state.get('search_results'):
        st.markdown("---")
        st.subheader("Search Results")

        results = st.session_state.search_results

        # Display results as cards
        for i, player in enumerate(results):
            with st.expander(
                f"{i+1}. {player.get('name', 'Unknown')} - {player.get('position', 'N/A')} ({player.get('years', 'N/A')})",
                expanded=(len(results) == 1)
            ):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown("**Player Information**")
                    st.write(f"**Name:** {player.get('name', 'N/A')}")
                    st.write(f"**Position:** {player.get('position', 'N/A')}")
                    st.write(f"**Years Active:** {player.get('years', 'N/A')}")

                with col2:
                    st.markdown("**Teams**")
                    teams = player.get('teams', [])
                    if teams:
                        for team in teams:
                            st.write(f"• {team}")
                    else:
                        st.write("N/A")

                with col3:
                    st.markdown("**Actions**")
                    if st.button(f"📊 View Stats", key=f"view_stats_{i}"):
                        st.session_state.selected_player = player
                        st.rerun()

        # If a player is selected, show stats options
        if st.session_state.get('selected_player'):
            show_player_stats(st.session_state.selected_player, st.session_state.selected_sport)


def show_player_stats(player, sport):
    """Display stats options and data for a selected player."""
    st.markdown("---")
    st.markdown(f"## 📊 Statistics for {player['name']}")

    # Stats options
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        stat_type = st.selectbox(
            "Stat Type",
            ["Season Stats", "Career Stats", "Game Logs", "Playoff Stats"] if sport == "MLB" else ["Season Stats", "Career Stats", "Game Logs"],
            key="stat_type_select"
        )

    with col2:
        if stat_type in ["Season Stats", "Game Logs"]:
            current_year = datetime.now().year
            year = st.number_input(
                "Year",
                min_value=1900,
                max_value=current_year,
                value=current_year,
                key="year_select"
            )
        else:
            year = None

    with col3:
        if stat_type != "Game Logs":
            stat_category = st.selectbox(
                "Category",
                ["Basic", "Advanced"],
                key="stat_category_select"
            )
        else:
            stat_category = "basic"

    with col4:
        st.markdown("&nbsp;")  # Spacing
        fetch_button = st.button("📥 Fetch Stats", type="primary", key="fetch_stats_btn")

    # Fetch and display stats
    if fetch_button:
        scraper = st.session_state.nfl_scraper if sport == "NFL" else st.session_state.mlb_scraper

        with st.spinner("Fetching statistics..."):
            try:
                if stat_type == "Game Logs":
                    stats_data = scraper.get_game_logs(player['player_id'], year)
                    if stats_data:
                        st.session_state.current_stats = {
                            'type': 'game_logs',
                            'data': stats_data,
                            'player': player,
                            'year': year
                        }
                elif stat_type == "Playoff Stats" and sport == "MLB":
                    stats_data = scraper.get_playoff_stats(player['player_id'], stat_category.lower())
                    if stats_data:
                        st.session_state.current_stats = {
                            'type': 'stats',
                            'data': stats_data,
                            'player': player
                        }
                else:
                    # Season or Career stats
                    stats_year = year if stat_type == "Season Stats" else None
                    stats_data = scraper.get_season_stats(
                        player['player_id'],
                        year=stats_year,
                        stat_category=stat_category.lower()
                    )
                    if stats_data:
                        st.session_state.current_stats = {
                            'type': 'stats',
                            'data': stats_data,
                            'player': player,
                            'year': stats_year
                        }

                if not stats_data:
                    st.error("Could not fetch statistics for this player")
                    st.session_state.current_stats = None
                else:
                    st.success("Statistics loaded successfully!")
                    # Log the successful scrape
                    st.session_state.logger.log_scrape(
                        sport,
                        player['name'],
                        f"{stat_type}_{year if year else 'career'}",
                        True
                    )

            except Exception as e:
                st.error(f"Error fetching stats: {str(e)}")
                st.session_state.logger.error(f"Error fetching stats: {e}", exc_info=True)

    # Display current stats if available
    if st.session_state.get('current_stats'):
        display_stats(st.session_state.current_stats)


def display_stats(stats_info):
    """Display statistics in various formats."""
    st.markdown("---")

    if stats_info['type'] == 'game_logs':
        display_game_logs(stats_info['data'], stats_info['player']['name'], stats_info['year'])
    else:
        display_player_stats_table(stats_info['data'], stats_info['player']['name'])

    # Export options
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.markdown("### 📤 Export Options")

    with col2:
        if st.button("💾 Export as CSV", use_container_width=True):
            export_stats(stats_info, 'csv')

    with col3:
        if st.button("💾 Export as JSON", use_container_width=True):
            export_stats(stats_info, 'json')

    # Add to favorites
    with col1:
        if st.button("⭐ Add to Favorites", use_container_width=True):
            sport = st.session_state.selected_sport.lower()
            st.session_state.config.add_favorite(sport, stats_info['player'])
            st.success(f"{stats_info['player']['name']} added to favorites!")


def display_player_stats_table(stats_data, player_name):
    """Display player stats in a table and chart."""
    st.subheader(f"📊 Statistics for {player_name}")

    if 'stats' not in stats_data:
        st.warning("No statistics available")
        return

    stats = stats_data['stats']

    # Display metadata
    col1, col2, col3 = st.columns(3)
    with col1:
        if 'position' in stats_data:
            st.metric("Position", stats_data['position'])
    with col2:
        if 'player_type' in stats_data:
            st.metric("Type", stats_data['player_type'].title())
    with col3:
        if 'year' in stats_data and stats_data['year']:
            st.metric("Season", stats_data['year'])
        else:
            st.metric("Type", "Career")

    # Convert to DataFrame for better display
    df = pd.DataFrame(list(stats.items()), columns=['Stat', 'Value'])
    df['Stat'] = df['Stat'].str.replace('_', ' ').str.title()

    # Display as table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Stat": st.column_config.TextColumn("Statistic", width="medium"),
            "Value": st.column_config.TextColumn("Value", width="medium"),
        }
    )

    # Try to create a visualization for numeric stats
    try:
        numeric_stats = {}
        for stat_name, value in stats.items():
            try:
                # Try to convert to float
                clean_value = str(value).replace('%', '').replace(',', '')
                numeric_value = float(clean_value)
                if -1000000 < numeric_value < 1000000:  # Reasonable range
                    numeric_stats[stat_name.replace('_', ' ').title()] = numeric_value
            except (ValueError, AttributeError):
                continue

        if numeric_stats and len(numeric_stats) > 2:
            st.markdown("### 📈 Visual Breakdown (Top Stats)")

            # Select top stats for visualization
            sorted_stats = dict(sorted(numeric_stats.items(), key=lambda x: abs(x[1]), reverse=True)[:10])

            fig = go.Figure(data=[
                go.Bar(
                    x=list(sorted_stats.values()),
                    y=list(sorted_stats.keys()),
                    orientation='h',
                    marker=dict(color='#1f77b4'),
                )
            ])

            fig.update_layout(
                title="Key Statistics",
                xaxis_title="Value",
                yaxis_title="Statistic",
                height=400,
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        # Silently skip visualization if there's an error
        pass


def display_game_logs(game_logs, player_name, year):
    """Display game logs in a table."""
    st.subheader(f"📅 Game Logs for {player_name} ({year})")

    if not game_logs:
        st.warning("No game logs available")
        return

    st.info(f"Total Games: {len(game_logs)}")

    # Convert to DataFrame
    df = pd.DataFrame(game_logs)

    # Format column names
    df.columns = [col.replace('_', ' ').title() for col in df.columns]

    # Display the table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=400
    )

    # Try to create a trend chart if possible
    try:
        # Look for common stats to chart
        possible_y_cols = []
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['yards', 'points', 'completions', 'attempts', 'hits', 'runs']):
                # Try to convert to numeric
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    if df[col].notna().any():
                        possible_y_cols.append(col)
                except:
                    pass

        if possible_y_cols:
            st.markdown("### 📈 Performance Trend")

            # Let user select which stat to chart
            selected_stat = st.selectbox("Select Stat to Chart", possible_y_cols)

            # Create x-axis (game number or week)
            x_col = 'Week' if 'Week' in df.columns else 'Game Num' if 'Game Num' in df.columns else df.columns[0]

            # Filter out non-numeric or NaN values
            chart_df = df[[x_col, selected_stat]].dropna()

            if not chart_df.empty:
                fig = px.line(
                    chart_df,
                    x=x_col,
                    y=selected_stat,
                    markers=True,
                    title=f"{selected_stat} Over Season"
                )

                fig.update_traces(line=dict(color='#1f77b4', width=3))
                fig.update_layout(height=400)

                st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        # Silently skip visualization if there's an error
        pass


def export_stats(stats_info, format_type):
    """Export statistics to file."""
    try:
        exporter = st.session_state.exporter
        player_name = stats_info['player']['name']
        safe_name = player_name.replace(' ', '_').lower()

        if stats_info['type'] == 'game_logs':
            year = stats_info['year']
            filepath = exporter.export_game_logs(
                stats_info['data'],
                player_name,
                year,
                format=format_type
            )
        else:
            # Regular stats
            year_str = f"_{stats_info.get('year')}" if stats_info.get('year') else "_career"
            filename = f"{safe_name}{year_str}"

            data = {player_name: stats_info['data']}
            filepath = exporter.export_comparison(data, filename, format=format_type)

        st.success(f"✅ Exported to: `{filepath}`")

    except Exception as e:
        st.error(f"Export failed: {str(e)}")
        st.session_state.logger.error(f"Export error: {e}", exc_info=True)
