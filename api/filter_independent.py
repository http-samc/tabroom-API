import json

def getData():
    with open('data/team_data.json', 'r') as f:
        return json.loads(f.read())

def getNames():
    data = getData()

    last_names = []

    for team in list(data.keys()):
        tournament = list(data[team].keys())[0]
        names = data[team][tournament]["names"].replace(" ","").split("&")
        last_names.append({'team' : team, 'names' : names})

    return last_names

def getMatchingNames(target, last_names):
    matches = []
    for last_name in last_names:
        if len(last_name['names']) != 2 and len(target) != 2:
            continue

        names = last_name['names']
        
        if (target[0] in names) and (target[1] in names):
            matches.append(last_name['team'])
    
    return matches

def write(data):
    with open('data/team_data.json', 'w') as f:
        json.dump(data, f)

def main():
    data = getData()
    teams = list(data.keys())
    last_names = getNames()
    m = {}

    for team in teams:
        m[team] = data[team]

        names = data[team][list(data[team].keys())[0]]["names"].replace(" ","").split("&")
        codes = getMatchingNames(names, last_names)

        if len(codes) == 0:
            m[team] = data[team]
            continue
        
        aliases = ""
        for code in codes: # Some long blocks of non matching codes ... make sure both names match FIXME
            # TODO remove code from last_names (avoid repeats)
            aliases += code + ";"
            tournaments = list(data[code].keys())
            for tournament in tournaments:
                m[team][tournament] = data[code][tournament]
        
        m[aliases] = m[team]
        del m[team]  

    write(m)      

# with open('data/team_data.json', 'r') as f:
#     data = json.loads(f.read())

# for key in list(data.keys()):
#     if len(key.split(';')) > 4:
#         print(key)
#         s = input("0 to delete: ")
#         if s == "0":
#             del data[key]

# with open('data/team_data.json', 'w') as f:
#     json.dump(data, f)

#main()