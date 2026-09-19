import plotly.graph_objects as go
import streamlit as st
from data_loader import available_years, load_games, load_plays
from theme import CATEGORICAL, PLOTLY_LAYOUT

st.set_page_config(page_title="Game Explorer", page_icon="🏈", layout="wide")
st.title("Game Explorer")

years = available_years()
if not years:
    st.warning("No processed data found. Run `python scripts/build_dataset.py <year>` first.")
    st.stop()

year = st.selectbox("Season", years, index=len(years) - 1)
games = load_games(year)
plays = load_plays(year)

games_with_plays = set(plays["gameId"].unique())
games = games[games["completed"] & games["id"].isin(games_with_plays)].copy()

week = st.selectbox("Week", sorted(games["week"].unique()))
week_games = games[games["week"] == week].copy()
week_games["label"] = week_games["awayTeam"] + " @ " + week_games["homeTeam"] + " (" + week_games["awayPoints"].astype("Int64").astype(str) + "-" + week_games["homePoints"].astype("Int64").astype(str) + ")"

game_label = st.selectbox("Game", week_games["label"].tolist())
game_row = week_games[week_games["label"] == game_label].iloc[0]
game_id = game_row["id"]

game_plays = plays[(plays["gameId"] == game_id) & plays["success"].notna()].sort_values(["driveNumber", "playNumber"])

teams = [game_row["awayTeam"], game_row["homeTeam"]]
colors = [CATEGORICAL["primary"], CATEGORICAL["secondary"]]

st.subheader(f"{game_label} — cumulative success rate")
fig = go.Figure()
for team, color in zip(teams, colors):
    team_plays = game_plays[game_plays["offense"] == team].reset_index(drop=True)
    if team_plays.empty:
        continue
    cumulative = team_plays["success"].expanding().mean()
    fig.add_trace(
        go.Scatter(
            x=list(range(1, len(cumulative) + 1)),
            y=cumulative,
            name=team,
            mode="lines",
            line=dict(color=color, width=2),
            hovertemplate=f"{team} play %{{x}}: %{{y:.1%}}<extra></extra>",
        )
    )
fig.update_layout(**PLOTLY_LAYOUT, height=450, yaxis_tickformat=".0%", xaxis_title="Offensive play #", yaxis_title="Cumulative success rate")
st.plotly_chart(fig, use_container_width=True)
st.caption("Each line is that team's own running success rate across its offensive plays in the game (not aligned to game clock).")

st.subheader("Play-by-play")
display_cols = ["offense", "defense", "period", "down", "distance", "yardsGained", "playType", "success", "playText"]
st.dataframe(game_plays[display_cols], use_container_width=True, height=400)
