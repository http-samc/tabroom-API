import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from colorama import Fore
from const import DIVISIONS, REJECT

def getDivision(URL: str) -> str | None:
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

    for name in divisionData:
        # Storing orignal divisionName for return reference
        originalDivisionName = name

        # Lowering divisionName
        name = name.lower()

        # Checking autoreject
        autoreject = False
        for keyword in REJECT:
            if keyword in name: autoreject = True
        if autoreject: continue

        # Iterating through all combos of keywords
        for keywordSet in DIVISIONS:

            # Setting counter to 0
            i = 0

            # Adding every positive keyword to counter
            for keyword in keywordSet:

                if not keyword.startswith("-"):
                    i += 1

            # Iterating through all keywords
            for keyword in keywordSet:

                # Lowering keyword (to match divisionName)
                keyword = keyword.lower()

                # If negative keyword in name -> make it impossible to get counter back to 0
                if keyword.startswith("-") and keyword[1:len(keyword)] in name:
                    i += 69420

                # If keyword in name, lowering counter by 1
                elif keyword in name:
                    i -= 1

                # If all keywords in name and no negative keywords -> return the original name
                if i == 0:
                    return divisionData[originalDivisionName]

    # Manual scraping if not found
    i = 0
    print(Fore.YELLOW + "Division Not Found, Scrape Manually: ")
    for name in divisionData:
        print(f"[{i}] - {name}")
        i += 1
    choice = int(input("Enter Selection: "))

    try:
        return divisionData[choice]
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
            <(str) URL of the brackets page | None if null>
        ]
    """
    retURIs = [None, None]
    BASE = "https://www.tabroom.com"

    r = requests.get(URL)
    soup = BeautifulSoup(r.text, 'html.parser')

    resCategories = soup.find_all(class_="blue full nowrap")
    for category in resCategories:
        name = category.get_text().lower()
        if "round results" in name: continue
        if "final places" in name: retURIs[0] = BASE + category["href"]
        elif "bracket" in name: retURIs[1] = BASE + category["href"]

    return retURIs

if __name__ == "__main__": ...
    #print(rounds("https://www.tabroom.com/index/tourn/results/round_results.mhtml?tourn_id=14991&round_id=620969"))