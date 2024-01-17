# Event -> Geo -> Division -> Season

def get_lookup(circuits):
    event_2_geo = {}
    event_geo_2_division = {}
    event_geo_division_2_season = {}

    for circuit in circuits:
        event = circuit['event']
        geo = circuit['geo']
        division = circuit['division']
        season = circuit['season']

        if event not in event_2_geo:
            event_2_geo[event] = []

        event_2_geo[event].append(geo)

        k = f"{event}_{geo}"

        if k not in event_geo_2_division:
            event_geo_2_division[k] = []

        event_geo_2_division[k].append(division)

        j = f"{k}_{division}"

        if j not in event_geo_division_2_season:
            event_geo_division_2_season[j] = []

        event_geo_division_2_season[j].append(season)
