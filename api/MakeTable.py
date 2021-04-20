# import json

# with open('data/team_data.json', 'r') as f:
#     data = json.loads(f.read())

# teams = list(data.keys())

# m = {}

# for team in teams:

#     tournaments = list(data[team].keys())

#     wins = 0
#     losses = 0 
#     win_pct = None

#     numTournaments = len(tournaments)

#     for tournament in tournaments:

#         names = data[team][tournament]["names"]
#         record = data[team][tournament]["record"].split('-')

#         wins += int(record[0])
#         losses += int(record[1])


#         win_pct = float(str(float(100*wins/(losses+wins)))[0:4])

#     m[win_pct] = {
#         "team" : team,
#         "wins" : wins,
#         "losses" : losses,
#         "win_pct" : win_pct,
#         "numTournaments" : numTournaments
#     }

# with open('t.json', 'w') as f:
#     json.dump(m, f)

from json2html import *

data = {
    "BASIS Independent Silicon Valley AV / BASIS Independent Silicon Valley VA / BISV AV / ": {
        "Alta Silver and Black Invitational": {
            "names": "Agarwal & Vellore ",
            "record": "4-2",
            "break round": "Quarter",
            "ranking": 7,
            "speaks": [{
                    "name": "Vinay Vellore",
                    "total points": 117.33,
                    "ranking": "11"
                },
                {
                    "name": "Ayush Agarwal",
                    "total points": 115.87,
                    "ranking": "36"
                }
            ]
        }
    }
}

print(json2html.convert(json=data))