import plotly.graph_objects as go
import streamlit as st
from components import inject_css, page_header, play_row_html, scoreboard_html, section_title
from data_loader import available_years, load_games, load_plays, load_teams
from theme import FALLBACK_PRIMARY, FALLBACK_SECONDARY, PLOTLY_LAYOUT, team_colors, team_logo

st.set_page_config(page_title="Game Explorer", page_icon="🏈", layout="wide")
inject_css(st)
page_header(st, "Game Explorer")

years = available_years()
if not years:
    st.warning("No processed data found. Run `python scripts/build_dataset.py <year>` first.")
    st.stop()

year = st.selectbox("Season", years, index=len(years) - 1)
games = load_games(year)
plays = load_plays(year)
teams = load_teams(year).set_index("school")

games_with_plays = set(plays["gameId"].unique())
games = games[games["completed"] & games["id"].isin(games_with_plays)].copy()

week = st.selectbox("Week", sorted(games["week"].unique()))
week_games = games[games["week"] == week].copy()
week_games["label"] = (
    week_games["awayTeam"]
    + " @ "
    + week_games["homeTeam"]
    + " ("
    + week_games["awayPoints"].astype("Int64").astype(str)
    + "-"
    + week_games["homePoints"].astype("Int64").astype(str)
    + ")"
)

game_label = st.selectbox("Game", week_games["label"].tolist())
game_row = week_games[week_games["label"] == game_label].iloc[0]
game_id = game_row["id"]

away_team, home_team = game_row["awayTeam"], game_row["homeTeam"]
away_logo = team_logo(teams.loc[away_team]) if away_team in teams.index else None
home_logo = team_logo(teams.loc[home_team]) if home_team in teams.index else None
away_color = team_colors(teams.loc[away_team])["primary"] if away_team in teams.index else FALLBACK_PRIMARY
home_color = team_colors(teams.loc[home_team])["primary"] if home_team in teams.index else FALLBACK_SECONDARY
if away_color == home_color:
    home_color = FALLBACK_SECONDARY

def _int_or_none(v):
    return None if v is None or v != v else int(v)


st.markdown(
    scoreboard_html(
        away_team, away_logo, _int_or_none(game_row["awayPoints"]), home_team, home_logo, _int_or_none(game_row["homePoints"])
    ),
    unsafe_allow_html=True,
)

game_plays = plays[(plays["gameId"] == game_id) & plays["success"].notna()].sort_values(["driveNumber", "playNumber"])

section_title(st, "Cumulative Success Rate")
fig = go.Figure()
for team, color in [(away_team, away_color), (home_team, home_color)]:
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
            line=dict(color=color, width=2.5),
            hovertemplate=f"{team} play %{{x}}: %{{y:.1%}}<extra></extra>",
        )
    )
fig.update_layout(
    **PLOTLY_LAYOUT,
    height=420,
    yaxis_tickformat=".0%",
    xaxis_title="Offensive play #",
    yaxis_title="Cumulative success rate",
    hovermode="x unified",
)
st.plotly_chart(fig, use_container_width=True)
st.caption("Each line is that team's own running success rate across its offensive plays in the game (not aligned to game clock).")

section_title(st, "Play-by-Play")

rows_html = []
for _, p in game_plays.iterrows():
    down_distance = f"{int(p['down'])}{'st' if p['down']==1 else 'nd' if p['down']==2 else 'rd' if p['down']==3 else 'th'} &amp; {int(p['distance'])}"
    tag = f"{p['offense']} — {down_distance}"
    rows_html.append(play_row_html(tag, p["playText"], p["success"]))

st.markdown("".join(rows_html[:60]), unsafe_allow_html=True)
if len(rows_html) > 60:
    st.caption(f"Showing first 60 of {len(rows_html)} plays.")
