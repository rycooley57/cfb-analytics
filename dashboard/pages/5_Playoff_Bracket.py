import streamlit as st
import streamlit.components.v1 as components
from bracket import bracket_html
from components import inject_css, page_header
from data_loader import available_years, load_ap_top25, load_d1_teams
from scenarios import PROJECT_RUDY_BLURB, PROJECT_RUDY_LABEL, PROJECT_RUDY_RANKED
from theme import team_colors, team_logo

st.set_page_config(page_title="Playoff Bracket", page_icon="🏆", layout="wide")
inject_css(st)
page_header(
    st,
    "Playoff Bracket",
    "Seeded from the latest AP Top 25. Pick a bracket size, drag teams to re-seed the first round, "
    "and click a team to advance them.",
)

years = available_years()
if not years:
    st.warning("No processed data found. Run `python scripts/build_dataset.py <year>` first.")
    st.stop()

year_options = years + [2199]
year = st.selectbox(
    "Season",
    year_options,
    index=len(years) - 1,
    format_func=lambda y: PROJECT_RUDY_LABEL if y == 2199 else str(y),
)

if year == 2199:
    st.caption(PROJECT_RUDY_BLURB)
    teams = load_d1_teams(max(years)).set_index("school")
    teams_payload = [
        {
            "id": school,
            "name": school,
            "rank": i + 1,
            "logo": (team_logo(teams.loc[school]) if school in teams.index else "") or "",
            "color": team_colors(teams.loc[school])["primary"] if school in teams.index else "",
        }
        for i, school in enumerate(PROJECT_RUDY_RANKED)
    ]
    storage_prefix = "cfb-bracket-2199-rudy"
else:
    ap = load_ap_top25(year)
    if ap.empty:
        st.warning("No AP Top 25 poll available for this season yet.")
        st.stop()

    week = int(ap["week"].iloc[0])
    st.caption(f"AP Top 25 — Week {week}, {year}")

    teams_payload = [
        {
            "id": row["school"],
            "name": row["school"],
            "rank": int(row["rank"]),
            "logo": row["logo"] or "",
            "color": row["color"] or "",
        }
        for _, row in ap.iterrows()
    ]
    storage_prefix = f"cfb-bracket-{year}-w{week}"

components.html(bracket_html(teams_payload, storage_prefix), height=950, scrolling=False)
