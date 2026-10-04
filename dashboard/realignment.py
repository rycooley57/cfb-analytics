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

  .board-wrapper {{ flex: 1; min-height: 0; display: flex; flex-direction: column; gap: 10px; }}
  .row-group {{ display: flex; flex-direction: column; min-height: 0; }}
  .row-group-top {{ flex: 0 0 auto; }}
  .row-group-top .column {{ max-height: none; }}
  .row-group-top .chip-list {{ overflow-y: visible; }}
  .row-group-bottom {{ flex: 1; min-height: 0; border-top: 1px solid {BORDER}; padding-top: 10px; }}
  .row-label {{
    flex: 0 0 auto; font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.06em;
    color: {TEXT_MUTED}; margin-bottom: 4px;
  }}
  .board-row {{ flex: 1; min-height: 0; display: flex; gap: 12px; overflow-x: auto; overflow-y: hidden; padding-bottom: 8px; align-items: stretch; }}

  .column {{
    flex: 0 0 220px; max-width: 220px; display: flex; flex-direction: column;
    background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 8px; max-height: 100%;
  }}
  .column.dragging-col {{ opacity: 0.35; }}
  .column.drag-over-col {{ outline: 2px dashed {ACCENT}; outline-offset: -2px; }}
  .column-header {{ display: flex; align-items: center; gap: 6px; padding: 10px 10px 8px 10px; border-bottom: 1px solid {BORDER}; }}
  .column-handle {{
    cursor: grab; color: {TEXT_MUTED}; font-size: 0.72rem; letter-spacing: -2px;
    padding: 0 2px; user-select: none; flex-shrink: 0;
  }}
  .column-handle:active {{ cursor: grabbing; }}
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
  <div class="board-wrapper">
    <div class="row-group row-group-top">
      <div class="row-label">Power 4</div>
      <div class="board-row" id="board-top"></div>
    </div>
    <div class="row-group row-group-bottom">
      <div class="row-label">Everyone Else</div>
      <div class="board-row" id="board-bottom"></div>
    </div>
  </div>
</div>

<script>
const TEAMS = {teams_json};
const STORAGE_KEY = "{storage_key}";
const TOP_CONF_NAMES = ["Big Ten", "SEC", "Big 12", "ACC"];

function seedColumns() {{
  const byConf = {{}};
  TEAMS.forEach(t => {{
    const conf = t.conference || "Unassigned";
    if (!byConf[conf]) byConf[conf] = [];
    byConf[conf].push(t.id);
  }});
  if (!byConf.hasOwnProperty("Unassigned")) byConf["Unassigned"] = [];

  // Array order IS display order within each row (no re-sort at render
  // time, so drag-reordering sticks) — so the initial order matters:
  // Big Ten/SEC/Big 12/ACC lead the top row, Unassigned leads the
  // bottom row, everything else follows alphabetically.
  const allNames = Object.keys(byConf).sort();
  const topNames = TOP_CONF_NAMES.filter(n => allNames.includes(n));
  const restNames = allNames.filter(n => !TOP_CONF_NAMES.includes(n) && n !== "Unassigned");

  const topCols = topNames.map(n => ({{ name: n, teamIds: byConf[n], top: true }}));
  const restCols = [
    {{ name: "Unassigned", teamIds: byConf["Unassigned"], top: false }},
    ...restNames.map(n => ({{ name: n, teamIds: byConf[n], top: false }})),
  ];
  return [...topCols, ...restCols];
}}

