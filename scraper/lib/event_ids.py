import requests

def get_event_ids(tab_tourn_id: int):
    res = requests.get(f"https://tabroom.com/api/download_data?tourn_id={tab_tourn_id}")

    for category in res.json()['categories']:
        print(f"{category['abbr']} Events")

        for i, event in enumerate(category['events']):
            print(f"\t[ {i + 1} ] {event['abbr']} ({event['id']})")

        print()

if __name__ == "__main__":
    get_event_ids(28198)