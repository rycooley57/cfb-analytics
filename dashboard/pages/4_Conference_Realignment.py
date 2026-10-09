import streamlit as st
import streamlit.components.v1 as components
from components import inject_css, page_header
from data_loader import available_years, load_conference_snapshot, load_d1_teams
from realignment import realignment_board_html
from scenarios import (
    PROJECT_RUDY_BLURB,
    PROJECT_RUDY_CONFERENCE,
    SCENARIO_2032_BLURB,
    SCENARIO_2032_MOVES,
    SPECULATIVE_YEARS,
)
from theme import team_colors, team_logo

st.set_page_config(page_title="Conference Realignment", page_icon="🔀", layout="wide")
inject_css(st)
page_header(
    st,
    "Conference Realignment",
    "Drag any program into a new conference. Create, rename, or remove conferences freely — "
    "your board is saved automatically in this browser.",
)

HISTORICAL_YEARS = [1932, 1980, 1999, 2004, 2011, 2024]
current_years = available_years()
year_options = sorted(set(current_years) | set(HISTORICAL_YEARS) | set(SPECULATIVE_YEARS))
if not year_options:
    st.warning("No processed data found. Run `python scripts/build_dataset.py <year>` first.")
    st.stop()

year = st.selectbox(
    "Starting alignment (season)",
    year_options,
    index=year_options.index(max(current_years)) if current_years else len(year_options) - 1,
    format_func=lambda y: SPECULATIVE_YEARS.get(y, str(y)),
)

latest_real_year = max(current_years) if current_years else max(year_options)

if year == 2032:
    st.caption(SCENARIO_2032_BLURB)
    pool = load_d1_teams(latest_real_year).copy()
    pool["conference"] = pool.apply(lambda r: SCENARIO_2032_MOVES.get(r["school"], r["conference"]), axis=1)
elif year == 2199:
    st.caption(PROJECT_RUDY_BLURB)
    pool = load_d1_teams(latest_real_year)
    pool = pool[pool["school"].isin(PROJECT_RUDY_CONFERENCE)].copy()
    pool["conference"] = pool["school"].map(PROJECT_RUDY_CONFERENCE)
elif year in current_years:
    # Pre-1978 (and even early-2000s) conference membership predates FBS/FCS
    # as categories, so historical snapshots use "has a conference" rather
    # than the classification-based FBS+FCS filter the current-season view
    # uses.
    pool = load_d1_teams(year)
else:
    pool = load_conference_snapshot(year)

teams_payload = [
    {
        "id": row["school"],
        "name": row["school"],
        "conference": row["conference"] or "Unassigned",
        "logo": team_logo(row) or "",
        "color": team_colors(row)["primary"],
    }
    for _, row in pool.iterrows()
]

storage_key = f"cfb-realignment-{year}"
components.html(realignment_board_html(teams_payload, storage_key), height=1500, scrolling=False)
