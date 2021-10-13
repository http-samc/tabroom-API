"""This file contains specific constants that are used
universally and can be updated quickly here in the event
that Tabroom makes a backend change
"""

"""This list holds our standardized names of break rounds,
starting at finals and working our way down
"""
breakNames = [
    "Finals",
    "Semifinals",
    "Quarterfinals",
    "Octafinals",
    "Double Octafinals",
    "Triple Octafinals",
    "Quadruple Octafinals"
]

"""This dictionary holds the bidlevels and their associated tournament
boost factors"""
BOOSTS = {
    "Octafinals": 2,
    "Quarterfinals": 1.55,
    "Semifinals": 1.25,
    "Finals": 1
}

"Accepted decisions for a round"
WIN = ["W", "w"]
LOSS = ["L", "l"]

"Accepted sides"
PRO = ["Pro", "PRO", "Aff"]
CON = ["Con", "CON", "Neg"]

"Accepted divisions, starting with most specific -> generic"
DIVISIONS = [
        ['TOC', 'Public', 'Forum'],
        ['VPF'],
        ['V', 'PF'],
        ['varsity', 'public'],
        ['Varsity', 'PF'],
        ['Open', 'PF'],
        ['Open', 'Public'],
        ['O', 'PF'],
        ['PF'],
        ['Public', 'Forum']
]

"Partial keywords that trigger an auto-reject of a division"
REJECT = ["round robin",
    "middle",
    "jv",
    "novice",
    "ms",
    "junior varsity",
    "npf",
]