import requests
from bs4 import BeautifulSoup
import json

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
    ... # TODO implement

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
    getParadigms("https://www.tabroom.com/index/tourn/paradigms.mhtml?category_id=53735&tourn_id=21009")