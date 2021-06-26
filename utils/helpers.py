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