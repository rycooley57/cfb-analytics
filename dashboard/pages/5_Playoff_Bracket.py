import streamlit as st
import streamlit.components.v1 as components
from bracket import bracket_html
from components import inject_css, page_header
from data_loader import available_years, load_ap_top25

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

year = st.selectbox("Season", years, index=len(years) - 1)

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
