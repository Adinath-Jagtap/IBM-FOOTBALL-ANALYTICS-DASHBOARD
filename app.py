"""
app.py
------
Football Player Performance Analytics Dashboard
Built with Streamlit + Plotly.

NOTE: All data displayed is SYNTHETIC and does NOT represent real-world football results.
Run:  streamlit run app.py
"""

import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Page configuration ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Football Analytics Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Constants ────────────────────────────────────────────────────────────────
CSV_PATH       = "football_players.csv"
CHART_TEMPLATE = "plotly_dark"
PAPER_BG       = "#060810"
PLOT_BG        = "#0D1117"
GREEN          = "#00E676"
ACCENT_COLORS  = [
    "#00E676", "#2979FF", "#FF6D00", "#E040FB",
    "#FF1744", "#00BCD4", "#FFD600", "#76FF03",
]

# ── Helper: hex → rgba ───────────────────────────────────────────────────────
def hex_to_rgba(hex_color: str, alpha: float = 0.18) -> str:
    """Convert #RRGGBB to rgba(r,g,b,alpha) string safe for Plotly."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

# ── Premium CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: linear-gradient(135deg,#060810 0%,#0a0f1e 50%,#060c14 100%); }
.hero-header {
    background: linear-gradient(135deg,#00E676 0%,#00C853 30%,#00897B 70%,#1565C0 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    font-family: 'Rajdhani', sans-serif; font-size: 2.8rem; font-weight: 700;
    letter-spacing: 2px; margin-bottom: 0; line-height: 1.1;
}
.hero-subtitle {
    color: #5a7a6a; font-size: 0.82rem; letter-spacing: 3px;
    text-transform: uppercase; margin-top: 2px; margin-bottom: 20px;
}
div[data-testid="metric-container"] {
    background: linear-gradient(135deg,rgba(0,230,118,0.07) 0%,rgba(13,17,23,0.9) 100%);
    border: 1px solid rgba(0,230,118,0.2); border-radius: 12px;
    padding: 16px 20px; backdrop-filter: blur(10px); transition: all 0.3s ease;
}
div[data-testid="metric-container"]:hover {
    border-color: rgba(0,230,118,0.5);
    box-shadow: 0 0 20px rgba(0,230,118,0.12); transform: translateY(-2px);
}
div[data-testid="metric-container"] label {
    color: #6b8f7a !important; font-size: 0.72rem !important;
    font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase;
}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    color: #00E676 !important; font-size: 1.7rem !important;
    font-weight: 700; font-family: 'Rajdhani', sans-serif;
}
div[data-testid="metric-container"] div[data-testid="stMetricDelta"] {
    color: #4fc3f7 !important; font-size: 0.75rem !important;
}
button[data-baseweb="tab"] {
    font-family: 'Rajdhani', sans-serif !important; font-size: 0.92rem !important;
    font-weight: 600 !important; color: #5a7a6a !important;
    border-bottom: 2px solid transparent !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #00E676 !important; border-bottom-color: #00E676 !important;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#080d18 0%,#060810 100%);
    border-right: 1px solid rgba(0,230,118,0.1);
}
.sidebar-title {
    color: #00E676; font-size: 0.72rem; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase; margin-bottom: 6px;
}
.section-header {
    color: #FAFAFA; font-family: 'Rajdhani', sans-serif;
    font-size: 1.15rem; font-weight: 700; letter-spacing: 1px;
    border-bottom: 1px solid rgba(0,230,118,0.3);
    padding-bottom: 6px; margin-top: 28px; margin-bottom: 14px;
    text-transform: uppercase;
}
.section-header::before { content: "▸ "; color: #00E676; }
.disclaimer-banner {
    background: linear-gradient(90deg,rgba(0,230,118,0.06) 0%,rgba(0,0,0,0) 100%);
    border-left: 3px solid #00E676; border-radius: 4px;
    padding: 8px 16px; margin-bottom: 24px; font-size: 0.78rem; color: #5a7a6a;
}
.stat-pill {
    display: inline-block; background: rgba(0,230,118,0.08);
    border: 1px solid rgba(0,230,118,0.2); border-radius: 20px;
    padding: 3px 12px; font-size: 0.72rem; color: #00E676;
    font-weight: 600; letter-spacing: 1px; text-transform: uppercase; margin: 2px 4px;
}
div[data-testid="stDataFrame"] {
    border: 1px solid rgba(0,230,118,0.15); border-radius: 8px; overflow: hidden;
}
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #060810; }
::-webkit-scrollbar-thumb { background: rgba(0,230,118,0.3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #00E676; }
div[data-testid="stDownloadButton"] button {
    background: linear-gradient(135deg,#00E676,#00C853) !important;
    color: #060810 !important; font-weight: 700 !important;
    border: none !important; border-radius: 8px !important;
    font-family: 'Rajdhani', sans-serif !important; letter-spacing: 1px;
}
div[data-testid="stDownloadButton"] button:hover {
    box-shadow: 0 4px 20px rgba(0,230,118,0.4) !important;
}
.pitch-divider {
    height: 2px;
    background: linear-gradient(90deg,transparent,#00E676,transparent);
    margin: 24px 0; opacity: 0.4;
}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ════════════════════════════════════════════════════════════════════════════

@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and validate the CSV dataset."""
    if not os.path.exists(CSV_PATH):
        st.error(
            f"Dataset not found: `{CSV_PATH}`. "
            "Please run `python generate_data.py` first."
        )
        st.stop()

    df = pd.read_csv(CSV_PATH)

    # Fix encoding in data_source column
    if "data_source" in df.columns:
        df["data_source"] = "Synthetic — not real-world data"

    null_count = df.isnull().sum().sum()
    if null_count > 0:
        before = len(df)
        df = df.dropna()
        st.sidebar.info(
            f"Note: {null_count} missing value(s) found and {before - len(df)} "
            "row(s) removed from the dataset."
        )

    # Derived columns
    df["shot_conversion"] = np.where(
        df["shots"] > 0, (df["goals"] / df["shots"] * 100).round(1), 0.0
    )
    df["goal_contributions"] = df["goals"] + df["assists"]

    return df


# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR FILTERS
# ════════════════════════════════════════════════════════════════════════════

def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Render sidebar filter widgets and return the filtered DataFrame."""
    st.sidebar.markdown(
        '<p style="text-align:center;font-family:Rajdhani,sans-serif;font-size:1.4rem;'
        'font-weight:700;background:linear-gradient(135deg,#00E676,#2979FF);'
        '-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
        'letter-spacing:2px;">⚽ FOOTBALL<br>ANALYTICS</p>',
        unsafe_allow_html=True,
    )
    st.sidebar.divider()
    st.sidebar.markdown('<p class="sidebar-title">🔍 Filters</p>', unsafe_allow_html=True)

    # Season
    all_seasons = sorted(df["season"].unique().tolist())
    selected_seasons = st.sidebar.multiselect(
        "Season", options=all_seasons, default=all_seasons,
        help="Select one or more seasons to include.",
    )

    # Team
    all_teams = sorted(df["team"].unique().tolist())
    selected_teams = st.sidebar.multiselect(
        "Team", options=all_teams, default=all_teams,
        help="Select one or more teams to include.",
    )

    # Position
    all_positions = ["GK", "DEF", "MID", "FWD"]
    selected_positions = st.sidebar.multiselect(
        "Position", options=all_positions, default=all_positions,
        help="Select one or more positions to include.",
    )

    # Age Range
    min_age, max_age = int(df["age"].min()), int(df["age"].max())
    age_range = st.sidebar.slider(
        "Age Range", min_value=min_age, max_value=max_age,
        value=(min_age, max_age), help="Filter players by age.",
    )

    # Player name search
    player_search = st.sidebar.text_input(
        "Search Player Name", value="", placeholder="e.g. Silva",
        help="Filter by player name (case-insensitive).",
    )

    st.sidebar.divider()

    # Active filter summary
    active = []
    if len(selected_seasons) < len(all_seasons):
        active.append(f"📅 {len(selected_seasons)} seasons")
    if len(selected_teams) < len(all_teams):
        active.append(f"🏟 {len(selected_teams)} teams")
    if len(selected_positions) < len(all_positions):
        active.append(f"👤 {', '.join(selected_positions)}")
    if age_range != (min_age, max_age):
        active.append(f"🎂 {age_range[0]}–{age_range[1]} yrs")
    if player_search.strip():
        active.append(f'🔎 "{player_search.strip()}"')
    if active:
        st.sidebar.markdown(
            "**Active filters:**<br>" + "<br>".join(f"• {a}" for a in active),
            unsafe_allow_html=True,
        )
    else:
        st.sidebar.caption("No active filters — showing all data.")

    st.sidebar.divider()
    st.sidebar.caption(
        "⚠️ **Data notice:** All statistics are synthetic and do NOT represent "
        "real-world football results."
    )

    # Apply filters
    mask = (
        df["season"].isin(selected_seasons)
        & df["team"].isin(selected_teams)
        & df["position"].isin(selected_positions)
        & df["age"].between(age_range[0], age_range[1])
    )
    filtered = df[mask].copy()

    if player_search.strip():
        filtered = filtered[
            filtered["name"].str.contains(player_search.strip(), case=False, na=False)
        ]

    return filtered


# ════════════════════════════════════════════════════════════════════════════
# CHART HELPERS
# ════════════════════════════════════════════════════════════════════════════

def _apply_dark_layout(fig: go.Figure, title: str = "", height: int = 0) -> go.Figure:
    """Apply consistent premium dark theme layout to any Plotly figure."""
    kw: dict = dict(
        template=CHART_TEMPLATE,
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color="#CCDDCC", family="Inter, sans-serif", size=12),
        margin=dict(l=40, r=20, t=55 if title else 30, b=40),
        hoverlabel=dict(
            bgcolor="#0D1117",
            bordercolor="rgba(0,230,118,0.4)",
            font_color="#FAFAFA",
            font_size=13,
        ),
    )
    if title:
        kw["title"] = dict(
            text=title,
            font=dict(size=14, color="#CCDDCC", family="Rajdhani, sans-serif"),
        )
    if height:
        kw["height"] = height
    fig.update_layout(**kw)
    fig.update_xaxes(gridcolor="rgba(0,230,118,0.06)", zerolinecolor="rgba(0,230,118,0.12)")
    fig.update_yaxes(gridcolor="rgba(0,230,118,0.06)", zerolinecolor="rgba(0,230,118,0.12)")
    return fig


def _section(label: str) -> None:
    st.markdown(f'<p class="section-header">{label}</p>', unsafe_allow_html=True)


def _divider() -> None:
    st.markdown('<div class="pitch-divider"></div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ════════════════════════════════════════════════════════════════════════════

def render_overview(df: pd.DataFrame) -> None:
    """Render the Overview page: KPI cards + summary charts."""

    _section("Key Performance Indicators")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Players",      f"{df['player_id'].nunique():,}")
    c2.metric("Total Goals",        f"{df['goals'].sum():,}")
    c3.metric("Total Assists",      f"{df['assists'].sum():,}")
    c4.metric("Goal Contributions", f"{df['goal_contributions'].sum():,}")
    c5.metric("Avg Player Rating",  f"{df['rating'].mean():.2f}")
    c6.metric("Total Minutes",      f"{df['minutes_played'].sum() // 1000:,}K")

    _divider()
    _section("Summary Charts")
    col_a, col_b = st.columns([1.5, 1])

    # Top 10 Goalscorers
    with col_a:
        top10 = (
            df.groupby("name", as_index=False)["goals"]
            .sum().nlargest(10, "goals").sort_values("goals")
        )
        fig_top10 = px.bar(
            top10, x="goals", y="name", orientation="h", color="goals",
            color_continuous_scale=[[0, "#003d1a"], [0.5, "#00C853"], [1, "#00E676"]],
            labels={"goals": "Total Goals", "name": "Player"},
        )
        fig_top10.update_layout(showlegend=False, coloraxis_showscale=False)
        fig_top10.update_traces(
            hovertemplate="<b>%{y}</b><br>Goals: %{x}<extra></extra>",
            marker_line_width=0,
        )
        _apply_dark_layout(fig_top10, "Top 10 Goalscorers", height=380)
        st.plotly_chart(fig_top10, use_container_width=True)

    # Goals by Position donut
    with col_b:
        pos_goals = df.groupby("position", as_index=False)["goals"].sum()
        fig_donut = px.pie(
            pos_goals, names="position", values="goals", hole=0.55,
            color_discrete_sequence=ACCENT_COLORS,
        )
        fig_donut.update_traces(
            textposition="outside", textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Goals: %{value}<br>Share: %{percent}<extra></extra>",
            marker=dict(line=dict(color=PAPER_BG, width=2)),
        )
        _apply_dark_layout(fig_donut, "Goals by Position", height=380)
        st.plotly_chart(fig_donut, use_container_width=True)

    _divider()
    col_c, col_d = st.columns(2)

    # Rating Distribution histogram
    with col_c:
        fig_hist = px.histogram(
            df, x="rating", nbins=28, color_discrete_sequence=[GREEN],
            labels={"rating": "Player Rating", "count": "Number of Players"},
        )
        fig_hist.update_traces(
            hovertemplate="Rating: %{x:.1f}<br>Players: %{y}<extra></extra>",
            marker_line_width=0, opacity=0.85,
        )
        _apply_dark_layout(fig_hist, "Player Rating Distribution", height=320)
        st.plotly_chart(fig_hist, use_container_width=True)

    # Season Trends
    with col_d:
        season_goals = (
            df.groupby("season", as_index=False)
            .agg(total_goals=("goals", "sum"), total_assists=("assists", "sum"))
        )
        fig_season = go.Figure()
        fig_season.add_trace(go.Scatter(
            x=season_goals["season"], y=season_goals["total_goals"],
            mode="lines+markers", name="Goals",
            line=dict(color=GREEN, width=2.5),
            marker=dict(size=10, color=GREEN),
            fill="tozeroy", fillcolor=hex_to_rgba(GREEN, 0.08),
            hovertemplate="<b>%{x}</b><br>Goals: %{y}<extra></extra>",
        ))
        fig_season.add_trace(go.Scatter(
            x=season_goals["season"], y=season_goals["total_assists"],
            mode="lines+markers", name="Assists",
            line=dict(color="#2979FF", width=2.5),
            marker=dict(size=10, color="#2979FF", symbol="diamond"),
            fill="tozeroy", fillcolor=hex_to_rgba("#2979FF", 0.06),
            hovertemplate="<b>%{x}</b><br>Assists: %{y}<extra></extra>",
        ))
        _apply_dark_layout(fig_season, "Season Trends: Goals & Assists", height=320)
        st.plotly_chart(fig_season, use_container_width=True)

    _divider()
    _section("Team Leaderboard")
    team_lb = (
        df.groupby("team", as_index=False)
        .agg(Goals=("goals","sum"), Assists=("assists","sum"),
             Players=("player_id","nunique"), Avg_Rating=("rating","mean"))
        .sort_values("Goals", ascending=False).reset_index(drop=True)
    )
    team_lb["Avg_Rating"] = team_lb["Avg_Rating"].round(2)
    team_lb.rename(columns={"Avg_Rating": "Avg Rating"}, inplace=True)
    team_lb.insert(0, "Rank", [f"#{i+1}" for i in range(len(team_lb))])
    st.dataframe(
        team_lb, use_container_width=True, height=310, hide_index=True,
        column_config={
            "Rank":       st.column_config.TextColumn("Rank"),
            "team":       st.column_config.TextColumn("Team"),
            "Goals":      st.column_config.NumberColumn("Goals", format="%d"),
            "Assists":    st.column_config.NumberColumn("Assists", format="%d"),
            "Players":    st.column_config.NumberColumn("Players", format="%d"),
            "Avg Rating": st.column_config.ProgressColumn(
                "Avg Rating", min_value=0, max_value=10, format="%.2f"),
        },
    )


# ════════════════════════════════════════════════════════════════════════════
# PAGE 2 — PLAYER ANALYSIS
# ════════════════════════════════════════════════════════════════════════════

def render_player_analysis(df: pd.DataFrame) -> None:
    """Render the Player Analysis page."""

    _section("Player Comparison — Radar Chart")
    all_players = sorted(df["name"].unique().tolist())

    if len(all_players) < 2:
        st.warning("Not enough players in the filtered data. Please adjust your filters.")
    else:
        default_players = all_players[:2]
        selected = st.multiselect(
            "Select up to 4 players to compare",
            options=all_players, default=default_players, max_selections=4,
            help="Choose 2-4 players. Stats are averaged across all selected seasons.",
        )

        if len(selected) < 2:
            st.info("Please select at least 2 players to display the radar chart.")
        else:
            radar_cols = ["goals", "assists", "shots", "pass_accuracy",
                          "dribbles", "tackles", "rating"]
            player_stats = (
                df[df["name"].isin(selected)]
                .groupby("name")[radar_cols].mean().reset_index()
            )
            for col in radar_cols:
                col_min = df[col].min()
                col_max = df[col].max()
                denom = col_max - col_min if col_max != col_min else 1
                player_stats[f"{col}_norm"] = (player_stats[col] - col_min) / denom

            norm_cols  = [f"{c}_norm" for c in radar_cols]
            categories = ["Goals", "Assists", "Shots", "Pass Acc.",
                          "Dribbles", "Tackles", "Rating"]

            fig_radar = go.Figure()
            for i, (_, row) in enumerate(player_stats.iterrows()):
                color = ACCENT_COLORS[i % len(ACCENT_COLORS)]
                values = [row[c] for c in norm_cols] + [row[norm_cols[0]]]
                fig_radar.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories + [categories[0]],
                    fill="toself",
                    name=row["name"],
                    line=dict(color=color, width=2),
                    fillcolor=hex_to_rgba(color, 0.15),  # BUG FIX: proper rgba()
                    hovertemplate=(
                        f"<b>{row['name']}</b><br>"
                        + "<br>".join(
                            f"{cat}: {row[col]:.1f}"
                            for cat, col in zip(categories, radar_cols)
                        )
                        + "<extra></extra>"
                    ),
                ))
            fig_radar.update_layout(
                polar=dict(
                    bgcolor=PLOT_BG,
                    radialaxis=dict(visible=True, range=[0, 1],
                                    showticklabels=False,
                                    gridcolor="rgba(0,230,118,0.1)"),
                    angularaxis=dict(tickfont=dict(size=12, color="#CCDDCC"),
                                     gridcolor="rgba(0,230,118,0.08)"),
                ),
                showlegend=True,
                legend=dict(font=dict(color="#FAFAFA"),
                            bgcolor="rgba(0,0,0,0.3)",
                            bordercolor="rgba(0,230,118,0.2)"),
            )
            _apply_dark_layout(fig_radar,
                               "Player Stats Comparison (Normalised 0-1)", height=480)
            st.plotly_chart(fig_radar, use_container_width=True)

    _divider()

    # Top Performers table
    _section("Top Performers")
    metric_choice = st.selectbox(
        "Rank by metric",
        ["goal_contributions", "goals", "assists", "rating",
         "pass_accuracy", "dribbles", "tackles"],
        format_func=lambda x: x.replace("_", " ").title(),
    )
    top_n = st.slider("Show top N players", 5, 30, 10, step=5)
    top_players = (
        df.groupby("name", as_index=False)
        .agg(
            team=("team","first"), position=("position","first"),
            goals=("goals","sum"), assists=("assists","sum"),
            goal_contributions=("goal_contributions","sum"),
            rating=("rating","mean"), pass_accuracy=("pass_accuracy","mean"),
            dribbles=("dribbles","sum"), tackles=("tackles","sum"),
        )
        .nlargest(top_n, metric_choice).reset_index(drop=True)
    )
    top_players["rating"] = top_players["rating"].round(2)
    top_players["pass_accuracy"] = top_players["pass_accuracy"].round(1)
    st.dataframe(
        top_players, use_container_width=True,
        height=min(400, 50 + top_n * 35), hide_index=True,
        column_config={
            "name":               st.column_config.TextColumn("Player"),
            "team":               st.column_config.TextColumn("Team"),
            "position":           st.column_config.TextColumn("Pos"),
            "goals":              st.column_config.NumberColumn("Goals"),
            "assists":            st.column_config.NumberColumn("Assists"),
            "goal_contributions": st.column_config.NumberColumn("G+A"),
            "rating":             st.column_config.ProgressColumn(
                "Rating", min_value=0, max_value=10, format="%.2f"),
            "pass_accuracy":      st.column_config.ProgressColumn(
                "Pass%", min_value=0, max_value=100, format="%.1f"),
            "dribbles":           st.column_config.NumberColumn("Dribbles"),
            "tackles":            st.column_config.NumberColumn("Tackles"),
        },
    )

    _divider()
    col_left, col_right = st.columns(2)

    # Goals vs Assists scatter
    with col_left:
        _section("Goals vs Assists")
        fig_ga = px.scatter(
            df, x="goals", y="assists", color="position",
            hover_name="name",
            hover_data={"team": True, "season": True, "goals": True, "assists": True},
            color_discrete_sequence=ACCENT_COLORS,
            labels={"goals": "Goals", "assists": "Assists"},
            opacity=0.8,
        )
        fig_ga.update_traces(marker=dict(size=9))
        _apply_dark_layout(fig_ga, "Goals vs Assists (by Position)", height=380)
        st.plotly_chart(fig_ga, use_container_width=True)

    # Shots vs Goals scatter with trendline
    with col_right:
        _section("Shots vs Goals")
        fig_sg = px.scatter(
            df, x="shots", y="goals", color="position",
            hover_name="name",
            hover_data={"team": True, "season": True, "shots": True, "goals": True},
            color_discrete_sequence=ACCENT_COLORS,
            labels={"shots": "Shots", "goals": "Goals"},
            trendline="ols", trendline_scope="overall",
            trendline_color_override=GREEN, opacity=0.75,
        )
        fig_sg.update_traces(selector=dict(mode="markers"), marker=dict(size=7))
        _apply_dark_layout(fig_sg, "Shots vs Goals (OLS Trend)", height=380)
        st.plotly_chart(fig_sg, use_container_width=True)

    _divider()
    col_e, col_f = st.columns(2)

    # Shot Conversion Rate by Position
    with col_e:
        _section("Shot Conversion Rate by Position")
        pos_conv = df.groupby("position", as_index=False)["shot_conversion"].mean().round(1)
        fig_conv = px.bar(
            pos_conv, x="position", y="shot_conversion",
            color="shot_conversion",
            color_continuous_scale=[[0, "#003d1a"], [1, GREEN]],
            labels={"shot_conversion": "Conversion %", "position": "Position"},
            text="shot_conversion",
        )
        fig_conv.update_traces(texttemplate="%{text:.1f}%", textposition="outside",
                               marker_line_width=0)
        fig_conv.update_layout(coloraxis_showscale=False)
        _apply_dark_layout(fig_conv, "Avg Shot Conversion % by Position", height=360)
        st.plotly_chart(fig_conv, use_container_width=True)

    # Age vs Rating
    with col_f:
        _section("Age vs Rating")
        fig_age = px.scatter(
            df, x="age", y="rating", color="position",
            hover_name="name",
            hover_data={"team": True, "age": True, "rating": True},
            color_discrete_sequence=ACCENT_COLORS,
            labels={"age": "Player Age", "rating": "Rating"},
            trendline="lowess", trendline_scope="overall",
            trendline_color_override=GREEN, opacity=0.75,
        )
        fig_age.update_traces(selector=dict(mode="markers"), marker=dict(size=7))
        _apply_dark_layout(fig_age, "Age vs Rating (LOWESS Trend)", height=360)
        st.plotly_chart(fig_age, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 3 — TEAM ANALYSIS
# ════════════════════════════════════════════════════════════════════════════

def render_team_analysis(df: pd.DataFrame) -> None:
    """Render the Team Analysis page."""

    team_agg = (
        df.groupby("team")
        .agg(
            total_goals  =("goals",        "sum"),
            total_assists=("assists",       "sum"),
            player_count =("player_id",    "nunique"),
            avg_rating   =("rating",       "mean"),
            total_minutes=("minutes_played","sum"),
            avg_pass_acc =("pass_accuracy","mean"),
        )
        .reset_index().sort_values("total_goals", ascending=False)
    )
    team_agg["avg_rating"]   = team_agg["avg_rating"].round(2)
    team_agg["avg_pass_acc"] = team_agg["avg_pass_acc"].round(1)

    _section("Goals & Assists per Team")
    fig_ga = go.Figure()
    fig_ga.add_trace(go.Bar(
        name="Goals", x=team_agg["team"], y=team_agg["total_goals"],
        marker_color=GREEN, marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>Goals: %{y}<extra></extra>",
    ))
    fig_ga.add_trace(go.Bar(
        name="Assists", x=team_agg["team"], y=team_agg["total_assists"],
        marker_color="#2979FF", marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>Assists: %{y}<extra></extra>",
    ))
    fig_ga.update_layout(barmode="group", xaxis_title="Team", yaxis_title="Count")
    _apply_dark_layout(fig_ga, "Total Goals & Assists per Team", height=380)
    st.plotly_chart(fig_ga, use_container_width=True)

    _divider()
    col1, col2 = st.columns(2)

    with col1:
        _section("Unique Players per Team")
        sorted_pc = team_agg.sort_values("player_count")
        fig_pc = px.bar(
            sorted_pc, x="player_count", y="team", orientation="h",
            color="player_count",
            color_continuous_scale=[[0, "#003d1a"], [1, GREEN]],
            labels={"player_count": "Players", "team": "Team"},
        )
        fig_pc.update_layout(coloraxis_showscale=False)
        fig_pc.update_traces(marker_line_width=0)
        _apply_dark_layout(fig_pc, "Unique Players per Team", height=340)
        st.plotly_chart(fig_pc, use_container_width=True)

    with col2:
        _section("Average Rating per Team")
        sorted_ar = team_agg.sort_values("avg_rating", ascending=False)
        fig_ar = px.bar(
            sorted_ar, x="team", y="avg_rating", color="avg_rating",
            color_continuous_scale=[[0, "#003d1a"], [1, GREEN]],
            labels={"avg_rating": "Avg Rating", "team": "Team"},
            text="avg_rating",
        )
        fig_ar.update_traces(texttemplate="%{text:.2f}", textposition="outside",
                             marker_line_width=0)
        fig_ar.update_layout(coloraxis_showscale=False, yaxis_range=[0, 10])
        _apply_dark_layout(fig_ar, "Average Player Rating by Team", height=340)
        st.plotly_chart(fig_ar, use_container_width=True)

    _divider()
    col3, col4 = st.columns(2)

    with col3:
        _section("Avg Pass Accuracy per Team")
        sorted_pa = team_agg.sort_values("avg_pass_acc", ascending=False)
        fig_pa = px.bar(
            sorted_pa, x="avg_pass_acc", y="team", orientation="h",
            color="avg_pass_acc",
            color_continuous_scale=[[0, "#001a3d"], [1, "#2979FF"]],
            labels={"avg_pass_acc": "Pass Acc (%)", "team": "Team"},
            text="avg_pass_acc",
        )
        fig_pa.update_traces(texttemplate="%{text:.1f}%", textposition="outside",
                             marker_line_width=0)
        fig_pa.update_layout(coloraxis_showscale=False, xaxis_range=[0, 100])
        _apply_dark_layout(fig_pa, "Average Pass Accuracy per Team", height=340)
        st.plotly_chart(fig_pa, use_container_width=True)

    with col4:
        _section("Total Minutes per Team")
        sorted_mn = team_agg.sort_values("total_minutes", ascending=False)
        fig_mn = px.bar(
            sorted_mn, x="team", y="total_minutes", color="total_minutes",
            color_continuous_scale=[[0, "#1a0040"], [1, "#E040FB"]],
            labels={"total_minutes": "Total Minutes", "team": "Team"},
            text=sorted_mn["total_minutes"].apply(lambda x: f"{x // 1000:.0f}K"),
        )
        fig_mn.update_traces(textposition="outside", marker_line_width=0)
        fig_mn.update_layout(coloraxis_showscale=False)
        _apply_dark_layout(fig_mn, "Total Minutes Played per Team", height=340)
        st.plotly_chart(fig_mn, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 4 — POSITION ANALYSIS
# ════════════════════════════════════════════════════════════════════════════

def render_position_analysis(df: pd.DataFrame) -> None:
    """Render the Position Analysis page."""

    pos_order  = ["GK", "DEF", "MID", "FWD"]
    pos_labels = {
        "GK": "Goalkeeper (GK)", "DEF": "Defender (DEF)",
        "MID": "Midfielder (MID)", "FWD": "Forward (FWD)",
    }

    pos_agg = (
        df.groupby("position")
        .agg(
            avg_goals    =("goals",        "mean"),
            avg_assists  =("assists",       "mean"),
            avg_pass_acc =("pass_accuracy", "mean"),
            avg_rating   =("rating",        "mean"),
            avg_dribbles =("dribbles",      "mean"),
            avg_tackles  =("tackles",       "mean"),
            avg_shots    =("shots",         "mean"),
            total_goals  =("goals",         "sum"),
            total_assists=("assists",        "sum"),
        )
        .reset_index()
    )

    _section("Position Averages (Goals per Player)")
    cols = st.columns(4)
    for col, pos in zip(cols, pos_order):
        row = pos_agg[pos_agg["position"] == pos]
        if not row.empty:
            avg_g = row["avg_goals"].values[0]
            avg_r = row["avg_rating"].values[0]
            avg_a = row["avg_assists"].values[0]
            col.metric(
                label=pos_labels[pos],
                value=f"{avg_g:.1f} goals",
                delta=f"Rating: {avg_r:.2f} | Assists: {avg_a:.1f}",
            )
        else:
            col.metric(label=pos_labels.get(pos, pos), value="N/A")

    _divider()
    col_a, col_b = st.columns(2)

    with col_a:
        _section("Goals Distribution by Position")
        fig_box = px.box(
            df, x="position", y="goals", color="position",
            category_orders={"position": pos_order},
            color_discrete_sequence=ACCENT_COLORS,
            labels={"position": "Position", "goals": "Goals"},
            notched=False, points="outliers",
        )
        fig_box.update_traces(hovertemplate="<b>%{x}</b><br>Goals: %{y}<extra></extra>")
        _apply_dark_layout(fig_box, "Goals Distribution by Position", height=360)
        st.plotly_chart(fig_box, use_container_width=True)

    with col_b:
        _section("Pass Accuracy by Position")
        fig_vio = px.violin(
            df, x="position", y="pass_accuracy", color="position",
            category_orders={"position": pos_order},
            color_discrete_sequence=ACCENT_COLORS,
            labels={"position": "Position", "pass_accuracy": "Pass Accuracy (%)"},
            box=True, points="outliers",
        )
        _apply_dark_layout(fig_vio, "Pass Accuracy Distribution by Position", height=360)
        st.plotly_chart(fig_vio, use_container_width=True)

    _divider()
    _section("Tackles & Dribbles by Position (Avg)")
    pos_agg_ordered = (
        pos_agg.set_index("position")
        .reindex([p for p in pos_order if p in pos_agg["position"].values])
        .reset_index()
    )
    fig_td = go.Figure()
    fig_td.add_trace(go.Bar(
        name="Avg Tackles", x=pos_agg_ordered["position"],
        y=pos_agg_ordered["avg_tackles"].round(1),
        marker_color=ACCENT_COLORS[0], marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>Avg Tackles: %{y}<extra></extra>",
    ))
    fig_td.add_trace(go.Bar(
        name="Avg Dribbles", x=pos_agg_ordered["position"],
        y=pos_agg_ordered["avg_dribbles"].round(1),
        marker_color=ACCENT_COLORS[1], marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>Avg Dribbles: %{y}<extra></extra>",
    ))
    fig_td.update_layout(barmode="group", xaxis_title="Position", yaxis_title="Average Count")
    _apply_dark_layout(fig_td, "Average Tackles & Dribbles by Position", height=360)
    st.plotly_chart(fig_td, use_container_width=True)

    _divider()
    _section("Position Profile Radar")
    radar_metrics = ["avg_goals", "avg_assists", "avg_shots",
                     "avg_pass_acc", "avg_dribbles", "avg_tackles"]
    radar_labels  = ["Goals", "Assists", "Shots", "Pass Acc.", "Dribbles", "Tackles"]
    fig_pos_radar = go.Figure()
    for i, pos in enumerate([p for p in pos_order if p in pos_agg["position"].values]):
        row   = pos_agg[pos_agg["position"] == pos].iloc[0]
        color = ACCENT_COLORS[i % len(ACCENT_COLORS)]
        raw   = [row[m] for m in radar_metrics]
        norms = []
        for j, m in enumerate(radar_metrics):
            col_min = pos_agg[m].min()
            col_max = pos_agg[m].max()
            denom = col_max - col_min if col_max != col_min else 1
            norms.append((raw[j] - col_min) / denom)
        norms += [norms[0]]
        fig_pos_radar.add_trace(go.Scatterpolar(
            r=norms, theta=radar_labels + [radar_labels[0]],
            fill="toself", name=pos_labels.get(pos, pos),
            line=dict(color=color, width=2),
            fillcolor=hex_to_rgba(color, 0.12),
        ))
    fig_pos_radar.update_layout(
        polar=dict(
            bgcolor=PLOT_BG,
            radialaxis=dict(visible=True, range=[0, 1], showticklabels=False,
                            gridcolor="rgba(0,230,118,0.1)"),
            angularaxis=dict(tickfont=dict(size=12, color="#CCDDCC"),
                             gridcolor="rgba(0,230,118,0.08)"),
        ),
        showlegend=True,
        legend=dict(font=dict(color="#FAFAFA"), bgcolor="rgba(0,0,0,0.3)"),
    )
    _apply_dark_layout(fig_pos_radar, "Position Average Profile (Normalised 0-1)", height=500)
    st.plotly_chart(fig_pos_radar, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 5 — DISCIPLINE
# ════════════════════════════════════════════════════════════════════════════

def render_discipline(df: pd.DataFrame) -> None:
    """Render Discipline page: yellow/red cards analysis."""

    _section("Disciplinary Overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Yellow Cards", f"{df['yellow_cards'].sum():,}")
    c2.metric("Total Red Cards",    f"{df['red_cards'].sum():,}")
    most_carded_team = df.groupby("team")["yellow_cards"].sum().idxmax()
    c3.metric("Most Carded Team", most_carded_team)
    mc = df.groupby("name")[["yellow_cards", "red_cards"]].sum()
    mc["total"] = mc["yellow_cards"] + mc["red_cards"]
    c4.metric("Most Carded Player", mc["total"].idxmax())

    _divider()
    col1, col2 = st.columns(2)

    with col1:
        _section("Cards by Position")
        card_pos = (
            df.groupby("position", as_index=False)
            .agg(yellow=("yellow_cards","sum"), red=("red_cards","sum"))
        )
        fig_cp = go.Figure()
        fig_cp.add_trace(go.Bar(
            name="Yellow Cards", x=card_pos["position"], y=card_pos["yellow"],
            marker_color="#FFD600", marker_line_width=0,
            hovertemplate="<b>%{x}</b><br>Yellow: %{y}<extra></extra>",
        ))
        fig_cp.add_trace(go.Bar(
            name="Red Cards", x=card_pos["position"], y=card_pos["red"],
            marker_color="#FF1744", marker_line_width=0,
            hovertemplate="<b>%{x}</b><br>Red: %{y}<extra></extra>",
        ))
        fig_cp.update_layout(barmode="group")
        _apply_dark_layout(fig_cp, "Cards by Position", height=360)
        st.plotly_chart(fig_cp, use_container_width=True)

    with col2:
        _section("Cards by Team")
        card_team = (
            df.groupby("team", as_index=False)
            .agg(yellow=("yellow_cards","sum"), red=("red_cards","sum"))
            .sort_values("yellow", ascending=False)
        )
        fig_ct = go.Figure()
        fig_ct.add_trace(go.Bar(
            name="Yellow", x=card_team["team"], y=card_team["yellow"],
            marker_color="#FFD600", marker_line_width=0,
        ))
        fig_ct.add_trace(go.Bar(
            name="Red", x=card_team["team"], y=card_team["red"],
            marker_color="#FF1744", marker_line_width=0,
        ))
        fig_ct.update_layout(barmode="group")
        _apply_dark_layout(fig_ct, "Cards by Team", height=360)
        st.plotly_chart(fig_ct, use_container_width=True)

    _divider()
    _section("Top 15 Most Disciplined Players")
    carded = (
        df.groupby("name", as_index=False)
        .agg(team=("team","first"), position=("position","first"),
             yellow=("yellow_cards","sum"), red=("red_cards","sum"))
    )
    carded["total"] = carded["yellow"] + carded["red"]
    carded = carded.nlargest(15, "total").reset_index(drop=True)
    fig_carded = go.Figure()
    fig_carded.add_trace(go.Bar(
        name="Yellow", x=carded["name"], y=carded["yellow"],
        marker_color="#FFD600", marker_line_width=0,
    ))
    fig_carded.add_trace(go.Bar(
        name="Red", x=carded["name"], y=carded["red"],
        marker_color="#FF1744", marker_line_width=0,
    ))
    fig_carded.update_layout(barmode="stack")
    _apply_dark_layout(fig_carded, "Top 15 Most Carded Players", height=400)
    st.plotly_chart(fig_carded, use_container_width=True)

    _divider()
    _section("Rating vs Total Cards (Scatter)")
    card_rating = (
        df.groupby("name", as_index=False)
        .agg(rating=("rating","mean"), yellow=("yellow_cards","sum"),
             red=("red_cards","sum"), position=("position","first"))
    )
    card_rating["total_cards"] = card_rating["yellow"] + card_rating["red"]
    fig_cr = px.scatter(
        card_rating, x="total_cards", y="rating", color="position",
        hover_name="name", color_discrete_sequence=ACCENT_COLORS,
        labels={"total_cards": "Total Cards", "rating": "Avg Rating"},
        opacity=0.8, trendline="ols", trendline_scope="overall",
        trendline_color_override=GREEN,
    )
    fig_cr.update_traces(selector=dict(mode="markers"), marker=dict(size=8))
    _apply_dark_layout(fig_cr, "Rating vs Total Cards (OLS Trend)", height=380)
    st.plotly_chart(fig_cr, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 6 — STATS TABLE + CSV DOWNLOAD
# ════════════════════════════════════════════════════════════════════════════

def render_stats_table(df: pd.DataFrame) -> None:
    """Render a searchable player statistics table and a CSV download button."""

    _section("Player Statistics Table")
    col_search, col_pos, col_dl = st.columns([2.5, 1.5, 1])

    with col_search:
        search = st.text_input(
            "Search player by name", placeholder="Type a player name…",
            key="table_search",
        )
    with col_pos:
        pos_filter = st.selectbox(
            "Filter by Position", options=["All", "GK", "DEF", "MID", "FWD"],
            key="table_pos",
        )
    with col_dl:
        st.markdown("<br>", unsafe_allow_html=True)
        if df.empty:
            st.button("Download CSV", disabled=True, help="No data to download.")
        else:
            csv_bytes = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download CSV",
                data=csv_bytes,
                file_name="football_players_filtered.csv",
                mime="text/csv",
                help="Download the currently filtered dataset as a CSV file.",
            )

    display_df = df.copy()
    if search.strip():
        display_df = display_df[
            display_df["name"].str.contains(search.strip(), case=False, na=False)
        ]
    if pos_filter != "All":
        display_df = display_df[display_df["position"] == pos_filter]

    display_cols = [
        "name", "team", "position", "season", "age", "nationality",
        "goals", "assists", "goal_contributions", "shots", "shot_conversion",
        "pass_accuracy", "tackles", "dribbles", "rating",
        "minutes_played", "yellow_cards", "red_cards",
    ]
    display_cols = [c for c in display_cols if c in display_df.columns]

    st.dataframe(
        display_df[display_cols].reset_index(drop=True),
        use_container_width=True, height=440, hide_index=True,
        column_config={
            "name":             st.column_config.TextColumn("Player"),
            "team":             st.column_config.TextColumn("Team"),
            "position":         st.column_config.TextColumn("Pos"),
            "season":           st.column_config.TextColumn("Season"),
            "age":              st.column_config.NumberColumn("Age"),
            "nationality":      st.column_config.TextColumn("Nation"),
            "goals":            st.column_config.NumberColumn("Goals"),
            "assists":          st.column_config.NumberColumn("Assists"),
            "goal_contributions": st.column_config.NumberColumn("G+A"),
            "shots":            st.column_config.NumberColumn("Shots"),
            "shot_conversion":  st.column_config.ProgressColumn(
                "Conv%", min_value=0, max_value=100, format="%.1f"),
            "pass_accuracy":    st.column_config.ProgressColumn(
                "Pass%", min_value=0, max_value=100, format="%.1f"),
            "tackles":          st.column_config.NumberColumn("Tackles"),
            "dribbles":         st.column_config.NumberColumn("Dribbles"),
            "rating":           st.column_config.ProgressColumn(
                "Rating", min_value=0, max_value=10, format="%.1f"),
            "minutes_played":   st.column_config.NumberColumn("Minutes"),
            "yellow_cards":     st.column_config.NumberColumn("Yellow"),
            "red_cards":        st.column_config.NumberColumn("Red"),
        },
    )
    st.caption(
        f"Showing **{len(display_df):,}** records | "
        "Data source: Synthetic — not real-world data"
    )


# ════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════

def main() -> None:
    """Main app entry point."""

    st.markdown(
        '<h1 class="hero-header">Football Analytics Dashboard</h1>'
        '<p class="hero-subtitle">Portfolio-Grade · Synthetic Data · Python + Streamlit + Plotly</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="disclaimer-banner">'
        "<strong>Data notice:</strong> All player statistics shown are <strong>synthetic</strong> "
        "and do <strong>not</strong> represent real-world football results. "
        "Generated with <code>numpy.random.seed(42)</code> for reproducibility."
        "</div>",
        unsafe_allow_html=True,
    )

    df_raw = load_data()
    df = apply_filters(df_raw)

    if df.empty:
        st.warning(
            "No data matches the selected filters. "
            "Please adjust your Season, Team, Position, Age Range, or Player Name selections."
        )
        return

    # Quick stat pills
    st.markdown(
        f'<span class="stat-pill">{df["player_id"].nunique():,} Players</span>'
        f'<span class="stat-pill">{df["goals"].sum():,} Goals</span>'
        f'<span class="stat-pill">{df["assists"].sum():,} Assists</span>'
        f'<span class="stat-pill">{df["season"].nunique()} Seasons</span>'
        f'<span class="stat-pill">{df["team"].nunique()} Teams</span>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Overview",
        "Player Analysis",
        "Team Analysis",
        "Position Analysis",
        "Discipline",
        "Stats Table",
    ])

    with tab1:
        render_overview(df)
    with tab2:
        render_player_analysis(df)
    with tab3:
        render_team_analysis(df)
    with tab4:
        render_position_analysis(df)
    with tab5:
        render_discipline(df)
    with tab6:
        render_stats_table(df)


if __name__ == "__main__":
    main()
