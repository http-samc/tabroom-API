from shared.const import API_BASE

import requests
import meilisearch
import os

client = meilisearch.Client(
    os.environ['MEILISEARCH_URL'], os.environ['MEILISEARCH_KEY'])

# TODO: Add more indicies for Tournaments, Schools, etc.
optedOutUuids = list(map(lambda u: u['uuid'], requests.get(f"{API_BASE}/opted-out-uuids").json()))

def configure_index(index):
    index.update_filterable_attributes([
        'scopes.circuitId',
        'scopes.seasonId',
        'scopes.circuitIdSeasonId'
    ])

    index.delete_all_documents()


def update_team_index():
    index = client.index("teams")

    configure_index(index)

    teams = requests.post(f"{API_BASE}/teams/advanced/findMany", json={
        "include": {
            "aliases": {
                "select": {
                    "code": True
                }
            },
            "rankings": {
                "select": {
                    "circuitId": True,
                    "seasonId": True
                }
            }
        }
    }).json()

    teams = list(map(lambda t: {
        'id': t['id'],
        'search': list(map(lambda a: a['code'], t['aliases'])),
        'scopes': list(map(lambda r: {
            'circuitId': r['circuitId'],
            'seasonId': r['seasonId'],
            'circuitIdSeasonId': f"{r['circuitId']}_{r['seasonId']}"
        }, t['rankings']))
    } if t['id'] not in optedOutUuids else None, teams))

    index.update_documents(list(filter(lambda t: t != None, teams)))


def update_judge_index():
    index = client.index("judges")

    configure_index(index)

    judges = requests.post(f"{API_BASE}/judges/advanced/findMany", json={
        "include": {
            "rankings": {
                "select": {
                    "circuitId": True,
                    "seasonId": True
                }
            }
        }
    }).json()

    judges = list(map(lambda t: {
        'id': t['id'],
        'search': [t['name']],
        'scopes': list(map(lambda r: {
            'circuitId': r['circuitId'],
            'seasonId': r['seasonId'],
            'circuitIdSeasonId': f"{r['circuitId']}_{r['seasonId']}"
        }, t['rankings']))
    } if t['id'] not in optedOutUuids else None, judges))

    index.update_documents(list(filter(lambda t: t != None, judges)))


def update_competitor_index():
    index = client.index("competitors")

    configure_index(index)

    competitors = requests.post(f"{API_BASE}/competitors/advanced/findMany", json={
        "include": {
            "teams": {
                "select": {
                    "rankings": {
                        "select": {
                            "circuitId": True,
                            "seasonId": True
                        }
                    }
                }
            }
        }
    }).json()

    competitors_fmt = []

    for c in competitors:
        if c['id'] in optedOutUuids:
            continue
        scopes = []
        for r in c['teams']:
            for s in r['rankings']:
                scopes.append(s)

        competitors_fmt.append({
            'id': c['id'],
            'search': [c['name']],
            'scopes': list(map(lambda s: {
                'circuitId': s['circuitId'],
                'seasonId': s['seasonId'],
                'circuitIdSeasonId': f"{s['circuitId']}_{s['seasonId']}"
            }, scopes))
        })

    index.update_documents(competitors_fmt)


if __name__ == "__main__":
    update_team_index()
    update_judge_index()
    update_competitor_index()
