import json

from colorama import Fore

from utils.const import breakNames


def calcBid(data: dict) -> dict:
    """Adds bid data to condensed tournament-level dataset

    Args:
        data (dict): condensed tournament-level dataset

    Returns:
        dict: dataset with bid levels for each team included
    """

    tournName = list(data.keys())[0]

    with open('data/tournInfo.json', 'r') as f:
        tournData = json.loads(f.read())

    if tournName not in tournData:
        print(tournData[tournName])
        return data

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

        try: 
            elim = breakNames.index(data[tournName][team]["eliminated"][3])
        except Exception: # Handles unknown round names (eg. International Silver TOC breakout) and defaults to no bid
            data[tournName][team]["goldBid"] = False
            data[tournName][team]["silverBid"] = False
            data[tournName][team]["eliminated"].insert(3, data[tournName][team]["eliminated"][2]) # no std for unknown rd name
            continue

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
        del data[tourn][team]["prelims"] # removing unneeded data from main
        opps = []
        for prelimRound in prelims:
            opp = prelimRound["opp"]
            if not opp: continue # bye
            if opp in data[tourn]: # no data for entries that drop in the middle of the tournament
                opps.append(opp)
        oppWins = 0
        for opp in opps:
            oppWins += data[tourn][opp]["prelimRecord"][0]
        if len(opps) > 0:
            OPwpm = round(oppWins/len(opps), 3)
            data[tourn][team]["OPwpm"] = OPwpm
        else:
            print(Fore.YELLOW + f"No opponents found for {team}")

    return data

def calcTournamentComp(data: dict) -> dict:
    """Adds tournamentComp to condensed tournament-level dataset.
    Required to be called last, after OPwpm calculation

    Args:
        data (dict): condensed tournament-level dataset

    Returns:
        dict: dataset with tournamentComp for each team included
    """
    tourn = list(data.keys())[0]

    for team in data[tourn]:
        OPwpm = data[tourn][team]["OPwpm"]
        wins = data[tourn][team]["prelimRecord"][0]

        losses = data[tourn][team]["prelimRecord"][1]
        numPrelims = wins + losses

        breakBoost = data[tourn][team]["breakBoost"]
        tournamentBoost = data[tourn][team]["tournamentBoost"]

        tournamentComp = round(((OPwpm * wins)/(numPrelims*numPrelims))*breakBoost*tournamentBoost, 3)
        data[tourn][team]["tournamentComp"] = tournamentComp

    return data

def orderCond(data: dict) -> dict:
    """Orders all keys in the given condensed tournament dict

    Args:
        data (dict): condensed tournament dict

    Returns:
        dict: ordered dict (matches schema)
    """
    tourn = list(data.keys())[0]

    ordered = {tourn: {}}

    for team in data[tourn]:
        ordered[tourn][team] = {
            "tournamentComp" : data[tourn][team]["tournamentComp"],
            "fullNames" : data[tourn][team]["fullNames"],
            "lastNames" : data[tourn][team]["lastNames"],
            "prelimRecord" : data[tourn][team]["prelimRecord"],
            "prelimRank" : data[tourn][team]["prelimRank"],
            "breakRecord" : data[tourn][team]["breakRecord"],
            "eliminated" : data[tourn][team]["eliminated"],
            "speaks" : data[tourn][team]["speaks"],
            "goldBid" : data[tourn][team]["goldBid"],
            "silverBid" : data[tourn][team]["silverBid"],
            "breakBoost" : data[tourn][team]["breakBoost"],
            "tournamentBoost" : data[tourn][team]["tournamentBoost"],
            "OPwpm" : data[tourn][team]["OPwpm"],
        }

    return ordered
