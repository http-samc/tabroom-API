import json
from argparse import Namespace

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