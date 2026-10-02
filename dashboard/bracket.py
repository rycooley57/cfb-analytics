"""Playoff bracket builder: a self-contained HTML/CSS/JS component (same
vanilla drag-and-drop approach as realignment.py) seeded from the latest
AP Top 25. Drag teams between seed slots to re-seed the first round;
click a team in a decided matchup to pick the winner and advance them.

Bracket math: for N teams, P = the next power of two >= N, and the first
round is built from the standard recursive tournament-seeding order (the
same scheme real single-elimination brackets use), so seeds that don't
fit evenly get byes in exactly the positions a real seeded bracket would
give them — e.g. for N=12 this reproduces the actual 12-team CFP format
(top 4 seeds bye, 5v12/6v11/7v10/8v9) without hardcoding it.
"""

import json

from theme import ACCENT, BG, BORDER, STATUS_BAD, SURFACE, SURFACE_ALT, TEXT_MUTED, TEXT_PRIMARY, TEXT_SECONDARY

BRACKET_SIZES = [4, 6, 8, 12, 14, 16, 24]


def bracket_html(teams: list[dict], storage_prefix: str, default_size: int = 12) -> str:
    """`teams` is the AP Top 25 in rank order: [{id, name, rank, logo, color}, ...]."""
    teams_json = json.dumps(teams)
    sizes_json = json.dumps(BRACKET_SIZES)
    return f"""
<style>
  html, body {{ height: 100%; margin: 0; background: {BG}; }}
  * {{ box-sizing: border-box; font-family: system-ui, -apple-system, Segoe UI, sans-serif; }}
  .bracket-root {{ height: 100%; display: flex; flex-direction: column; color: {TEXT_PRIMARY}; }}

  .toolbar {{ display: flex; align-items: center; gap: 8px; padding: 4px 2px 12px 2px; flex-wrap: wrap; }}
  .size-btn {{
    background: {SURFACE}; border: 1px solid {BORDER}; color: {TEXT_SECONDARY};
    border-radius: 6px; padding: 7px 14px; font-size: 0.82rem; cursor: pointer; font-weight: 600;
  }}
  .size-btn:hover {{ border-color: {ACCENT}; color: {TEXT_PRIMARY}; }}
  .size-btn.active {{ background: {ACCENT}; border-color: {ACCENT}; color: white; }}
  .toolbar button.reset-btn {{
    background: {SURFACE}; border: 1px solid {BORDER}; color: {TEXT_PRIMARY};
    border-radius: 6px; padding: 7px 12px; font-size: 0.82rem; cursor: pointer; margin-left: auto;
  }}
  .toolbar button.reset-btn:hover {{ border-color: {STATUS_BAD}; color: {STATUS_BAD}; }}
  .hint-text {{ color: {TEXT_MUTED}; font-size: 0.76rem; width: 100%; margin-top: 2px; }}

  .bracket-board {{ flex: 1; min-height: 0; display: flex; gap: 22px; overflow-x: auto; overflow-y: auto; padding: 4px 4px 14px 4px; }}

  .round-col {{ flex: 0 0 196px; display: flex; flex-direction: column; }}
  .round-header {{
    text-align: center; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.06em;
    color: {TEXT_MUTED}; margin-bottom: 10px; flex: 0 0 auto;
  }}
  .round-matches {{ flex: 1; display: flex; flex-direction: column; justify-content: space-around; gap: 10px; }}

  .match-card {{ background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 7px; overflow: hidden; }}
  .match-slot {{
    display: flex; align-items: center; gap: 6px; padding: 6px 8px; font-size: 0.78rem; cursor: pointer;
  }}
  .match-slot + .match-slot {{ border-top: 1px solid {BORDER}; }}
  .match-slot.bye {{ color: {TEXT_MUTED}; font-style: italic; cursor: default; }}
  .match-slot.tbd {{ color: {TEXT_MUTED}; cursor: default; }}
  .match-slot.winner {{ background: {SURFACE_ALT}; font-weight: 600; }}
  .match-slot.loser {{ opacity: 0.4; }}
  .match-slot .rank-badge {{ font-size: 0.65rem; color: {TEXT_MUTED}; width: 16px; text-align: right; flex-shrink: 0; }}
  .match-slot img {{ width: 18px; height: 18px; object-fit: contain; flex-shrink: 0; }}
  .match-slot span {{ white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}

  .round-col.seed-col .match-slot {{ cursor: grab; }}
  .round-col.seed-col .match-slot:active {{ cursor: grabbing; }}
  .round-col.seed-col .match-slot.dragging {{ opacity: 0.35; }}
  .round-col.seed-col .match-slot.drag-over {{ outline: 2px dashed {ACCENT}; outline-offset: -2px; }}

  .champion-col {{ flex: 0 0 210px; display: flex; flex-direction: column; justify-content: center; align-items: center; }}
  .champion-card {{
    background: {SURFACE}; border: 2px solid {ACCENT}; border-radius: 10px; padding: 20px 16px;
    text-align: center; width: 100%;
  }}
  .champion-card .trophy {{ font-size: 1.6rem; margin-bottom: 6px; }}
  .champion-card img {{ width: 56px; height: 56px; object-fit: contain; margin-bottom: 8px; }}
  .champion-card .name {{ font-weight: 700; font-size: 1.05rem; }}
  .champion-card .placeholder {{ color: {TEXT_MUTED}; font-size: 0.85rem; }}
</style>

<div class="bracket-root">
  <div class="toolbar" id="toolbar">
    <button class="reset-btn" id="reset-btn">Reset Seeding &amp; Picks</button>
    <div class="hint-text">Drag teams to re-seed the first round. Click a team to pick them as the winner.</div>
  </div>
  <div class="bracket-board" id="board"></div>
</div>

<script>
const TEAMS = {teams_json};
const SIZES = {sizes_json};
const STORAGE_PREFIX = "{storage_prefix}";
let currentSize = {default_size};

function nextPow2(n) {{
  let p = 1;
  while (p < n) p *= 2;
  return p;
}}

function seedOrderList(p) {{
  if (p === 1) return [1];
  const prev = seedOrderList(p / 2);
  const out = [];
  prev.forEach(s => {{ out.push(s); out.push(p + 1 - s); }});
  return out;
}}

function buildRound0Slots(n) {{
  const p = nextPow2(n);
  return seedOrderList(p).map(seed => (seed <= n ? TEAMS[seed - 1].id : null));
}}

function defaultState(n) {{
  return {{ size: n, slots: buildRound0Slots(n), picks: {{}} }};
}}

function storageKey(n) {{ return STORAGE_PREFIX + "-" + n; }}

function loadState(n) {{
  try {{
    const raw = localStorage.getItem(storageKey(n));
    if (raw) return JSON.parse(raw);
  }} catch (e) {{}}
  return defaultState(n);
}}

function saveState() {{
  try {{ localStorage.setItem(storageKey(state.size), JSON.stringify(state)); }} catch (e) {{}}
}}

let state = loadState(currentSize);
const teamById = {{}};
TEAMS.forEach(t => teamById[t.id] = t);

function computeRounds() {{
  const rounds = [];
  let slots = state.slots;
  let roundIdx = 0;
  while (slots.length >= 2) {{
    const matches = [];
    for (let i = 0; i < slots.length; i += 2) {{
      const a = slots[i], b = slots[i + 1];
      const key = roundIdx + "_" + (i / 2);
      // A null opponent is only an automatic win (a bye) in round 0 — the
      // true structural byes from seeding. In later rounds, a null side
      // means "previous match not decided yet", so it must stay TBD
      // rather than auto-advancing whoever happens to be the other side.
      let winner = null;
      if (roundIdx === 0 && a && !b) winner = a;
      else if (roundIdx === 0 && b && !a) winner = b;
      else if (a && b) {{
        const picked = state.picks[key];
        if (picked === a || picked === b) winner = picked;
      }}
      matches.push({{ a, b, winner, key }});
    }}
    rounds.push(matches);
    slots = matches.map(m => m.winner);
    roundIdx++;
  }}
  return rounds;
}}

function roundLabel(matchCount, isFirst, hadByes) {{
  if (isFirst && hadByes) return "First Round";
  if (matchCount === 1) return "Championship";
  if (matchCount === 2) return "Semifinals";
  if (matchCount === 4) return "Quarterfinals";
  if (matchCount === 8) return "Round of 16";
  return "Round of " + (matchCount * 2);
}}

function pickWinner(matchKey, teamId) {{
  state.picks[matchKey] = teamId;
  saveState();
  render();
}}

function swapSlots(i, j) {{
  if (i === j) return;
  const tmp = state.slots[i];
  state.slots[i] = state.slots[j];
  state.slots[j] = tmp;
  state.picks = {{}}; // re-seeding invalidates downstream picks
  saveState();
  render();
}}

function slotEl(teamId, {{ draggable, slotIndex, winner, decided }}) {{
  const el = document.createElement("div");
  if (teamId === null) {{
    el.className = "match-slot " + (draggable ? "bye" : "tbd");
    el.textContent = draggable ? "BYE" : "TBD";
  }} else {{
    const t = teamById[teamId];
    el.className = "match-slot";
    if (decided) el.classList.add(winner ? "winner" : "loser");
    const rank = document.createElement("span");
    rank.className = "rank-badge";
    rank.textContent = "#" + t.rank;
    const img = document.createElement("img");
    img.src = t.logo || "";
    img.loading = "lazy";
    const name = document.createElement("span");
    name.textContent = t.name;
    el.appendChild(rank);
    el.appendChild(img);
    el.appendChild(name);
  }}

  if (draggable && teamId !== null) {{
    el.draggable = true;
    el.addEventListener("dragstart", e => {{
      e.dataTransfer.setData("text/plain", String(slotIndex));
      el.classList.add("dragging");
    }});
    el.addEventListener("dragend", () => el.classList.remove("dragging"));
  }}
  if (draggable) {{
    el.addEventListener("dragover", e => {{ e.preventDefault(); el.classList.add("drag-over"); }});
    el.addEventListener("dragleave", () => el.classList.remove("drag-over"));
    el.addEventListener("drop", e => {{
      e.preventDefault();
      el.classList.remove("drag-over");
      const src = parseInt(e.dataTransfer.getData("text/plain"), 10);
      swapSlots(src, slotIndex);
    }});
  }}
  return el;
}}

function render() {{
  document.querySelectorAll(".size-btn").forEach(btn => {{
    btn.classList.toggle("active", parseInt(btn.dataset.size, 10) === state.size);
  }});

  const board = document.getElementById("board");
  board.innerHTML = "";

  const rounds = computeRounds();
  const hadByes = state.slots.includes(null);

  rounds.forEach((matches, roundIdx) => {{
    const col = document.createElement("div");
    col.className = "round-col" + (roundIdx === 0 ? " seed-col" : "");

    const header = document.createElement("div");
    header.className = "round-header";
    header.textContent = roundLabel(matches.length, roundIdx === 0, hadByes);
    col.appendChild(header);

    const list = document.createElement("div");
    list.className = "round-matches";

    matches.forEach((m, matchIdx) => {{
      const card = document.createElement("div");
      card.className = "match-card";

      [["a", m.a], ["b", m.b]].forEach(([side, teamId]) => {{
        const decided = m.winner !== null && m.a !== null && m.b !== null;
        const isDraggable = roundIdx === 0;
        const slotIndex = roundIdx === 0 ? matchIdx * 2 + (side === "a" ? 0 : 1) : null;

        const el = slotEl(teamId, {{
          draggable: isDraggable,
          slotIndex,
          winner: teamId === m.winner,
          decided,
        }});

        if (isDraggable && teamId === null) {{
          // bye slot still needs to be a drop target even with no chip
          el.addEventListener("dragover", e => {{ e.preventDefault(); el.classList.add("drag-over"); }});
          el.addEventListener("dragleave", () => el.classList.remove("drag-over"));
          el.addEventListener("drop", e => {{
            e.preventDefault();
            el.classList.remove("drag-over");
            const src = parseInt(e.dataTransfer.getData("text/plain"), 10);
            swapSlots(src, slotIndex);
          }});
        }}

        // Any real head-to-head matchup is clickable to pick a winner,
        // regardless of round — including round 0, which is also
        // draggable (for re-seeding) at the same time.
        if (teamId !== null && m.a !== null && m.b !== null) {{
          el.style.cursor = "pointer";
          el.addEventListener("click", () => pickWinner(m.key, teamId));
        }}

        card.appendChild(el);
      }});

      list.appendChild(card);
    }});

    col.appendChild(list);
    board.appendChild(col);
  }});

  const championCol = document.createElement("div");
  championCol.className = "champion-col";
  const championCard = document.createElement("div");
  championCard.className = "champion-card";
  const lastRound = rounds[rounds.length - 1];
  const champ = lastRound && lastRound[0] ? lastRound[0].winner : null;
  if (champ) {{
    const t = teamById[champ];
    championCard.innerHTML =
      '<div class="trophy">\\ud83c\\udfc6</div>' +
      '<img src="' + (t.logo || "") + '">' +
      '<div class="name">' + t.name + '</div>';
  }} else {{
    championCard.innerHTML = '<div class="trophy">\\ud83c\\udfc6</div><div class="placeholder">Champion TBD</div>';
  }}
  championCol.appendChild(championCard);
  board.appendChild(championCol);
}}

function setSize(n) {{
  currentSize = n;
  state = loadState(n);
  render();
}}

function resetCurrent() {{
  if (!confirm("Reset this bracket's seeding and picks?")) return;
  state = defaultState(state.size);
  saveState();
  render();
}}

const toolbar = document.getElementById("toolbar");
SIZES.forEach(n => {{
  const btn = document.createElement("button");
  btn.className = "size-btn";
  btn.dataset.size = n;
  btn.textContent = n + " Teams";
  btn.addEventListener("click", () => setSize(n));
  toolbar.insertBefore(btn, document.getElementById("reset-btn"));
}});
document.getElementById("reset-btn").addEventListener("click", resetCurrent);

render();
</script>
"""
