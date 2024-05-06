import math
import requests
from shared.const import API_BASE
from requests_cache import DO_NOT_CACHE, CachedSession
requests = CachedSession(expire_after=DO_NOT_CACHE)

def get_otr_deflator(numTourns: int) -> float:
    """Gets the amount to deflate a raw OTR average by given the number of tournaments attended.

    Args:
        numTourns (int): The number of tournaments attended.

    Returns:
        float: The proportion of the original OTR that should be retained (from [0, 1)).
    """
    N = 1
    Y0 = 0.15  # g
    K = 1.3

    return round(N/((N/Y0 - 1)*math.pow(math.e, -K*numTourns) + 1), 2)


def update_otrs(tab_event_id: int) -> None:
    """Updates all OTRs for all entries in an event (tab_event_id).

    Args:
        tab_event_id (int): The unique ID assigned to the event, visible in the `event_id` query parameter.
    """

    # Get all teamIds participating and the season + all circuits in scope
    # lprint("Getting teams")
    # teams = list(map(lambda t: t['id'], requests.get(
    #     f"{API_BASE}/teams").json()))

    event = requests.post(f'{API_BASE}/tournaments/divisions/advanced/findUnique', json={
        'where': {
            'tabEventId': tab_event_id
        },
        'select': {
            'teamResults': {
                'select': {
                    'teamId': True
                }
            },
            'circuits': {
                'select': {
                    'id': True
                }
            },
            'tournament': {
                'select': {
                    'seasonId': True
                }
            }
        }
    }).json()

    circuits = list(map(lambda c: c['id'], event['circuits']))
    season = event['tournament']['seasonId']
    # circuits = [25, 26, 27, 28, 29, 30, 31, 32, 33, 34]
    # season = 16
    teams = list(map(lambda r: r['teamId'], event['teamResults']))

    for circuit in circuits:
        print(f"Circuit {circuit}")
        for i, team in enumerate(teams):
            print(f"{i+1}/{len(teams)} {team}")
            results = requests.post(f'{API_BASE}/results/teams/advanced/findMany', json={
                'where': {
                    'teamId': team,
                    'division': {
                        'circuits': {
                            'some': {
                                'id': circuit
                            }
                        },
                        'tournament': {
                            'seasonId': season
                        }
                    },
                },
                'select': {
                    'otrComp': True
                }
            }).json()

            if not len(results):
                continue

            otrs = list(map(lambda r: r['otrComp'], results))
            updated_otr = get_otr_deflator(len(otrs)) * sum(otrs)/len(otrs)

            rankings_res = requests.post(f'{API_BASE}/rankings/teams/advanced/upsert', json={
                'where': {
                    'teamId_circuitId_seasonId': {
                        'teamId': team,
                        'seasonId': season,
                        'circuitId': circuit
                    }
                },
                'create': {
                    'team': {
                        'connect': {
                            'id': team
                        }
                    },
                    'season': {
                        'connect': {
                            'id': season
                        }
                    },
                    'circuit': {
                        'connect': {
                            'id': circuit
                        }
                    },
                    'otr': updated_otr
                },
                'update': {
                    'otr': updated_otr
                }
            })


if __name__ == "__main__":
    update_otrs(242828)
