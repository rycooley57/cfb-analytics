"""Play-level advanced metrics computed from CFBD raw play-by-play.

Success rate is the standard down-based threshold rule (Bill Connelly's
definition): a play "succeeds" if it gains at least 50% of yards-to-go on
1st down, 70% on 2nd down, or 100% (i.e. converts) on 3rd/4th down.
Touchdowns always succeed; turnovers always fail, regardless of yards gained.

Havoc/stuff rate are defensive disruption metrics. CFBD's /plays endpoint
doesn't expose pass breakups, so `is_havoc` here (sacks + stuffed runs +
turnovers) is a lower bound on "true" havoc rate, which usually also
counts pass breakups.
"""

import numpy as np
import pandas as pd

SCRIMMAGE_PLAY_TYPES = {
    "Rush",
    "Rushing Touchdown",
    "Pass Reception",
    "Passing Touchdown",
    "Pass Incompletion",
    "Sack",
    "Interception",
    "Pass Interception Return",
    "Interception Return Touchdown",
    "Fumble Recovery (Opponent)",
    "Fumble Recovery (Own)",
    "Fumble Return Touchdown",
    "Safety",
}

TURNOVER_PLAY_TYPES = {
    "Interception",
    "Pass Interception Return",
    "Interception Return Touchdown",
    "Fumble Recovery (Opponent)",
    "Fumble Return Touchdown",
}

TOUCHDOWN_PLAY_TYPES = {
    "Rushing Touchdown",
    "Passing Touchdown",
    "Fumble Return Touchdown",
    "Interception Return Touchdown",
}

RUN_PLAY_TYPES = {"Rush", "Rushing Touchdown"}


def is_scrimmage_play(df: pd.DataFrame) -> pd.Series:
    """True for normal downs (rush/pass/sack/turnover), excluding special
    teams (punts, kickoffs, field goals), penalties, and clock/admin plays."""
    return df["playType"].isin(SCRIMMAGE_PLAY_TYPES) & df["down"].notna()


def add_success_rate(df: pd.DataFrame) -> pd.DataFrame:
    """Adds a boolean `success` column (NaN for non-scrimmage plays)."""
    df = df.copy()
    scrimmage = is_scrimmage_play(df)

    threshold = np.select(
        [df["down"] == 1, df["down"] == 2],
        [0.5 * df["distance"], 0.7 * df["distance"]],
        default=df["distance"],
    )
    met_threshold = df["yardsGained"].fillna(0) >= threshold
    success = (met_threshold | df["playType"].isin(TOUCHDOWN_PLAY_TYPES)) & ~df[
        "playType"
    ].isin(TURNOVER_PLAY_TYPES)

    df["success"] = np.where(scrimmage, success, np.nan)
    return df


def add_havoc_flags(df: pd.DataFrame) -> pd.DataFrame:
    """Adds boolean `is_stuff` (run stopped at/behind the line) and
    `is_havoc` (stuff, sack, or turnover) columns, NaN for non-scrimmage plays."""
    df = df.copy()
    scrimmage = is_scrimmage_play(df)

    is_stuff = df["playType"].isin(RUN_PLAY_TYPES) & (df["yardsGained"].fillna(0) <= 0)
    is_sack = df["playType"] == "Sack"
    is_turnover = df["playType"].isin(TURNOVER_PLAY_TYPES)

    df["is_stuff"] = np.where(scrimmage, is_stuff, np.nan)
    df["is_havoc"] = np.where(scrimmage, is_stuff | is_sack | is_turnover, np.nan)
    return df


def add_all_metrics(df: pd.DataFrame) -> pd.DataFrame:
    df = add_success_rate(df)
    df = add_havoc_flags(df)
    return df
