from os import listdir
from os.path import isfile, join
import json

with open("data/tournInfo.json", "r") as f:
    tInfo = json.loads(f.read())

    onlyfiles = [f for f in listdir('data/tournaments') if isfile(join('data/tournaments', f))]

for P in onlyfiles:
    PATH = 'data/tournaments/' + P
    with open(PATH, 'r') as f:
        data = json.loads(f.read())
        initialData = data

    tourn = P.replace('.json', '')

    for team in data[tourn]:
        # Only champs
        if not (data[tourn][team]["eliminated"] is None): continue

        # Only champs w/ a loss
        if data[tourn][team]["breakRecord"][1] != 0:
            data[tourn][team]["breakRecord"][0] += data[tourn][team]["breakRecord"][1]
            data[tourn][team]["breakRecord"][1] = 0

    if data == initialData: continue
    with open(PATH, 'w') as f:
        json.dump(data, f)