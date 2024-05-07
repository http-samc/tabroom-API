from bs4 import BeautifulSoup
from ..utils.soup import get_soup
from ..utils.clean import clean_element
from typing import TypedDict, List
from urllib.parse import urlparse, parse_qs
from datetime import datetime


class TournamentSite(TypedDict):
    tab_site_id: int
    name: str
    host: str


class TournamentContact(TypedDict):
    name: str
    email: str


class TournamentEmail(TypedDict):
    subject: str
    sender: str
    recipients: str
    sent: str
    text: str


class tournamentDivisionMetadata(TypedDict):
    abbreviation: str
    format: str
    topic: str | None
    topic_classification: str | None
    entry_fee: float
    event_entry_limit: int
    school_entry_limit: int
    competitors_per_entry: List[int]


class TournamentInstitutionInAttendance(TypedDict):
    name: str
    state: str


class TournamentPage(TypedDict):
    title: str
    tab_webpage_id: int | None
    text: str
    html: str


class TournamentAsset(TypedDict):
    title: str
    url: str


class TabroomCircuit(TypedDict):
    name: str
    abbreviation: str
    tab_circuit_id: int


class TournamentPastResult(TypedDict):
    name: str
    year: int
    tab_tourn_id: int


class Tournament(TypedDict):
    name: str
    location: str
    year: int
    start: str
    end: str
    registration_opens: str
    registration_closes: str
    fees_frozen: str
    judging_due: str
    drop_online: str
    penalty_fines: str
    webname: str | None
    sites: List[TournamentSite]
    contacts: List[TournamentContact]
    emails: List[TournamentEmail]
    event_metadata: List[tournamentDivisionMetadata]
    schools: List[TournamentInstitutionInAttendance]
    pages: List[TournamentPage]
    assets: List[TournamentAsset]
    tab_circuits: List[TabroomCircuit]
    past_results: List[TournamentPastResult]


def scrape_tournament_page(tab_tourn_id: int, tab_webpage_id: int | None = None) -> TournamentPage:
    """Scrapes a tournament page.

    Args:
        tab_tourn_id (int): The unique ID assigned to the tournament, visible in the `tourn_id` query parameter.
        tab_webpage_id (int | None, optional): The unique ID assigned to the webpage, visible in the `webpage_id` query parameter. Defaults to None, in which case the home (invite) page will be scraped.

    Returns:
        TournamentPage: All pertinent information gathered from the page.
    """

    page: TournamentPage = {}

    soup = get_soup(
        f'https://www.tabroom.com/index/tourn/index.mhtml?tourn_id={tab_tourn_id}{f"&webpage_id={tab_webpage_id}" if tab_webpage_id else ""}')
    elements = soup.find(class_="main index").find('ul').find_next_siblings()

    page['title'] = clean_element(elements[0]) if tab_webpage_id else "Invite"
    page['tab_webpage_id'] = tab_webpage_id
    page['html'] = ''.join(
        list(map(lambda element: str(element), elements[1:])))
    page['text'] = BeautifulSoup(page['html'], 'html.parser').get_text()

    return page


def scrape_event_metadata(tab_tourn_id: int, tab_event_id: int) -> tournamentDivisionMetadata:
    """Scrapes the event metadata.

    Args:
        tab_tourn_id (int): The unique ID assigned to the tournament, visible in the `tourn_id` query parameter.
        tab_event_id (int): The unique ID assigned to the event, visible in the `event_id` query parameter.

    Returns:
        tournamentDivisionMetadata: All pertinent information gathered about the event.
    """

    metadata: tournamentDivisionMetadata = {
        'topic': None,
        'topic_classification': None,
        'abbreviation': None,
        'format': None,
        'entry_fee': None,
        'competitors_per_entry': None,
        'event_entry_limit': None,
        'school_entry_limit': None
    }

    soup = get_soup(
        f'https://www.tabroom.com/index/tourn/events.mhtml?event_id={tab_event_id}&tourn_id={tab_tourn_id}')
    for row in soup.find_all(class_="row"):
        if not 'full' in row['class']:
            continue
        elements = row.find_all('span')
        value = clean_element(elements[1])
        match clean_element(elements[0]):
            case 'Abbreviation':
                metadata['abbreviation'] = value
            case 'Format':
                metadata['format'] = value
            case 'Topic:':
                # TODO: Test this
                metadata['topic_classification'], metadata['topic'] = list(
                    map(lambda element: clean_element(element), elements[1].find_all()))
            case 'Entry Fee':
                metadata['entry_fee'] = float(value[1:])
            case 'Overall Entry Limit':
                metadata['event_entry_limit'] = int(value)
            case 'Entry Limit Per School':
                metadata['school_entry_limit'] = int(value)
            case 'Entry':
                constraints = []
                for char in value:
                    if char.isnumeric():
                        print
                        constraints.append(int(char))
                constraints.sort()
                metadata['competitors_per_entry'] = constraints

    return metadata