function loadState() {{
  try {{
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {{
      const parsed = JSON.parse(raw);
      // Older saved boards predate the `top` flag — infer it from name so
      // existing layouts don't lose their Power 4 placement.
      parsed.columns.forEach(c => {{
        if (c.top === undefined) c.top = TOP_CONF_NAMES.includes(c.name);
      }});
      return parsed;
    }}
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

function reorderColumn(draggedName, targetName, isTopRow) {{
  if (draggedName === targetName) return;
  const fromIdx = state.columns.findIndex(c => c.name === draggedName);
  if (fromIdx === -1) return;
  const [col] = state.columns.splice(fromIdx, 1);
  col.top = isTopRow;
  if (targetName === null) {{
    // Dropped on empty row space, not on a specific column — send to the
    // end of that row. filter() preserves relative order of matching
    // elements regardless of what's interspersed, so a plain push here
    // still lands it last within its row, not necessarily last overall.
    state.columns.push(col);
  }} else {{
    const targetIdx = state.columns.findIndex(c => c.name === targetName);
    state.columns.splice(targetIdx === -1 ? state.columns.length : targetIdx, 0, col);
  }}
  saveState();
  render();
}}

function ensureUnassigned() {{
  let col = state.columns.find(c => c.name === "Unassigned");
  if (!col) {{
    col = {{ name: "Unassigned", teamIds: [], top: false }};
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
  // New conferences join the Power 4 row at top, same as Big Ten/SEC/Big 12/ACC.
  state.columns.push({{ name: trimmed, teamIds: [], top: true }});
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

function buildColumnElement(col, isTopRow) {{
    const colEl = document.createElement("div");
    colEl.className = "column";

    // Conference reordering: drag the handle to move this column, including
    // across the Power 4 / Everyone Else boundary. Uses a distinct
    // dataTransfer type so it never gets confused with a team-chip drag.
    colEl.addEventListener("dragover", e => {{
      if (!e.dataTransfer.types.includes("application/x-conf")) return;
      e.preventDefault();
      colEl.classList.add("drag-over-col");
    }});
    colEl.addEventListener("dragleave", () => colEl.classList.remove("drag-over-col"));
    colEl.addEventListener("drop", e => {{
      if (!e.dataTransfer.types.includes("application/x-conf")) return;
      e.preventDefault();
      e.stopPropagation();
      colEl.classList.remove("drag-over-col");
      const draggedName = e.dataTransfer.getData("application/x-conf");
      if (draggedName) reorderColumn(draggedName, col.name, isTopRow);
    }});

    const header = document.createElement("div");
    header.className = "column-header";

    const handle = document.createElement("div");
    handle.className = "column-handle";
    handle.textContent = "\\u22ee\\u22ee";
    handle.title = "Drag to reorder";
    handle.draggable = true;
    handle.addEventListener("dragstart", e => {{
      e.dataTransfer.setData("application/x-conf", col.name);
      e.stopPropagation();
      colEl.classList.add("dragging-col");
    }});
    handle.addEventListener("dragend", () => colEl.classList.remove("dragging-col"));

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

    header.appendChild(handle);
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
    list.addEventListener("dragover", e => {{
      if (!e.dataTransfer.types.includes("text/plain")) return;
      e.preventDefault();
      list.classList.add("drag-over");
    }});
    list.addEventListener("dragleave", () => list.classList.remove("drag-over"));
    list.addEventListener("drop", e => {{
      if (!e.dataTransfer.types.includes("text/plain")) return;
      e.preventDefault();
      e.stopPropagation();
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
    return colEl;
}}

function render() {{
  const top = document.getElementById("board-top");
  const bottom = document.getElementById("board-bottom");
  top.innerHTML = "";
  bottom.innerHTML = "";

  // Array order is display order (see seedColumns) — no re-sort here, so
  // drag-reordering sticks across renders.
  const topCols = state.columns.filter(c => c.top);
  const restCols = state.columns.filter(c => !c.top);

  topCols.forEach(col => top.appendChild(buildColumnElement(col, true)));
  restCols.forEach(col => bottom.appendChild(buildColumnElement(col, false)));

  document.getElementById("summary").textContent =
    state.columns.length + " conferences \\u00b7 " + TEAMS.length + " teams";
  applySearch();
}}

function makeRowDropTarget(rowEl, isTopRow) {{
  // Fallback for dropping on empty row space rather than on a column —
  // column-level drop handlers call stopPropagation, so this only fires
  // when the drop didn't land on a column.
  rowEl.addEventListener("dragover", e => {{
    if (!e.dataTransfer.types.includes("application/x-conf")) return;
    e.preventDefault();
  }});
  rowEl.addEventListener("drop", e => {{
    if (!e.dataTransfer.types.includes("application/x-conf")) return;
    e.preventDefault();
    const draggedName = e.dataTransfer.getData("application/x-conf");
    if (draggedName) reorderColumn(draggedName, null, isTopRow);
  }});
}}

document.getElementById("add-conf-btn").addEventListener("click", addConference);
document.getElementById("reset-btn").addEventListener("click", resetBoard);
document.getElementById("search").addEventListener("input", applySearch);
makeRowDropTarget(document.getElementById("board-top"), true);
makeRowDropTarget(document.getElementById("board-bottom"), false);

render();
</script>
"""
