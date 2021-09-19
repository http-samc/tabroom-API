import numpy as np
import requests
from bs4 import BeautifulSoup, NavigableString

from utils.const import CON, LOSS, PRO, WIN, breakNames

"""This file contains various functions used to scrape parts
of the Tabroom.com website
"""

def _clean(string: str, stripNum: bool = False, stripPeriods: bool = True) -> str:
    """Removes tabs, periods, newlines, nums (opt) from a string

    Args:
        string (str): string to clean
        stripNum (bool): whether or not to remove numbers. Defaults to False.
        stripPreiods (bool) whether or not to remove periods. Defaults to True.
    Returns:
        str: cleaned version of string
        None: if string had no characters
    """
    if stripNum: string = ''.join([i for i in string if not i.isdigit()])
    string = string.replace('\n', '').replace('\t', '').replace('(', ' (')
    if stripPeriods: string = string.replace('.', '')
    string = string.replace('  ', ' ')

    return string if string != "" else None

def _adjScores(x: list, outlierConstant: float = 2) -> list:
    """Filters a list by removing outliers

    Args:
        x (list): the list to filter
        outlierConstant (float, optional): what value used to determine outlier status. Defaults to 2.

    Returns:
        list: the outlier-filtered list
    """
    a = np.array(x)
    upper_quartile = np.percentile(a, 75)
    lower_quartile = np.percentile(a, 25)
    IQR = (upper_quartile - lower_quartile) * outlierConstant
    quartileSet = (lower_quartile - IQR, upper_quartile + IQR)
    resultList = []
    for y in a.tolist():
        if y >= quartileSet[0] and y <= quartileSet[1]:
            resultList.append(y)
    return resultList

