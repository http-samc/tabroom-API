import statistics
import requests
from requests_cache import DO_NOT_CACHE, CachedSession
requests = CachedSession(expire_after=DO_NOT_CACHE)

API_BASE = 'http://localhost:8080'

# Update all indicies given a tab tourn id to get judges from


def update_indicies(tab_event_id: int):
    """_summary_

    Args:
        tab_event_id (int): _description_
    """

    # TODO: Abstract
    event = requests.post(f'{API_BASE}/core/v1/tournament-divisions/advanced/findUnique', json={
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

    judges = requests.post(f'{API_BASE}/core/v1/judges/advanced/findMany', json={
        'where': {
            'results': {
                'some': {
                    'division': {
                        'tabEventId': tab_event_id
                    }
                }
            }
        }
    }).json()

    # print(f"Found {len(judges)} who judged at {tab_event_id}")

    for circuit in circuits:
        speaking_aggregation = requests.post(f'{API_BASE}/core/v1/speaking/rounds/advanced/aggregate', json={
            "where": {
                "round": {
                    "result": {
                        "division": {
                            "circuits": {
                                "some": {
                                    "id": circuit
                                }
                            },
                            "tournament": {
                                "seasonId": season
                            }
                        },
                    }
                }
            },
            "_avg": {
                "points": True
            }
        }).json()

        scope_avg = speaking_aggregation['_avg']['points'] or 28.5

        for judge in judges:
            # Get all of the judge's records in scope
            records = requests.post(f'{API_BASE}/core/v1/judge-records/advanced/findMany', json={
                'where': {
                    'result': {
                        'judgeId': judge['id'],
                        'division': {
                            'tournament': {
                                'seasonId': season
                            },
                            'circuits': {
                                'some': {
                                    'id': circuit
                                }
                            }
                        }
                    },
                },
                'include': {
                    'teams': {
                        'include': {
                            'rankings': {
                                'where': {
                                    'seasonId': season,
                                    'circuitId': circuit
                                }
                            }
                        },
                    },
                    'rounds': {
                        'include': {
                            'result': True,
                            "speaking": {
                                "where": {
                                    "judgeId": judge['id']
                                }
                            }
                        }
                    }
                }
            }).json()

            screw_sum = 0
            squirrel_sum = 0
            prelims = 0
            elims = 0
            tourns = []
            rounds = 0
            speaks = []
            pro_speaks = []
            con_speaks = []
            pro_ballots = 0
            low_point_wins = 0

            for record in records:
                try:
                    if len(record['teams']) != 2:
                        continue  # Filter out bye rounds

                    if record['resultId'] not in tourns:
                        tourns.append(record['resultId'])

                    rounds += 1

                    team_1 = record['teams'][0]['id']
                    team_2 = record['teams'][1]['id']
                    team_1_result = None
                    team_2_result = None

                    team_1_speaks = []
                    team_2_speaks = []

                    for round in record['rounds']:
                        if round['result']['teamId'] == team_1:
                            team_1_result = round['result']
                        elif round['result']['teamId'] == team_2:
                            team_2_result = round['result']

                        if round['side'] == "Pro":
                            pro_ballots += 1

                        # print(round['type'])
                        if round['type'] == "Prelim":
                            prelims += 1
                        else:
                            elims += 1
                        # print(prelims, elims)

                        if round['speaking']:
                            for speak in round['speaking']:
                                points = speak['points']
                                speaks.append(points)
                                if round['side'] == "Pro":
                                    pro_speaks.append(points)
                                elif round['side'] == "Con":
                                    con_speaks.append(points)
                                if round['result']['teamId'] == team_1:
                                    team_1_speaks.append(points)
                                elif round['result']['teamId'] == team_2:
                                    team_2_speaks.append(points)

                    if len(team_1_speaks) and len(team_2_speaks):
                        team_1_speaks = statistics.mean(team_1_speaks)
                        team_2_speaks = statistics.mean(team_2_speaks)

                        if team_1_speaks > team_2_speaks and record['winnerId'] == team_2:
                            low_point_wins += 1
                        elif team_2_speaks > team_1_speaks and record['winnerId'] == team_1:
                            low_point_wins += 1

                    team_1_p_wp = team_1_result['prelimWins'] / (
                        team_1_result['prelimWins'] + team_1_result['prelimLosses'])
                    team_1_otr = record['teams'][0]['rankings'][0]['otr']
                    team_1_e_wp = None

                    team_2_p_wp = team_2_result['prelimWins'] / (
                        team_2_result['prelimWins'] + team_2_result['prelimLosses'])
                    team_2_otr = record['teams'][1]['rankings'][0]['otr']
                    team_2_e_wp = None

                    # Calculate & Assign EWP
                    wp_high = (1.2 * abs(team_1_otr - team_2_otr))**2 / \
                        statistics.mean([team_1_otr, team_2_otr]) + 0.5
                    if wp_high > 0.99:
                        wp_high = 0.99
                    wp_low = 1 - wp_high

                    if team_1_otr >= team_2_otr:
                        team_1_e_wp = wp_high
                        team_2_e_wp = wp_low
                    else:
                        team_1_e_wp = wp_low
                        team_2_e_wp = wp_high

                    # Record screw factor (if any) (only given in prelim rounds with incorrect result and otr delta of gte. 0.5)
                    screw_factor = 0

                    otr_delta = abs(team_1_otr - team_2_otr)
                    avg_otr = statistics.mean([team_1_otr, team_2_otr])

                    wpHi = ((1.47 * pow(otr_delta, 0.8094)) * (1 /
                            (4 * avg_otr))) / (1 + pow(2, -(10 - 6))) + 0.5
                    # print("WP Hi " + str(wpHi))

                    if ((record['winnerId'] == team_1 and team_1_otr < team_2_otr) or (record['winnerId'] == team_2 and team_2_otr < team_1_otr)) and record['type'] == "Prelim" and wpHi >= 0.7:
                        screw_factor = 4.5**abs(0.5 - team_1_otr) - 1
                        # print("Screw factor " + str(screw_factor))

                    for round in record['rounds']:
                        e_wp = None
                        if round['result']['teamId'] == team_1:
                            e_wp = team_1_e_wp
                        else:
                            e_wp = team_2_e_wp

                        if not e_wp:
                            ...
                            # print(round['result']['teamId'], team_1,
                           #       team_2, team_1_e_wp, team_2_e_wp)
                           # input("Err: ")

                        res = requests.post(f'{API_BASE}/core/v1/rounds/advanced/update', json={
                            'where': {
                                'id': round['id']
                            },
                            'data': {
                                'expectedWinProbability': e_wp,
                            }
                        })

                    # Update Judge Record with screw data
                    res = requests.post(f'{API_BASE}/core/v1/judge-records/advanced/update', json={
                        'where': {
                            'id': record['id']
                        },
                        'data': {
                            'screwFactor': screw_factor if round['type'] == "Prelim" else None
                        }
                    })

                    # Update counts
                    # Any nonzero screw factor counts as one screw
                    screw_sum += 1 if screw_factor > 0 else 0
                    squirrel_sum += 1 if record['wasSquirrel'] else 0

                    # print("Screw sum: " + str(screw_sum))

                except Exception as e:
                    # from pprint import pprint
                    import traceback
                    traceback.print_exc()
                    # pprint({
                    #     'where': {
                    #         'result': {
                    #             'judgeId': judge['id'],
                    #             'division': {
                    #                 'tournament': {
                    #                     'seasonId': season
                    #                 },
                    #                 'circuits': {
                    #                     'some': {
                    #                         'id': circuit
                    #                     }
                    #                 }
                    #             }
                    #         },
                    #     },
                    #     'include': {
                    #         'teams': {
                    #             'include': {
                    #                 'rankings': {
                    #                     'where': {
                    #                         'seasonId': season,
                    #                         'circuitId': circuit
                    #                     }
                    #                 },
                    #                 'results': {
                    #                     'where': {
                    #                         'division': {
                    #                             'tabEventId': tab_event_id
                    #                         }
                    #                     },
                    #                     'select': {
                    #                         'prelimWins': True,
                    #                         'prelimLosses': True
                    #                     }
                    #                 }
                    #             },
                    #         },
                    #         'rounds': {
                    #             'include': {
                    #                 'result': True
                    #             }
                    #         }
                    #     }
                    # })
                    # print(
                    #     "Index computation failed on round lookup for record " + str(record['id']))
                    # print(e.with_traceback(None))

            # Calculate and update index
            if not len(records):
                continue
            index = 10 - (13 * squirrel_sum + 7 * screw_sum)/len(records)
            if index < 0:
                index = 0
            elif index > 10:
                index = 10

            # print(screw_sum, squirrel_sum, len(records), index)

            res = requests.post(f'{API_BASE}/core/v1/rankings/judges/advanced/upsert', json={
                'where': {
                    'judgeId_circuitId_seasonId': {
                        'judgeId': judge['id'],
                        'circuitId': circuit,
                        'seasonId': season
                    },
                },
                'create': {
                    'seasonId': season,
                    'judgeId': judge['id'],
                    'circuitId': circuit,
                    'index': index,
                    'tourns': len(tourns),
                    'rounds': rounds,
                    'prelims': prelims,
                    'elims': elims,
                    'squirrels': squirrel_sum,
                    'squirrelPct': squirrel_sum/len(records),
                    'screws': screw_sum,
                    'screwPct': screw_sum/len(records),
                    'squirrelAndScrewPct': (squirrel_sum + screw_sum)/len(records),
                    'avgSpks': statistics.mean(speaks) if len(speaks) else None,
                    'stdSpks': statistics.stdev(speaks) if len(speaks) > 1 else None,
                    'pctPro': pro_ballots/len(records),
                    'lowPointWins': low_point_wins,
                    'lowPointWinPct': low_point_wins/len(records),
                    'avgProSpks': statistics.mean(pro_speaks) if len(pro_speaks) else None,
                    'avgConSpks': statistics.mean(con_speaks) if len(con_speaks) else None,
                    'saa': (statistics.mean(speaks) - scope_avg) if len(speaks) and scope_avg else None
                },
                'update': {
                    'index': index,
                    'tourns': len(tourns),
                    'rounds': rounds,
                    'prelims': prelims,
                    'elims': elims,
                    'squirrels': squirrel_sum,
                    'squirrelPct': squirrel_sum/len(records),
                    'screws': screw_sum,
                    'screwPct': screw_sum/len(records),
                    'squirrelAndScrewPct': (squirrel_sum + screw_sum)/len(records),
                    'avgSpks': statistics.mean(speaks) if len(speaks) else None,
                    'stdSpks': statistics.stdev(speaks) if len(speaks) > 1 else None,
                    'pctPro': pro_ballots/len(records),
                    'lowPointWins': low_point_wins,
                    'lowPointWinPct': low_point_wins/len(records),
                    'avgProSpks': statistics.mean(pro_speaks) if len(pro_speaks) else None,
                    'avgConSpks': statistics.mean(con_speaks) if len(con_speaks) else None,
                    'saa': (statistics.mean(speaks) - scope_avg) if len(speaks) and scope_avg else None
                }
            })

            # print(f"Upserted ranking {res.json()['id']}")


if __name__ == "__main__":
    tourns = requests.get(
        "http://localhost:8080/core/v1/tournament-divisions").json()
    for tourn in tourns:
        print(f"Updating {tourn['tabEventId']}")
        update_indicies(tourn['tabEventId'])
