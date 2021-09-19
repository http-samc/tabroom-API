import requests
from bs4 import BeautifulSoup
from colorama import Fore

from utils.const import DIVISIONS, REJECT


def getDivision(URL: str) -> str:
    """Finds the target division from the
    tournament results homepage

    Args:
        URL (str): a Tabroom tournament's generic results page

    Returns:
        str: name of the matching division
        None: if no division could be found
    """

    r = requests.get(URL)
    soup = BeautifulSoup(r.text, "html.parser")

    divisions = soup.find_all("option")

    divisionData = {}

    for division in divisions:
        divisionData[division.get_text()] = division['value']

    i = 0
    print(Fore.WHITE + "Choose Division: ")
    for name in divisionData:
        print(f"[{i}] - {name}")
        i += 1
    choice = int(input("Enter Selection: "))

    try:
        return divisionData[list(divisionData.keys())[choice]]
    except Exception:
        return None

def getResultsURLs(URL: str) -> list:
    """Finds appropriate result page link in the rounds section

    Args:
        URL (str): the URL of the division results page
        breaks (bool, optional): Return the link of the

    Returns:
        list: the URL of the requested page(s)

        RETURN SCHEMA:
        [
            <(str) URL of final places page | None if null>,
            <(str) URL of the brackets page | None if null>,
            <(str) URL of the prelim seeds page | None if null>,
        ]
    """
    retURIs = [None, None, None]
    BASE = "https://www.tabroom.com"

    r = requests.get(URL)
    soup = BeautifulSoup(r.text, 'html.parser')

    resCategories = soup.find_all(class_="blue full nowrap")
    for category in resCategories:
        name = category.get_text().lower()
        if "round results" in name: continue
        if "final places" in name: retURIs[0] = BASE + category["href"]
        elif "bracket" in name: retURIs[1] = BASE + category["href"]
        elif "seed" in name: retURIs[2] = BASE + category["href"]

    return retURIs

if __name__ == "__main__":
    ...