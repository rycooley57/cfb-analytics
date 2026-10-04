import sys
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cfb_analytics.client import get_ap_top25, get_teams_all  # noqa: E402
from cfb_analytics.config import DATA_PROCESSED_DIR  # noqa: E402

from theme import team_colors, team_logo  # noqa: E402


@st.cache_data
def available_years() -> list[int]:
    years = sorted({int(p.stem.split("_")[-1]) for p in DATA_PROCESSED_DIR.glob("teams_*.parquet")})
    return years


@st.cache_data
def load_teams(year: int) -> pd.DataFrame:
    return pd.read_parquet(DATA_PROCESSED_DIR / f"teams_{year}.parquet")


@st.cache_data
def load_games(year: int) -> pd.DataFrame:
    return pd.read_parquet(DATA_PROCESSED_DIR / f"games_{year}.parquet")


@st.cache_data
def load_plays(year: int) -> pd.DataFrame:
    return pd.read_parquet(DATA_PROCESSED_DIR / f"plays_{year}.parquet")


@st.cache_data
def load_team_game_splits(year: int, side: str) -> pd.DataFrame:
    return pd.read_parquet(DATA_PROCESSED_DIR / f"team_game_{side}_{year}.parquet")


@st.cache_data
def load_team_season_splits(year: int, side: str) -> pd.DataFrame:
    return pd.read_parquet(DATA_PROCESSED_DIR / f"team_season_{side}_{year}.parquet")


@st.cache_data
def load_d1_teams(year: int) -> pd.DataFrame:
    """FBS + FCS teams (Division I football) with conference, color, and
    logo — independent of build_dataset.py, since this only needs the
    teams endpoint, not play-by-play."""
    df = get_teams_all(year)
    return df[df["classification"].isin(["fbs", "fcs"])].reset_index(drop=True)


@st.cache_data
def load_conference_snapshot(year: int) -> pd.DataFrame:
    """All teams with a known conference for a season — used for the
    realignment board's historical snapshots. Unlike load_d1_teams, this
    does NOT filter by classification: FBS/FCS as categories didn't exist
    before 1978 (Division I itself didn't exist before 1973), and CFBD's
    classification field isn't reliably period-accurate for older seasons.
    Conference membership itself is the meaningful signal for an era."""
    df = get_teams_all(year)
    return df[df["conference"].notna()].reset_index(drop=True)


@st.cache_data(ttl=3600)
def load_ap_top25(year: int) -> pd.DataFrame:
    """Latest AP Top 25 joined with team logo/color. Short TTL (not the
    usual unbounded st.cache_data) since the poll changes weekly in-season."""
    ap = get_ap_top25(year)
    if ap.empty:
        return ap
    teams = load_d1_teams(year).set_index("school")
    ap = ap.copy()
    ap["logo"] = ap["school"].map(lambda s: team_logo(teams.loc[s]) if s in teams.index else None)
    ap["color"] = ap["school"].map(lambda s: team_colors(teams.loc[s])["primary"] if s in teams.index else None)
    return ap


@st.cache_resource
def load_model():
    path = DATA_PROCESSED_DIR / "models" / "play_success_model.joblib"
    if not path.exists():
        return None
    return joblib.load(path)


@st.cache_data
def load_eval_results() -> pd.DataFrame | None:
    path = DATA_PROCESSED_DIR / "models" / "eval_results.parquet"
    if not path.exists():
        return None
    return pd.read_parquet(path)
