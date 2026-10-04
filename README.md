# CFB Analytics

Play-by-play college football success rate and defensive efficiency metrics, built from [collegefootballdata.com](https://collegefootballdata.com) data — a project for learning ML/data-engineering end to end, ending in a Streamlit dashboard.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Get a free API key from https://collegefootballdata.com/key, then:

```bash
cp .env.example .env
# edit .env and set CFBD_API_KEY
```

## Pipeline

```bash
# 1. Pull a season's play-by-play and build processed feature tables
python scripts/build_dataset.py 2023 2024

# 2. Train the baseline play-success model (train on one season, test on another)
python scripts/train_baseline_model.py --train 2023 --test 2024

# 3. Run tests
pytest tests/

# 4. Launch the dashboard
streamlit run dashboard/app.py
```

## How the metrics are built

- **Success rate** (`src/cfb_analytics/metrics.py`): the standard down-based threshold rule — a play succeeds if it gains ≥50% of yards-to-go on 1st down, ≥70% on 2nd, or converts outright on 3rd/4th. Touchdowns always succeed; turnovers always fail.
- **Defensive efficiency**: success rate allowed, PPA allowed per play (CFBD's own EPA-equivalent), stuff rate (runs stopped at/behind the line), and havoc rate (stuffs + sacks + turnovers forced — a lower bound, since CFBD's `/plays` endpoint doesn't expose pass breakups).
- **Baseline ML model** (`src/cfb_analytics/models.py`): predicts whether a play will succeed from pre-snap situational features only (down, distance, field position, score differential, quarter, the offense's rolling success rate so far in the game). Trained on one season, evaluated on a different one, so the reported accuracy/log-loss reflect real generalization.

## Conference Realignment

A drag-and-drop board (`dashboard/pages/4_Conference_Realignment.py`, `dashboard/realignment.py`) for rearranging all 266 FBS + FCS (Division I) programs into any conference grouping you want. It's a self-contained HTML/CSS/JS component (vanilla drag-and-drop, no libraries) embedded via `st.components.v1.html` — team moves are pure client-side JS, so dragging never triggers a Streamlit rerun, and your layout is saved automatically per-browser via `localStorage`.

Conferences themselves are draggable too, via the ⋮⋮ handle next to each name — reorder within a row, or drag across the Power 4 / Everyone Else boundary to pin or unpin one. Uses a separate `dataTransfer` type (`application/x-conf`) from team-chip drags (plain `text/plain`) so the two never get confused even when one drag crosses over the other's drop zones.

The season selector also includes historical snapshots (1932, 1980, 1999, 2004, 2011, 2024) seeded from CFBD's actual conference records for that year — e.g. 1932 shows Alabama still in the old Southern Conference, a year before the SEC split off. Pre-1978 (and even early-2000s) alignment predates FBS/FCS as categories, so historical years are pulled by "has a conference" rather than the classification-based filter the current season uses (`load_conference_snapshot` vs. `load_d1_teams` in `dashboard/data_loader.py`). The Power 4 pinned row naturally adapts too — in 1932 none of Big Ten/SEC/Big 12/ACC match (Big 12 didn't exist until 1994), so it's just empty; in 1980 it shows Big Ten/SEC/ACC since the Big 12 still didn't exist.

## Playoff Bracket

A single-elimination bracket (`dashboard/pages/5_Playoff_Bracket.py`, `dashboard/bracket.py`) seeded from the latest AP Top 25, with selectable field sizes (4/6/8/12/14/16/24 teams). Byes are computed from the standard recursive tournament-seeding order used by real single-elim brackets, so a size like 12 reproduces the actual CFP format (top 4 seeds bye, 5v12/6v11/7v10/8v9) without hardcoding it — the same math just works for every size. Drag teams between first-round seeds to re-seed, click a team in any decided matchup to advance them, and the champion crowns itself once every round is picked. Same component pattern as the realignment board: vanilla drag-and-drop, no libraries, `localStorage` persistence per bracket size.

## Project layout

```
src/cfb_analytics/   ingestion (client.py), metrics, aggregation, model code
scripts/             CLI entrypoints: build_dataset.py, train_baseline_model.py
notebooks/           exploratory walkthroughs — the learning on-ramp
dashboard/           Streamlit app: Team Explorer, Game Explorer, Model Explorer, Conference Realignment, Playoff Bracket
tests/               unit tests for the metrics logic
data/raw/            cached raw API responses (gitignored)
data/processed/      engineered feature tables + trained model (gitignored)
```

`data/` is gitignored — re-run `build_dataset.py` (and `train_baseline_model.py`) after cloning to regenerate it.

## What's next

- More seasons, and a wider metric set (explosiveness, line yards, PPA splits by play type).
- Live in-progress game tracking (deferred deliberately for v1 — `client.py` is structured so this doesn't require a rewrite).
- Model improvements: more features, better calibration, a full win-probability model.
