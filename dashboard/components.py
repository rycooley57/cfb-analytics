"""Reusable ESPN-style UI pieces, built as plain HTML strings injected via
st.markdown. All inputs come from CFBD data / our own computed metrics, not
free-text user input, so string interpolation into HTML is safe here."""

import re

from theme import ACCENT, BORDER, STATUS_BAD, STATUS_GOOD, SURFACE, SURFACE_ALT, TEXT_MUTED, TEXT_PRIMARY, TEXT_SECONDARY


def _flatten(html: str) -> str:
    """Collapses a multi-line, indented HTML template to a single line.
    st.markdown runs content through a Markdown parser even with
    unsafe_allow_html=True, and CommonMark treats 4+ leading spaces as an
    indented code block — which is exactly what our triple-quoted,
    function-indented f-strings produce. Flattening avoids that entirely."""
    return re.sub(r"\n\s*", "", html.strip())

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&display=swap');

.section-title {{
  font-family: 'Oswald', sans-serif;
  font-weight: 700;
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 0.08em;
  color: {TEXT_SECONDARY};
  border-left: 4px solid {ACCENT};
  padding-left: 10px;
  margin: 1.75rem 0 0.9rem 0;
}}

.page-title {{
  font-family: 'Oswald', sans-serif;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.02em;
  font-size: 2.1rem;
  color: {TEXT_PRIMARY};
  margin-bottom: 0.1rem;
}}
.page-subtitle {{
  color: {TEXT_SECONDARY};
  font-size: 0.92rem;
  margin-bottom: 1.2rem;
}}

.stat-grid {{ display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 0.5rem; }}
.stat-tile {{
  background: {SURFACE};
  border: 1px solid {BORDER};
  border-radius: 8px;
  padding: 14px 18px;
  flex: 1;
  min-width: 140px;
}}
.stat-tile .stat-label {{
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: {TEXT_SECONDARY};
  margin-bottom: 4px;
}}
.stat-tile .stat-value {{
  font-family: 'Oswald', sans-serif;
  font-size: 1.9rem;
  font-weight: 600;
  color: {TEXT_PRIMARY};
  line-height: 1.1;
}}
.stat-tile .stat-delta {{ font-size: 0.78rem; margin-top: 3px; font-weight: 600; }}
.stat-tile .stat-delta.good {{ color: {STATUS_GOOD}; }}
.stat-tile .stat-delta.bad {{ color: {STATUS_BAD}; }}
.stat-tile .stat-delta.flat {{ color: {TEXT_MUTED}; }}

.scoreboard {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: {SURFACE};
  border: 1px solid {BORDER};
  border-radius: 10px;
  padding: 20px 28px;
  margin-bottom: 0.5rem;
}}
.scoreboard .team {{ display: flex; align-items: center; gap: 14px; flex: 1; }}
.scoreboard .team.away {{ justify-content: flex-start; }}
.scoreboard .team.home {{ justify-content: flex-end; flex-direction: row-reverse; }}
.scoreboard .team img {{ width: 52px; height: 52px; object-fit: contain; }}
.scoreboard .team-name {{
  font-family: 'Oswald', sans-serif;
  font-weight: 600;
  font-size: 1.1rem;
  color: {TEXT_PRIMARY};
  text-transform: uppercase;
}}
.scoreboard .team-score {{
  font-family: 'Oswald', sans-serif;
  font-weight: 700;
  font-size: 2.4rem;
  color: {TEXT_PRIMARY};
  min-width: 56px;
  text-align: center;
}}
.scoreboard .team-score.winner {{ color: {ACCENT}; }}
.scoreboard .at {{ color: {TEXT_MUTED}; font-size: 0.85rem; padding: 0 18px; }}

.team-header {{ display: flex; align-items: center; gap: 16px; margin-bottom: 0.3rem; }}
.team-header img {{ width: 64px; height: 64px; object-fit: contain; }}
.team-header .name {{
  font-family: 'Oswald', sans-serif;
  font-weight: 700;
  text-transform: uppercase;
  font-size: 1.8rem;
  color: {TEXT_PRIMARY};
  line-height: 1.05;
}}
.team-header .conf {{ color: {TEXT_SECONDARY}; font-size: 0.85rem; }}

