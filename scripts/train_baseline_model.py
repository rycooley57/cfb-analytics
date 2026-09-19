"""Train the baseline play-success model on one season and evaluate it on
a later one, then save the best model for the dashboard to load.

Usage: python scripts/train_baseline_model.py --train 2023 --test 2024
"""

import argparse

import joblib
import pandas as pd

from cfb_analytics.config import DATA_PROCESSED_DIR
from cfb_analytics.models import add_situational_features, build_training_frame, evaluate, train_baseline_models


def load_season(year: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    plays = pd.read_parquet(DATA_PROCESSED_DIR / f"plays_{year}.parquet")
    games = pd.read_parquet(DATA_PROCESSED_DIR / f"games_{year}.parquet")
    return plays, games


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", type=int, required=True)
    parser.add_argument("--test", type=int, required=True)
    args = parser.parse_args()

    train_plays, train_games = load_season(args.train)
    test_plays, test_games = load_season(args.test)

    train_features = add_situational_features(train_plays, train_games)
    test_features = add_situational_features(test_plays, test_games)

    X_train, y_train, fill_value = build_training_frame(train_features)
    X_test, y_test, _ = build_training_frame(test_features, fill_value=fill_value)

    print(f"train ({args.train}): {len(X_train)} plays, test ({args.test}): {len(X_test)} plays")

    models = train_baseline_models(X_train, y_train)
    results = evaluate(models, X_test, y_test)
    print(results.to_string(index=False))

    best_name = results.sort_values("log_loss").iloc[0]["model"]
    best_model = models[best_name]
    model_dir = DATA_PROCESSED_DIR / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": best_model, "fill_value": fill_value, "name": best_name}, model_dir / "play_success_model.joblib")
    results.assign(train_year=args.train, test_year=args.test).to_parquet(model_dir / "eval_results.parquet")
    print(f"saved best model ({best_name}) to {model_dir / 'play_success_model.joblib'}")
