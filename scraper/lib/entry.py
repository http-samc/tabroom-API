from typing import List, TypedDict
from enum import Enum
from urllib.parse import urlparse, parse_qs
from ..utils.soup import get_soup
from ..utils.round_type import get_round_type, RoundType
from ..utils.side import get_side
from ..utils.clean import clean_element
from ..utils.decision import get_decision
from .entries import EntryFragment
from urllib.parse import urlparse, parse_qs


class Opponent(TypedDict):
    code: str
    tab_entry_id: int


class SpeakingResult(TypedDict):
    competitor: str
    points: float
    reply_score: float | None


class VoteType(Enum):
    WIN = "Win"
    LOSS = "Loss"


class RoundOutcome(Enum):
    WIN = "Win"
    LOSS = "Loss"
    SPLIT = "Split"


class RoundSide(Enum):
    PRO = "Pro"
    CON = "Con"
    BYE = "Bye"


class RecordFragment(TypedDict):
    name: str
    was_squirrel: bool | None
    speaking: List[SpeakingResult]


class Record(RecordFragment):
    result: VoteType
    tab_judge_id: int


class RoundFragment(TypedDict):
    name: str
    side: RoundSide
    type: RoundType
    outcome: RoundOutcome
    ballots_won: int
    ballots_lost: int


class Round(RoundFragment):
    opponent: Opponent | None
    judge_records: List[Record]


class Entry(EntryFragment):
    rounds: List[Round]
    competitors: List[str]


def scrape_entry(tab_tourn_id: int, entry_fragment: EntryFragment) -> Entry:
    """Scrapes the "Entry" page on Tabroom to gather round data.

    Args:
        tab_tourn_id (int): The unique ID assigned to the tournament, visible in the `tourn_id` query parameter.
        entry_fragment (EntryFragment): Basic information about the entry.

    Returns:
        Entry: The fully populated Entry with all pertinent information from Tabroom.
    """

    entry: Entry = entry_fragment
    soup = get_soup(
        f"https://www.tabroom.com/index/tourn/postings/entry_record.mhtml?tourn_id={tab_tourn_id}&entry_id={entry_fragment['tab_entry_id']}")

    entry['rounds'] = []
    entry['competitors'] = clean_element(
        soup.find('h4', class_="nospace semibold")).split(' & ')
    h6s = soup.find_all('h6')
    alias = None
    for h6 in h6s:
        if "Login" not in clean_element(h6):
            alias = clean_element(h6).strip()
    if not entry['code']:
        entry['code'] = alias
    if 'school' not in entry or not entry['school']:
        if ':' in alias:
            entry['school'] = alias.split(':')[0]
        else:
            nodes = alias.split(' ')
            if '&' in nodes:
                nodes = nodes[0:nodes.index('&') - 1]
            else:
                nodes = nodes[0:-1]
            entry['school'] = " ".join(nodes)

    for row in soup.find_all('div', class_="row"):
        round: Round = {}
        cells = row.find_all('span')

        # Round name
        round['name'] = clean_element(cells[0])

        # Round type
        round['type'] = str(get_round_type(round['name']))

        # Side
        round['side'] = get_side(clean_element(cells[1]))

        # Opp.
        opponent = clean_element(cells[2])
        if opponent:
            round['opponent'] = {}
            round['opponent']['code'] = opponent.replace('vs ', '')
            opponent_link = cells[2].find('a')['href']
            round['opponent']['tab_entry_id'] = int(parse_qs(
                urlparse(f"https://tabroom.com/{opponent_link}").query)['entry_id'][0])
        else:
            round['opponent'] = None

        # Judge Records
        round['judge_records'] = []
        for row in cells[3].findChildren('div'):
            judge_elem = row.find('a')
            if not judge_elem:
                continue

            record: Record = {'speaking': []}
            record_text = clean_element(row)

            record['tab_judge_id'] = int(parse_qs(
                urlparse(f"https://tabroom.com/{judge_elem['href']}").query)['judge_id'][0])

            parts = record_text.strip().split()
            judge_parts = []
            speaking_parts = []
            for part in parts:
                if len(judge_parts) and judge_parts[-1] in ["W", "L"]:
                    speaking_parts.append(part)
                else:
                    judge_parts.append(part)

            record['result'] = get_decision(round['side'], judge_parts.pop())

            first_name_parts = []
            last_name_parts = []
            all_last_names_added = False

            for part in judge_parts:
                if not last_name_parts or not all_last_names_added:
                    last_name_parts.append(part.replace(',', ''))
                else:
                    first_name_parts.append(part)
                if ',' in part:
                    all_last_names_added = True

            record['name'] = f"{' '.join(first_name_parts + last_name_parts)}"

            # LD Pattern, competitor names are not displayed
            if len(speaking_parts) == 1 and len(entry['competitors']) == 1:
                record['speaking'].append({
                    'competitor': entry['competitors'][0],
                    'score': float(speaking_parts[0]),
                    'reply_score': None
                })
            # Multi-competitor pattern
            else:
                nodes = []
                for part in speaking_parts:
                    # Start a new subarray when we have a string AND either no last node OR last node ended in number
                    if not part.replace('.', '').isdigit() and (not len(nodes) or (len(nodes[-1]) and type(nodes[-1][-1]) == float)):
                        nodes.append([part])
                    elif len(nodes):
                        nodes[-1].append(float(part)
                                         if part.replace('.', '').isdigit() else part)

                for node in nodes:
                    name_nodes = []
                    for subnode in node:
                        if type(subnode) == str:
                            name_nodes.append(subnode)  # Name components
                    if type(node[-1]) == float:
                        if len(node) > 2 and type(node[-2]) == float and node[-2] >= 60 and node[-1] >= 30:
                            score = node[-2]
                            reply_score = node[-1]
                        else:
                            score = node[-1]
                            reply_score = None

                        record['speaking'].append({
                            'competitor': f"{name_nodes[-1]} {' '.join(name_nodes[0:-1])}",
                            'score': score,
                            "reply_score": reply_score
                        })

            round['judge_records'].append(record)

        winningBallots = 0
        losingBallots = 0

        for record in round['judge_records']:
            if record['result'] == round['side']:
                winningBallots += 1
            else:
                losingBallots += 1

        round['ballots_won'] = winningBallots
        round['ballots_lost'] = losingBallots

        if winningBallots > losingBallots or round['side'] == "Bye":
            round['outcome'] = "Win"
        elif winningBallots == losingBallots and winningBallots:
            round['outcome'] = "Split"
        elif winningBallots == losingBallots:
            round['outcome'] = "Win"
        else:
            round['outcome'] = "Loss"

        for record in round['judge_records']:
            if record['result'] == round['side'] and round['outcome'] == "Loss":
                record['was_squirrel'] = True
            elif record['result'] != round['side'] and round['outcome'] == "Win":
                record['was_squirrel'] = True
            else:
                record['was_squirrel'] = False
        entry['rounds'].append(round)

    return entry