# breaks() and bracket() return the same schema from different pages - use one or the other
# depending on what the tournament has published (prefer breaks)

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
        RETURN SCHEMA:
        {
            <(str) team code> : [
                <(int) roundPrestige [num of break rounds debated]>,
                <(str) name of final break round debated as provided>,
                <(str) name of final break round debated, standardized>
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

def breaks(URL: str) -> dict:
    """Parses the final places page of a tournament

    Args:
        URL (str): the URL of the final places page of a certain division

    Returns:
        dict: a dict containing the parsed break round data

        RETURN SCHEMA:
        {
            <(str) team code> : [
                <(int) roundPrestige [num of break rounds debated]>,
                <(str) name of final break round debated as provided>,
                <(str) name of final break round debated, standardized>
            ],
            ...
        }
    """
    data = {}

    # Getting page and setting up parser
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, "html.parser")

    # Getting all rows except for the first header
    table = soup.find('table') # only gets break rounds table
    rawData = table.find_all("tr")
    rawData = rawData[1:len(rawData)]

    # Storing as list initially
    teams = []

    for element in rawData:

        rawEntryData = element.find_all("td")
        textData = []

        for node in rawEntryData:
            nodeText = node.get_text().replace('\t','').split('\n')
            textData.append(nodeText)

        try:
            struct = {
                'code' : _clean(textData[1][1]),
                'break' : textData[0][1]
            }
            teams.append(struct)

        except Exception as e:
            print(e)

    i = 1
    prevIDX = 0
    while True:
        # Handle for uneven first break round (byes)
        roundEndIDX = len(teams) if pow(2, i) > len(teams) else pow(2, i)

        # Get team data
        teamsElim = teams[prevIDX:roundEndIDX]
        for team in teamsElim:
            if team["code"] is None: # Blank col
                continue
            data[_clean(team["code"])] = [
                i, # what break round it was (finals = 1, ...)
                team["break"], # provided round name
                breakNames[i-1] # std round name
            ]

        # Break if we evenly filled the exponential growth
        if roundEndIDX == len(teams): break

        # Preparing for next iter
        i += 1
        prevIDX = roundEndIDX

    currI = i + 1 # Helps us reorganize

    # Reorganizing to include roundPrestige
    for team in data:
        data[team][0] = currI - data[team][0]

    return data

def entry(URL: str) -> dict:
    """Returns the results from a team's individual entry page

    Args:
        URL (str): the URL of a team's entry page

    Returns:
        dict: contains team code, full names, prelim records,
            break round data, opponent names,
            decision data, speaker point data

            RETURN SCHEMA:
            {
                "code" : <(str) entry's team code>,
                "names" : <(str) both partner's full names, separated by an '&'>,
                "prelimRecord" : [
                    <(int) prelim wins (incl. byes)>,
                    <(int) prelim losses>
                ],
                "debatedPrelims" : <(int) the number of debated (non-bye) preliminary rounds>, # used in OPwpm calculation
                "elimIn" : <(str) nonstandardized final break round ["prelim" if none]>
                "speaks" : [
                    {
                        "name" : <(str) speaker's name>,
                        "rawAVG" : <(float) [round: 2 dec.] the mean of each prelims's speaks>,
                        "adjAVG" : <(float) [round: 2 dec.] the adjusted mean of each prelims's speaks>, # removes outliers
                    },
                    {
                        "name" : <(str) speaker's name>,
                        "rawAVG" : <(float) [round: 2 dec.] the mean of each prelims's speaks>,
                        "adjAVG" : <(float) [round: 2 dec.] the adjusted mean of each prelims's speaks>, # removes outliers
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
            ''' If there was no opponent, all keys will be null except for the round name, side (-> bye), & win (-> True) '''
            {
                "round" : <(str) round name>,
                "win" : <(bool) whether or not the team won {null if draw}>,
                "side" : <(str) what side the team was on -> PRO or CON>,
                "opp" : <(str) opponent's team code>,
                "decision" : [
                    <(int) numBallotsWon>,
                    <(int) numBallotsLost>
                ]
            },
    """
    # Getting page and setting up parser
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, 'html.parser')

    # Getting Team Attrs
    code = _clean(soup.find("h2").get_text())
    nodes = (soup.find_all("h4"))
    if len(nodes) > 3:
        names = _clean(nodes[3].get_text()).replace("&", " & ")
    else:
        names = _clean(nodes[2].get_text()).replace("&", " & ")

    # Creating round framework
    prelims = []
    breaks = []

    # Round counters
    numPrelims = 0 # num of "real" non-bye prelims
    prelimRecord = [0, 0] # running prelim record

    # Getting round names and appending to appropriate list
    rows = soup.find_all(class_="row")

    for row in rows:
        meta = row.find_all(class_="tenth")

        # Getting round name and figuring out if it's a break round
        roundName = _clean(meta[0].get_text())
        isBreak = False if "round" in roundName.lower() else True# or "R" == roundName[0:1] else True

        # Getting side and standardizing it
        side = _clean(meta[1].get_text())
        if side in PRO: side = "PRO"
        elif side in CON: side = "CON"
        else: side = "BYE"

        # If we have a BYE -> append data with null values and go onto next iter
        if side == "BYE":
            if not isBreak: prelimRecord[0] += 1
            roundData = {"round":roundName,"win":True,"side":side,"opp":None,"decision":None}
            if isBreak: breaks.append(roundData)
            else: prelims.append(roundData)
            continue

        # Find opponent code
        opp = _clean(row.find(class_="threetenths padno").get_text()).replace('vs ', '')

        # Trimming to only include decisions
        meta = meta[2:]

        # Tabulating decisions
        decision = [0, 0]
        for node in meta:
            node = _clean(node.get_text())
            if node not in WIN and node not in LOSS: continue
            decision[0] += 1 if node in WIN else 0
            decision[1] += 1 if node in LOSS else 0

        # Determining win/loss/draw
        if decision[0] > decision[1]: win = True
        elif decision[1] > decision[0]: win = False
        else: win = None

        # Updating counters
        if not isBreak:
            if win: prelimRecord[0] += 1
            else: prelimRecord[1] += 1
            numPrelims += 1

        roundData = {
            "round" : roundName,
            "win" : win,
            "side" : side,
            "opp" : opp,
            "decision" : decision
        }

        # Appending data
        if isBreak: breaks.append(roundData)
        else: prelims.append(roundData)

    # Polling speaker data

    speakerNames = soup.find_all(class_="threefifths")
    speakerOne = _clean(speakerNames[0].get_text()) if len(speakerNames) > 1 else None
    speakerTwo = _clean(speakerNames[1].get_text()) if len(speakerNames) > 1 else None
    speakerOnePTS = []
    speakerTwoPTS = []

    speakerData = soup.find_all(class_="fifth")

    i = 0
    for score in speakerData:
        score = _clean(score.get_text(), stripPeriods=False)

        if len(score) == 1: continue
        else: score = float(score)

        if i % 2 == 0:
            speakerOnePTS.append(score)
        else:
            speakerTwoPTS.append(score)

        i += 1

    if len(speakerOnePTS) and len(speakerTwoPTS) != 0:
        # Generating raw averages
        speakerOneRAW = round(sum(speakerOnePTS)/len(speakerOnePTS), 2)
        speakerTwoRAW = round(sum(speakerTwoPTS)/len(speakerTwoPTS), 2)

        # Generating adjusted averages
        speakerOneTRIM = _adjScores(speakerOnePTS, outlierConstant=1.5)
        speakerTwoTRIM = _adjScores(speakerTwoPTS, outlierConstant=1.5)

        speakerOneADJ = round(sum(speakerOneTRIM)/len(speakerOneTRIM), 2)
        speakerTwoADJ = round(sum(speakerTwoTRIM)/len(speakerTwoTRIM), 2)
    else:
        speakerOneRAW = None
        speakerTwoRAW = None

        speakerOneADJ = None
        speakerTwoADJ = None

    data = {
        "code" : code,
        "names" : names,
        "prelimRecord" : prelimRecord,
        "debatedPrelims" : numPrelims,
        "elimIn" : breaks[0]["round"] if breaks != [] else "Prelims",
        "speaks" : [
            {
                "name" : speakerOne,
                "rawAVG" : speakerOneRAW,
                "adjAVG" : speakerOneADJ
            },
            {
                "name" : speakerTwo,
                "rawAVG" : speakerTwoRAW,
                "adjAVG" : speakerTwoADJ
            }
        ],
        "prelims" : prelims,
        "breaks" : breaks
    }

    return data

