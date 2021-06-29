from utils.generator import getTournamentData
from colorama import Fore
import json
from utils.scrapers import *
def scrapeAll():
    "Driver for the generator function - scrapes all listed tournaments"
    with open("data/tournInfo.json", 'r') as f:
        data = json.loads(f.read())
    for tournament in data:
        if tournament.startswith("!"): continue
        bidLevel = data[tournament]["bidLevel"]

        if bidLevel == "Octafinals":
            tournamentBoost = 2
        elif bidLevel == "Quarterfinals":
            tournamentBoost = 1.55
        elif bidLevel == "Semifinals":
            tournamentBoost = 1.25
        else:
            tournamentBoost = 1

        print(Fore.CYAN + "Scraping: " + tournament)
        getTournamentData(data[tournament]["link"], tournamentBoost)
        print(Fore.GREEN + "Scraped: " + tournament)

if __name__ == "__main__":
    scrapeAll()
