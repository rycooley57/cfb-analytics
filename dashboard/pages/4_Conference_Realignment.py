import streamlit as st
import streamlit.components.v1 as components
from components import inject_css, page_header
from data_loader import available_years, load_d1_teams
from realignment import realignment_board_html
from theme import team_colors, team_logo

st.set_page_config(page_title="Conference Realignment", page_icon="🔀", layout="wide")
inject_css(st)
page_header(
    st,
    "Conference Realignment",
    "Drag any FBS or FCS program into a new conference. Create, rename, or remove conferences freely — "
    "your board is saved automatically in this browser.",
)

years = available_years()
if not years:
    st.warning("No processed data found. Run `python scripts/build_dataset.py <year>` first.")
    st.stop()

year = st.selectbox("Starting alignment (season)", years, index=len(years) - 1)

d1 = load_d1_teams(year)

teams_payload = [
    {
        "id": row["school"],
        "name": row["school"],
        "conference": row["conference"] or "Unassigned",
        "logo": team_logo(row) or "",
        "color": team_colors(row)["primary"],
    }
    for _, row in d1.iterrows()
]

storage_key = f"cfb-realignment-{year}"
components.html(realignment_board_html(teams_payload, storage_key), height=1500, scrolling=False)
