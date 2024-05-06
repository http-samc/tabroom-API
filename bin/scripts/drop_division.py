import requests
from pprint import pprint
from shared.const import API_BASE


def drop_division(division_id: int):
    res = requests.post(f"{API_BASE}/speaking/rounds/advanced/deleteMany", json={
        "where": {
            "round": {
                "result": {
                    "divisionId": division_id
                }
            }
        }
    })

    pprint(res.json())

    res = requests.post(f"{API_BASE}/judge-records/advanced/deleteMany", json={
        "where": {
            "result": {
                "divisionId": division_id
            }
        }
    })

    pprint(res.json())

    res = requests.post(f"{API_BASE}/speaking/rounds/advanced/deleteMany", json={
        "where": {
            "round": {
                "result": {
                    "divisionId": division_id
                }
            }
        }
    })

    pprint(res.json())

    res = requests.post(f"{API_BASE}/rounds/advanced/deleteMany", json={
        "where": {
            "result": {
                "divisionId": division_id
            }
        }
    })

    pprint(res.json())

    res = requests.post(f"{API_BASE}/speaking/tournaments/advanced/deleteMany", json={
        "where": {
            "result": {
                "divisionId": division_id
            }
        }
    })

    pprint(res.json())

    res = requests.post(f"{API_BASE}/bids/advanced/deleteMany", json={
        "where": {
            "result": {
                "divisionId": division_id
            }
        }
    })

    pprint(res.json())

    res = requests.post(f"{API_BASE}/results/teams/advanced/deleteMany", json={
        "where": {
            "divisionId": division_id
        }
    })

    pprint(res.json())

    res = requests.post(f"{API_BASE}/results/judges/advanced/deleteMany", json={
        "where": {
            "divisionId": division_id
        }
    })

    pprint(res.json())

    res = requests.post(f"{API_BASE}/tournaments/divisions/advanced/deleteMany", json={
        "where": {
            "id": division_id
        }
    })

    pprint(res.json())


if __name__ == "__main__":
    for i in range(236, 238):
        drop_division(i)
