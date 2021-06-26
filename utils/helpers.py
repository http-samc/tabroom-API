import json
from const import breakNames

def calcBid(data: dict) -> dict:
    """Adds bid data to condensed tournament-level dataset

    Args:
        data (dict): condensed tournament-level dataset

    Returns:
        dict: dataset with bid levels for each team included
    """

    tournName = list(data.keys())[0]

    with open('utils/tournInfo.json', 'r') as f:
        tournData = json.loads(f.read())

    if tournName not in list(tournData.keys()): return data

    gold = breakNames.index(tournData[tournName]["bidLevel"])
    silver = gold + 1

    for team in data[tournName]:
        if not data[tournName][team]["breakRecord"]:
            data[tournName][team]["goldBid"] = False
            data[tournName][team]["silverBid"] = False
            continue

        elif not data[tournName][team]["eliminated"]: # Championed -> gold
            data[tournName][team]["goldBid"] = True
            data[tournName][team]["silverBid"] = False
            continue

        elim = breakNames.index(data[tournName][team]["eliminated"][3])

        if elim <= gold: # Broke w/ gold
            data[tournName][team]["goldBid"] = True
            data[tournName][team]["silverBid"] = False

        elif elim <= silver: # Broke w/ silver
            data[tournName][team]["goldBid"] = False
            data[tournName][team]["silverBid"] = True

        else: # Broke but no bid
            data[tournName][team]["goldBid"] = False
            data[tournName][team]["silverBid"] = False

    return data

def calcOPwpm(data: dict) -> dict:
    """Adds OPwpm to semi-condensed tournament-level dataset.
    Required to be called before round data is removed to preserve
    the opponent data needed in order to gen OPwpm.

    Args:
        data (dict): semi-condensed tournament-level dataset

    Returns:
        dict: dataset with OPwpm for each team included
    """
    tourn = list(data.keys())[0]

    for team in data[tourn]:
        prelims = data[tourn][team]["prelims"]
        opps = []
        for prelimRound in prelims:
            opp = prelimRound["opp"]
            if not opp: continue # bye
            if opp in data[tourn]:
                opps.append(opp)
            else:
                print("Can't find " + opp) # handle mid-tourn dropped entries
        oppWins = 0
        for opp in opps:
            oppWins += data[tourn][opp]["prelimRecord"][0]

        OPwpm = round(oppWins/len(opps), 3)
        data[tourn][team]["OPwpm"] = OPwpm

    return data