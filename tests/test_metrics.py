import pandas as pd

from cfb_analytics.metrics import add_all_metrics


def make_play(playType="Rush", down=1, distance=10, yardsGained=0):
    return {"playType": playType, "down": down, "distance": distance, "yardsGained": yardsGained}


def test_first_down_success_threshold():
    df = pd.DataFrame([
        make_play(down=1, distance=10, yardsGained=6),  # >= 5.0 -> success
        make_play(down=1, distance=10, yardsGained=4),  # < 5.0 -> failure
    ])
    result = add_all_metrics(df)
    assert result["success"].tolist() == [True, False]


def test_second_down_success_threshold():
    df = pd.DataFrame([
        make_play(down=2, distance=7, yardsGained=5),  # >= 4.9 -> success
        make_play(down=2, distance=7, yardsGained=4),  # < 4.9 -> failure
    ])
    result = add_all_metrics(df)
    assert result["success"].tolist() == [True, False]


def test_third_and_fourth_down_require_conversion():
    df = pd.DataFrame([
        make_play(down=3, distance=3, yardsGained=3),  # meets distance -> success
        make_play(down=3, distance=3, yardsGained=2),  # short -> failure
        make_play(down=4, distance=1, yardsGained=1),  # meets distance -> success
    ])
    result = add_all_metrics(df)
    assert result["success"].tolist() == [True, False, True]


def test_touchdown_is_always_success():
    df = pd.DataFrame([
        make_play(playType="Rushing Touchdown", down=3, distance=8, yardsGained=8),
        make_play(playType="Passing Touchdown", down=2, distance=15, yardsGained=15),
    ])
    result = add_all_metrics(df)
    assert result["success"].tolist() == [True, True]


def test_turnover_is_always_failure():
    df = pd.DataFrame([
        make_play(playType="Interception", down=2, distance=5, yardsGained=25),
        make_play(playType="Fumble Recovery (Opponent)", down=1, distance=10, yardsGained=12),
    ])
    result = add_all_metrics(df)
    assert result["success"].tolist() == [False, False]


def test_non_scrimmage_plays_are_excluded():
    df = pd.DataFrame([
        {"playType": "Punt", "down": 4, "distance": 8, "yardsGained": 40},
        {"playType": "Kickoff", "down": None, "distance": None, "yardsGained": 0},
        {"playType": "Field Goal Good", "down": 4, "distance": 3, "yardsGained": 0},
    ])
    result = add_all_metrics(df)
    assert result["success"].isna().all()
    assert result["is_havoc"].isna().all()


def test_stuff_and_havoc_flags():
    df = pd.DataFrame([
        make_play(playType="Rush", down=2, distance=5, yardsGained=-2),  # stuff + havoc
        make_play(playType="Rush", down=2, distance=5, yardsGained=3),  # neither
        make_play(playType="Sack", down=1, distance=10, yardsGained=-7),  # havoc, not stuff
        make_play(playType="Interception", down=3, distance=6, yardsGained=0),  # havoc, not stuff
    ])
    result = add_all_metrics(df)
    assert result["is_stuff"].tolist() == [True, False, False, False]
    assert result["is_havoc"].tolist() == [True, False, True, True]
