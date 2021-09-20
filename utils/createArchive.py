"""
    Converts season-long results into a single markdown file
    with all the data from the site.
"""

from os import listdir
from os.path import isfile, join
import json

# Dynamic vars
SEASON_NAME = "2020-21"
DIVISION = "Varsity Public Forum"
CIRCUIT = "National Circuit"
METHODOLOGY = "" # TODO, mention leaderboard requires 4 tourns.
MESSAGE = """
This report is an archive of data from [tournaments.tech](http://tournaments.tech),
a site designed to standardize results and ranking for the national high school debate
circuit. The site and the api (which is open sourced and can be found on [GitHub](https://github.com/http-samc))
were coded and developed by [Samarth Chitgopekar](https://www.smrth.dev) and the formula used
for ranking debaters (the OTR Score) was developed by Adithya Vaidyanathan. The project was carefullly
crafted to be as accurate as possible, and though perfection isn't guarenteed due to the unstandardized
nature of [tabroom.com](https://tabroom.com) (the site we pull rankings from), we are by far
the most accurate source currently available.
"""

MARKDOWN: str = f"""
# Tournaments.Tech's {SEASON_NAME} {DIVISION} {CIRCUIT} Archive
## Our Mission
{MESSAGE}
## Tournaments Scraped
Our archives encompass every major bid tournament (and the Tournament of Champions) and to
generate our rankings. In no particular order, you can find what we scraped this year below:
<details>
<summary><b>View Tournaments</b></summary>
"""

# Adding tournaments scraped
tournFiles = [f for f in listdir('data/tournaments') if isfile(join('data/tournaments', f))]
for i, file in enumerate(tournFiles):
    MARKDOWN += f"{i+1}. {file.replace('.json', '')}<br>\n"

MARKDOWN += "</details><br>\n"

MARKDOWN += f"""
## Final Rankings
{METHODOLOGY}

With that being said, our final rankings for the {SEASON_NAME} {DIVISION} {CIRCUIT}
are below:
<details>
<summary><b>View Final Rankings</b></summary>
"""

# Adding leaderboard
with open("data/leaders.json", "r") as f:
    data = json.loads(f.read())

for team in data["leaders"]:
    MARKDOWN += f"""
    {team["pos"]}. {team["code"]} {team["names"]}
        - OTR Score 📚: {team["score"]}
        - Gold Bids 🥇: {team["golds"]} 
        - Silver Bids 🥈: {team["silvers"]}
    """

MARKDOWN += "\n</details><br>\n"

MARKDOWN += f"""
## Overall Dataset
Here is a visually-friendly representation this season's dataset. If you'd like to use
the data in your own projects, you'll find our [open sourced JSON dataset](https://github.com/http-samc/tabroom-API/releases)
to be more helpful.
<details>
<summary><b>View Overall Dataset</b></summary>
"""

# Adding master data
with open(f"data/{SEASON_NAME} MASTER.json", "r") as f:
    data = json.loads(f.read())

for t in data:
    team = data[t]
    code = team["codes"][0]
    del team["codes"][0]
    codes = ""
    for c in team["codes"]:
        codes += c + ", "
    codes = codes[:-1]
    try:
        team["breakWinPCT"]
    except Exception:
        team["breakWinPCT"] = 0.0

    MARKDOWN += f"""
| Code | Names | Alt. Codes | OTR Score | Gold Bids | Silver Bids | Break % | Prelim Win % | Break Win % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| {code} | {team["fullNames"]} | {codes} | {team["otrScore"]} | {team["goldBids"]} | {team["silverBids"]} | {round(team["breakPCT"]*100, 1)}% | {round(team["prelimWinPCT"]*100, 1)}% ({team["prelimRecord"][0]}-{team["prelimRecord"][1]})| {round(team["breakWinPCT"]*100, 1)}% ({team["breakRecord"][0]}-{team["breakRecord"][1]})|
    """
    # TODO add ALL data later
#     MARKDOWN += """<details>
# <summary><b>View Tournament Results</b></summary>
#     | Tournament | OTR Comp. | Prelim Record | Prelim Rank | Break Record | Eliminated | Gold Bid | Silver Bid | 
#     """
#     for tourn in team["tournaments"]:
#         MARKDOWN += """
# | Tournament | 
#         """

MARKDOWN += "</details><br>\n"

with open("t.md", 'w') as f:
    f.write(MARKDOWN)