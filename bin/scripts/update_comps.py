from shared.const import API_BASE
import math
import requests

def get_break_boost(numElimRoundsDebated: int) -> float:
    F = 5
    D = 0.8002
    C = 3.2
    B = 0.7

    return round(F/(1+math.pow(math.e, -B*numElimRoundsDebated + C)) + D, 2)

results = requests.post(f"{API_BASE}/results/teams/advanced/findMany", json={
    # 'where': {
    #     # 'id': 56950
    #     'teamId': '78c29e42a7ff2269083daa10',
    #     'division': {
    #         'tournament': {
    #             'season': {
    #                 'year': 2024
    #             }
    #         }
    #     }
    # },
    # 'take': 5,
    'include': {
        'division': {
            'select': {
                'boost': True
            }
        }
    }
}).json()

for i, result in enumerate(results):
    print(f"Updating {i + 1}/{len(results)}")
    rxr = 0
    p_wp = result['prelimBallotsWon'] / (result['prelimBallotsWon'] + result['prelimBallotsLost'])
    break_boost = (result['elimWins'] or 0) + (result['elimLosses'] or 0) + 1
    tournament_boost = result['division']['boost'] or 1

    prelims = requests.post(f"{API_BASE}/rounds/advanced/findMany", json={
        "where": {
            "resultId": result['id'],
            'type': "Prelim",
            'opponentId': {
                'not': None
            }
        },
    }).json()

    for prelim in prelims:
        opp_result = requests.post(f"{API_BASE}/results/teams/advanced/findFirst", json={
            "where": {
                'teamId': prelim['opponentId'],
                'divisionId': result['divisionId']
            }
        }).json()

        op_pwp = opp_result['prelimBallotsWon'] / (opp_result['prelimBallotsWon'] + opp_result['prelimBallotsLost'])
        delta_pwp = op_pwp - p_wp

        if delta_pwp <= 0 or prelim['outcome'] != "Win":
            continue
        rxr += .12 * ((delta_pwp + 0.7)**16 /
                        (0.5 + (delta_pwp + 0.7)**10))**(1/2)

    otrcomp = (p_wp * break_boost * (result['opWpM'] + 0.625) * tournament_boost + rxr) / 3
    # otrcomp2 = (p_wp * get_break_boost(break_boost) * (result['opWpM'] + 0.625) * tournament_boost + rxr) / 3
    res = requests.patch(f"{API_BASE}/results/teams/{result['id']}", json={
        "otrComp": otrcomp
    })

    # print(result['id'], otrcomp1, otrcomp2, result['otrComp'])

print(f"Updated {len(results)} results.")