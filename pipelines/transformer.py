from typing import TypedDict, List, Tuple, Mapping
from enum import Enum
from shared.lprint import lprint
import statistics
from .utils.deflator import get_deflator
from .utils.id import get_id
from .utils.iqr import apply_iqr
from scraper.lib import tournament, entries, entry, paradigm
from scraper.utils.decision import get_decision
from scraper.utils.constants import ELIM_ROUND_NAMES


class TournamentData(TypedDict):
    tournament: tournament.Tournament
    entries: List[entry.Entry]


class BidType(Enum):
    FULL = "Full"
    PARTIAL = "Partial"


class Bid(TypedDict):
    value: BidType
    is_ghost_bid: bool


class Competitor(TypedDict):
    id: str
    name: str


class TournamentSpeakerResult(TypedDict):
    competitor_id: str
    raw_avg_points: float
    adj_avg_points: float
    std_dev_points: float


class TransformedEntryResult(entries.EntryFragment):
    team_id: str
    competitors: List[Competitor]
    prelim_pos: int
    prelim_pool_size: int
    prelim_wins: float
    prelim_losses: float
    prelim_ballots_won: int
    prelim_ballots_lost: int
    elim_wins: int
    elim_losses: int
    elim_ballots_won: int
    elim_ballots_lost: int
    op_wp_m: float
    otr_comp: float
    bid: Bid | None
    speaking: List[TournamentSpeakerResult]

# TODO: Implement


class RoundSpeaking(TypedDict):
    competitor_id: str
    judge_id: str
    points: float


class TransformedRound(entry.RoundFragment):
    name_std: str
    team_id: str
    speaking: List[RoundSpeaking]
    opponent_id: str | None


class TransformedJudgeResult(TypedDict):
    judge_id: str
    tab_judge_id: int
    name: str
    avg_raw_points: str | None
    points_1HL: float | None
    avg_adj_points: str | None
    std_dev_points: str | None
    num_prelims: int
    num_elims: int | None
    num_squirrels: int | None
    num_screws: int | None
    num_pro: int
    num_con: int


class DecisionType(Enum):
    PRO = "Pro"
    CON = "Con"


class TransformedRecord(entry.RecordFragment):
    decision: DecisionType
    avg_points: float | None
    judge_id: str
    teams: List[str]
    winner_id: str
    round_name_std: str
    type: entry.RoundType


class TransformedParadigm(paradigm.Paradigm):
    judge_id: str
    tab_tourn_id: int
    flow_confidence: float
    progressive_confidence: float


class TransformedTournament(tournament.Tournament):
    tab_tourn_id: int
    tab_event_id: int
    level: str
    division_name: str
    classification: str
    season: int
    circuits: List[str]
    boost: float
    first_elim_round: str | None
    bid_level: str
    event: str
    nickname: str


class TransformedTournamentData(TypedDict):
    tournament: TransformedTournament
    team_results: List[TransformedEntryResult]
    rounds: List[TransformedRound]
    judge_results: List[TransformedJudgeResult]
    records: List[TransformedRecord]
    paradigms: List[TransformedParadigm]


