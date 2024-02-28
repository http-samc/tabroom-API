import time
import requests
API_BASE = "http://localhost:8080/core/v1"

rankings = requests.post(f"{API_BASE}/rankings/teams/advanced/findMany", json={
    "include": {
        "team": {
            "include": {
                "bids": True
            }
        },
        "circuit": True
    }
}).json()

i = 0

print(len(rankings))

for ranking in rankings:
    print(i)
    i += 1
    level = (ranking['circuit']['classification'])
    bids = ranking['team']['bids']

    if len(bids) == 0 or level != "Varsity":
        continue
    total = 0
    for bid in bids:
        if bid['value'] == "Full":
            total += 1
        else:
            total += 0.5

    requests.patch(f"{API_BASE}/rankings/teams/{ranking['id']}", json={
        "bids": total
    })

# print(len(rankings))

# rankings = requests.get(f"{API_BASE}/rankings/judges").json()
# print(len(rankings))
# for ranking in rankings:
#     rounds = requests.post(f"{API_BASE}/judge-records/advanced/findMany", json={
#         "where": {
#             "result": {
#                 "judgeId": ranking["judgeId"],
#                 "division": {
#                     "circuits": {
#                         "some": {
#                             "id": ranking['circuitId']
#                         }
#                     },
#                     "tournament": {
#                         "seasonId": ranking['seasonId']
#                     }
#                 }
#             }
#         },
#         "select": {
#             "decision": True,
#             "id": True
#         }
#     }).json()

#     if not len(rounds):
#         continue

#     numPro = len(list(filter(lambda r: r['decision'] == "Pro", rounds)))
#     numCon = len(list(filter(lambda r: r['decision'] == "Con", rounds)))

#     requests.patch(f"{API_BASE}/rankings/judges/{ranking['id']}", json={
#         "pctPro": numPro/(numPro + numCon)
#     })

#     print(numPro/(numPro + numCon))
#     time.sleep(0.1)
