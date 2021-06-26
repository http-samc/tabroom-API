import json
from helpers import *

def condense(data: dict = None) -> dict:
    """Condenses redundant data from various scrapers
    into a single file. The redundant data exists to
    check back against the accuracy of each scraper.
    For reference, an uncondensed output from a large
    tournament can be a dict more than 30,000 lines long,
    which can be compressed by 300%, or to under 10,000 lines.
    This also calls the helper functions OPwpm (to generate OPwpm)
    and bidCalc (to calculate if performance level warranted a bid)

    Args:
        raw (dict): the uncondensed data

        ARG SCHEMA:
        {
            "tournamentName" : <(str) name of the tournament>,
            "tournamentBoost" : <(float) tournament-wide difficulty booster"
            "prelimData" : <(dict) output from prelim() scraper>,
            "entryData" : <(dict) output from entry() scraper for all teams>,
            "resultData" : <(dict) output from either breaks() or final() scraper for all teams>
        }

    Returns:
        dict: the condensed data

        RETURN SCHEMA:
        {
            <(str) tournament name> : {
                <(str) team code> : {
                    "fullNames" : <(str) full names of both members>,
                    "lastNames" : [
                        <(str) last name of 1st competitor>,
                        <(str) last name of 2nd competitor>
                    ],
                    "prelimRecord" : [
                        <(int) number of prelim wins (byes incl.)>,
                        <(int) number of prelim losses>
                    ],
                    "prelimRank" : [
                        <(int) prelim final rank>,
                        <(int) total # of prelim competitors>
                    ]
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
                    "breakBoost" : <(int) breakBoost value | None if no break>,
                    "tournamentBoost" : <(float) tournament-wide difficulty booster>
                    "OPwpm" : <(float) opponent's average win percentage>,
                },
                ...
            }
        }
    """
    # TODO gen OPwpm while entryData b4 we overwrite, write bid helpers
    with open("uncondensedTourn.json", 'r') as f:
        data = json.loads(f.read())

    name = data["tournamentName"]
    tournamentBoost = data["tournamentBoost"]

    # Starting condensed dataset
    condensed = {name: {}}

    # Adding all competitors
    prelimData = data["prelimData"]
    for team in prelimData:

        lastNames = prelimData[team]["names"]
        prelimWins = prelimData[team]["wins"]
        prelimRank = prelimData[team]["prelimRank"]

        condensed[name][team] = {
            "lastNames" : lastNames,
            "prelimRank" : prelimRank,
            "prelimWins" : prelimWins, # used as an acc check, del later
            "breakBoost" : 1, # base boost
            "tournamentBoost" : tournamentBoost
        }

    # Getting advanced individual entry stats
    entryData = data["entryData"]
    for team in entryData:
        teamData = condensed[name][team] # Shorthand for ref

        # Getting quick meta
        fullNames =  entryData[team]["names"]
        prelimRecord = entryData[team]["prelimRecord"]
        speaks = entryData[team]["speaks"]

        # Temporarily adding prelim round data
        prelims = entryData[team]["prelims"]

        # Getting break data if applicable
        if len(entryData[team]["breaks"]) != 0:

            # Getting breakRecord
            outWins = 0
            outLosses = 0

            for round in entryData[team]["breaks"]:
                decision = round["decision"]
                outWins += decision[0]
                outLosses += decision[1]

            breakRecord = [outWins, outLosses]

            # Getting final round stats
            finalRound = entryData[team]["breaks"][0] # Shorthand for final rd

            if finalRound["win"]:
                eliminated = None # They won their last outround -> championed -> never elim'd

            else: # They didn't win their final round

                decision = finalRound["decision"] # How much they lost by
                eliminated = [
                    decision[0], # final ballots won
                    decision[1], # final ballots lost
                    finalRound["round"], # final round name non std
                    finalRound["opp"] # final opponent
                ]

        else: # If they don't have any breakrounds -> elim in prelims, no breakRecord
            eliminated = "Prelims"
            breakRecord = None

        if teamData["prelimWins"] == prelimRecord[0]: # check for accuracy
            del teamData["prelimWins"] # if the two match -> delete the ref

        else:
            print("Error validating prelim wins for: " + team)

        # Updating team data
        teamData["fullNames"] = fullNames
        teamData["prelimRecord"] = prelimRecord
        teamData["speaks"] = speaks
        teamData["eliminated"] = eliminated
        teamData["breakRecord"] = breakRecord
        teamData["prelims"] = prelims

        # Merging into condensed
        condensed[name][team] = teamData

    # Calling OPwpm calculation (auto-removes unneeded temp round data)
    condensed = calcOPwpm(condensed)

    # Getting breakBoost & std name of final round
    resultData = data["resultData"]
    for team in resultData:
        teamData = condensed[name][team] # Shorthand for ref

        breakBoost = resultData[team][0] + 1 # roundPrestige + 1 = breakBoost
        finalRdSTD = resultData[team][2]

        teamData["breakBoost"] = breakBoost
        if teamData["eliminated"] is not None: # Champion was never elim
            teamData["eliminated"].insert(3, finalRdSTD)

    # Calculating bids
    condensed = calcBid(condensed)

    # Calculating tournamentComp
    condensed = calcTournamentComp(condensed)

    return condensed

if __name__ == "__main__":
    data = condense()
    with open('condense.json', 'w') as f:
        json.dump(data, f)