"""Conference realignment board: a self-contained HTML/CSS/JS component
(vanilla HTML5 drag-and-drop, no external libraries) embedded via
st.components.v1.html. Pure client-side — team movement never round-trips
to Python, so dragging doesn't trigger a Streamlit rerun, and the layout
is persisted per-browser via localStorage.
"""

import json

from theme import ACCENT, BG, BORDER, STATUS_BAD, SURFACE, SURFACE_ALT, TEXT_MUTED, TEXT_PRIMARY, TEXT_SECONDARY


def realignment_board_html(teams: list[dict], storage_key: str) -> str:
    """`teams` is a list of {id, name, conference, logo, color} dicts."""
    teams_json = json.dumps(teams)
    return f"""
<style>
  html, body {{ height: 100%; margin: 0; background: {BG}; }}
  * {{ box-sizing: border-box; font-family: system-ui, -apple-system, Segoe UI, sans-serif; }}
  .realign-root {{ height: 100%; display: flex; flex-direction: column; color: {TEXT_PRIMARY}; }}

  .toolbar {{ display: flex; align-items: center; gap: 10px; padding: 4px 2px 12px 2px; flex-wrap: wrap; }}
  .toolbar input {{
    background: {SURFACE}; border: 1px solid {BORDER}; color: {TEXT_PRIMARY};
    border-radius: 6px; padding: 7px 10px; font-size: 0.85rem; width: 220px;
  }}
  .toolbar button {{
    background: {SURFACE}; border: 1px solid {BORDER}; color: {TEXT_PRIMARY};
    border-radius: 6px; padding: 7px 12px; font-size: 0.82rem; cursor: pointer;
  }}
  .toolbar button:hover {{ border-color: {ACCENT}; }}
  .toolbar button.danger:hover {{ border-color: {STATUS_BAD}; color: {STATUS_BAD}; }}
  .summary-text {{ color: {TEXT_SECONDARY}; font-size: 0.82rem; margin-left: auto; }}

  .board {{ flex: 1; min-height: 0; display: flex; gap: 12px; overflow-x: auto; overflow-y: hidden; padding-bottom: 10px; align-items: stretch; }}

  .column {{
    flex: 0 0 220px; max-width: 220px; display: flex; flex-direction: column;
    background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 8px; max-height: 100%;
  }}
  .column-header {{ display: flex; align-items: center; gap: 6px; padding: 10px 10px 8px 10px; border-bottom: 1px solid {BORDER}; }}
  .column-title {{
    font-weight: 600; font-size: 0.85rem; flex: 1; outline: none; white-space: nowrap;
    overflow: hidden; text-overflow: ellipsis; cursor: text;
  }}
  .column-title:focus {{ color: {ACCENT}; }}
  .column-count {{ font-size: 0.72rem; color: {TEXT_MUTED}; background: {SURFACE_ALT}; border-radius: 9px; padding: 1px 7px; }}
  .column-remove {{ cursor: pointer; color: {TEXT_MUTED}; font-size: 0.95rem; line-height: 1; padding: 0 2px; }}
  .column-remove:hover {{ color: {STATUS_BAD}; }}

  .chip-list {{ flex: 1; min-height: 40px; overflow-y: auto; padding: 6px; }}
  .chip-list.drag-over {{ background: {SURFACE_ALT}; outline: 2px dashed {ACCENT}; outline-offset: -2px; }}

  .chip {{
    display: flex; align-items: center; gap: 7px; padding: 5px 7px; margin-bottom: 4px;
    background: {BG}; border: 1px solid {BORDER}; border-radius: 6px; cursor: grab; font-size: 0.78rem;
  }}
  .chip:active {{ cursor: grabbing; }}
  .chip.dragging {{ opacity: 0.35; }}
  .chip img {{ width: 20px; height: 20px; object-fit: contain; flex-shrink: 0; }}
  .chip span {{ white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .chip.hidden {{ display: none; }}
</style>

<div class="realign-root">
  <div class="toolbar">
    <input id="search" type="text" placeholder="Search teams...">
    <button id="add-conf-btn">+ New Conference</button>
    <button id="reset-btn" class="danger">Reset to Real Conferences</button>
    <span class="summary-text" id="summary"></span>
  </div>
  <div class="board" id="board"></div>
</div>

<script>
const TEAMS = {teams_json};
const STORAGE_KEY = "{storage_key}";

function seedColumns() {{
  const byConf = {{}};
  TEAMS.forEach(t => {{
    const conf = t.conference || "Unassigned";
    if (!byConf[conf]) byConf[conf] = [];
    byConf[conf].push(t.id);
  }});
  const names = Object.keys(byConf).sort();
  const cols = names.map(n => ({{ name: n, teamIds: byConf[n] }}));
  if (!byConf.hasOwnProperty("Unassigned")) {{
    cols.unshift({{ name: "Unassigned", teamIds: [] }});
  }}
  return cols;
}}

function loadState() {{
  try {{
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  }} catch (e) {{}}
  return {{ columns: seedColumns() }};
}}

function saveState() {{
  try {{ localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); }} catch (e) {{}}
}}

let state = loadState();
const teamById = {{}};
TEAMS.forEach(t => teamById[t.id] = t);

function findColumnOf(teamId) {{
  return state.columns.find(c => c.teamIds.includes(teamId));
}}

function moveTeam(teamId, destName) {{
  const src = findColumnOf(teamId);
  if (src) src.teamIds = src.teamIds.filter(id => id !== teamId);
  const dest = state.columns.find(c => c.name === destName);
  if (dest && !dest.teamIds.includes(teamId)) dest.teamIds.push(teamId);
  saveState();
  render();
}}

function ensureUnassigned() {{
  let col = state.columns.find(c => c.name === "Unassigned");
  if (!col) {{
    col = {{ name: "Unassigned", teamIds: [] }};
    state.columns.unshift(col);
  }}
  return col;
}}

function addConference() {{
  const name = prompt("New conference name:");
  if (!name) return;
  const trimmed = name.trim();
  if (!trimmed) return;
  if (state.columns.some(c => c.name.toLowerCase() === trimmed.toLowerCase())) {{
    alert("A conference with that name already exists.");
    return;
  }}
  state.columns.push({{ name: trimmed, teamIds: [] }});
  saveState();
  render();
}}

function removeColumn(name) {{
  if (name === "Unassigned") return;
  if (!confirm(`Remove "${{name}}"? Its teams will move to Unassigned.`)) return;
  const col = state.columns.find(c => c.name === name);
  const unassigned = ensureUnassigned();
  col.teamIds.forEach(id => {{ if (!unassigned.teamIds.includes(id)) unassigned.teamIds.push(id); }});
  state.columns = state.columns.filter(c => c.name !== name);
  saveState();
  render();
}}

function renameColumn(oldName, newName) {{
  const trimmed = newName.trim();
  if (!trimmed || trimmed === oldName) {{ render(); return; }}
  if (state.columns.some(c => c.name.toLowerCase() === trimmed.toLowerCase() && c.name !== oldName)) {{
    alert("A conference with that name already exists.");
    render();
    return;
  }}
  const col = state.columns.find(c => c.name === oldName);
  col.name = trimmed;
  saveState();
  render();
}}

function resetBoard() {{
  if (!confirm("Reset the board to real current conferences? This clears your layout.")) return;
  try {{ localStorage.removeItem(STORAGE_KEY); }} catch (e) {{}}
  state = {{ columns: seedColumns() }};
  saveState();
  render();
}}

function applySearch() {{
  const q = document.getElementById("search").value.trim().toLowerCase();
  document.querySelectorAll(".chip").forEach(chip => {{
    const match = !q || chip.dataset.name.toLowerCase().includes(q);
    chip.classList.toggle("hidden", !match);
  }});
}}

function render() {{
  const board = document.getElementById("board");
  board.innerHTML = "";
  state.columns.forEach(col => {{
    const colEl = document.createElement("div");
    colEl.className = "column";

    const header = document.createElement("div");
    header.className = "column-header";

    const title = document.createElement("div");
    title.className = "column-title";
    title.contentEditable = "true";
    title.spellcheck = false;
    title.textContent = col.name;
    title.addEventListener("blur", () => renameColumn(col.name, title.textContent));
    title.addEventListener("keydown", e => {{ if (e.key === "Enter") {{ e.preventDefault(); title.blur(); }} }});

    const count = document.createElement("div");
    count.className = "column-count";
    count.textContent = col.teamIds.length;

    header.appendChild(title);
    header.appendChild(count);

    if (col.name !== "Unassigned") {{
      const remove = document.createElement("div");
      remove.className = "column-remove";
      remove.textContent = "\\u00d7";
      remove.title = "Remove conference";
      remove.addEventListener("click", () => removeColumn(col.name));
      header.appendChild(remove);
    }}

    const list = document.createElement("div");
    list.className = "chip-list";
    list.addEventListener("dragover", e => {{ e.preventDefault(); list.classList.add("drag-over"); }});
    list.addEventListener("dragleave", () => list.classList.remove("drag-over"));
    list.addEventListener("drop", e => {{
      e.preventDefault();
      list.classList.remove("drag-over");
      const teamId = e.dataTransfer.getData("text/plain");
      moveTeam(teamId, col.name);
    }});

    col.teamIds.forEach(id => {{
      const t = teamById[id];
      if (!t) return;
      const chip = document.createElement("div");
      chip.className = "chip";
      chip.draggable = true;
      chip.dataset.name = t.name;
      chip.title = t.name;
      chip.addEventListener("dragstart", e => {{
        e.dataTransfer.setData("text/plain", t.id);
        chip.classList.add("dragging");
      }});
      chip.addEventListener("dragend", () => chip.classList.remove("dragging"));

      const img = document.createElement("img");
      img.src = t.logo;
      img.loading = "lazy";
      const span = document.createElement("span");
      span.textContent = t.name;

      chip.appendChild(img);
      chip.appendChild(span);
      list.appendChild(chip);
    }});

    colEl.appendChild(header);
    colEl.appendChild(list);
    board.appendChild(colEl);
  }});

  document.getElementById("summary").textContent =
    state.columns.length + " conferences \\u00b7 " + TEAMS.length + " teams";
  applySearch();
}}

document.getElementById("add-conf-btn").addEventListener("click", addConference);
document.getElementById("reset-btn").addEventListener("click", resetBoard);
document.getElementById("search").addEventListener("input", applySearch);

render();
</script>
"""
