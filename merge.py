from os import listdir
from os.path import isfile, join
import json

def merge():
    "Merges each individual tournament result into the master file."

    onlyfiles = [f for f in listdir('data/tournaments') if isfile(join('data/tournaments', f))]
    master = {} # should be reading from file

    for P in onlyfiles:
        PATH = 'data/tournaments/' + P
        with open(PATH, 'r') as f:
            data = json.loads(f.read())

        name = list(data.keys())[0]

        for team in data[name]: # all teams in tourn
            names = data[name][team]["lastNames"]
            if len(names) < 2:
                names.append(names[0])

            target = None
            # getting all teams in master and checking keys
            for key in master:
                optOne = f"{names[0]} & {names[1]}"
                optTwo = f"{names[1]} & {names[0]}"
                #if names[0] in key and names[1] in key:
                if optOne == key or optTwo == key:
                    target = key
                    break
            # didn't find team in master -> create entry
            if not target:
                keyName = f"{names[0]} & {names[1]}"
                master[keyName] = {
                    "codes" : [],
                    "otrScore" : None,
                    "goldBids" : 0,
                    "silverBids" : 0,
                    "prelimRecord" : [0, 0],
                    "breakRecord" : [0, 0],
                    "breakPCT" : None,
                    "tournaments" : []
                }
                target = keyName

            teamData = master[target]
            newData = data[name][team]

            # Updating codes
            if team not in teamData["codes"]: teamData["codes"].append(team)

            # Updating bids score
            teamData["goldBids"] += 1 if newData["goldBid"] else 0
            teamData["silverBids"] += 1 if newData["silverBid"] else 0

            # Updating records
            teamData["prelimRecord"][0] += newData["prelimRecord"][0]
            teamData["prelimRecord"][1] += newData["prelimRecord"][1]

            if newData["breakRecord"]:
                teamData["breakRecord"][0] += newData["breakRecord"][0]
                teamData["breakRecord"][1] += newData["breakRecord"][1]

            # Adding tournament to list
            teamData["tournaments"].append({name : newData})

            breaks = 0
            comps = 0
            numTourns = len(teamData["tournaments"]) # We can assume non0 len

            for tourn in teamData["tournaments"]:
                tourn = tourn[list(tourn.keys())[0]]
                if tourn["breakRecord"] is not None: breaks += 1
                comps += tourn["tournamentComp"]

            teamData["otrScore"] = round(comps/(numTourns * 20), 3)
            teamData["breakPCT"] = round(breaks/numTourns, 3)

            prelimRecord = teamData["prelimRecord"]
            teamData["prelimWinPCT"] = round(prelimRecord[0]/sum(prelimRecord), 3)

            breakRecord = teamData["breakRecord"]
            if sum(breakRecord) != 0: # never broke
                teamData["breakWinPCT"] = round(breakRecord[0]/sum(breakRecord), 3)

            master[target] = teamData

    with open("m.json", 'w') as f:
        json.dump(master, f)

merge()