def transform_data(job_id: int | None, tab_tourn_id: int, tab_event_id: int, nickname: str, event_name: str, tournament: tournament.Tournament, entries: List[entry.Entry], circuits: List[str], season: int, tournament_boost: float, classification: str, division_name: str, first_elim_round: str | None = None, toc_full_bid_level: str | None = None, has_partial_bids: bool = False) -> TransformedTournamentData:
    """Transforms raw Tabroom-native output from the scraper module into a format matching Debate Land's schema for API uploading.
    Adds in computed stats used by Debate Land.

    Args:
        tab_tourn_id (int): The unique ID assigned to the tournament, visible in the `tourn_id` query parameter.
        tab_event_id (int): The unique ID assigned to the event, visible in the `event_id` query parameter.
        event_name (str): The event name.
        nickname (str): A nickname for the tournament.
        tournament (tournament.Tournament): The scraped tournament.
        entries (List[entry.Entry]): The scraped entries.
        tournament_boost (float): The difficulty multiplier of the tournament.
        classification (str): The competitive level of the division.
        division_name (str): The name of the division on Tabroom.
        first_elim_round (str | None, optional): The standardized name of the first elimination round. Defaults to None.
        toc_full_bid_level (str | None, optional): The standardized name of the round awarding a full TOC bid. Defaults to None.
        has_partial_bids (bool, optional): Whether there are silver (partial) bids. Defaults to False.
    Returns:
        TransformedTournamentData: Tournament data in Debate Land's upload format.
    """
    lookup = {}

    tournament['tab_tourn_id'] = tab_tourn_id
    tournament['tab_event_id'] = tab_event_id
    tournament['season'] = season
    tournament['circuits'] = circuits
    tournament['boost'] = tournament_boost
    tournament['bid_level'] = toc_full_bid_level
    tournament['first_elim_round'] = first_elim_round
    tournament['event'] = event_name
    tournament['nickname'] = nickname
    tournament['classification'] = classification
    tournament['division_name'] = division_name

    team_results: List[TransformedEntryResult] = []
    rounds: List[TransformedRound] = []
    judge_results: List[TransformedJudgeResult] = []
    records: List[TransformedRecord] = []

    tab_entry_id_to_entry_uuid = {}
    judge_uuid_to_records_and_rounds: Mapping[str,
                                              List[Tuple[TransformedRecord, TransformedRound]]] = {}

    # Assign UUIDs
    for entry in entries:
        entry['team_id'] = get_id(' '.join(entry['competitors']).split(' '))
        tab_entry_id_to_entry_uuid[entry['tab_entry_id']] = entry['team_id']

    # Standardize round names
    round_to_std_name: Mapping[str, str] = {}
    entry_uuid_to_school: Mapping[str, str] = {}
    entry_uuid_to_last_elim: Mapping[str, TransformedRound | None] = {}

    # Use UUIDs in links
    # Handle Tab ID changes

    for entry in entries:
        result: TransformedEntryResult = {
            'team_id': entry['team_id'],
            'competitors': list(map(
                lambda c: {
                    'id': get_id(c.split(' ')),
                    'name': c
                },
                entry['competitors']
            )),
            'tab_entry_id': entry['tab_entry_id'],
            'code': entry['code'],
            'prelim_pos': None,
            'prelim_pool_size': len(entries),
            'prelim_wins': 0,
            'prelim_losses': 0,
            'prelim_ballots_won': 0,
            'prelim_ballots_lost': 0,
            'elim_wins': 0 if first_elim_round else None,
            'elim_losses': 0 if first_elim_round else None,
            'elim_ballots_won': 0 if first_elim_round else None,
            'elim_ballots_lost':  0 if first_elim_round else None,
            'school': entry['school'],
            'location': entry['location'],
            'op_wp_m': [],
            'op_wp_m_winning': [],
            'op_wp_m_losing': [],
            'otr_comp': None,
        }

        # Log school (for ghost bid detection)
        entry_uuid_to_school[result['team_id']] = result['school']

        # Standardize round names
        prelim_rounds: List[TransformedRound] = []
        elim_rounds: List[TransformedRound] = []

        for round in entry['rounds']:
            if round['type'] == "Prelim":
                prelim_rounds.append(round)
            else:
                elim_rounds.append(round)

        # Put rounds in chronological orer
        prelim_rounds.reverse()
        elim_rounds.reverse()

        # Log last elim round (for ghost bid detection)
        if len(elim_rounds):
            entry_uuid_to_last_elim[result['team_id']] = elim_rounds[-1]
        else:
            entry_uuid_to_last_elim[result['team_id']] = None

        for i, round in enumerate(prelim_rounds):
            # Update result
            if round['outcome'] == "Win":
                result['prelim_wins'] += 1
            elif round['outcome'] == "Loss":
                result['prelim_losses'] += 1
            elif round['outcome'] == "Split":
                result['prelim_wins'] += 0.5
                result['prelim_losses'] += 0.5
            result['prelim_ballots_won'] += round['ballots_won']
            result['prelim_ballots_lost'] += round['ballots_lost']

            # Handle name manipulations
            if round['name'] in round_to_std_name:
                continue
            round_to_std_name[round['name']] = f"Round {i + 1}"

        for i, round in enumerate(elim_rounds):
            # Update result
            if round['outcome'] == "Win":
                result['elim_wins'] += 1
            elif round['outcome'] == "Loss":
                result['elim_losses'] += 1
            result['elim_ballots_won'] += round['ballots_won']
            result['elim_ballots_lost'] += round['ballots_lost']

            # Handle name manipulations
            if round['name'] in round_to_std_name:
                continue
            first_elim_round_idx = ELIM_ROUND_NAMES.index(first_elim_round)
            round_to_std_name[round['name']
                              ] = ELIM_ROUND_NAMES[first_elim_round_idx - i]

        for i, round in enumerate(entry['rounds']):
            if round['opponent']:
                round['opponent_id'] = tab_entry_id_to_entry_uuid[round['opponent']
                                                                  ['tab_entry_id']]
            else:
                round['opponent_id'] = None
            round['name_std'] = round_to_std_name[round['name']]
            round['team_id'] = entry['team_id']

            judge_records = round['judge_records']
            round['speaking'] = []
            for record in judge_records:
                if 'speaking' not in record:
                    continue
                for speak in record['speaking']:
                    speak['judgeId'] = get_id(record['name'].split(' '))
                    speak['competitorId'] = get_id(
                        speak['competitor'].split(' '))
                    speak['points'] = speak['score']
                    del speak['reply_score']
                    del speak['score']
                    del speak['competitor']
                    round['speaking'].append(speak)
            del round['judge_records']
            del round['opponent']

            rounds.append(round)

            matchup_id = get_id([round['team_id'], round['opponent_id'] or ""])

            for record in judge_records:
                uuid = get_id(record['name'].split(' '))
                record['judge_id'] = uuid

                # Register judge in the lookup if they aren't in already
                if not uuid in judge_uuid_to_records_and_rounds:
                    judge_uuid_to_records_and_rounds[uuid] = {}

                # If the lookup has recorded the specific round for the judge, add this specific round & record to it
                if round['name_std'] in judge_uuid_to_records_and_rounds[uuid] and matchup_id in judge_uuid_to_records_and_rounds[uuid][round['name_std']]:
                    judge_uuid_to_records_and_rounds[uuid][round['name_std']][matchup_id]['rounds'].append(
                        round)
                    judge_uuid_to_records_and_rounds[uuid][round['name_std']][matchup_id]['records'].append(
                        record)

                # Register the round for the judge and initialize with the this specific round & record
                else:
                    # Register the round if not already done
                    if round['name_std'] not in judge_uuid_to_records_and_rounds[uuid]:
                        judge_uuid_to_records_and_rounds[uuid][round['name_std']] = {
                        }

                    # Register the matchup
                    judge_uuid_to_records_and_rounds[uuid][round['name_std']][matchup_id] = {
                        'rounds': [round],
                        'records': [record]
                    }

        result['speaking']: List[TournamentSpeakerResult] = []
        competitor_to_speaks: Mapping(str, List[float]) = {}

        for round in entry['rounds']:
            for speak in round['speaking']:
                competitor = speak['competitorId']
                if competitor not in competitor_to_speaks:
                    competitor_to_speaks[competitor] = []
                competitor_to_speaks[competitor].append(speak['points'])

        for competitor, speaks in competitor_to_speaks.items():
            result['speaking'].append({
                'competitor_id': competitor,
                'raw_avg_points': statistics.mean(speaks),
                'adj_avg_points': statistics.mean(apply_iqr(speaks)),
                'std_dev_points': statistics.stdev(speaks) if len(speaks) > 1 else 0
            })

        team_results.append(result)

    # Handle bids
    for result in team_results:
        result['bid'] = None

        last_elim = entry_uuid_to_last_elim[result['team_id']]
        if not last_elim or not toc_full_bid_level:
            continue

        last_op_school = entry_uuid_to_school[last_elim['opponent_id']
                                              ] if last_elim['opponent_id'] in entry_uuid_to_school else None
        if not last_op_school:
            lprint(job_id, "Info", message=f"Last school not detected for team '{entry['code']}'")
            continue

        idx = ELIM_ROUND_NAMES.index(last_elim['name_std'])

        if last_op_school == entry['school']:
            lprint(job_id, "Info", message=f"Ghost bid detected for {entry['code']} (Their school is {entry['school']} and their last opponent was from {last_op_school}).")
            is_ghost_bid = True
        else:
            is_ghost_bid = False

        full_bid_idx = ELIM_ROUND_NAMES.index(
            toc_full_bid_level) + (1 if is_ghost_bid else 0)

        if has_partial_bids:
            partial_bid_idx = full_bid_idx + 1
        else:
            partial_bid_idx = None
        if idx <= full_bid_idx:
            result['bid'] = {
                "value": "Full",
                "isGhostBid": is_ghost_bid
            }
        elif partial_bid_idx and idx <= partial_bid_idx:
            result['bid'] = {
                "value": "Partial",
                "isGhostBid": is_ghost_bid
            }

    # Compute opWpM and OTR Comp
    for entry in entries:
        result: TransformedEntryResult | None = None

        for _result in team_results:
            if _result['team_id'] == tab_entry_id_to_entry_uuid[entry['tab_entry_id']]:
                result = _result

        if not result or (result['prelim_ballots_won'] + result['prelim_ballots_lost']) == 0:
            continue

        rxr = 0
        break_boost = (result['elim_wins'] or 0) + \
            (result['elim_losses'] or 0) + 1
        p_wp = result['prelim_ballots_won'] / \
            (result['prelim_ballots_won'] + result['prelim_ballots_lost'])
        result['uds'] = []
        for round in entry['rounds']:
            opponent_result: TransformedEntryResult | None = None

            for _result in team_results:
                if not 'opponent_id' in round:
                    continue
                if _result['team_id'] == round['opponent_id']:
                    opponent_result = _result

            if not opponent_result or (opponent_result['prelim_ballots_lost'] + opponent_result['prelim_ballots_won']) == 0:
                continue

            op_pwp = opponent_result['prelim_ballots_won'] / (
                opponent_result['prelim_ballots_won'] + opponent_result['prelim_ballots_lost'])
            if round['outcome'] == "Win":
                try:
                    result['op_wp_m_winning'].append(op_pwp)
                except Exception:
                    result['op_wp_m_winning'] = [
                        result['op_wp_m_winning'], op_pwp]
            else:
                try:
                    result['op_wp_m_losing'].append(op_pwp)
                except Exception:
                    result['op_wp_m_losing'] = [
                        result['op_wp_m_losing'], op_pwp]

            try:
                result['op_wp_m'].append(op_pwp)
            except Exception:
                result['op_wp_m'] = [
                    result['op_wp_m'], op_pwp]

            delta_pwp = op_pwp - p_wp

            if round['type'] == "Elim" or delta_pwp <= 0 or round['outcome'] != "Win":
                continue
            result['uds'].append(
                {'round': round, 'rxr': .12 * ((delta_pwp + 0.7)**16 / (0.5 + (delta_pwp + 0.7)**10))**(1/2)})
            rxr += .12 * ((delta_pwp + 0.7)**16 /
                          (0.5 + (delta_pwp + 0.7)**10))**(1/2)

        result['op_wp_m'] = statistics.mean(result['op_wp_m'])
        result['op_wp_m_winning'] = statistics.mean(
            result['op_wp_m_winning']) if type(result['op_wp_m_winning']) is list and len(result['op_wp_m_winning']) else 0
        result['op_wp_m_losing'] = statistics.mean(
            result['op_wp_m_losing']) if type(result['op_wp_m_losing']) is list and len(result['op_wp_m_losing']) else 0
        result['p_wp'] = p_wp
        result['bb'] = break_boost
        result['tb'] = tournament_boost
        result['rxr'] = rxr
        result['otr_comp'] = (p_wp * break_boost *
                              (result['op_wp_m'] + 0.625) * tournament_boost + rxr) / 3

    # Sort results by OTR Comp, using OpWpM as a tiebreaker
    team_results = list(
        filter(lambda r: r['op_wp_m'] is not None and r['otr_comp'] is not None, team_results))
    team_results.sort(key=lambda r: (
        r['otr_comp'], r['op_wp_m']), reverse=True)

    # Assign prelim seeds based on index
    for i, result in enumerate(team_results):
        result['prelim_pos'] = i + 1

    # Create judge results
    for uuid, data in judge_uuid_to_records_and_rounds.items():
        first_record = list(list(data.values())[0].values())[0]['records'][0]

        result: TransformedJudgeResult = {
            'judge_id': uuid,
            'name': first_record['name'],
            'tab_judge_id': first_record['tab_judge_id'],
            'avg_raw_points': [],
            'avg_adj_points': [],
            'std_dev_points': [],
            'num_prelims': 0,
            'num_elims': 0,
            'num_squirrels': 0,
            'num_screws': None,
            'num_pro': 0,
            'num_con': 0
        }

        for round_matchups in data.values():
            for matchup in round_matchups.values():
                matchup_records = matchup['records']
                matchup_rounds = matchup['rounds']

                # Merge rounds
                matchup_round = matchup_rounds[0]

                # Merge records
                matchup_record = matchup_records[0]
                all_speaks = []
                for _record in matchup_records:
                    for speak in _record['speaking']:
                        all_speaks.append(speak)

                matchup_record['speaking'] = all_speaks

                del matchup_record['name']
                del matchup_record['tab_judge_id']
                matchup_record['type'] = matchup_round['type']

                if matchup_record['speaking']:
                    matchup_record['avg_points'] = statistics.mean(
                        list(map(lambda s: s['points'], matchup_record['speaking'])))
                else:
                    matchup_record['avg_points'] = None

                matchup_record['teams'] = list(
                    map(lambda r: r['team_id'], matchup_rounds))

                if matchup_round['outcome'] == "Win":
                    matchup_record['winner_id'] = matchup_round['team_id']
                elif matchup_round['outcome'] != "Split":
                    matchup_record['winner_id'] = matchup_round['opponent_id']
                else:
                    matchup_record['winner_id'] = None

                matchup_record['round_name_std'] = matchup_round['name_std']
                matchup_record['decision'] = matchup_record['result']
                del matchup_record['result']

                if matchup_record['decision'] == "Pro":
                    result['num_pro'] += 1
                else:
                    result['num_con'] += 1
                if matchup_record['was_squirrel']:
                    result['num_squirrels'] += 1
                if matchup_record['type'] == "Prelim":
                    result['num_prelims'] += 1
                else:
                    result['num_elims'] += 1

                if matchup_record['speaking']:
                    for speak in matchup_record['speaking']:
                        result['avg_raw_points'].append(speak['points'])

                records.append(matchup_record)

        if result['avg_raw_points'] and len(result['avg_raw_points']) > 1:
            result['avg_adj_points'] = statistics.mean(
                apply_iqr(result['avg_raw_points']))
            result['std_dev_points'] = statistics.stdev(
                result['avg_raw_points'])
            try:
                result['points_1HL'] = statistics.mean(
                    sorted(result['avg_raw_points'])[1:-1])
            except Exception:
                result['points_1HL'] = None
            result['avg_raw_points'] = statistics.mean(
                result['avg_raw_points'])

        else:
            result['avg_raw_points'] = None
            result['avg_adj_points'] = None
            result['std_dev_points'] = None

        judge_results.append(result)

    # Scrape and classify paradigms
    paradigms: List[TransformedParadigm] = []
    for i, result in enumerate(judge_results):
        raw_paradigm: TransformedParadigm | None = paradigm.scrape_paradigm(
            tab_tourn_id, result['tab_judge_id'])
        if not raw_paradigm or paradigm.check_paradigm_cache(raw_paradigm['hash']):
            continue
        raw_paradigm['tab_tourn_id'] = tab_tourn_id
        raw_paradigm['judge_id'] = result['judge_id']
        # result = paradigm.classify_paradigm(
        #     raw_paradigm['text'])
        # if not result:
        #     continue
        raw_paradigm['flow_confidence'] = -1 #result[0]
        raw_paradigm['progressive_confidence'] = -1 #result[1]
        paradigms.append(raw_paradigm)

    return {
        'tournament': tournament,
        'team_results': team_results,
        'rounds': rounds,
        'judge_results': judge_results,
        'records': records,
        'paradigms': paradigms
    }
