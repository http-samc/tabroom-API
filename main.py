from utils.generator import getTournamentData
from colorama import Fore
import json
from utils.scrapers import *
from utils.const import BOOSTS

def scrapeAll():
    "Driver for the generator function - scrapes all listed tournaments"
    with open("data/tournInfo.json", 'r') as f:
        data = json.loads(f.read())
    for tournament in data:
        if data[tournament]["done"]: continue # skip scraped tournaments

        # find boost factor
        bidLevel = data[tournament]["bidLevel"]
        tournamentBoost = BOOSTS[bidLevel]

        print(Fore.CYAN + "Scraping: " + tournament)
        getTournamentData(data[tournament]["link"], tournamentBoost)
        print(Fore.GREEN + "Scraped: " + tournament)

if __name__ == "__main__":
    scrapeAll()
    import utils.merge # check for bye conflicts and merge
    import utils.checkGhostBid # check for ghost bids

    import utils.db 
    import utils.makeBidList
    # these are only available on Sam's local machine
    # it's used to push to the MongoDB that runs the frontend and update the Bid List
    # , so the keys within it are kept private to keep trolls out

    import utils.refreshServersideLeaderboard
    # this is also only available on Sam's local machine
    # it's used to hit a private endpoint to refresh the leaderboard rankings
    # this takes a lot of CPU power so it isn't made public to avoid trolls