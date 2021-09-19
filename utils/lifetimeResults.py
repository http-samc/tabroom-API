import json

import requests
from bs4 import BeautifulSoup

BASE = "https://www.tabroom.com/index/results/team_lifetime_record.mhtml?id1=&id2="

def genTabNamesAndIDs() -> dict:
    """Finds the Tabroom ID (int) of a debater
    by starting at 1128 and going up to 1,091,266, and then
    scraping the name from each page.

    Returns:
        dict: A dictionary representing pairs of Tabroom
        IDs and their real names.

        SCHEMA: {
            "<(str) Tabroom ID>": <(str) Competitor Name>,
            ...
        }
    """

    master = {}

    for i in range(1128, 1091266):
        id = str(i)
        r = requests.get(BASE+id)
        soup = BeautifulSoup(r.text, 'html.parser')
        try:
            name = soup.find_all("h4")[4].text
            name = name[1:len(name)].replace('\n','').replace('\t','')
            master[id] = name
        except:
            continue

    return master

# from csv import reader
# d = {}
# with open("t.csv", 'r') as f:
#     c = reader(f)

#     for row in c:
#         d[row[1]] = row[0]

# with open("tabIDs.json", 'w') as f:
#     json.dump(d, f)