.compare-row {{ margin-bottom: 14px; }}
.compare-row .labels {{ display:flex; justify-content: space-between; font-size: 0.82rem; color: {TEXT_SECONDARY}; margin-bottom: 4px; }}
.compare-row .labels .val {{ font-weight: 600; color: {TEXT_PRIMARY}; }}
.compare-track {{ display: flex; height: 10px; border-radius: 5px; overflow: hidden; background: {SURFACE_ALT}; }}
.compare-track .seg {{ height: 100%; }}
.compare-row .metric-name {{ text-align:center; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; color: {TEXT_MUTED}; margin-top: 3px; }}

.leader-row {{ display: flex; align-items: center; gap: 12px; padding: 7px 4px; border-bottom: 1px solid {BORDER}; }}
.leader-row .rank {{ color: {TEXT_MUTED}; font-size: 0.85rem; width: 20px; }}
.leader-row img {{ width: 28px; height: 28px; object-fit: contain; }}
.leader-row .name {{ color: {TEXT_PRIMARY}; font-size: 0.9rem; flex: 0 0 150px; }}
.leader-row .bar-track {{ flex: 1; background: {SURFACE_ALT}; border-radius: 4px; height: 16px; overflow: hidden; }}
.leader-row .bar-fill {{ height: 100%; border-radius: 4px; }}
.leader-row .value {{ color: {TEXT_PRIMARY}; font-weight: 600; font-size: 0.88rem; width: 52px; text-align: right; }}

.play-row {{
  display: flex;
  align-items: center;
  gap: 10px;
  background: {SURFACE};
  border-left: 3px solid {TEXT_MUTED};
  border-radius: 4px;
  padding: 8px 12px;
  margin-bottom: 4px;
  font-size: 0.86rem;
}}
.play-row.success {{ border-left-color: {STATUS_GOOD}; }}
.play-row.fail {{ border-left-color: {STATUS_BAD}; }}
.play-row .down-pill {{
  background: {SURFACE_ALT};
  color: {TEXT_SECONDARY};
  font-size: 0.72rem;
  padding: 2px 9px;
  border-radius: 10px;
  white-space: nowrap;
  flex-shrink: 0;
}}
.play-row .play-text {{ color: {TEXT_PRIMARY}; }}

.badge {{
  display: inline-block;
  background: {ACCENT};
  color: white;
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 2px 8px;
  border-radius: 3px;
}}

.model-card {{
  background: {SURFACE};
  border: 1px solid {BORDER};
  border-radius: 8px;
  padding: 16px 18px;
  flex: 1;
  min-width: 220px;
}}
.model-card.active {{ border-color: {ACCENT}; }}
.model-card .model-name {{ font-family: 'Oswald', sans-serif; font-weight: 600; font-size: 1.05rem; color: {TEXT_PRIMARY}; text-transform: uppercase; margin-bottom: 8px; }}
.model-card .model-metric {{ display: flex; justify-content: space-between; font-size: 0.85rem; color: {TEXT_SECONDARY}; padding: 2px 0; }}
.model-card .model-metric .val {{ color: {TEXT_PRIMARY}; font-weight: 600; }}