def scrape_tournament_email(tab_tourn_id: int, tab_email_id: int) -> TournamentEmail:
    """Scrapes an email sent by a tournament.

    Args:
        tab_tourn_id (int): The unique ID assigned to the tournament, visible in the `tourn_id` query parameter.
        tab_email_id (int): The unique ID assigned to the email, visible in the `email_id` query parameter.

    Returns:
        TournamentEmail: All pertinent information gathered about the email.
    """

    email: TournamentEmail = {}
    soup = get_soup(
        f'https://www.tabroom.com/index/tourn/emails.mhtml?tourn_id={tab_tourn_id}&email_id={tab_email_id}')

    for row in soup.find_all(class_="row"):
        if 'bigger' not in row['class']:
            continue
        elements = row.find_all('span')
        value = clean_element(elements[1])
        match clean_element(elements[0]):
            case 'Subject':
                email['subject'] = value
            case 'Sender':
                email['sender'] = value
            case 'Recipients':
                email['recipients'] = value or "All"
            case 'Sent':
                email['sent'] = datetime.strptime(
                    value, "%A %d %B %Y at %I:%M %p").isoformat() + "Z"

    email['text'] = clean_element(soup.find(class_="padmore bigger"))

    return email


def scrape_tournament_site(tab_tourn_id: int, tab_site_id: int) -> TournamentSite:
    """Scrapes a tournament site.

    Args:
        tab_tourn_id (int): The unique ID assigned to the tournament, visible in the `tourn_id` query parameter.
        tab_site_id (int): The unique ID assigned to the site, visible in the `site_id` query parameter.

    Returns:
        TournamentSite: All pertinent information gathered about the site.
    """

    site: TournamentSite = {}
    soup = get_soup(
        f'https://www.tabroom.com/index/tourn/index.mhtml?site_id={tab_site_id}&tourn_id={tab_tourn_id}')

    site['name'] = clean_element(soup.find('h3'))
    site['host'] = clean_element(soup.find('p')).replace('Host: ', '')
    site['tab_site_id'] = tab_site_id

    return site

# TODO: Timezones


