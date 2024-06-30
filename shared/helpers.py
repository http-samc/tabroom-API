import re

def enum_to_string(string: str | None) -> str:
    if string is None:
        return string
    match = re.findall('[A-Z][^A-Z]*', string)
    return " ".join(match) if match is not None else string

def get_tourn_boost(firstElimRound: str | None) -> float:
    boost = 1
    elim = firstElimRound

    if elim == "Semifinals":
        boost = 1.2
    elif elim == "Quarterfinals":
        boost = 1.4
    elif elim == "Octofinals":
        boost = 1.6
    elif elim == "DoubleOctofinals":
        boost = 1.8
    elif elim == "TripleOctofinals":
        boost = 2
    elif elim == "QuadrupleOctofinals":
        boost = 2.2

    return boost