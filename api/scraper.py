import requests
from bs4 import BeautifulSoup
from colorama import Fore
import json
import os
from scrape_by_entry import entryResults

"""
<head>
    <link href="http://json2table.com/viewer.css" rel="stylesheet">
</head>
"""
"""
Did not Scrape:
Essex (no available URL)
Ridge (Speechwire)
Jack Howe (weird tourn)
--
Scraped w/ No Data:
Cal Berkeley (no tournament in 2020 or 2021)
Capitol Beltway (not a real tournament) 
--
Scraped w/ Missing Outround Data:
Arizona State * 
Bellaire
Cavalier
UNLV * 
Blue Key * 
La Costa Canyon
Laird Lewis
Villiger
Lincoln Southwest
Millard West
Puget Sound
PLU
Dempsey Cronin
Nano Nagle
Cal State
--
MISC:
Stanny - wrong division (need TOC)
"""
class CompetitorData:

    def __init__(self, dataPath: str, keywords: list, speakers: bool) -> None:

        """
        Checks for a valid data writing path and keyword list to search for divisions

            :param: dataPath (req) (str) r/w -able PATH//TO//DATA.json
                that has a single tournaments key with a list value of URL's of tournaments,
                as seen in Tabroom
            
            :param: keywords (req) (list) made up of lists of strings. Each string in this
                list must be present in the division name to choose it as the correct division.
                Use - values in front of words to make any division that has the word in its name
                automatically get skipped. Make sure to put - keywords first in the sublist.
                Case does not matter and is auto-filtered, spelling does.

                eg. [
                    ["Public", "Forum", "Varsity"],
                    ["PF", "Varisty"],
                    ["V", "Public", "Forum"],
                    ["VPF"],
                    ["PF"],
                    ["-LD", "-CX", "-Congress"]
                ]
            
            :param: speakers (req) (bool) whether or not to poll speaker awards 
                (if false, time to parse is 1000+ % faster)
        """

        # Checking if .json exists
        if os.path.exists(dataPath):
            with open(dataPath, 'r') as f:
                self.data = json.loads(f.read())
            
            # if (not self.data["tournaments"]) or (not isinstance(self.data["tournaments"], list)):
            #     raise Exception(f"Your Tournament Data PATH ({dataPath}) isn't formatted correctly.")
        
        else:
            raise Exception(f"Your Tournament Data PATH ({dataPath}) is invalid.")
        
        # Making sure keywords are in correct format
        if not isinstance(keywords, list):
            raise Exception(f"Your Keywords List ({keywords}) is not a List.")
        
        for keywordSet in keywords:
            if not isinstance(keywordSet, list):
                raise Exception(f"Your Keywords List ({keywords}) is not a made up of Lists.")
        
        self.speakers = speakers
        self.keywords = keywords
        self.returnData = {}
    
    def scrapeAll(self) -> None:
        
        """
        Scrapes all tournaments from the dataPath .json file
        """

        self.master_data = {}

        for tournament in list(self.data.keys()):

            print(Fore.CYAN + f"Scraping: {tournament}")

            tournamentURL = self.data[tournament]["link"]
            if tournamentURL is None:
                continue
            tournamentID = tournamentURL.replace("https://www.tabroom.com/index/tourn/index.mhtml?tourn_id=", "")
            resultsURL = "https://www.tabroom.com/index/tourn/results/index.mhtml?tourn_id=" + tournamentID

            r = requests.get(resultsURL)
            soup = BeautifulSoup(r.text, "html.parser")

            divisionClass = soup.find_all(class_="threequarters")
            divisions = soup.find_all("option")

            divisionData = {}

            for division in divisions:
                divisionData[division.get_text()] = division['value']
            
            divisionName = self.parseDivisions(list(divisionData.keys()))

            if not divisionName:
                print(Fore.RED + tournament + " - Division Not Found!")
                continue
            print(Fore.GREEN + tournament + " - Found Division: " + divisionName)

            eventID = divisionData[divisionName]

            divisionURL = "https://www.tabroom.com/index/tourn/results/index.mhtml?tourn_id=" + tournamentID + "&event_id=" + eventID
            prelimURL = "https://www.tabroom.com/index/tourn/results/ranked_list.mhtml?event_id=" + eventID + "&tourn_id=" + tournamentID
            finalsURL = None
            speakerURL = None

            r = requests.get(divisionURL)
            soup = BeautifulSoup(r.text, "html.parser")

            resultCategories = soup.find_all(class_="blue full nowrap")
            for category in resultCategories:
                if ("round results" not in str(category.get_text()).lower()) and ("final places" in str(category.get_text).lower()):
                    finalsURL = "https://www.tabroom.com" + category['href']

                elif "speaker awards" in str(category.get_text()).lower():
                    speakerURL = "https://www.tabroom.com" + category['href']

            print(Fore.CYAN + f"Scraping: {tournament} (Getting Number of Prelim Rounds)")
            numPrelimRounds = self.numPrelims(tournamentURL, divisionName)
            print(Fore.CYAN + f"Scraping: {tournament} (Getting Prelim Data)")
            prelimData = self.parsePrelims(prelimURL)
            print(Fore.CYAN + f"Scraping: {tournament} (Getting Outround Data)")
            outroundData = self.parseFinals(finalsURL) if finalsURL else None
            print(Fore.CYAN + f"Scraping: {tournament} (Getting Speaker Award Data)")
            speakerAwardData = self.parseSpeaks(speakerURL) if speakerURL else None
            print(Fore.CYAN + f"Scraping: {tournament} (Getting Speaker Data)")
            speakerData = self.getSpeaks(prelimURL) if self.speakers else {}

            self.returnData = {
                "num-prelims" : numPrelimRounds,
                "prelims" : prelimData,
                "outrounds" : outroundData,
                "speaker-awards" : speakerAwardData,
                "all-speakers" : speakerData
            }

            self.master_data[tournament] = self.condenseData() if self.speakers else self.returnData
            self.updateData()
            print(Fore.CYAN + f"Scraping: {tournament} (DONE)")
               
    def updateData(self):

        with open('data/raw_data.json', 'w') as f:
            json.dump(self.master_data, f)

    def parseDivisions(self, divisionNames) -> str:
            
        """
        Uses the keywords passed in the __init__ constructor to filter through the divisions

            :param: divisionNames (req) (list) (elemType:str) all available division names on Tabroom
            :return: divisionName (str or None) the first division name to match the keywords,
                or None if none.
        """

        # This loop works by getting each sub-keyword list and initializing a counter var (i).
        # First, all the positive keywords are added to i. By the end of this step, i represents
        # the number of keywords that need to exist in the division name to allow it to pass.
        # Then, the same list is looped through, and everytime a keyword pops up in the name,
        # the counter is reduced by 1. At the end of the iteration, if i = 0 (all keywords 
        # in the sublist were found in the name) then that means the name passes and it is
        # returned. To add negative keyword functionality, if a word with the - operand is found
        # in the name, i is increased by so much (69420) that it would be impossible for the 
        # divisionName to ever get returned through 0 and have it be returned.

        # Iterating through all division names
        for name in divisionNames:
            
            # Storing orignal divisionName for return reference
            originalDivisionName = name

            # Lowering divisionName
            name = name.lower()

            if "round robin" in name or "middle" in name or "jv" in name or "novice" in name or "ms" in name or "junior varsity" in name or "npf" in name:
                continue

            # Iterating through all combos of keywords
            for keywordSet in self.keywords:
                
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
                        # print("Using KeywordSet: ")
                        # for k in keywordSet:
                        #     print(k)
                        # input()
                        return originalDivisionName
        i = 0
        print(Fore.YELLOW + "Division Not Found, Scrape Manually: ") 
        for name in divisionNames:
            print(f"[{i}] - {name}")
            i += 1
        choice = int(input("Enter Selection: "))

        try: 
            return divisionNames[choice]
        except Exception:
            return None
    @staticmethod       
    def parsePrelims(self, URL) -> dict:

        r = requests.get(URL)
        soup = BeautifulSoup(r.text, "html.parser")
        raw_data = soup.find_all("tr")
        raw_data = raw_data[1:len(raw_data)]

        tournamentData = {}

        for element in raw_data:

            raw_entry_data = element.find_all("td")
            only_text_data = []

            for tag in raw_entry_data:
                only_text_data.append(tag.get_text().replace('  ', '').replace('\t','').split('\n'))

            try:
                tournamentData[only_text_data[2][2]] = {
                    'names' : only_text_data[1][2].replace(' ', '').split('&'),
                    'wins' : int(only_text_data[0][1]),
                }
            
            except Exception:
                continue
        
        return tournamentData
    
    def parseFinals(self, URL) -> dict:

        r = requests.get(URL)
        soup = BeautifulSoup(r.text, "html.parser")
        raw_data = soup.find_all("tr")
        raw_data = raw_data[1:len(raw_data)]

        tournamentData = {}
        ranking = 1

        for element in raw_data:

            raw_entry_data = element.find_all("td")
            only_text_data = []

            for tag in raw_entry_data:
                only_text_data.append(tag.get_text().replace('  ', '').replace('\t','').split('\n'))

            try:
                tournamentData[only_text_data[1][1]] = {
                    'names' : only_text_data[2][1].replace(' ', '').split('&'),
                    'break-round' : only_text_data[0][1],
                    'ranking' : ranking
                }

                ranking += 1
            
            except Exception:
                continue

        return tournamentData

    def parseSpeaks(self, URL) -> dict:

        r = requests.get(URL)
        soup = BeautifulSoup(r.text, "html.parser")
        raw_data = soup.find_all("tr")
        raw_data = raw_data[1:len(raw_data)]

        tournamentData = {}

        for element in raw_data:

            raw_entry_data = element.find_all("td")
            only_text_data = []

            for tag in raw_entry_data:
                only_text_data.append(tag.get_text().replace('  ', '').replace('\t','').split('\n'))

            try:
                if not only_text_data[3][1] in tournamentData:
                    tournamentData[only_text_data[3][1]] = []

                tournamentData[only_text_data[3][1]].append({
                    'name' : f"{only_text_data[1][1]} {only_text_data[2][1]}",
                    'total-points' : float(only_text_data[5][1]),
                    'ranking' : only_text_data[0][1]
                })
            
            except Exception:
                continue

        return tournamentData

    def getSpeaks(self, URL) -> dict:

        r = requests.get(URL)
        soup = BeautifulSoup(r.text, "html.parser")
        raw_data = soup.find_all("tr")
        raw_data = raw_data[1:len(raw_data)]

        tournamentData = {}
        entry_report_objs = {}

        for element in raw_data:
            
            try: 
                entry_metadata = element.find_all("td")
                
                entry_link = "https://www.tabroom.com" + entry_metadata[2].find("a")['href']
                entry_code = entry_metadata[2].get_text().replace('\n', '').replace('\t','').replace('  ', '')

                entry_report_objs[entry_code] = entry_link
            
            except Exception:
                continue
        
        for obj in entry_report_objs:
            
            try: 
                entry_report_url = entry_report_objs[obj]
                r = requests.get(entry_report_url)
                soup = BeautifulSoup(r.text, 'html.parser')

                entry_names = soup.find(class_='nospace semibold')
                entry_names = entry_names.get_text().replace('\n', '').replace('\t','').split('&')

                round_speaks = soup.find_all(class_='fifth marno')
                entry_speaks = []

                for round_speak in round_speaks:
                    entry_speaks.append(float(round_speak.get_text().replace('\n', '').replace('\t','')))
                
                debater_1_speaks = entry_speaks[::2]
                debater_2_speaks = entry_speaks[1::2]

                debater_1_avg = round(sum(debater_1_speaks)/len(debater_1_speaks), 2)
                debater_2_avg = round(sum(debater_2_speaks)/len(debater_2_speaks), 2)

                tournamentData[obj] = {
                    entry_names[0] : debater_1_avg,
                    entry_names[1] : debater_2_avg
                }
            
            except Exception:
                continue
        
        return tournamentData

    def numPrelims(self, URL, divisionName):

        tournamentID = URL.replace('https://www.tabroom.com/index/tourn/index.mhtml?tourn_id=', '')

        BASEURL = "https://www.tabroom.com/index/tourn/results/index.mhtml?tourn_id=" + tournamentID

        r = requests.get(BASEURL)

        soup = BeautifulSoup(r.text, "html.parser")

        response = soup.find_all(class_="threequarters")
        divisions = soup.find_all("option")

        divisionData = {}

        for division in divisions:
            divisionData[division.get_text()] = division['value']

        divisionNames = list(divisionData.keys())
        
        if divisionName:

            eventID = divisionData[divisionName]


            divisionURL = "https://www.tabroom.com/index/tourn/results/index.mhtml?tourn_id=" + tournamentID + "&event_id=" + eventID
            
            r = requests.get(divisionURL)
            soup = BeautifulSoup(r.text, "html.parser")
            
            resultCategories = soup.find_all(class_="blue full nowrap")

            numPrelims = 0

            for category in resultCategories:
                if any(char.isdigit() for char in category.get_text()) and "x" not in category.get_text():
                    numPrelims += 1
            
            return numPrelims

    def condenseData(self) -> dict:

        prelim_data = self.returnData['prelims']
        outround_data = self.returnData['outrounds']
        top_speaker_data = self.returnData['speaker-awards']
        speaker_data = self.returnData['all-speakers']

        teams = list(prelim_data.keys())

        formatted_data = {}

        for team in teams:
            
            result = {}

            names = list(speaker_data[team].keys()) if team in speaker_data else team
            result['names'] = names[0] + " & " + names[1]

            result['prelim-wins'] = prelim_data[team]['wins']
            
            result['break-round'] = outround_data[team]['break-round'] if team in outround_data else 'prelims'
            result['ranking'] = outround_data[team]['ranking'] if team in outround_data else 'prelims'

            result['speaks'] = speaker_data[team] if team in speaker_data else None
            result['speaker-awards'] = top_speaker_data[team] if team in top_speaker_data else None

            formatted_data[team] = result

        return formatted_data
