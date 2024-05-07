import requests
import json
from shared.const import API_BASE

i = 0

rounds = []

while i < 10:
    rnds = requests.post(f"{API_BASE}/rounds/advanced/findMany", json={
        "where": {
            "result": {
                "tournament": {
                    "event": "PublicForum"
                }
            }
        },
        "include": {
            "result": {
                "include": {
                    "alias": True
                }
            }
        },
        "take": 10000,
        "skip": 10000 * i
    }).json()

    for r in rnds:
        rounds.append(r)

    i += 1

with open("rounds.json", "w") as f:
    json.dump(rounds, f)
