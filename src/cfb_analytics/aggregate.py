"""Roll play-level metrics up to team-game and team-season splits, for both
offense (team on offense) and defense (team on defense, i.e. what it allows).
"""

import pandas as pd

from cfb_analytics.metrics import add_all_metrics, is_scrimmage_play

RATE_COLS = ["success", "is_stuff", "is_havoc"]


def _side_summary(df: pd.DataFrame, side_col: str, group_cols: list[str]) -> pd.DataFrame:
    scrimmage = df[is_scrimmage_play(df)]
    agg = (
        scrimmage.groupby(group_cols + [side_col])
        .agg(
            plays=("success", "size"),
            success_rate=("success", "mean"),
            stuff_rate=("is_stuff", "mean"),
            havoc_rate=("is_havoc", "mean"),
            ppa_per_play=("ppa", "mean"),
        )
        .reset_index()
        .rename(columns={side_col: "team"})
    )
    return agg


def team_game_splits(plays: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Returns {"offense": df, "defense": df} of per-team, per-game metrics."""
    df = add_all_metrics(plays)
    offense = _side_summary(df, "offense", ["gameId"])
    defense = _side_summary(df, "defense", ["gameId"])
    return {"offense": offense, "defense": defense}


def team_season_splits(plays: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Returns {"offense": df, "defense": df} of per-team season-long metrics."""
    df = add_all_metrics(plays)
    offense = _side_summary(df, "offense", [])
    defense = _side_summary(df, "defense", [])
    return {"offense": offense, "defense": defense}


def national_averages(season_offense: pd.DataFrame) -> pd.Series:
    """Simple average-of-teams national baseline, used to benchmark a single
    team against the field on the dashboard."""
    return season_offense[["success_rate", "stuff_rate", "havoc_rate", "ppa_per_play"]].mean()
