import requests
import json
from bs4 import BeautifulSoup
from PDF_GEN import FPDF
from colorama import Fore
import sys
import os

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def getEntries(URL) -> list:
    """
    Gets all the team codes in a tournament

    :param: URL (req) - entries section of tournament
    :return: (list) (type:str) a list of the team codes
    """
    r = requests.get(URL)

    soup = BeautifulSoup(r.text, "html.parser")
    data = soup.find_all("tr")
    teams = data[1:len(data)]

    codes = [   ]

    for team in teams:

        raw_team = team.get_text()
        raw_team = raw_team.replace('  ', '').replace('\t','').split('\n')
        team = []

        for element in raw_team:

            if element != '':

                team.append(element)

        if len(team) >= 4:
            codes.append(team[3])

    return codes

def getData():
    with open(resource_path('team_data.json'), 'r') as f:
        return json.loads(f.read())

def generatePDF(Name, URL):

    data = getData()
    teams = getEntries(URL)
    pdf = FPDF()  
    pdf.add_page()
    pdf.set_font("Times", size = 12) 
    pdf.cell(200, 10, txt = f"{Name} Competitor Report", ln = 1, align = 'C')   
    pdf.cell(200, 10, txt = "by Offtime Roadmap, LLC", ln = 1, align = 'C')   

    team_data = ""
    most_wins = ["", 0]
    highest_win_pct = ["", 0]

    for team in teams:

        if team not in data:
            continue
        
        tournaments = list(data[team].keys())
        numTournaments = len(tournaments)

        team_data += team + " (" + data[team][tournaments[0]]["names"][:-1] + "):\n" 
        team_data +=  "    Stats: (Tournaments: " + str(numTournaments) + ") "
        i = len(team_data)
        running_record = [0,0]

        for tournament in tournaments:
            raw_record = data[team][tournament]["record"].split('-')
            running_record[0] = running_record[0] + int(raw_record[0])
            running_record[1] = running_record[1] + int(raw_record[1])

            team_data += "    " + tournament + "\n"
            team_data += "    - Results: (Record: " + data[team][tournament]["record"] + ") "
            if data[team][tournament]["break-round"] is not None:
                team_data += "(Break Round: " + data[team][tournament]["break-round"] + ") "
            if data[team][tournament]["ranking"] is not None:
                team_data += "(Ranking: " + str(data[team][tournament]["ranking"]) + ") "

            speaker_awards = data[team][tournament]["speaker-awards"]
            if speaker_awards is not None:
                team_data += "\n    - Speaks:\n"
                for top_speaker in speaker_awards:
                    team_data += "          " + top_speaker["name"] 
                    team_data += " - (Rank: " + top_speaker["ranking"] 
                    team_data += ") (Pts: " + str(top_speaker["total-points"]) + ")\n"
            else:
                team_data += "\n"
        
        cum_record = str(running_record[0]) + "-" + str(running_record[1])
        win_pct = str(int(100*running_record[0]/(running_record[1]+running_record[0])))

        if running_record[0] > most_wins[1]:
            most_wins[0] = team
            most_wins[1] = running_record[0]
        
        if int(win_pct) > highest_win_pct[1]:
            highest_win_pct[0] = team
            highest_win_pct[1] = int(win_pct)

        team_data = team_data[:i]  + " (Record: " + cum_record + ") (Win Rate: " + win_pct + "%)\n" + team_data[i:]
    
    team_data = f"Top Competitors: (Most Wins: {most_wins[0]}, {most_wins[1]}) (Highest Win %: {highest_win_pct[0]}, {highest_win_pct[1]}%)\n\n" + team_data
    pdf.multi_cell(200, 5, team_data, 0, 'L', False)
    pdf.output(f"{Name}.pdf")

while True:
    print(Fore.CYAN + "Welcome to Offtime Roadmap's Tabroom Competitor Report API!")
    Name = input("What is the name of the tournament? ")
    URL = input("Enter the link of the 'Entries' section: ")
    print("Generating Threat Sheet . . .")
    generatePDF(Name, URL)
    print(f"Success: {Name}.pdf saved!")