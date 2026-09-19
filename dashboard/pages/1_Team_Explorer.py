import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from data_loader import available_years, load_games, load_team_game_splits, load_team_season_splits, load_teams
from theme import CATEGORICAL, PLOTLY_LAYOUT

st.set_page_config(page_title="Team Explorer", page_icon="🏈", layout="wide")
st.title("Team Explorer")

years = available_years()
if not years:
    st.warning("No processed data found. Run `python scripts/build_dataset.py <year>` first.")
    st.stop()

col1, col2 = st.columns([1, 2])
year = col1.selectbox("Season", years, index=len(years) - 1)

teams = sorted(load_teams(year)["school"].tolist())
team = col2.selectbox("Team", teams, index=teams.index("Ohio State") if "Ohio State" in teams else 0)

season_off = load_team_season_splits(year, "offense")
season_def = load_team_season_splits(year, "defense")

team_off = season_off[season_off["team"] == team]
team_def = season_def[season_def["team"] == team]
national_off = season_off[season_off["plays"] >= 200][["success_rate", "stuff_rate", "havoc_rate", "ppa_per_play"]].mean()
national_def = season_def[season_def["plays"] >= 200][["success_rate", "stuff_rate", "havoc_rate", "ppa_per_play"]].mean()

st.subheader(f"{team} vs. national average — {year}")

METRIC_LABELS = {
    "success_rate": "Success rate",
    "stuff_rate": "Stuff rate (runs stopped at/behind line)",
    "havoc_rate": "Havoc rate (sacks + stuffs + turnovers forced)",
    "ppa_per_play": "PPA per play",
}


def comparison_chart(team_row: pd.Series, national_row: pd.Series, title: str, higher_is_better_ppa: bool = True):
    metrics = list(METRIC_LABELS.keys())
    fig = go.Figure()
    fig.add_bar(
        name=team,
        x=[METRIC_LABELS[m] for m in metrics],
        y=[team_row[m] for m in metrics],
        marker_color=CATEGORICAL["primary"],
    )
    fig.add_bar(
        name="National avg",
        x=[METRIC_LABELS[m] for m in metrics],
        y=[national_row[m] for m in metrics],
        marker_color=CATEGORICAL["secondary"],
    )
    fig.update_layout(**PLOTLY_LAYOUT, barmode="group", title=title, height=380)
    return fig


left, right = st.columns(2)
if team_off.empty:
    left.info("No offensive plays recorded for this team/season.")
else:
    left.plotly_chart(comparison_chart(team_off.iloc[0], national_off, "Offense"), use_container_width=True)

if team_def.empty:
    right.info("No defensive plays recorded for this team/season.")
else:
    right.plotly_chart(comparison_chart(team_def.iloc[0], national_def, "Defense (allowed)"), use_container_width=True)

st.subheader("Game-by-game trend")

games = load_games(year)[["id", "week", "homeTeam", "awayTeam"]].rename(columns={"id": "gameId"})
game_off = load_team_game_splits(year, "offense")
game_def = load_team_game_splits(year, "defense")

trend_off = game_off[game_off["team"] == team].merge(games, on="gameId").sort_values("week")
trend_def = game_def[game_def["team"] == team].merge(games, on="gameId").sort_values("week")

if trend_off.empty and trend_def.empty:
    st.info("No game-level data for this team/season.")
else:
    fig = go.Figure()
    if not trend_off.empty:
        fig.add_trace(
            go.Scatter(
                x=trend_off["week"],
                y=trend_off["success_rate"],
                name="Offense success rate",
                mode="lines+markers",
                line=dict(color=CATEGORICAL["primary"], width=2),
                marker=dict(size=8),
                hovertemplate="Week %{x}: %{y:.1%}<extra></extra>",
            )
        )
    if not trend_def.empty:
        fig.add_trace(
            go.Scatter(
                x=trend_def["week"],
                y=trend_def["success_rate"],
                name="Defense success rate allowed",
                mode="lines+markers",
                line=dict(color=CATEGORICAL["secondary"], width=2),
                marker=dict(size=8),
                hovertemplate="Week %{x}: %{y:.1%}<extra></extra>",
            )
        )
    fig.update_layout(**PLOTLY_LAYOUT, height=420, yaxis_tickformat=".0%", xaxis_title="Week")
    st.plotly_chart(fig, use_container_width=True)
