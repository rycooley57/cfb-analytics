import plotly.graph_objects as go
import streamlit as st
from data_loader import available_years, load_team_season_splits
from theme import CATEGORICAL, PLOTLY_LAYOUT

st.set_page_config(page_title="CFB Analytics", page_icon="🏈", layout="wide")

st.title("College Football Analytics")
st.caption(
    "Play-by-play success rate & defensive efficiency, built from "
    "collegefootballdata.com data. Use the sidebar to explore a team, a "
    "single game, or the baseline play-success model."
)

years = available_years()
if not years:
    st.warning("No processed data found. Run `python scripts/build_dataset.py <year>` first.")
    st.stop()

year = st.selectbox("Season", years, index=len(years) - 1)

offense = load_team_season_splits(year, "offense")
top = offense[offense["plays"] >= 200].sort_values("success_rate", ascending=False).head(15)

st.subheader(f"Top offenses by success rate — {year}")
fig = go.Figure(
    go.Bar(
        x=top["success_rate"],
        y=top["team"],
        orientation="h",
        marker_color=CATEGORICAL["primary"],
        text=[f"{v:.1%}" for v in top["success_rate"]],
        textposition="outside",
        hovertemplate="%{y}: %{x:.1%}<extra></extra>",
    )
)
fig.update_layout(**PLOTLY_LAYOUT, height=500, xaxis_tickformat=".0%")
fig.update_yaxes(autorange="reversed")
st.plotly_chart(fig, use_container_width=True)

st.caption("Minimum 200 offensive plays. Success rate: 50% of distance on 1st down, 70% on 2nd, 100% on 3rd/4th.")
