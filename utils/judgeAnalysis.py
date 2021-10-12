import requests
from bs4 import BeautifulSoup
import json

def analysis(URL: str) -> str:
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, "html.parser")

    judgeData = []
    judges = soup.find_all('div', attrs = {'class': 'bordertop borderbottom'})

    for judge in judges:
        judgeDataDict = {}
        judgeDataDict['name'] = str(judge.find('span', attrs = {'class': 'threetenths semibold bluetext'}).string).replace('\t', '').replace('\n', '')
        judgeDataDict['school'] = str(judge.find('span', attrs = {'class': 'fourtenths'}).string).replace('\t', '').replace('\n', '')
        judgeDataDict['paradigm'] = str(judge.parent.find('div', attrs = {'class': 'paradigm hidden'}).text).replace('\t', '')
        judgeData.append(judgeDataDict)

        #Debugging
        print("Name:", judgeDataDict['name'])
        print("School:", judgeDataDict['name'])
        print("Paradigm:", judgeDataDict['paradigm'])


analysis("https://www.tabroom.com/index/tourn/paradigms.mhtml?category_id=53735&tourn_id=21009")