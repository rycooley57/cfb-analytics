"""Shared chart color roles, kept in one place so every page assigns color
consistently (fixed categorical order, single-hue sequential ramp)."""

CATEGORICAL = {
    "primary": "#2a78d6",  # blue - slot 1: the selected team / first entity
    "secondary": "#eb6834",  # orange - slot 2: comparison / second entity
}

SEQUENTIAL_BLUE = ["#cde2fb", "#9ec5f4", "#5598e7", "#2a78d6", "#184f95"]

INK = "#0b0b0b"
MUTED = "#898781"
GRIDLINE = "#e1e0d9"

PLOTLY_LAYOUT = dict(
    plot_bgcolor="#fcfcfb",
    paper_bgcolor="#fcfcfb",
    font=dict(color=INK, family="system-ui, -apple-system, Segoe UI, sans-serif"),
    xaxis=dict(gridcolor=GRIDLINE, zeroline=False, linecolor=MUTED),
    yaxis=dict(gridcolor=GRIDLINE, zeroline=False, linecolor=MUTED),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    margin=dict(t=40, b=40, l=40, r=20),
)