def scrape_tournament(tab_tourn_id: int) -> Tournament:
    """Scrapes a tournament for top-level metadata, including key dates, forms, locations, and contacts.

    Args:
        tab_tourn_id (int): The unique tournament ID assigned to the tournament, visible in the `tourn_id` query parameter.

    Returns:
        Tournament: All pertinent information gathered from the homepage.
    """

    tournament: Tournament = {}

    soup = get_soup(
        f'https://www.tabroom.com/index/tourn/index.mhtml?tourn_id={tab_tourn_id}')

    # Header
    tournament['name'] = clean_element(soup.find('h2'))
    year, location = clean_element(soup.find('h5')).split(' -- ')
    tournament['year'] = int(year)
    tournament['location'] = location

    # Pages & Forms
    tournament['pages'] = []
    tournament['assets'] = []
    for link in soup.find_all(class_="yellow full"):
        # Relative link indicates Tabroom webpage
        if link["href"][0] == "/":
            query = parse_qs(urlparse(link["href"]).query)
            tournament['pages'].append(scrape_tournament_page(
                tab_tourn_id, int(query["webpage_id"][0])))
        # Absolute link indicates external asset
        else:
            tournament['assets'].append({
                "title": clean_element(link),
                "url": link["href"]
            })

    # Packets
    for link in soup.find_all(class_="green full"):
        if not link['href'].startswith('/'):
            tournament['assets'].append({
                'title': clean_element(link),
                'url': link['href']
            })

    # Manually scrape invitation
    tournament['pages'].append(scrape_tournament_page(tab_tourn_id))

    # Scrape circuits
    tournament['tab_circuits'] = []
    for link in soup.find_all('a', class_="third"):
        circuit: TabroomCircuit = {}
        circuit['abbreviation'] = clean_element(link)
        circuit['name'] = link['title']
        query = parse_qs(urlparse(link["href"]).query)
        circuit['tab_circuit_id'] = int(query['circuit_id'][0])
        tournament['tab_circuits'].append(circuit)

    # Scrape dates
    for row in soup.find_all(class_="row"):
        label, value = list(
            map(lambda element: clean_element(element), row.find_all()))
        if label == "Tournament Dates":
            duration = list(map(lambda s: datetime.strptime(
                f"{s} {tournament['year']}", "%b %d %Y").isoformat() + "Z", value.replace(f" {tournament['year']}", "").split(' to ')))
            if len(duration) == 2:
                tournament['start'], tournament['end'] = duration
            else:  # One day tournament
                tournament['start'] = duration[0]
                tournament['end'] = duration[0]
        else:
            try:
                date_string = f"{tournament['year']} {value}"
                iso = datetime.strptime(
                    date_string, "%Y %a %b %d at %I:%M %p").isoformat() + "Z"
            except Exception:
                continue

            match label:
                case "Registration Opens":
                    tournament['registration_opens'] = iso
                case "Registration Closes":
                    tournament['registration_closes'] = iso
                case "Fees Freeze After":
                    tournament['fees_frozen'] = iso
                case "Judge Information Due":
                    tournament['judging_due'] = iso
                case "Drop online until":
                    tournament['drop_online'] = iso
                case "Change fees apply after":
                    tournament['penalty_fines'] = iso
                case _:
                    print(label)

    # Scrape sites and contacts
    tournament['sites'] = []
    tournament['contacts'] = []
    for link in soup.find_all(class_="blue full"):
        if link['href'].startswith("mailto:"):
            tournament['contacts'].append({
                'email': link['href'].replace('mailto:', ''),
                'name': clean_element(link)
            })
        else:
            query = parse_qs(urlparse(link["href"]).query)
            tournament['sites'].append(scrape_tournament_site(
                tab_tourn_id, int(query['site_id'][0])))

    # Scrape past results
    tournament['past_results'] = []
    tournament['webname'] = None
    past_results_elem = soup.find(class_="martop blue full")
    if past_results_elem:
        past_results_link = f'https://www.tabroom.com{past_results_elem["href"]}'
        query = parse_qs(urlparse(past_results_link).query)
        tournament['webname'] = query['webname'][0]
        soup = get_soup(past_results_link)

        for i, row in enumerate(soup.find_all('tr')):
            if i == 0:
                continue
            past_result: TournamentPastResult = {}
            for i, cell in enumerate(row.find_all('td')):
                if i == 0:
                    past_result['year'] = int(clean_element(cell))
                elif i == 1:
                    past_result['name'] = clean_element(cell)
                    tournament_url = cell.find('a')['href']
                    query = parse_qs(urlparse(tournament_url).query)
                    past_result['tab_tourn_id'] = int(query['tourn_id'][0])
            tournament['past_results'].append(past_result)

    # Scrape events
    tournament['event_metadata'] = []
    soup = get_soup(
        f'https://www.tabroom.com/index/tourn/events.mhtml?tourn_id={tab_tourn_id}')
    for link in soup.find_all(class_="blue half nowrap marvertno"):
        query = parse_qs(urlparse(link["href"]).query)
        tournament['event_metadata'].append(
            scrape_event_metadata(tab_tourn_id, int(query['event_id'][0])))

    # Scrape schools
    # TODO: Test with other countries
    # TODO: Filter only for schools in the event
    tournament['schools'] = []
    soup = get_soup(
        f'https://www.tabroom.com/index/tourn/schools.mhtml?tourn_id={tab_tourn_id}')
    for row in soup.find_all(class_="even") + soup.find_all(class_="odd"):
        school: TournamentInstitutionInAttendance = {}
        school['name'], school['state'] = list(
            map(lambda element: clean_element(element), row.find_all()))
        tournament['schools'].append(school)

    # Scrape emails
    tournament['emails'] = []
    soup = get_soup(
        f'https://www.tabroom.com/index/tourn/emails.mhtml?tourn_id={tab_tourn_id}')
    for link in soup.find_all(class_="blue block"):
        query = parse_qs(urlparse(link["href"]).query)
        tournament['emails'].append(scrape_tournament_email(
            tab_tourn_id, int(query['email_id'][0])))

    return tournament
