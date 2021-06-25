import json

import requests
from bs4 import BeautifulSoup, NavigableString, Tag

if __name__ == "__main__":
    from const import size, breakNames
else:
    from utils.const import size, breakNames

"""This file contains various functions used to scrape parts
of the Tabroom.com website
"""

def _clean(string: str, stripNum: bool = False) -> str | None:
    """Removes tabs, periods, newlines, nums (opt) from a string

    Args:
        string (str): string to clean
        stripNum (bool): whether or not to remove numbers. Defaults to False.

    Returns:
        str: cleaned version of string
        None: if string had no characters
    """
    if stripNum: string = ''.join([i for i in string if not i.isdigit()])
    string = string.replace('\n', '').replace('\t', '').replace('.', '').replace('(', ' (')

    return string if string != "" else None

def bracket(URL: str) -> dict:
    """Scrapes a Tabroom bracket as an HTML table & returns
    a dict that contains a set of keys representing team names,
    with each value representing a list containing the number
    of break rounds they debated (starts at 1) (equals roundPrestige
    factor), the name of that break round as designated by the
    tournament, and the name of that break round as designated by
    our own standardized convention.

    Args:
        URL (str): the URL to the Tabroom bracket page

    Returns:
        dict: as described with the following {example} schema:
        {
            "TEAM AB" : [
                1,
                "Triples (64)",
                "Triples"
            ],
            "TEAM BC" : [
                3,
                "Octafinals (16)",
                "Octafinals"
            ],
            ...
        }
    """
    data = {}

    # Getting page and setting up parser
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, 'html.parser')

    table = soup.find("table") # Bracket

    # Get round names
    roundNames = []
    rounds = table.find("tr") # There are multiple rows, but 1st one is the header w/ names
    for round in rounds:
        if not isinstance(round, NavigableString):
            roundNames.append(_clean(round.get_text()))

    # Calculate number of break rounds
    numBreaks = len(roundNames)

    # Get all rows in table
    rows = table.find_all("tr")[1:] # Skip idx 0 because it only has round names

    # Calculate number of teams broken (used later to eliminate "champion" column)
    numBroken = len(rows)

    # Loop through all the rows
    for row in rows:
        cols = row.find_all("td") # all the columns in the row

        i = 0
        for col in cols:
            code = _clean(col.get_text(), stripNum=True)
            if not code: continue

            if 'rowspan' in col.attrs and int(col['rowspan']) > numBroken:
                numBreaks -= 1
                print(numBreaks)
                continue

            if code not in data: data[code] = i
            data[code] = i if i > data[code] else data[code]
            i += 1

    # Condensing data & calculating additional information
    for team in data:
        breakRoundsDebated = data[team] + 1
        tournRoundName = roundNames[data[team]]
        stdRoundName = breakNames[numBreaks - breakRoundsDebated]

        data[team] = [
            breakRoundsDebated,
            tournRoundName,
            stdRoundName
        ]

    return data

if __name__ == "__main__":
    from pprint import pprint
    pprint(bracket("https://www.tabroom.com/index/tourn/results/bracket.mhtml?tourn_id=16768&result_id=160238"))