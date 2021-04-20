import json
import requests
from bs4 import BeautifulSoup

# This code is pretty rough, will be tidy soon
# These are functions I had to make to wrap the round function because 
# I was dumb enough to name vars round

def round_(float, **kwargs):
    if kwargs:
        return round(float, kwargs[0])
    return round(float)

def round_to(float, to):
    return round(float, to)

def clean(string: str):
    """
        Cleans an input string by removing tabs, newlines, and double spaces
        
        :param: string (str) (req) the string to clean
        :return: (str) the cleaned input string
    """

    return string.replace('\n', '').replace('\t', '').replace('  ', '').replace('Jesuit', 'Jesuit ').replace('vs ', '')

def entryResults(URL: str):
    """
        Returns the results from the individual entry page
            - speaker points
            - full names
            - prelim record
            - elim rounds
        /* Does NOT pull seeding and speaker awards */

    :param: URL (str) (req) the Tabroom URL of an 'entry' at a tournament
        eg. "https://www.tabroom.com/index/tourn/postings/entry_record.mhtml?tourn_id=14991&entry_id=2996682"
    :return: (dict) JSON-like representation of the data in the supplied URL with the following schema:
        {
            "<(str) team code> {
                "names" : [
                    <(str) speaker #1 full name>,
                    <(str) speaker #2 last name>
                ],
                "speaks" : [{
                    "name" : <(str) speaker full name>,
                    "avg" : <(float round:3) speaker avg>
                },
                {
                    "name" : <(str) speaker full name>,
                    "avg" : <(float round:3) speaker avg>
                }]
                "rounds" : {
                    "prelims" : [
                        <(str) round name> : {
                            "win" : <(bool) True -> entry won; False -> opp. won>,
                            "side" : <(str) Pro OR Con>,
                            "decision" : [
                                <(int) numBallots won>,
                                <(int) numBallots lost>
                            ],
                            "judges" : [
                                {
                                    "name" : <(str) name of judge>,
                                    "profile" : <(str) URL to judge's profile>
                                }
                            ]
                            "opp" : <(str) opponent>,
                            "speaks" : [
                                {
                                    "name" : <(str) speaker #1 name>,
                                    "points" : <(float) speaker #2 points (0 - 30)>
                                },
                                {
                                    "name" : <(str) speaker #1 name>,
                                    "points" : <(float) speaker #2 points (0 - 30)>
                                }
                            ]
                        }
                    ],
                    "outrounds" : [
                        <(str) round name> : {
                            "win" : <(bool) True -> entry won; False -> opp. won>,
                            "decision" : [
                                <(int) numBallots won>,
                                <(int) numBallots lost>
                            ],
                            "judges" : [
                                {
                                    "name" : <(str) name of judge>,
                                    "profile" : <(str) URL to judge's profile>
                                }
                            ]
                            "opp" : <(str) opponent>,
                            "opp-win-pct" : <(float) opp. win %>
                        }
                    ]
                }
            }
        }
    """
    # Defining constants 
    ACCEPTED_SIDES = ["pro", "con", "aff", "neg"]
    ACCEPTED_DECISIONS = ["w", "l"]

    # Vars
    speakerOneName = None
    speakerTwoName = None
    speakerOnePoints = 0
    speakerTwoPoints = 0
    speakerOneScores = []
    speakerTwoScores = []

    # Return Dataset
    master = {}

    # Getting page
    r = requests.get(URL)

    # Creating parser
    soup = BeautifulSoup(r.text, 'html.parser')

    # Get entry code
    code = soup.find('h2')
    code = code.get_text()
    code = clean(code)

    # Get entry names
    names = soup.find_all('h4')[3]
    names = names.get_text()
    names = clean(names)
    names = names.split('&')

    # Get round names
    raw_rounds = soup.find_all(class_="tenth semibold")
    rounds = []
    for round in raw_rounds:
        rounds.append(clean(round.get_text()))
    
    # Get number of rounds
    numRounds = len(rounds)

    # Get number prelim rounds
    numPrelims = 0
    loweredRounds = []
    for round in rounds:
        loweredRounds.append(round.lower())
    for round in loweredRounds:
        if "round" in round:
            numPrelims += 1
    
    # Get number of outrounds
    numOutrounds = numRounds - numPrelims

    # Getting speaker names (in order)
    entry_names = soup.find_all(class_="threefifths")
    if entry_names != []:
        speakerOneName = clean(entry_names[0].get_text())
        speakerOneName = speakerOneName.split(' ')[1] + " " + speakerOneName.split(' ')[0]

    if entry_names != []:
        speakerTwoName = clean(entry_names[1].get_text())
        speakerTwoName = speakerTwoName.split(' ')[1] + " " + speakerTwoName.split(' ')[0]

    # Getting round data
    c = 0
    round_speaker_data = soup.find_all(class_="fifth")
    for round in round_speaker_data:
        if c % 2 == 0:
            points = float(clean(round.get_text()))
            speakerOnePoints += points
            speakerOneScores.append(points)
            c += 1

        else:
            points = float(clean(round.get_text()))
            speakerTwoPoints += points
            speakerTwoScores.append(points)
            c += 1

    speakerOneAvg = round_to((speakerOnePoints/numPrelims), 3)
    speakerTwoAvg = round_to((speakerTwoPoints/numPrelims), 3)

    # Parsing Table
    table = soup.find_all(class_="row")
    tableData = {"rounds" : []}
    for row in table:

        meta = row.find_all(class_="tenth") # Has Round Name, Side, and Decision

        roundName = clean(meta[0].get_text())
        isPrelim = True if "round" in roundName.lower() else False
        side = clean(meta[1].get_text())
        decisions = []
        win = None
        oppCode = None
        judges = []

        meta = meta[2:]

        # Adding all decisions
        for decision in meta:
            c += 1
            
            decision = clean(decision.get_text())

            if decision.lower() not in ACCEPTED_DECISIONS:
                continue
            
            bool_decision = False if decision == "l" else True
            decisions.append(bool_decision)
        
        # Determining winner
        numBallotsToWin = round_((len(decisions) - 1)/2)
        
        numBallots = 0
        for decision in decisions:
            if decision is True:
                numBallots += 1

        if numBallots >= numBallotsToWin:
            win = True
        
        # Handling for even number of judges (draw)
        if ((len(decisions) - 1) % 2 == 0) and numBallots == numBallotsToWin:
            win = None
        
        decision = [numBallots, (len(decisions))-numBallots]

        meta = row.find_all(class_="white") # Has opponent and judge info
        if len(meta) != 0:
            oppCode = clean(meta[0].get_text())
        meta = meta[1:]

        for elem in meta:
            judgeName = clean(elem.get_text())
            judgeProfile = "https://www.tabroom.com/index/tourn/postings/" + elem['href']
            judges.append({
                "name" : judgeName[:-1],
                "profile" : judgeProfile
            })
        
        tableData["rounds"].append(
            {
                "name" : roundName,
                "isPrelim" : isPrelim,
                "win" : win,
                "side" : side,
                "decision" : decision,
                "judges" : judges,
                "opp" : oppCode,
            }
        )

    master[code] = {
        "names" : [
            names[0],
            names[1]
        ],
        "speaks" : [
            {
                "name" : speakerOneName,
                "avg" : speakerOneAvg,
            },
            {
                "name" : speakerTwoName,
                "avg" : speakerTwoAvg
            }
        ],
        "rounds" : {
            "prelims" : [],
            "outrounds" : []
        }
    }

    i = 0

    # Handling tournament w/o speaks
    if len(speakerOneScores) == 0:
        for _ in range(numPrelims):
            speakerOneScores.append(None)
    if len(speakerTwoScores) == 0:
        for _ in range(numPrelims):
            speakerTwoScores.append(None)


    for round in tableData["rounds"]:

        if round["isPrelim"]:
            
            # Checking to make sure index exists
            if (len(speakerOneScores)-1) >= i and (len(speakerTwoScores)-1) >= i:

                # Filtering for byes
                s_1 = speakerOneScores[i] if round["side"] != "Bye" else None
                s_2 = speakerTwoScores[i] if round["side"] != "Bye" else None
            else:
                # Adding default of 0; todo -> add filter to remove rounds from avg calc w/o speaks
                s_1 = 0
                s_2 = 0

            master[code]["rounds"]["prelims"].append(
                {
                    round["name"] : {
                        "win" : round["win"],
                        "side" : round["side"],
                        "decision" : round["decision"],
                        "judges" : round["judges"],
                        "opp" : round["opp"],
                        "speaks" : [
                            {
                                "name" : speakerOneName,
                                "points" : s_1
                            },
                            {
                                "name" : speakerTwoName,
                                "points" : s_2
                            }
                        ]
                    }
                }
            )

            i += 1 if round["side"] != "Bye" else 0
        
        else:

            master[code]["rounds"]["outrounds"].append(
                {
                    round["name"] : {
                        "win" : round["win"],
                        "side" : round["side"],
                        "decision" : round["decision"],
                        "judges" : round["judges"],
                        "opp" : round["opp"]
                    }
                }
            )

    return master

