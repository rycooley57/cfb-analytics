"""Baseline play-success model: predict whether an individual play succeeds
(per the success-rate definition in metrics.py) from pre-snap situational
features. Meant to be trained on one season and evaluated on a later one,
so it's checked for generalizing rather than memorizing a single year's teams.
"""

import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

FEATURE_COLS = ["down", "distance", "yardsToGoal", "score_diff", "period", "rolling_success_rate"]


def add_situational_features(plays: pd.DataFrame, games: pd.DataFrame) -> pd.DataFrame:
    """Adds `score_diff` and `rolling_success_rate` (a team's expanding,
    pre-play season success rate, in chronological play order — shifted by
    one so a play never sees its own outcome, avoiding leakage)."""
    df = plays.merge(games[["id", "week"]], left_on="gameId", right_on="id", how="left")
    df["score_diff"] = df["offenseScore"] - df["defenseScore"]

    df = df.sort_values(["offense", "week", "gameId", "driveNumber", "playNumber"])
    df["rolling_success_rate"] = df.groupby("offense")["success"].transform(
        lambda s: s.expanding().mean().shift(1)
    )
    return df


def build_training_frame(
    plays_with_features: pd.DataFrame, fill_value: float | None = None
) -> tuple[pd.DataFrame, pd.Series, float]:
    """Filters to scrimmage plays; fills missing rolling_success_rate (a
    team's first plays of the season, before it has any history) with
    `fill_value`, or the frame's own mean if none is given. Pass the
    training set's fill_value back in when building the test frame so
    nothing about the test season leaks into it."""
    df = plays_with_features[plays_with_features["success"].notna()].copy()
    if fill_value is None:
        fill_value = df["rolling_success_rate"].mean()
    df["rolling_success_rate"] = df["rolling_success_rate"].fillna(fill_value)
    X = df[FEATURE_COLS]
    y = df["success"].astype(int)
    return X, y, fill_value


def train_baseline_models(X_train: pd.DataFrame, y_train: pd.Series) -> dict:
    models = {
        "logistic_regression": Pipeline(
            [("scale", StandardScaler()), ("clf", LogisticRegression(max_iter=1000))]
        ),
        "gradient_boosting": HistGradientBoostingClassifier(random_state=0),
    }
    for model in models.values():
        model.fit(X_train, y_train)
    return models


def evaluate(models: dict, X_test: pd.DataFrame, y_test: pd.Series) -> pd.DataFrame:
    rows = []
    for name, model in models.items():
        proba = model.predict_proba(X_test)[:, 1]
        preds = (proba >= 0.5).astype(int)
        rows.append(
            {
                "model": name,
                "accuracy": accuracy_score(y_test, preds),
                "log_loss": log_loss(y_test, proba),
            }
        )
    return pd.DataFrame(rows)
