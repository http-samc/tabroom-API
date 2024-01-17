import requests
import json

i = 0

rounds = []

while i < 10:
    rnds = requests.post("http://localhost:8080/core/v1/rounds/advanced/findMany", json={
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
