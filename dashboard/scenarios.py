"""Speculative/fictional conference-realignment scenarios for the
realignment board and playoff bracket — not CFBD data, since neither
2032 nor 2199 has happened. Real team names/logos/colors are reused
(pulled from the real current roster); only the conference/tier
assignment is invented.
"""

# --- 2032: a grounded extrapolation of real, already-reported realignment
# chatter (ACC's FSU/Clemson exit-fee litigation, Miami/UNC speculated as
# next dominoes, Stanford/Cal returning to a rebuilt Pac-12, a Big 12 raid
# on the American's best brand) — not a leak, just "if current trends keep
# going." Everything not listed here keeps its real 2026 conference.
SCENARIO_2032_LABEL = "2032 (Projected)"
SCENARIO_2032_BLURB = (
    "Speculative — a grounded extrapolation of real realignment chatter (not a leak): "
    "the ACC loses Florida State, Clemson, and Miami to the SEC and North Carolina to the "
    "Big Ten; Stanford and Cal return to a rebuilt Pac-12; the Big 12 raids the American's "
    "best brand. Everything else keeps its real 2026 conference."
)
SCENARIO_2032_MOVES = {
    "Florida State": "SEC",
    "Clemson": "SEC",
    "Miami": "SEC",
    "North Carolina": "Big Ten",
    "Stanford": "Pac-12",
    "California": "Pac-12",
    "Memphis": "Big 12",
}

# --- Project Rudy (2199): the real private-equity-backed "super league"
# pitch reported by The Athletic in Oct. 2024 — a 70-team, 3-tier structure
# (Tier 1 top 16, Tier 2 next 22, Tier 3 next 32) covering only the Power
# Four + Notre Dame, with promotion/relegation between tiers and no G5/FCS
# games. The real pitch's exact 70-school list was never publicly
# disclosed, so this is a reconstruction by current (2026) brand strength —
# all real Power Four + Notre Dame members, plus Boise State and Memphis as
# the two strongest Group of Five brands, which is how the reporting
# described the pitch reaching beyond the conferences' current membership.
# "2199" is just a fictional placeholder year for "someday, maybe."
PROJECT_RUDY_LABEL = "2199 — Project Rudy"
PROJECT_RUDY_BLURB = (
    "Speculative — 'Project Rudy' is a real pitch (The Athletic, Oct. 2024): a 70-team, "
    "3-tier super league with promotion/relegation, $9B in private equity, and no G5/FCS "
    "games. The real pitch's exact 70-school list was never published, so tiers here are "
    "reconstructed by current brand strength. Year '2199' is just a placeholder."
)
PROJECT_RUDY_TIERS = {
    "Tier 1": [
        "Ohio State", "Michigan", "Georgia", "Alabama", "Texas", "Oklahoma", "Oregon",
        "Penn State", "USC", "Notre Dame", "LSU", "Florida", "Clemson", "Miami",
        "Florida State", "Tennessee",
    ],
    "Tier 2": [
        "Auburn", "Wisconsin", "Nebraska", "Washington", "Texas A&M", "Ole Miss", "Utah",
        "Iowa", "Oklahoma State", "North Carolina", "Virginia Tech", "Louisville",
        "Kansas State", "Baylor", "TCU", "Arizona State", "Missouri", "South Carolina",
        "Kentucky", "Michigan State", "Colorado", "BYU",
    ],
    "Tier 3": [
        "Arkansas", "Mississippi State", "Vanderbilt", "Duke", "NC State", "Pittsburgh",
        "Virginia", "Wake Forest", "Boston College", "Syracuse", "Georgia Tech", "SMU",
        "California", "Stanford", "Illinois", "Indiana", "Maryland", "Minnesota",
        "Northwestern", "Purdue", "Rutgers", "UCLA", "Texas Tech", "Arizona", "Cincinnati",
        "Houston", "Iowa State", "Kansas", "West Virginia", "UCF", "Boise State", "Memphis",
    ],
}

PROJECT_RUDY_CONFERENCE = {team: tier for tier, teams in PROJECT_RUDY_TIERS.items() for team in teams}

# Bracket seed order: Tier 1 first (ranks 1-16), then Tier 2, then Tier 3 —
# same role the AP Top 25 plays for the real-season bracket.
PROJECT_RUDY_RANKED = (
    PROJECT_RUDY_TIERS["Tier 1"] + PROJECT_RUDY_TIERS["Tier 2"] + PROJECT_RUDY_TIERS["Tier 3"]
)

SPECULATIVE_YEARS = {2032: SCENARIO_2032_LABEL, 2199: PROJECT_RUDY_LABEL}
