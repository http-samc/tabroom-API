from pprint import pprint
import requests
import meilisearch

client = meilisearch.Client(
    'https://meilisearch-production-6814.up.railway.app/', '03ng9o9hltoyw8kmaf1f19zaydiwq04b')


def configure_index(index):
    index.update_filterable_attributes([
        'scopes.circuitId',
        'scopes.seasonId',
        'scopes.circuitIdSeasonId'
    ])


def update_team_index():
    index = client.index("teams")

    configure_index(index)

    teams = requests.post("http://localhost:8080/core/v1/teams/advanced/findMany", json={
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
    }, teams))

    index.update_documents(teams)


def update_judge_index():
    index = client.index("judges")

    configure_index(index)

    judges = requests.post("http://localhost:8080/core/v1/judges/advanced/findMany", json={
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
    }, judges))

    index.update_documents(judges)


def update_competitor_index():
    index = client.index("competitors")

    configure_index(index)

    competitors = requests.post("http://localhost:8080/core/v1/competitors/advanced/findMany", json={
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
