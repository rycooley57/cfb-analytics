"""Speculative/fictional conference-realignment scenarios for the
realignment board and playoff bracket — not CFBD data, since neither
2032 nor 2199 has happened. Real team names/logos/colors are reused
(pulled from the real current roster); only the conference/tier
assignment is invented.
"""

# Real 2026 Power Four membership — the shared baseline both scenarios
# below build on top of (as explicit moves/overrides), rather than two
# independently hand-maintained rosters that could drift out of sync.
REAL_2026_P4 = {
    "ACC": [
        "Boston College", "California", "Clemson", "Duke", "Florida State", "Georgia Tech",
        "Louisville", "Miami", "NC State", "North Carolina", "Pittsburgh", "SMU", "Stanford",
        "Syracuse", "Virginia", "Virginia Tech", "Wake Forest",
    ],
    "Big 12": [
        "Arizona", "Arizona State", "BYU", "Baylor", "Cincinnati", "Colorado", "Houston",
        "Iowa State", "Kansas", "Kansas State", "Oklahoma State", "TCU", "Texas Tech", "UCF",
        "Utah", "West Virginia",
    ],
    "Big Ten": [
        "Illinois", "Indiana", "Iowa", "Maryland", "Michigan", "Michigan State", "Minnesota",
        "Nebraska", "Northwestern", "Ohio State", "Oregon", "Penn State", "Purdue", "Rutgers",
        "UCLA", "USC", "Washington", "Wisconsin",
    ],
    "SEC": [
        "Alabama", "Arkansas", "Auburn", "Florida", "Georgia", "Kentucky", "LSU",
        "Mississippi State", "Missouri", "Oklahoma", "Ole Miss", "South Carolina", "Tennessee",
        "Texas", "Texas A&M", "Vanderbilt",
    ],
    "Pac-12": [
        "Boise State", "Colorado State", "Fresno State", "Oregon State", "San Diego State",
        "Texas State", "Utah State", "Washington State",
    ],
}
REAL_2026_CONFERENCE = {team: conf for conf, teams in REAL_2026_P4.items() for team in teams}

# --- 2032: a grounded extrapolation of real, already-reported realignment
# chatter — the SEC and Big Ten each consolidate to 24 teams (the "Big 2"),
# raiding the ACC's strongest remaining brands plus Notre Dame; what's left
# of the ACC combines with an untouched Big 12 and the rebuilt Pac-12 into
# a single 28-team "Tier 2" conference. Not a leak — a plausible shape for
# where the sport's financial gravity keeps pulling.
SCENARIO_2032_LABEL = "2032 (Projected)"
SCENARIO_2032_BLURB = (
    "Speculative — a grounded extrapolation of real realignment chatter (not a leak): the SEC "
    "and Big Ten each consolidate to 24 teams, raiding the ACC's strongest remaining brands "
    "and Notre Dame. What's left of the ACC, plus an untouched Big 12 and Pac-12, merges into "
    "a single 28-team 'Tier 2' conference."
)
_SEC_ADDS_2032 = [
    "Florida State", "Clemson", "Miami", "North Carolina", "Virginia Tech", "Louisville",
    "NC State", "Georgia Tech",
]
_BIG_TEN_ADDS_2032 = ["Duke", "Virginia", "Pittsburgh", "Syracuse", "Boston College", "Notre Dame"]
_TIER2_2032 = (
    [t for t in REAL_2026_P4["ACC"] if t not in _SEC_ADDS_2032 and t not in _BIG_TEN_ADDS_2032]
    + REAL_2026_P4["Big 12"]
    + REAL_2026_P4["Pac-12"]
)
SCENARIO_2032_MOVES = (
    {team: "SEC" for team in _SEC_ADDS_2032}
    | {team: "Big Ten" for team in _BIG_TEN_ADDS_2032}
    | {team: "Tier 2" for team in _TIER2_2032}
)

# --- Project Rudy (2199): the real private-equity-backed "super league"
# pitch reported by The Athletic in Oct. 2024 — a 70-team structure with a
# 3-tier revenue/seeding split (Tier 1 top 16, Tier 2 next 22, Tier 3 next
# 32), $9B in private capital, promotion/relegation, and no G5/FCS games.
# Reporting is explicit that the pitch *preserves* the four power
# conferences rather than replacing them — the tiers are a revenue overlay
# on top, not new conferences — so the realignment board groups teams by
# their real conference; the tier ranking instead drives playoff bracket
# seeding below. The real pitch's exact 70-school list was never publicly
# disclosed, so both the roster and tier placement are a reconstruction by
# current (2026) brand strength: all real Power Four members, plus Notre
# Dame (folded into the ACC, its real scheduling partner) and Boise State
# + Memphis (folded into the Big 12, the real landing conference for the
# American's best recent brands) as the two strongest Group of Five
# additions. "2199" is just a fictional placeholder year.
PROJECT_RUDY_LABEL = "2199 — Project Rudy"
PROJECT_RUDY_BLURB = (
    "Speculative — 'Project Rudy' is a real pitch (The Athletic, Oct. 2024): a 70-team super "
    "league with $9B in private equity and no G5/FCS games. Reporting says it preserves the "
    "four power conferences, so teams are grouped here by real conference (Notre Dame -> ACC, "
    "Boise State/Memphis -> Big 12); a 3-tier revenue split from the pitch instead drives "
    "playoff bracket seeding. The real 70-school list was never published, so this is a "
    "reconstruction by current brand strength. Year '2199' is just a placeholder."
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

# Bracket seed order: Tier 1 first (ranks 1-16), then Tier 2, then Tier 3 —
# same role the AP Top 25 plays for the real-season bracket.
PROJECT_RUDY_RANKED = (
    PROJECT_RUDY_TIERS["Tier 1"] + PROJECT_RUDY_TIERS["Tier 2"] + PROJECT_RUDY_TIERS["Tier 3"]
)

_PROJECT_RUDY_REGIONAL_OVERRIDES = {"Notre Dame": "ACC", "Boise State": "Big 12", "Memphis": "Big 12"}
PROJECT_RUDY_CONFERENCE = {
    team: _PROJECT_RUDY_REGIONAL_OVERRIDES.get(team, REAL_2026_CONFERENCE.get(team))
    for team in PROJECT_RUDY_RANKED
}

SPECULATIVE_YEARS = {2032: SCENARIO_2032_LABEL, 2199: PROJECT_RUDY_LABEL}
