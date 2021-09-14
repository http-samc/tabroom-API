`Tournament.Tech's Tabroom API` **2021 Q1**
## [merge.py](/merge.py)
---
### merge.`merge` [function]
<details style='color: #333333'><summary>Details</summary>

```Python
Merges each individual tournament result from ./data/tournaments into the master file.
```
</details>

## [main.py](/main.py)
---
### main.`scrapeAll` [function]
<details style='color: #333333'><summary>Details</summary>

```Python
Driver for the generator function - scrapes all listed tournaments
```
</details>

## [utils.parsers.py](/utils/parsers.py)
---
### utils.parsers.`getDivision` [function]
<details style='color: #333333'><summary>Details</summary>

```Python
Finds the target division from the
tournament results homepage

Args:
    URL (str): a Tabroom tournament's generic results page

Returns:
    str: name of the matching division
    None: if no division could be found
```
</details>

### utils.parsers.`getResultsURLs` [function]
<details style='color: #333333'><summary>Details</summary>

```Python
Finds appropriate result page link in the rounds section

Args:
    URL (str): the URL of the division results page
    breaks (bool, optional): Return the link of the

Returns:
    list: the URL of the requested page(s)

    RETURN SCHEMA:
    [
        <(str) URL of final places page | None if null>,
        <(str) URL of the brackets page | None if null>
    ]
```
</details>

## [utils.generator.py](/utils/generator.py)
---
### utils.generator.`getTournamentData` [function]
<details style='color: #333333'><summary>Details</summary>

```Python
Generates all available tournament data

Args:
    URL (str): the URL to the homepage of a Tabroom tournament
    tournamentBoost (float): the tournament-wide difficulty booster

Returns:
    dict: the tournament data

    RETURN SCHEMA:
    {
        <(str) tournament name> : [
            <(str) team code> : {
                "names" : <(str) full names of both members>,
                "lastNames" : [
                    <(str) last name of 1st competitor>,
                    <(str) last name of 2nd competitor>
                ],
                "prelimRecord" : [
                    <(int) number of prelim wins (byes incl.)>,
                    <(int) number of prelim losses>
                ],
                "prelimRank" : <(int) prelim record seed rank>
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
                "breakBoost" : <(int) breakBoost value>,
                "tournamentBoost" : <(float) tournament-wide difficulty booster>
                "OPwpm" : <(float) opponent's average win percentage>,
            }
        ],
        ...
    }
```
</details>

## [utils.scrapers.py](/utils/scrapers.py)
---
### utils.scrapers.`_clean` [function]
<details style='color: #333333'><summary>Details</summary>

```Python
Removes tabs, periods, newlines, nums (opt) from a string

Args:
    string (str): string to clean
    stripNum (bool): whether or not to remove numbers. Defaults to False.
    stripPreiods (bool) whether or not to remove periods. Defaults to True.
Returns:
    str: cleaned version of string
    None: if string had no characters
```
</details>

### utils.scrapers.`_adjScores` [function]
<details style='color: #333333'><summary>Details</summary>

```Python
Filters a list by removing outliers

Args:
    x (list): the list to filter
    outlierConstant (float, optional): what value used to determine outlier status. Defaults to 2.

Returns:
    list: the outlier-filtered list
```
</details>

### utils.scrapers.`bracket` [function]
<details style='color: #333333'><summary>Details</summary>

```Python
Scrapes a Tabroom bracket as an HTML table & returns
a dict that contains a set of keys representing team names,
with each value representing a list containing the number
of break rounds they debated (starts at 1) (equals roundPrestige
factor), the name of that break round as designated by the
tournament, and the name of that break round as designated by
our own standardized convention.

Args:
    URL (str): the URL to the Tabroom bracket page

Returns:
    RETURN SCHEMA:
    {
        <(str) team code> : [
            <(int) roundPrestige [num of break rounds debated]>,
            <(str) name of final break round debated as provided>,
            <(str) name of final break round debated, standardized>
        ],
        ...
    }
```
</details>

### utils.scrapers.`breaks` [function]
<details style='color: #333333'><summary>Details</summary>

```Python
Parses the final places page of a tournament

Args:
    URL (str): the URL of the final places page of a certain division

Returns:
    dict: a dict containing the parsed break round data

    RETURN SCHEMA:
    {
        <(str) team code> : [
            <(int) roundPrestige [num of break rounds debated]>,
            <(str) name of final break round debated as provided>,
            <(str) name of final break round debated, standardized>
        ],
        ...
    }
```
</details>

