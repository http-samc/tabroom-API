import json

import requests
from bs4 import BeautifulSoup, NavigableString, Tag

"""This file contains various functions used to scrape parts
of the Tabroom.com website
"""

def _clean(string: str) -> str:
    """Removes tabs and newlines from a string

    Args:
        string (str): string to clean

    Returns:
        str: cleaned version of string
    """
    return string.replace('\n', '').replace('\t', '')

def bracket(URL: str) -> dict:
    """Scrapes a Tabroom bracket as an HTML table & returns
    a dict that contains a set of keys representing rounds
    (from const) with each value representing the teams who
    were eliminated at that round (*finals will include both teams)

    Args:
        URL (str): the URL to the Tabroom bracket page

    Returns:
        dict: as described with the following {example} schema:
        {
            "fin" : ["TEAM AB", "TEAM CD"],
            "sem" : ["TEAM EF", "TEAM GH", ...],
            "qtr" : ["TEAM IJ", "TEAM KL", ...],
            ... ,
            "lastBreakRound" : ["TEAM !@", "TEAM #$", ...]
        }
    """
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, 'html.parser')

    table = soup.find("table")

    # Get round names
    roundNames = []
    rounds = table.find("tr")
    for round in rounds:
        if not isinstance(round, NavigableString):
            roundNames.append(_clean(round.get_text()))
    print(roundNames)

with open('utils/tournInfo.json', 'r') as f:
    data = json.loads(f.read())

for t in list(data.keys()):
    m = data[t]["meta"]
    if "oct" in m:
        data[t]["bidLevel"] = "oct"
        data[t]["meta"].replace("oct", "")
    elif "qtr" in m:
        data[t]["bidLevel"] = "qtr"
        data[t]["meta"].replace("qtr", "")
    elif "sem" in m:
        data[t]["bidLevel"] = "sem"
        data[t]["meta"].replace("sem", "")
    elif "fin" in m:
        data[t]["bidLevel"] = "fin"
        data[t]["meta"].replace("fin", "")
    else: print(t)

if __name__ != "__main__":
    (bracket("https://www.tabroom.com/index/tourn/results/bracket.mhtml?tourn_id=16776&result_id=166138"))