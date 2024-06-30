from shared.const import API_BASE
from shared.helpers import get_tourn_boost

import requests

divisions = requests.post(f"{API_BASE}/tournaments/divisions/advanced/findMany", json={}).json()

for division in divisions:
    boost = get_tourn_boost(division['firstElimRound'])

    res = requests.patch(f"{API_BASE}/tournaments/divisions/{division['id']}", json={
        'boost': boost
    })

    print(res.status_code, boost)
