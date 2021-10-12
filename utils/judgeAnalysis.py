import json

import requests
from bs4 import BeautifulSoup

def findJudgePoolURL(URL: str) -> str:
    """Takes the given tournament url (general) and returns
    the judge pool url for Public Forum.

    Args:
        URL (str): A general tournament url.
            eg. https://www.tabroom.com/index/tourn/index.mhtml?tourn_id=21009

    Returns:
        str: A judge pool url to be used with getParadigms().
            eg. https://www.tabroom.com/index/tourn/paradigms.mhtml?category_id=53735&tourn_id=21009
    """
    judgesURL = URL[::-1].replace('xedni', 'segduj', 1)[::-1]
    BASE = "http://tabroom.com"

    r = requests.get(judgesURL)
    soup = BeautifulSoup(r.text, 'html.parser')
    sideNote = soup.find('div', attrs={'class': 'sidenote'}).find_all('div', attrs={'title': 'name'})

    for division in sideNote:
        divisionName = str(division.find('span', attrs={'class': 'third semibold bluetext'}).text).replace('\t', '').replace('\n', '').upper()
        for divisionKWs in DIVISIONS:
            if divisionName in divisionKWs:
                divisionParadigmsURL = BASE + str(division.find('span', attrs={'class': 'third nospace padvertless'}).find('a').get('href'))
                return divisionParadigmsURL
    return None

def getParadigms(URL: str) -> list:
    """Gets the paradigms for all judges in a pool.

    Args:
        URL (str): The division-specific judge pool url.

    Returns:
        list: A list containing all judges' names, schools, and paradigms.

        SCHEMA:
        [
            {
                "name": <(str) the judge name >,
                "school": <(str) the judge's school >,
                "paradigm": <(str) the judge's paradigm >
            },
            ...
        ]
    """
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, "html.parser")

    returnData = []
    judges = soup.find_all('div', attrs = {'class': 'bordertop borderbottom'})

    for judge in judges:
        judgeDataDict = {}
        judgeDataDict['name'] = str(judge.find('span', attrs = {'class': 'threetenths semibold bluetext'}).string).replace('\t', '').replace('\n', '')
        judgeDataDict['school'] = str(judge.find('span', attrs = {'class': 'fourtenths'}).string).replace('\t', '').replace('\n', '')
        judgeDataDict['paradigm'] = str(judge.parent.find('div', attrs = {'class': 'paradigm hidden'}).text).replace('\t', '')
        returnData.append(judgeDataDict)

    return returnData

if __name__ == "__main__":
    from const import DIVISIONS
    ... # run tests inside this block ONLY
else:
    from utils.const import DIVISIONS
