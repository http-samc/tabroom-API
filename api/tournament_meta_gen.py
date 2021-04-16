import json
import requests
from bs4 import BeautifulSoup

with open('d.json', 'r') as f:
    data = json.loads(f.read())

tournaments = list(data.keys())
new_data = {tournaments[0] : data[tournaments[0]]}
del tournaments[0]

for tournament in tournaments:

    keywords = tournament.split(" ")

    BASEURL = "https://www.tabroom.com/index/search.mhtml?search="

    for keyword in keywords:
        BASEURL += keyword + "+"
    
    r = requests.get(BASEURL [0:(len(BASEURL)-1)])

    soup = BeautifulSoup(r.text, "html.parser")

    results = soup.find_all("a", class_="plain full padvertless")

    try:
        link = "https://www.tabroom.com" + results[0]['href']
    except Exception:
        link = None

    new_data[tournament] = {
        "meta" : data[tournament],
        "link" : link,
        "acceptsUnaffiliated" : None
    }

with open('d.json', 'w') as f:
    json.dump(new_data, f)