def prelims(URL: str) -> dict:
    """Parses the prelims page of a tournament

    Args:
        URL (str): the URL of the prelims page of a certain division

    Returns:
        dict: a dict containing the parsed prelim data

        RETURN SCHEMA:
        {
            <(str) team code> : {
                ''' used in condensor / master dataset merger '''
                'names' : [
                    ''' These names are what Tabroom provides and might
                    not represent the speaking order of the entry '''
                    <(str) speaker #1 last name>,
                    <(str) speaker #2 last name>
                ],
                'entryPage' : <(str) URL of the team's entry page; can be used with entry()>,
                'prelimWins' : <(int) number of prelim wins>, ''' used for cross verification with entry() '''
                ''' used as a statistic '''
                'prelimRank' : [
                    <(int) position>,
                    <(int) total entries>
                ]
            }
        }
    """
    data = {}

    # Getting page and setting up parser
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, "html.parser")

    # Getting all rows except for the first header
    rawData = soup.find_all("tr")
    rawData = rawData[1:len(rawData)]

    # Getting number of entries
    numEntries = len(rawData)

    for r, element in enumerate(rawData, start = 1):

        rawEntryData = element.find_all("td")
        textData = []

        entryPage = "https://www.tabroom.com" + rawEntryData[1].find("a")['href']

        for node in rawEntryData:
            nodeText = node.get_text().replace('\t','').split('\n')
            textData.append(nodeText)
        try:
            code = _clean(textData[2][2])
            data[code] = {
                'names' : textData[1][2].replace(' ', '').split('&'),
                'entryPage' : entryPage,
                'wins' : int(textData[0][1]),
                'prelimRank' : [r, numEntries]
            }

        except Exception as e:
            print(e)

    return data

def prelimSeeds(URL: str) -> dict:
    """Parses the prelim seeds page of a tournament

    Args:
        URL (str): the URL of the prelim seeds page of a certain division

    Returns:
        dict: a dict containing the parsed prelim data

        RETURN SCHEMA:
        {
            <(str) team code> : [
                <(int) prelim rank>,
                <(int) total # of prelim teams>
            ],
            ...
        }
    """
    data = {}

    # Getting page and setting up parser
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, "html.parser")

    # Getting all rows except for the first header
    rawData = soup.find_all("tr")
    rawData = rawData[1:len(rawData)]

    # Getting number of entries
    numEntries = len(rawData)

    for r, element in enumerate(rawData, start = 1):

        rawEntryData = element.find_all("td")
        textData = []

        for node in rawEntryData:
            nodeText = node.get_text().replace('\t','').split('\n')
            textData.append(nodeText)
        try:
            pos = int(textData[0][1])
            code = textData[1][1]
            data[code] = [pos, numEntries]


        except Exception as e:
            print(e)

    return data

def name(URL: str) -> str:
    """Scrapes the name of a tournament

    Args:
        URL (str): the homepage URL of a Tabroom tournament

    Returns:
        str: the name of the tournament
    """

    r = requests.get(URL)
    soup = BeautifulSoup(r.text, 'html.parser')

    name = soup.find(class_="centeralign marno").get_text()

    return _clean(name)[:-1]

if __name__ == "__main__":
    prelimData = prelimSeeds("https://www.tabroom.com/index/tourn/results/event_results.mhtml?tourn_id=20446&result_id=187440")
    print(prelimData)