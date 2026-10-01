import plotly.graph_objects as go
import streamlit as st
from components import inject_css, page_header, section_title, stat_grid, stat_tile_html, team_header_html
from data_loader import available_years, load_games, load_team_game_splits, load_team_season_splits, load_teams
from theme import PLOTLY_LAYOUT, TEXT_MUTED, team_colors, team_logo

st.set_page_config(page_title="Team Explorer", page_icon="🏈", layout="wide")
inject_css(st)
page_header(st, "Team Explorer")

years = available_years()
if not years:
    st.warning("No processed data found. Run `python scripts/build_dataset.py <year>` first.")
    st.stop()

col1, col2 = st.columns([1, 2])
year = col1.selectbox("Season", years, index=len(years) - 1)

teams_df = load_teams(year)
teams = teams_df.set_index("school")
team_names = sorted(teams.index.tolist())
team = col2.selectbox("Team", team_names, index=team_names.index("Ohio State") if "Ohio State" in team_names else 0)

trow = teams.loc[team]
colors = team_colors(trow)
logo = team_logo(trow)

st.markdown(team_header_html(team, trow.get("conference", ""), logo), unsafe_allow_html=True)

season_off = load_team_season_splits(year, "offense")
season_def = load_team_season_splits(year, "defense")
team_off = season_off[season_off["team"] == team]
team_def = season_def[season_def["team"] == team]

qualified_off = season_off[season_off["plays"].ge(200) & season_off["team"].isin(teams.index)]
qualified_def = season_def[season_def["plays"].ge(200) & season_def["team"].isin(teams.index)]
nat_off = qualified_off[["success_rate", "stuff_rate", "havoc_rate", "ppa_per_play"]].mean()
nat_def = qualified_def[["success_rate", "stuff_rate", "havoc_rate", "ppa_per_play"]].mean()


def tile(label, value, national, higher_is_better, fmt="{:.1%}", diff_fmt="{:+.1f}pp vs avg", diff_scale=100):
    diff = (value - national) * diff_scale
    better = (diff > 0) if higher_is_better else (diff < 0)
    if abs(diff) < 0.05:
        better = None
    return stat_tile_html(label, fmt.format(value), diff_fmt.format(diff), better)


section_title(st, "Offense")
if team_off.empty:
    st.info("No offensive plays recorded for this team/season.")
else:
    r = team_off.iloc[0]
    stat_grid(
        st,
        [
            tile("Success Rate", r["success_rate"], nat_off["success_rate"], True),
            tile("PPA / Play", r["ppa_per_play"], nat_off["ppa_per_play"], True, fmt="{:.2f}", diff_fmt="{:+.2f} vs avg", diff_scale=1),
            tile("Stuffed Run Rate", r["stuff_rate"], nat_off["stuff_rate"], False),
            tile("Havoc Allowed Rate", r["havoc_rate"], nat_off["havoc_rate"], False),
        ],
    )

section_title(st, "Defense")
if team_def.empty:
    st.info("No defensive plays recorded for this team/season.")
else:
    r = team_def.iloc[0]
    stat_grid(
        st,
        [
            tile("Success Rate Allowed", r["success_rate"], nat_def["success_rate"], False),
            tile("PPA / Play Allowed", r["ppa_per_play"], nat_def["ppa_per_play"], False, fmt="{:.2f}", diff_fmt="{:+.2f} vs avg", diff_scale=1),
            tile("Opponent Stuff Rate", r["stuff_rate"], nat_def["stuff_rate"], True),
            tile("Havoc Rate", r["havoc_rate"], nat_def["havoc_rate"], True),
        ],
    )

section_title(st, "Game-by-Game Trend")

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
                name="Offense",
                mode="lines+markers",
                line=dict(color=colors["primary"], width=2, shape="spline", smoothing=0.3),
                marker=dict(size=7, line=dict(width=1, color=PLOTLY_LAYOUT["plot_bgcolor"])),
                hovertemplate="Week %{x}: %{y:.1%}<extra>Offense</extra>",
            )
        )
    if not trend_def.empty:
        fig.add_trace(
            go.Scatter(
                x=trend_def["week"],
                y=trend_def["success_rate"],
                name="Defense allowed",
                mode="lines+markers",
                line=dict(color=TEXT_MUTED, width=2, dash="dot", shape="spline", smoothing=0.3),
                marker=dict(size=7, line=dict(width=1, color=PLOTLY_LAYOUT["plot_bgcolor"])),
                hovertemplate="Week %{x}: %{y:.1%}<extra>Defense allowed</extra>",
            )
        )
    fig.update_layout(**PLOTLY_LAYOUT, height=420, yaxis_tickformat=".0%", xaxis_title="Week", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
