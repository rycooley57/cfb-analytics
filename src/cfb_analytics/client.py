import json

import pandas as pd
import requests

from cfb_analytics.config import CFBD_BASE_URL, DATA_RAW_DIR, require_api_key


def _get(endpoint: str, params: dict) -> list:
    headers = {"Authorization": f"Bearer {require_api_key()}"}
    resp = requests.get(f"{CFBD_BASE_URL}{endpoint}", headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _cache_path(name: str, **params) -> "Path":
    key = "_".join(f"{k}-{v}" for k, v in sorted(params.items()) if v is not None)
    return DATA_RAW_DIR / f"{name}_{key}.parquet"


def get_teams(year: int, use_cache: bool = True) -> pd.DataFrame:
    path = _cache_path("teams", year=year)
    if use_cache and path.exists():
        return pd.read_parquet(path)
    data = _get("/teams/fbs", {"year": year})
    df = pd.json_normalize(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path)
    return df


def get_teams_all(year: int, use_cache: bool = True) -> pd.DataFrame:
    """All classifications (FBS, FCS, II, III), unlike get_teams which is
    FBS-only. Used for D1 (FBS + FCS) features like conference realignment."""
    path = _cache_path("teams_all", year=year)
    if use_cache and path.exists():
        return pd.read_parquet(path)
    data = _get("/teams", {"year": year})
    df = pd.json_normalize(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path)
    return df


def get_ap_top25(year: int) -> pd.DataFrame:
    """The most recent week's AP Top 25 for the season. Not cached to disk —
    rankings change weekly during the season, so this always hits the API;
    callers should wrap it in a short-TTL cache if called often."""
    data = _get("/rankings", {"year": year})
    if not data:
        return pd.DataFrame()
    latest = max(data, key=lambda d: d["week"])
    ap = next((p for p in latest["polls"] if p["poll"] == "AP Top 25"), None)
    if ap is None:
        return pd.DataFrame()
    df = pd.json_normalize(ap["ranks"]).sort_values("rank").reset_index(drop=True)
    df["week"] = latest["week"]
    return df


def get_games(year: int, season_type: str = "regular", team: str | None = None, use_cache: bool = True) -> pd.DataFrame:
    path = _cache_path("games", year=year, season_type=season_type, team=team)
    if use_cache and path.exists():
        return pd.read_parquet(path)
    params = {"year": year, "seasonType": season_type}
    if team:
        params["team"] = team
    data = _get("/games", params)
    df = pd.json_normalize(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path)
    return df


def get_plays(year: int, week: int, season_type: str = "regular", use_cache: bool = True) -> pd.DataFrame:
    """Play-by-play is only queryable per-week from CFBD, so ingestion for a
    full season means looping over weeks 1..15ish and concatenating.

    A week that hasn't been played yet returns no data — that result is
    deliberately NOT cached, so re-running later (once the week is played)
    fetches it instead of replaying a stale empty cache forever. This
    matters for the current, in-progress season."""
    path = _cache_path("plays", year=year, week=week, season_type=season_type)
    if use_cache and path.exists():
        return pd.read_parquet(path)
    params = {"year": year, "week": week, "seasonType": season_type}
    data = _get("/plays", params)
    df = pd.json_normalize(data)
    if df.empty:
        return df
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path)
    return df


def get_season_plays(year: int, weeks: range = range(1, 16), season_type: str = "regular", use_cache: bool = True) -> pd.DataFrame:
    frames = []
    for week in weeks:
        df = get_plays(year, week, season_type=season_type, use_cache=use_cache)
        if not df.empty:
            frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
