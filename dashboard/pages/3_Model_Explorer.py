import sys
from pathlib import Path

import pandas as pd
import streamlit as st
from data_loader import load_eval_results, load_model

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from cfb_analytics.models import FEATURE_COLS  # noqa: E402

st.set_page_config(page_title="Model Explorer", page_icon="🏈", layout="wide")
st.title("Model Explorer — Play Success Prediction")
st.caption(
    "A baseline model predicting whether a play succeeds, from pre-snap "
    "situational features only (no knowledge of the play call). Trained on "
    "one season, evaluated on the next, so the numbers reflect real "
    "generalization rather than memorizing a season's teams."
)

bundle = load_model()
eval_results = load_eval_results()

if bundle is None:
    st.warning("No trained model found. Run `python scripts/train_baseline_model.py --train 2023 --test 2024` first.")
    st.stop()

model = bundle["model"]
fill_value = bundle["fill_value"]
model_name = bundle["name"]

st.subheader("Held-out season performance")
if eval_results is not None:
    st.dataframe(eval_results, use_container_width=True)
    st.caption(f"Deployed model: **{model_name}** (lowest log loss on the held-out test season).")

st.subheader("Try it")
st.write("Set a game situation and see the model's predicted probability the next play succeeds.")

col1, col2, col3 = st.columns(3)
down = col1.selectbox("Down", [1, 2, 3, 4], index=0)
distance = col1.slider("Distance to go", 1, 30, 10)
yards_to_goal = col2.slider("Yards from opponent's end zone", 1, 99, 50)
score_diff = col2.slider("Score differential (offense - defense)", -35, 35, 0)
period = col3.selectbox("Quarter", [1, 2, 3, 4], index=0)
rolling_success_rate = col3.slider("Offense's success rate so far this game", 0.0, 1.0, float(fill_value), step=0.01)

X = pd.DataFrame(
    [[down, distance, yards_to_goal, score_diff, period, rolling_success_rate]],
    columns=FEATURE_COLS,
)
proba = model.predict_proba(X)[0, 1]

st.metric("Predicted success probability", f"{proba:.1%}")
st.progress(min(max(proba, 0.0), 1.0))
