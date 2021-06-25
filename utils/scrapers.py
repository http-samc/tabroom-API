import json

import requests
from bs4 import BeautifulSoup, NavigableString, Tag

if __name__ == "__main__":
    from const import (size, breakNames, WIN, LOSS, PRO, CON)
else:
    from utils.const import (size, breakNames, WIN, LOSS, PRO, CON)

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
    string = string.replace('Jesuit', 'Jesuit ').replace('vs ', '')

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
        for col in cols: # Not using enumerate() - more lines required
            code = _clean(col.get_text(), stripNum=True) # get text & remove seed nums
            if not code: continue # Skip if we don't have a team at this pos

            # If our rowspan is larger than our numBroken we have a "champion" col to skip
            if 'rowspan' in col.attrs and int(col['rowspan']) >= numBroken:
                numBreaks -= 1
                continue

            if code not in data: data[code] = i # Create key if DNE
            data[code] = i if i > data[code] else data[code] # Overwrite if current col >
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

def entry(URL: str) -> dict:
    """Returns the results from a team's individual entry page

    Args:
        URL (str): the URL of a team's entry page

    Returns:
        dict: contains team code, full names, prelim records,
            break round data, opponent names, judge data,
            decision data, speaker point data

            RETURN SCHEMA:
            {
                "code" : <(str) entry's team code>,
                "names" : <(str) both partner's full names, separated by an '&'>,
                "speaks" : [
                    ''' We do not include outround speaks since they are rarely provided & skew sample sizes '''
                    {
                        "name" : <(str) speaker's name>,
                        "rawAVG" : <(float) [round: 3 dec.] the mean of each prelims's speaks>,
                        "adjAVG" : <(float) [round: 3 dec.] the adjusted mean of each prelims's speaks>, # removes outliers
                    },
                    {
                        "name" : <(str) speaker's name>,
                        "rawAVG" : <(float) [round: 3 dec.] the mean of each prelims's speaks>,
                        "adjAVG" : <(float) [round: 3 dec.] the adjusted mean of each prelims's speaks>, # removes outliers
                    }
                ],
                "prelims" : [
                    <variable number of round dictionaries>
                ],
                "breaks" : [
                    <variable number of round dictionaries>
                ]
            }

            ROUND SCHEMA:
            ''' If there was no opponent, all keys will be null except for the round name & win (-> True) '''
            {
                "round" : <(str) round name>,
                "win" : <(bool) whether or not the team won {null if draw}>,
                "side" : <(str) what side the team was on -> PRO or CON>,
                "opp" : <(str) opponent's team code>,
                "decision" : [
                    <(int) numBallotsWon>,
                    <(int) numBallotsLost>
                ],
                "judges" : [
                    {
                        "name" : <(str) name of judge>,
                        "profile" : <(str) URL to judge's tabroom profile>
                    },
                    ...
                ]
            },
    """
if __name__ == "__main__":
    from pprint import pprint
    pprint(bracket("https://www.tabroom.com/index/tourn/results/bracket.mhtml?tourn_id=16768&result_id=160238"))