import sys
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cfb_analytics.client import get_teams_all  # noqa: E402
from cfb_analytics.config import DATA_PROCESSED_DIR  # noqa: E402


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
