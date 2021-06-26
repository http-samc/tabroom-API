import json

from colorama import Fore

from utils.condensors import condense
from utils.parsers import *
from utils.scrapers import *


def getTournamentData(URL: str, tournamentBoost: float) -> dict: # TODO get name
    """Generates all available tournament data

    Args:
        URL (str): the URL to the homepage of a Tabroom tournament
        tournamentBoost (float): the tournament-wide difficulty booster

    Returns:
        dict: the tournament data

        RETURN SCHEMA:
        {
            <(str) tournament name> : [
                <(str) team code> : {
                    "names" : <(str) full names of both members>,
                    "lastNames" : [
                        <(str) last name of 1st competitor>,
                        <(str) last name of 2nd competitor>
                    ],
                    "prelimRecord" : [
                        <(int) number of prelim wins (byes incl.)>,
                        <(int) number of prelim losses>
                    ],
                    "prelimRank" : <(int) prelim record seed rank>
                    "breakRecord : [ # None if no break
                        <(int) number of outround wins (byes incl.)>,
                        <(int) number of outround losses>
                    ],
                    "eliminated" : [ # None if championed, "Prelims" if no break
                        <(int) ballots won in final debated round>,
                        <(int) ballots lost in final debated round>,
                        <(str) name of final debated round as provided>,
                        <(str) name of final debated round, standardized>,
                        <(str) code of team lost in final debated round>
                    ],
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
                    "goldBid" : <(bool) whether or not a gold bid was acquired>,
                    "silverBid" : <(bool) whether or not a silver bid was acquired>,
                    "tournamentComp" : <(float) tournamentComp value>
                    "breakBoost" : <(int) breakBoost value>,
                    "tournamentBoost" : <(float) tournament-wide difficulty booster>
                    "OPwpm" : <(float) opponent's average win percentage>,
                }
            ],
            ...
        }
    """
    NAME = name(URL)

    ID = URL.replace("https://www.tabroom.com/index/tourn/index.mhtml?tourn_id=", "")
    RESULTS = "https://www.tabroom.com/index/tourn/results/index.mhtml?tourn_id=" + ID

    eventID = getDivision(RESULTS)

    if not eventID:
        print(Fore.YELLOW + f"Error scraping {URL}: Division Not Found!")
        return None

    # Getting const URLs
    divisionURL = "https://www.tabroom.com/index/tourn/results/index.mhtml?tourn_id=" + ID + "&event_id=" + eventID
    prelimURL = "https://www.tabroom.com/index/tourn/results/ranked_list.mhtml?event_id=" + eventID + "&tourn_id=" + ID

    # Getting variable URLs
    resultsURLs = getResultsURLs(divisionURL)
    finalsURL = resultsURLs[0]
    bracketURL = resultsURLs[1]

    # Parsing prelims
    prelimData = prelims(prelimURL)

    # Parsing each team's entry page
    entryData = {}
    for team in prelimData:
        entryData[team] = entry(prelimData[team]["entryPage"])

    # Choosing either bracket or final places page
    if finalsURL:
        resultData = breaks(finalsURL)
        print("Using final places page")
    elif bracketURL:
        resultData = bracket(bracketURL)
        print("Using bracket page")
    else:
        print(Fore.YELLOW + f"Error scraping {URL}: No result URL found!")

    rawData = {"tournamentName":NAME, "tournamentBoost": tournamentBoost, "prelimData": prelimData,
        "entryData": entryData, "resultData": resultData}
    with open(f'data/tournaments/{NAME}.json', 'w') as f:
        json.dump(rawData, f)
    data = condense(rawData)
    with open(f'data/tournaments/{NAME}.json', 'w') as f:
        json.dump(data, f)

if __name__ == "__main__":
    import time
    s = time.time()
    print(getTournamentData("https://www.tabroom.com/index/tourn/index.mhtml?tourn_id=14991", 1))
    print("Finished in " + str(time.time() - s)[0:5])
