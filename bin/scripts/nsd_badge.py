import requests
import csv
from shared.const import API_BASE

competitors = []

with open("nsd.csv", "r") as f:
    table = csv.reader(f)

    for row in table:
        competitors.append(row[0].lower())

teams = requests.get(f"{API_BASE}/teams?expand=competitors").json()

for team in teams:
    has_affiliate = False

    for competitor in team['competitors']:
        if competitor['name'].lower() in competitors:
            has_affiliate = True

    if not has_affiliate:
        continue

    requests.patch(f"{API_BASE}/teams/{team['id']}", json={
        "metadata": {
            "nsdAlum": True
        }
    })
