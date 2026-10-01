import streamlit as st
from components import inject_css, leader_row_html, page_header, section_title
from data_loader import available_years, load_team_season_splits, load_teams
from theme import ACCENT, team_colors, team_logo

st.set_page_config(page_title="CFB Analytics", page_icon="🏈", layout="wide")
inject_css(st)

page_header(
    st,
    "College Football Analytics",
    "Play-by-play success rate &amp; defensive efficiency, built from collegefootballdata.com data.",
)

years = available_years()
if not years:
    st.warning("No processed data found. Run `python scripts/build_dataset.py <year>` first.")
    st.stop()

year = st.selectbox("Season", years, index=len(years) - 1)

teams = load_teams(year).set_index("school")
offense = load_team_season_splits(year, "offense")
fbs_offense = offense[offense["team"].isin(teams.index)]
top = fbs_offense[fbs_offense["plays"] >= 200].sort_values("success_rate", ascending=False).head(15).reset_index(drop=True)
max_rate = top["success_rate"].max()

section_title(st, f"Top Offenses by Success Rate — {year}")

rows_html = []
for i, row in top.iterrows():
    team_name = row["team"]
    logo = None
    color = ACCENT
    if team_name in teams.index:
        trow = teams.loc[team_name]
        logo = team_logo(trow)
        color = team_colors(trow)["primary"]
    rows_html.append(leader_row_html(i + 1, logo, team_name, row["success_rate"], max_rate, color))

st.markdown("".join(rows_html), unsafe_allow_html=True)
st.caption("Minimum 200 offensive plays. Success rate: 50% of distance on 1st down, 70% on 2nd, 100% on 3rd/4th.")
