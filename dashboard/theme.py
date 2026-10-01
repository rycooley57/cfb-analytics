"""ESPN-style dark theme: shared colors, Plotly layout, and per-team brand
color resolution. One palette, committed to dark — this app doesn't support
a light mode."""

import re

BG = "#0d1117"
SURFACE = "#1a1f26"
SURFACE_ALT = "#242933"
BORDER = "rgba(255,255,255,0.08)"

TEXT_PRIMARY = "#f5f5f5"
TEXT_SECONDARY = "#b0b7c0"
TEXT_MUTED = "#6b7280"

ACCENT = "#d5192c"  # brand red — headers, dividers, badges (chrome, not data)
GRIDLINE = "rgba(255,255,255,0.08)"

STATUS_GOOD = "#22c55e"
STATUS_BAD = "#ef4444"

# Fallback categorical pair when a team has no usable brand color (dark-mode
# steps from the validated default palette).
FALLBACK_PRIMARY = "#3987e5"
FALLBACK_SECONDARY = "#d95926"

PLOTLY_LAYOUT = dict(
    plot_bgcolor=SURFACE,
    paper_bgcolor=SURFACE,
    font=dict(color=TEXT_PRIMARY, family="system-ui, -apple-system, Segoe UI, sans-serif"),
    xaxis=dict(gridcolor=GRIDLINE, zeroline=False, linecolor=BORDER),
    yaxis=dict(gridcolor=GRIDLINE, zeroline=False, linecolor=BORDER),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(color=TEXT_SECONDARY)),
    margin=dict(t=40, b=40, l=40, r=20),
    hoverlabel=dict(bgcolor=SURFACE_ALT, font_color=TEXT_PRIMARY, bordercolor=BORDER),
)


def _relative_luminance(hex_color: str) -> float:
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        return 1.0
    r, g, b = (int(hex_color[i : i + 2], 16) / 255 for i in (0, 2, 4))

    def lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = lin(r), lin(g), lin(b)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _valid_hex(value) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"#[0-9a-fA-F]{6}", value))


def team_colors(team_row) -> dict:
    """Returns {"primary": hex, "secondary": hex} for a team row from the
    teams table, falling back to the default categorical pair when a brand
    color is missing or too dark to read against our near-black surface."""
    primary = team_row.get("color") if hasattr(team_row, "get") else team_row["color"]
    secondary = team_row.get("alternateColor") if hasattr(team_row, "get") else team_row["alternateColor"]

    if not _valid_hex(primary) or _relative_luminance(primary) < 0.06:
        primary = FALLBACK_PRIMARY
    if not _valid_hex(secondary) or secondary == primary:
        secondary = FALLBACK_SECONDARY

    return {"primary": primary, "secondary": secondary}


def team_logo(team_row) -> str | None:
    logos = team_row.get("logos") if hasattr(team_row, "get") else team_row["logos"]
    if logos is not None and len(logos) > 0:
        return logos[0]
    return None
