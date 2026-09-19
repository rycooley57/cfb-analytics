"""Pull a season's play-by-play from CFBD and write processed feature
tables (play-level metrics + team-game/team-season offense & defense
splits) to data/processed/, for the dashboard and notebooks to read.

Usage: python scripts/build_dataset.py 2023 2024
"""

import argparse

from cfb_analytics.aggregate import team_game_splits, team_season_splits
from cfb_analytics.client import get_games, get_season_plays, get_teams
from cfb_analytics.config import DATA_PROCESSED_DIR
from cfb_analytics.metrics import add_all_metrics


def build_season(year: int, weeks: range = range(1, 16)) -> None:
    print(f"[{year}] fetching play-by-play...")
    plays = get_season_plays(year, weeks=weeks)
    plays = add_all_metrics(plays)

    teams = get_teams(year)
    games = get_games(year)

    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    plays.to_parquet(DATA_PROCESSED_DIR / f"plays_{year}.parquet")
    teams.to_parquet(DATA_PROCESSED_DIR / f"teams_{year}.parquet")
    games.to_parquet(DATA_PROCESSED_DIR / f"games_{year}.parquet")

    game_splits = team_game_splits(plays)
    game_splits["offense"].to_parquet(DATA_PROCESSED_DIR / f"team_game_offense_{year}.parquet")
    game_splits["defense"].to_parquet(DATA_PROCESSED_DIR / f"team_game_defense_{year}.parquet")

    season_splits = team_season_splits(plays)
    season_splits["offense"].to_parquet(DATA_PROCESSED_DIR / f"team_season_offense_{year}.parquet")
    season_splits["defense"].to_parquet(DATA_PROCESSED_DIR / f"team_season_defense_{year}.parquet")

    print(f"[{year}] done: {len(plays)} plays, {len(teams)} teams, {len(games)} games")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("years", nargs="+", type=int)
    parser.add_argument("--weeks", type=int, default=15, help="number of regular-season weeks to pull")
    args = parser.parse_args()

    for year in args.years:
        build_season(year, weeks=range(1, args.weeks + 1))