### utils.scrapers.`entry` [function]
<details style='color: #333333'><summary>Details</summary>

```Python
Returns the results from a team's individual entry page

Args:
    URL (str): the URL of a team's entry page

Returns:
    dict: contains team code, full names, prelim records,
        break round data, opponent names,
        decision data, speaker point data

        RETURN SCHEMA:
        {
            "code" : <(str) entry's team code>,
            "names" : <(str) both partner's full names, separated by an '&'>,
            "prelimRecord" : [
                <(int) prelim wins (incl. byes)>,
                <(int) prelim losses>
            ],
            "debatedPrelims" : <(int) the number of debated (non-bye) preliminary rounds>, # used in OPwpm calculation
            "elimIn" : <(str) nonstandardized final break round ["prelim" if none]>
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
            "prelims" : [
                <variable number of round dictionaries>
            ],
            "breaks" : [
                <variable number of round dictionaries>
            ]
        }

        ROUND SCHEMA:
        ''' If there was no opponent, all keys will be null except for the round name, side (-> bye), & win (-> True) '''
        {
            "round" : <(str) round name>,
            "win" : <(bool) whether or not the team won {null if draw}>,
            "side" : <(str) what side the team was on -> PRO or CON>,
            "opp" : <(str) opponent's team code>,
            "decision" : [
                <(int) numBallotsWon>,
                <(int) numBallotsLost>
            ]
        },
```
</details>

### utils.scrapers.`prelims` [function]
<details style='color: #333333'><summary>Details</summary>

```Python
Parses the prelims page of a tournament

Args:
    URL (str): the URL of the prelims page of a certain division

Returns:
    dict: a dict containing the parsed prelim data

    RETURN SCHEMA:
    {
        <(str) team code> : {
            ''' used in condensor / master dataset merger '''
            'names' : [
                ''' These names are what Tabroom provides and might
                not represent the speaking order of the entry '''
                <(str) speaker #1 last name>,
                <(str) speaker #2 last name>
            ],
            'entryPage' : <(str) URL of the team's entry page; can be used with entry()>,
            'prelimWins' : <(int) number of prelim wins>, ''' used for cross verification with entry() '''
            ''' used as a statistic '''
            'prelimRank' : [
                <(int) position>,
                <(int) total entries>
            ]
        }
    }
```
</details>

### utils.scrapers.`name` [function]
<details style='color: #333333'><summary>Details</summary>

```Python
Scrapes the name of a tournament

Args:
    URL (str): the homepage URL of a Tabroom tournament

Returns:
    str: the name of the tournament
```
</details>

## [utils.condensors.py](/utils/condensors.py)
---
### utils.condensors.`condense` [function]
<details style='color: #333333'><summary>Details</summary>

```Python
Condenses redundant data from various scrapers
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
```
</details>

## [utils.helpers.py](/utils/helpers.py)
---
### utils.helpers.`calcBid` [function]
<details style='color: #333333'><summary>Details</summary>

```Python
Adds bid data to condensed tournament-level dataset

Args:
    data (dict): condensed tournament-level dataset

Returns:
    dict: dataset with bid levels for each team included
```
</details>

### utils.helpers.`calcOPwpm` [function]
<details style='color: #333333'><summary>Details</summary>

```Python
Adds OPwpm to semi-condensed tournament-level dataset.
Required to be called before round data is removed to preserve
the opponent data needed in order to gen OPwpm.

Args:
    data (dict): semi-condensed tournament-level dataset

Returns:
    dict: dataset with OPwpm for each team included
```
</details>

### utils.helpers.`calcTournamentComp` [function]
<details style='color: #333333'><summary>Details</summary>

```Python
Adds tournamentComp to condensed tournament-level dataset.
Required to be called last, after OPwpm calculation

Args:
    data (dict): condensed tournament-level dataset

Returns:
    dict: dataset with tournamentComp for each team included
```
</details>

### utils.helpers.`orderCond` [function]
<details style='color: #333333'><summary>Details</summary>

```Python
Orders all keys in the given condensed tournament dict

Args:
    data (dict): condensed tournament dict

Returns:
    dict: ordered dict (matches schema)
```
</details>