import json
import requests

matchup_2_freq = {}  # t1_t2: 3
team_to_meta = {}  # t1: School AB
team_to_freqs = {}

rounds = None

with open("rounds.json", "r") as f:
    rounds = json.loads(f.read())

for round in rounds:
    team1 = round['result']['teamId']

    if team1 not in team_to_meta:
        team_to_meta[team1] = {
            'code': round['result']['alias']['code'],
            'schoolId': round['result']['schoolId']
        }

    team2 = round['opponentId']

    if not team2:
        continue

    matchup_id = "_".join(sorted([team1, team2]))

    if matchup_id not in matchup_2_freq:
        matchup_2_freq[matchup_id] = 0

    matchup_2_freq[matchup_id] += 1

    if team1 not in team_to_freqs:
        team_to_freqs[team1] = 0
    if team2 not in team_to_freqs:
        team_to_freqs[team2] = 0

    team_to_freqs[team1] += 1
    team_to_freqs[team2] += 1

deletions = []

for matchup_id, _ in matchup_2_freq.items():
    ids = matchup_id.split("_")

    for id in ids:
        if id not in team_to_meta:
            deletions.append(matchup_id)

for deletion in deletions:
    del matchup_2_freq[deletion]

nodes = []

deletions = []

for team_id, freq in team_to_freqs.items():
    if freq < 50:
        deletions.append(team_id)

matchup_deletions = []

for deletion in deletions:
    del team_to_freqs[deletion]
    for key in matchup_2_freq:
        if deletion in key:
            matchup_deletions.append(key)

for deletion in matchup_deletions:
    if deletion in matchup_2_freq:
        del matchup_2_freq[deletion]

for team_id, meta in team_to_meta.items():
    if team_id in team_to_freqs:
        nodes.append({
            'id': team_id,
            'code': meta['code'],
            'schoolId': meta['schoolId'],
            'freq': team_to_freqs[team_id]
        })

edges = []

for matchup_id, freq in matchup_2_freq.items():
    ids = matchup_id.split("_")
    if len(ids) != 2:
        continue
    edges.append({
        "source": ids[0],
        "target": ids[1],
        "weight": freq,
    })

with open("round-network.json", "w") as f:
    json.dump({
        'nodes': nodes,
        'edges': edges
    }, f)
