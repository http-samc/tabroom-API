import json

with open('data/2020-21 Master.json', 'r') as f:
    data = json.loads(f.read())

sorted = sorted(data.keys(), key = lambda x: data[x]['otrScore'], reverse=True) # get teams by OTR score high to low

leaders = {"leaders": []}

p = 1
for team in sorted:
    teamData = data[team]
    tournaments = teamData["tournaments"]
    if len(tournaments) < 4: continue # they didn't have enough experience to be acc indexed

    score = teamData["otrScore"]
    golds = teamData["goldBids"]
    silvers = teamData["silverBids"]
    code = teamData["codes"][0]
    names = teamData["fullNames"]
    position = p

    leaders["leaders"].append({
        "pos": p,
        "score": score,
        "golds": golds,
        "silvers": silvers,
        "code": code,
        "names": names,
    })

    p += 1

with open('data/leaders.json', 'w') as f:
    json.dump(leaders, f)