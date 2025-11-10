"""Player Comparison page for Streamlit dashboard."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime


def show():
    """Display the Player Comparison page."""
    st.markdown('<div class="main-header">🔄 Compare Players</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Side-by-side player statistics comparison</div>', unsafe_allow_html=True)

    # Initialize comparison state
    if 'comparison_players' not in st.session_state:
        st.session_state.comparison_players = []

    # Sport selection
    sport = st.selectbox(
        "Select Sport",
        ["NFL", "MLB"],
        key="comparison_sport",
        index=0
    )

    st.markdown("---")

    # Player input section
    st.subheader("Add Players to Compare")

    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        player_name = st.text_input(
            "Enter Player Name",
            placeholder="e.g., Patrick Mahomes",
            key="comparison_player_input"
        )

    with col2:
        st.markdown("&nbsp;")  # Spacing
        search_button = st.button("🔍 Search", type="primary", use_container_width=True)

    with col3:
        st.markdown("&nbsp;")  # Spacing
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state.comparison_players = []
            st.session_state.comparison_results = None
            st.rerun()

    # Search for player
    if search_button and player_name:
        scraper = st.session_state.nfl_scraper if sport == "NFL" else st.session_state.mlb_scraper

        with st.spinner(f"Searching for {player_name}..."):
            results = scraper.search_player(player_name)

            if not results:
                st.warning(f"No players found matching '{player_name}'")
            else:
                # Store results without clearing previous searches
                if 'temp_search_results' not in st.session_state:
                    st.session_state.temp_search_results = []
                st.session_state.temp_search_results = results  # Update with latest search
                st.session_state.comparison_sport_type = sport

    # Display search results for selection
    if st.session_state.get('temp_search_results'):
        st.markdown("#### Select Player to Add")

        results = st.session_state.temp_search_results

        for i, player in enumerate(results):
            col1, col2 = st.columns([4, 1])

            with col1:
                st.write(f"**{player['name']}** - {player.get('position', 'N/A')} ({player.get('years', 'N/A')})")

            with col2:
                if st.button("➕ Add", key=f"add_player_{i}"):
                    # Check if already added
                    if not any(p['player_id'] == player['player_id'] for p in st.session_state.comparison_players):
                        if len(st.session_state.comparison_players) < 5:
                            st.session_state.comparison_players.append(player)
                            st.success(f"Added {player['name']}")
                            # Keep temp results so user can search for more players
                            st.rerun()
                        else:
                            st.error("Maximum 5 players allowed")
                    else:
                        st.warning("Player already added")

        if st.button("❌ Cancel Search Results"):
            st.session_state.temp_search_results = None
            st.rerun()

    # Display selected players
    if st.session_state.comparison_players:
        st.markdown("---")
        st.subheader("Selected Players")

        for i, player in enumerate(st.session_state.comparison_players):
            col1, col2, col3 = st.columns([1, 3, 1])

            with col1:
                st.write(f"**{i+1}.**")

            with col2:
                st.write(f"{player['name']} - {player.get('position', 'N/A')}")

            with col3:
                if st.button("🗑️", key=f"remove_player_{i}"):
                    st.session_state.comparison_players.pop(i)
                    st.rerun()

        # Comparison options
        if len(st.session_state.comparison_players) >= 2:
            st.markdown("---")
            st.subheader("Comparison Settings")

            col1, col2, col3 = st.columns(3)

            with col1:
                stat_type = st.selectbox(
                    "Stats Type",
                    ["Game Logs", "Season Stats", "Career Stats"],
                    key="comparison_stat_type",
                    index=0  # Default to Game Logs
                )

            with col2:
                if stat_type in ["Season Stats", "Game Logs"]:
                    current_year = datetime.now().year
                    year = st.number_input(
                        "Year",
                        min_value=1900,
                        max_value=current_year,
                        value=current_year,
                        key="comparison_year"
                    )
                else:
                    year = None

            with col3:
                if stat_type != "Game Logs":
                    stat_category = st.selectbox(
                        "Category",
                        ["Basic", "Advanced"],
                        key="comparison_category"
                    )
                else:
                    stat_category = "basic"
                    st.markdown("&nbsp;")  # Spacing
                    st.info("Game Logs selected")

            # Compare button
            if st.button("📊 Compare Players", type="primary", use_container_width=True):
                if stat_type == "Game Logs":
                    compare_game_logs(sport, year)
                else:
                    compare_players(sport, year, stat_category.lower())

        else:
            st.info("Add at least 2 players to compare")

    # Display comparison results
    if st.session_state.get('comparison_results'):
        display_comparison(st.session_state.comparison_results)


def compare_players(sport, year, stat_category):
    """Fetch and compare player statistics."""
    scraper = st.session_state.nfl_scraper if sport == "NFL" else st.session_state.mlb_scraper

    comparison_data = {}

    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, player in enumerate(st.session_state.comparison_players):
        status_text.text(f"Fetching stats for {player['name']}...")
        progress_bar.progress((i + 1) / len(st.session_state.comparison_players))

        try:
            stats_data = scraper.get_season_stats(
                player['player_id'],
                year=year,
                stat_category=stat_category
            )

            if stats_data:
                comparison_data[player['name']] = stats_data
            else:
                st.warning(f"Could not fetch stats for {player['name']}")

        except Exception as e:
            st.error(f"Error fetching stats for {player['name']}: {str(e)}")

    progress_bar.empty()
    status_text.empty()

    if len(comparison_data) >= 2:
        st.session_state.comparison_results = {
            'data': comparison_data,
            'year': year,
            'category': stat_category,
            'sport': sport
        }
        st.success(f"Successfully compared {len(comparison_data)} players!")
    else:
        st.error("Could not fetch stats for enough players to compare")


def compare_game_logs(sport, year):
    """Fetch and compare player game logs."""
    scraper = st.session_state.nfl_scraper if sport == "NFL" else st.session_state.mlb_scraper

    game_logs_data = {}

    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, player in enumerate(st.session_state.comparison_players):
        status_text.text(f"Fetching game logs for {player['name']}...")
        progress_bar.progress((i + 1) / len(st.session_state.comparison_players))

        try:
            logs = scraper.get_game_logs(player['player_id'], year)

            if logs:
                game_logs_data[player['name']] = logs
            else:
                st.warning(f"Could not fetch game logs for {player['name']}")

        except Exception as e:
            st.error(f"Error fetching game logs for {player['name']}: {str(e)}")

    progress_bar.empty()
    status_text.empty()

    if len(game_logs_data) >= 2:
        st.session_state.comparison_results = {
            'type': 'game_logs',
            'data': game_logs_data,
            'year': year,
            'sport': sport
        }
        st.success(f"Successfully compared game logs for {len(game_logs_data)} players!")
    else:
        st.error("Could not fetch game logs for enough players to compare")


def display_game_logs_comparison(comparison_info):
    """Display game logs comparison for multiple players."""
    game_logs_data = comparison_info['data']
    player_names = list(game_logs_data.keys())
    year = comparison_info['year']

    st.markdown(f"### Game Logs Comparison ({year})")

    # Create tabs for each player
    tabs = st.tabs(player_names)

    for i, player_name in enumerate(player_names):
        with tabs[i]:
            logs = game_logs_data[player_name]

            if not logs:
                st.warning(f"No game logs available for {player_name}")
                continue

            # Convert to DataFrame
            df = pd.DataFrame(logs)

            # Format column names
            df.columns = [col.replace('_', ' ').title() for col in df.columns]

            # Display the table
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                height=500
            )

            st.info(f"Total Games: {len(logs)}")

    # Create aggregate comparison
    st.markdown("---")
    st.markdown("### 📊 Aggregate Stats Comparison")

    # Calculate totals/averages for each player
    aggregate_stats = {}

    for player_name, logs in game_logs_data.items():
        if not logs:
            continue

        # Convert to DataFrame for easier aggregation
        df = pd.DataFrame(logs)

        # Calculate numeric aggregates
        numeric_cols = df.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns
        player_agg = {}

        for col in numeric_cols:
            # Skip columns that shouldn't be summed
            skip_cols = ['week', 'game', 'year', 'age']
            if any(skip in col.lower() for skip in skip_cols):
                continue

            try:
                total = df[col].sum()
                avg = df[col].mean()
                player_agg[f"{col}_total"] = total
                player_agg[f"{col}_avg"] = round(avg, 2)
            except:
                pass

        player_agg['games_played'] = len(logs)
        aggregate_stats[player_name] = player_agg

    if aggregate_stats:
        # Display aggregate comparison
        agg_df = pd.DataFrame(aggregate_stats).T
        agg_df.index.name = 'Player'

        st.dataframe(
            agg_df,
            use_container_width=True,
            height=400
        )

    # Export options
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Export All Game Logs as CSV", use_container_width=True):
            export_game_logs_comparison(comparison_info, 'csv')

    with col2:
        if st.button("💾 Export All Game Logs as JSON", use_container_width=True):
            export_game_logs_comparison(comparison_info, 'json')


def display_comparison(comparison_info):
    """Display player comparison results."""
    st.markdown("---")
    st.markdown("## 📊 Comparison Results")

    # Check if this is game logs comparison
    if comparison_info.get('type') == 'game_logs':
        display_game_logs_comparison(comparison_info)
        return

    comparison_data = comparison_info['data']
    player_names = list(comparison_data.keys())

    # Collect all unique stats
    all_stats = set()
    for data in comparison_data.values():
        if 'stats' in data:
            all_stats.update(data['stats'].keys())

    # Create comparison DataFrame
    comparison_rows = []

    for stat in sorted(all_stats):
        row = {'Statistic': stat.replace('_', ' ').title()}

        # Collect values and track for highlighting
        values = []
        numeric_values = []

        for player_name in player_names:
            player_data = comparison_data[player_name]
            stats = player_data.get('stats', {})
            value = stats.get(stat, 'N/A')

            row[player_name] = value
            values.append(value)

            # Try to extract numeric value for highlighting
            if value != 'N/A':
                try:
                    numeric = str(value).replace('%', '').replace(',', '')
                    numeric_values.append(float(numeric))
                except (ValueError, AttributeError):
                    numeric_values.append(None)
            else:
                numeric_values.append(None)

        # Find best value (simple heuristic: higher is better)
        if numeric_values and any(v is not None for v in numeric_values):
            valid_values = [(i, v) for i, v in enumerate(numeric_values) if v is not None]
            if valid_values:
                best_idx = max(valid_values, key=lambda x: x[1])[0]
                row['best_player'] = player_names[best_idx]
            else:
                row['best_player'] = None
        else:
            row['best_player'] = None

        comparison_rows.append(row)

    df = pd.DataFrame(comparison_rows)

    # Display table with highlighting
    st.dataframe(
        df.drop('best_player', axis=1) if 'best_player' in df.columns else df,
        use_container_width=True,
        hide_index=True,
        height=600
    )

    # Create radar chart for key stats
    try:
        create_radar_chart(comparison_data, player_names)
    except Exception as e:
        # Silently skip if radar chart fails
        pass

    # Create bar charts for selected stats
    try:
        create_comparison_bar_charts(comparison_data, player_names)
    except Exception as e:
        # Silently skip if bar charts fail
        pass

    # Export options
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Export as CSV", use_container_width=True, key="export_comparison_csv"):
            export_comparison(comparison_info, 'csv')

    with col2:
        if st.button("💾 Export as JSON", use_container_width=True, key="export_comparison_json"):
            export_comparison(comparison_info, 'json')


def create_radar_chart(comparison_data, player_names):
    """Create a radar chart for player comparison."""
    st.markdown("### 📊 Radar Chart Comparison")

    # Extract numeric stats that exist for all players
    common_stats = {}

    for player_name in player_names:
        stats = comparison_data[player_name].get('stats', {})
        for stat_name, value in stats.items():
            if stat_name not in common_stats:
                common_stats[stat_name] = {}
            try:
                numeric = str(value).replace('%', '').replace(',', '')
                common_stats[stat_name][player_name] = float(numeric)
            except (ValueError, AttributeError):
                pass

    # Filter to stats that exist for all players and are in reasonable range
    valid_stats = []
    for stat_name, player_values in common_stats.items():
        if len(player_values) == len(player_names):
            values = list(player_values.values())
            if all(-1000 < v < 1000 for v in values):  # Reasonable range
                valid_stats.append(stat_name)

    if len(valid_stats) < 3:
        st.info("Not enough common numeric stats for radar chart")
        return

    # Select top stats for radar chart
    selected_stats = valid_stats[:8]

    # Normalize values to 0-100 scale for each stat
    normalized_data = {}
    for stat_name in selected_stats:
        values = [common_stats[stat_name][p] for p in player_names]
        min_val = min(values)
        max_val = max(values)

        if max_val > min_val:
            for player_name in player_names:
                if player_name not in normalized_data:
                    normalized_data[player_name] = []
                val = common_stats[stat_name][player_name]
                normalized = ((val - min_val) / (max_val - min_val)) * 100
                normalized_data[player_name].append(normalized)
        else:
            for player_name in player_names:
                if player_name not in normalized_data:
                    normalized_data[player_name] = []
                normalized_data[player_name].append(50)

    # Create radar chart
    fig = go.Figure()

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

    for i, player_name in enumerate(player_names):
        fig.add_trace(go.Scatterpolar(
            r=normalized_data[player_name],
            theta=[s.replace('_', ' ').title() for s in selected_stats],
            fill='toself',
            name=player_name,
            line=dict(color=colors[i % len(colors)])
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True,
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)


def create_comparison_bar_charts(comparison_data, player_names):
    """Create bar charts for key statistics."""
    st.markdown("### 📊 Key Stats Comparison")

    # Extract numeric stats
    numeric_stats = {}

    for player_name in player_names:
        stats = comparison_data[player_name].get('stats', {})
        for stat_name, value in stats.items():
            if stat_name not in numeric_stats:
                numeric_stats[stat_name] = {}
            try:
                numeric = str(value).replace('%', '').replace(',', '')
                numeric_stats[stat_name][player_name] = float(numeric)
            except (ValueError, AttributeError):
                pass

    # Filter to stats that exist for all players
    common_numeric_stats = {
        k: v for k, v in numeric_stats.items()
        if len(v) == len(player_names) and all(-10000 < val < 10000 for val in v.values())
    }

    if not common_numeric_stats:
        return

    # Let user select stats to compare
    available_stats = [k.replace('_', ' ').title() for k in common_numeric_stats.keys()]

    if len(available_stats) > 5:
        selected_stats_display = st.multiselect(
            "Select stats to display (up to 5)",
            available_stats,
            default=available_stats[:5]
        )
    else:
        selected_stats_display = available_stats

    # Convert back to original keys
    selected_stats_keys = [k for k in common_numeric_stats.keys()
                          if k.replace('_', ' ').title() in selected_stats_display]

    # Create grouped bar chart
    fig = go.Figure()

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

    for i, player_name in enumerate(player_names):
        values = [common_numeric_stats[stat][player_name] for stat in selected_stats_keys]
        fig.add_trace(go.Bar(
            name=player_name,
            x=[s.replace('_', ' ').title() for s in selected_stats_keys],
            y=values,
            marker=dict(color=colors[i % len(colors)])
        ))

    fig.update_layout(
        barmode='group',
        height=400,
        xaxis_title="Statistic",
        yaxis_title="Value",
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)


def export_comparison(comparison_info, format_type):
    """Export comparison data."""
    try:
        exporter = st.session_state.exporter
        year_str = f"_{comparison_info['year']}" if comparison_info.get('year') else "_career"
        filename = f"comparison{year_str}"

        filepath = exporter.export_comparison(
            comparison_info['data'],
            filename,
            format=format_type
        )

        st.success(f"✅ Exported to: `{filepath}`")

    except Exception as e:
        st.error(f"Export failed: {str(e)}")


def export_game_logs_comparison(comparison_info, format_type):
    """Export game logs comparison data."""
    try:
        exporter = st.session_state.exporter
        year = comparison_info['year']
        game_logs_data = comparison_info['data']

        # Combine all game logs with player identifier
        all_logs = []
        for player_name, logs in game_logs_data.items():
            for log in logs:
                log_copy = {'player': player_name, 'season': year, **log}
                all_logs.append(log_copy)

        filename = f"game_logs_comparison_{year}"

        if format_type.lower() == 'json':
            filepath = exporter.export_to_json(all_logs, filename)
        else:
            filepath = exporter.export_to_csv(all_logs, filename)

        st.success(f"✅ Exported to: `{filepath}`")

    except Exception as e:
        st.error(f"Export failed: {str(e)}")
