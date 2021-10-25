import json
from utils.const import *

PATH = "data/2021-22 MASTER.json"

def getSchool(code: str):
    if "&" in code:
        code = code[0: code.rfind("&")]
        code = code[0:code.rfind(" ")]

    return code[0:code.rfind(" ")]

print("Adding ghost bids.")

with open(PATH, "r") as f:
    data = json.loads(f.read())

for t in data:
    team = data[t]

    i = 0
    for tournament in team["tournaments"]:
        if "New York City Inv" in data[t]["tournaments"][i]["name"]: continue # weird tournament

        data[t]["tournaments"][i]["ghostBid"] = False

        teamConflict = False
        ghostSilver = None
        ghostGold = None

        if not tournament["eliminated"]: continue # if they championed no ghost
        elimTeam = tournament["eliminated"][4]
        elimSchool = getSchool(elimTeam)
        for code in team["codes"]:
            if teamConflict: continue
            if getSchool(code) == elimSchool:
                teamConflict = True
                continue
        if teamConflict == False: continue
        tBoost = tournament["tournamentBoost"]
        elimRd = tournament["eliminated"][3]

        if tBoost == 2 and (elimRd == breakNames[5] or elimRd == breakNames[4]):
            if elimRd == breakNames[5]: ghostSilver = True
            elif elimRd == breakNames[4]: ghostGold = True

        elif tBoost == 1.55 and (elimRd == breakNames[3] or elimRd == breakNames[4]):
            if elimRd == breakNames[4]: ghostSilver = True
            elif elimRd == breakNames[3]: ghostGold = True

        elif tBoost == 1.25 and (elimRd == breakNames[2] or elimRd == breakNames[3]):
            if elimRd == breakNames[3]: ghostSilver = True
            elif elimRd == breakNames[2]: ghostGold = True

        elif tBoost == 1 and (elimRd == breakNames[1] or elimRd == breakNames[2]):
            if elimRd == breakNames[2]: ghostSilver = True
            elif elimRd == breakNames[1]: ghostGold = True

        if ghostGold == True:
            data[t]["tournaments"][i]["goldBid"] = True
            data[t]["goldBids"] = data[t]["goldBids"] + 1

            # remove the silver bid they got
            data[t]["tournaments"][i]["silverBid"] = False
            data[t]["silverBids"] = data[t]["silverBids"] - 1

        elif ghostSilver == True:
            data[t]["tournaments"][i]["silverBid"] = True
            data[t]["silverBids"] = data[t]["silverBids"] + 1

        if ghostSilver or ghostGold: data[t]["tournaments"][i]["ghostBid"] = True

        i += 1

with open(PATH, "w") as f:
    json.dump(data, f)

print("Added ghost bids.")