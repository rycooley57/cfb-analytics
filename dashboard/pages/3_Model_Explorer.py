import sys
from pathlib import Path

import pandas as pd
import streamlit as st
from components import inject_css, model_card_html, page_header, prob_bar_html, section_title
from data_loader import load_eval_results, load_model

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from cfb_analytics.models import FEATURE_COLS  # noqa: E402

st.set_page_config(page_title="Model Explorer", page_icon="🏈", layout="wide")
inject_css(st)
page_header(
    st,
    "Model Explorer",
    "Predicting play success from pre-snap situational features only. Trained on one season, "
    "evaluated on the next, so results reflect real generalization.",
)

bundle = load_model()
eval_results = load_eval_results()

if bundle is None:
    st.warning("No trained model found. Run `python scripts/train_baseline_model.py --train 2023 --test 2024` first.")
    st.stop()

model = bundle["model"]
fill_value = bundle["fill_value"]
model_name = bundle["name"]

section_title(st, "Held-Out Season Performance")
if eval_results is not None:
    cards = []
    for _, r in eval_results.iterrows():
        cards.append(
            model_card_html(
                r["model"].replace("_", " "),
                [("Accuracy", f"{r['accuracy']:.1%}"), ("Log loss", f"{r['log_loss']:.3f}")],
                active=r["model"] == model_name,
            )
        )
    st.markdown(f'<div class="stat-grid">{"".join(cards)}</div>', unsafe_allow_html=True)
    st.caption(f"Trained on {int(eval_results['train_year'].iloc[0])}, evaluated on {int(eval_results['test_year'].iloc[0])}.")

section_title(st, "Try It")
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

st.markdown(
    f"""
    <div class="stat-tile" style="max-width:320px;">
      <div class="stat-label">Predicted success probability</div>
      <div class="stat-value">{proba:.1%}</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(prob_bar_html(proba), unsafe_allow_html=True)
