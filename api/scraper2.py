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

    def getSpeakerAwards(self, URL) -> dict:

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
    
    @staticmethod
    def getEntryData(URL) -> dict:

        r = requests.get(URL)
        soup = BeautifulSoup(r.text, "html.parser")
        raw_data = soup.find_all("tr")
        raw_data = raw_data[1:len(raw_data)]

        entry_report_links = []
        data = {}

        for element in raw_data:
            
            try:
                entry_metadata = element.find_all("td")
                entry_link = "https://www.tabroom.com" + entry_metadata[1].find("a")['href']

                entry_report_links.append(entry_link)
            except:
                continue
        
        for link in entry_report_links:
            try:
                entry_result = entryResults(link)
                data[list(entry_result.keys())[0]] = entry_result
            except Exception:
                print("Error parsing " + link)

        
        with open('test.json', 'w') as f:
            json.dump(data,f)

#CompetitorData.getEntryData("https://www.tabroom.com/index/tourn/results/ranked_list.mhtml?event_id=140470&tourn_id=16776")