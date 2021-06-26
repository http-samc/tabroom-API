from argparse import Namespace

"""This file contains specific constants that are used
universally and can be updated quickly here in the event
that Tabroom makes a backend change
"""

"""This Namespace holds specific round abbreviations and
the maximum number of competitors in them
"""
size = Namespace(
    qad = 128,
    trp = 64,
    dub = 32,
    oct = 16,
    qtr = 8,
    sem = 4,
    fin = 2
)

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

"Accepted decisions for a round"
WIN = ["W", "w"]
LOSS = ["L", "l"]

"Accepted sides"
PRO = ["Pro", "Aff"]
CON = ["Con", "Neg"]

"Accepted divisions, starting with most specific -> generic"
DIVISIONS = [
        ['TOC', 'Public', 'Forum'],
        ['VPF'],
        ['V', 'PF'],
        ['varsity', 'public'],
        ['Varsity', 'PF'],
        ['Open', 'PF'],
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