.prob-track {{ background: {SURFACE_ALT}; height: 14px; border-radius: 7px; overflow: hidden; }}
.prob-fill {{ height: 100%; background: linear-gradient(90deg, #184f95, #3987e5); border-radius: 7px; }}
</style>
"""


def inject_css(st) -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def page_header(st, title: str, subtitle: str = "") -> None:
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def section_title(st, text: str) -> None:
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)


def _delta_class(better: bool | None) -> str:
    if better is None:
        return "flat"
    return "good" if better else "bad"


def _delta_arrow(better: bool | None) -> str:
    if better is None:
        return "–"
    return "▲" if better else "▼"


def stat_tile_html(label: str, value: str, delta_text: str | None = None, better: bool | None = None) -> str:
    delta_html = ""
    if delta_text:
        delta_html = f'<div class="stat-delta {_delta_class(better)}">{_delta_arrow(better)} {delta_text}</div>'
    return _flatten(f"""
    <div class="stat-tile">
      <div class="stat-label">{label}</div>
      <div class="stat-value">{value}</div>
      {delta_html}
    </div>
    """)


def stat_grid(st, tiles_html: list[str]) -> None:
    st.markdown(f'<div class="stat-grid">{"".join(tiles_html)}</div>', unsafe_allow_html=True)


def scoreboard_html(away_name, away_logo, away_score, home_name, home_logo, home_score) -> str:
    away_logo_html = f'<img src="{away_logo}">' if away_logo else ""
    home_logo_html = f'<img src="{home_logo}">' if home_logo else ""
    away_win = away_score is not None and home_score is not None and away_score > home_score
    home_win = away_score is not None and home_score is not None and home_score > away_score
    return _flatten(f"""
    <div class="scoreboard">
      <div class="team away">
        {away_logo_html}
        <div>
          <div class="team-name">{away_name}</div>
        </div>
      </div>
      <div class="team-score {'winner' if away_win else ''}">{away_score if away_score is not None else '-'}</div>
      <div class="at">@</div>
      <div class="team-score {'winner' if home_win else ''}">{home_score if home_score is not None else '-'}</div>
      <div class="team home">
        {home_logo_html}
        <div>
          <div class="team-name">{home_name}</div>
        </div>
      </div>
    </div>
    """)


def team_header_html(name: str, conference: str, logo_url: str | None) -> str:
    logo_html = f'<img src="{logo_url}">' if logo_url else ""
    return _flatten(f"""
    <div class="team-header">
      {logo_html}
      <div>
        <div class="name">{name}</div>
        <div class="conf">{conference}</div>
      </div>
    </div>
    """)


def compare_bar_html(metric_name: str, label_a: str, value_a: float, color_a: str, label_b: str, value_b: float, color_b: str, fmt: str = "{:.1%}") -> str:
    total = value_a + value_b
    pct_a = 50.0 if total == 0 else (value_a / total) * 100
    pct_b = 100 - pct_a
    return _flatten(f"""
    <div class="compare-row">
      <div class="labels">
        <span>{label_a} <span class="val">{fmt.format(value_a)}</span></span>
        <span><span class="val">{fmt.format(value_b)}</span> {label_b}</span>
      </div>
      <div class="compare-track">
        <div class="seg" style="width:{pct_a:.1f}%; background:{color_a};"></div>
        <div class="seg" style="width:{pct_b:.1f}%; background:{color_b};"></div>
      </div>
      <div class="metric-name">{metric_name}</div>
    </div>
    """)


def leader_row_html(rank: int, logo_url: str | None, name: str, value: float, max_value: float, color: str, fmt: str = "{:.1%}") -> str:
    logo_html = f'<img src="{logo_url}">' if logo_url else '<div style="width:28px"></div>'
    pct = 0 if max_value == 0 else max(2, (value / max_value) * 100)
    return _flatten(f"""
    <div class="leader-row">
      <div class="rank">{rank}</div>
      {logo_html}
      <div class="name">{name}</div>
      <div class="bar-track"><div class="bar-fill" style="width:{pct:.1f}%; background:{color};"></div></div>
      <div class="value">{fmt.format(value)}</div>
    </div>
    """)


def play_row_html(down_distance: str, play_text: str, success) -> str:
    cls = "success" if success == 1 else ("fail" if success == 0 else "")
    return _flatten(f"""
    <div class="play-row {cls}">
      <span class="down-pill">{down_distance}</span>
      <span class="play-text">{play_text}</span>
    </div>
    """)


def model_card_html(name: str, metrics: list[tuple[str, str]], active: bool) -> str:
    badge = '<span class="badge">Active</span>' if active else ""
    metrics_html = "".join(f'<div class="model-metric"><span>{k}</span><span class="val">{v}</span></div>' for k, v in metrics)
    return _flatten(f"""
    <div class="model-card {'active' if active else ''}">
      <div class="model-name">{name} {badge}</div>
      {metrics_html}
    </div>
    """)


def prob_bar_html(probability: float) -> str:
    pct = max(0, min(100, probability * 100))
    return _flatten(f"""
    <div class="prob-track"><div class="prob-fill" style="width:{pct:.1f}%;"></div></div>
    """)