d = CompetitorData.parsePrelims("", "https://www.tabroom.com/index/tourn/results/ranked_list.mhtml?event_id=153766&tourn_id=16714")
with open('ta.json', 'w') as f:
    json.dump(d,f )
# PATH = 'data/tournament_info_for_parsing.json'
# KEYWORDS = [['TOC', 'Public', 'Forum'], ['VPF'], [' v ', ' pf'], ['varsity', 'public'], ['PF'], ['Varsity', 'PF'], ['Open', 'PF'], ['O', 'PF']]

# c = CompetitorData(PATH, KEYWORDS, True)
# c.scrapeAll()

def condense_data():
    m = {}
    with open('data/raw_data.json', 'r') as f:
        data = json.loads(f.read())

    tournaments = list(data.keys())

    for tournament in tournaments:

        numPrelims = data[tournament]["num-prelims"]

        teams = list(data[tournament]["prelims"].keys())
        speaker_awards = data[tournament]["speaker-awards"]

        m[tournament] = {}

        for team in teams:

            wins = data[tournament]["prelims"][team]["wins"]
            names = data[tournament]["prelims"][team]["names"]
            name_str = ""

            for name in names:
                name_str += name + " & "
            
            name_str = name_str[:-2]

            if data[tournament]["outrounds"] is not None:
                try:
                    break_round = data[tournament]["outrounds"][team]["break-round"]
                    rank = data[tournament]["outrounds"][team]["ranking"]
                except Exception:
                    break_round = None
                    rank = None
            else:
                break_round = None
                rank = None
            
            speaker = None

            if data[tournament]["speaker-awards"] is not None:

                if team in data[tournament]["speaker-awards"]:
                    speaker = data[tournament]["speaker-awards"][team]

            team_data = {
                "names" : name_str,
                "record" : f"{wins}-{numPrelims-wins}",
                "break-round" : break_round,
                "ranking" : rank,
                "speaker-awards" : speaker
            }

            m[tournament][team] = team_data

    with open('data/tournament_data2.json', 'w') as f:
        json.dump(m, f)
#condense_data()

def team_data():

    with open('data/tournament_data.json', 'r') as f:
        data = json.loads(f.read())
    
    tournaments = list(data.keys())

    m = {}

    for tournament in tournaments:

        teams = list(data[tournament].keys())

        for team in teams:

            if team not in m:
                m[team] = {}
            
            m[team][tournament] = data[tournament][team]
    
    with open('data/team_data.json', 'w') as f:
        json.dump(m, f)

    #filter_independent.main()

#team_data()

# def merge():
#     with open('data/tournament_data.json', 'r') as f:
#         og = json.loads(f.read())

#     with open('data/tournament_data2.json', 'r') as f:
#         data = json.loads(f.read())
    
#     for tournament in list(data.keys()):
#         og[tournament] = data[tournament]
    
#     with open('data/tournament_data.json', 'w') as f:
#         json.dump(og, f)
# #merge()

def numTeams():
    with open('data/team_data.json', 'r') as f:
        data = json.loads(f.read())

    print(len(list(data.keys())))