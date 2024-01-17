from typing import List, TypedDict
from urllib.parse import urlparse, parse_qs
from ..utils.soup import get_soup
from ..utils.clean import clean_element


class Location(TypedDict):
    state: str | None
    country: str


class EntryFragment(TypedDict):
    school: str | None
    location: Location | None
    code: str
    tab_entry_id: int
    tab_competitor_ids: List[int]


def scrape_entries(tab_tourn_id: int, tab_event_id: int) -> List[EntryFragment]:
    """Gets a list of all entries in a tournament using the "Entries" and "Prelim Records" pages.

    Args:
        tab_tourn_id (int): The unique ID assigned to the tournament, visible in the `tourn_id` query parameter.
        tab_event_id (int): The unique ID assigned to the event, visible in the `event_id` query parameter.

    Returns:
        List[EntryFragment]: All pertinent entry information for each team.
    """

    # Try scraping event field page
    soup = get_soup(
        f"https://www.tabroom.com/index/tourn/fields.mhtml?tourn_id={tab_tourn_id}&event_id={tab_event_id}")
    rows = soup.find_all('tr')

    # Fall back to prelim records page (no location data) if event field page wasn't published
    if not len(rows):
        soup = get_soup(
            f"https://www.tabroom.com/index/tourn/results/ranked_list.mhtml?event_id={tab_event_id}&tourn_id={tab_tourn_id}")
        rows = soup.find_all('tr')

    headers = list(map(lambda e: clean_element(e), rows[0].find_all('th')))
    fragments: List[EntryFragment] = []

    for row in rows[1:]:
        fragment: EntryFragment = {
            'location': None,
            'tab_competitor_ids': [],
        }

        isWaitlisted = False
        for i, cell in enumerate(row.find_all('td')):
            text = clean_element(cell)
            match headers[i]:
                case "Status":
                    if text == "WL":
                        isWaitlisted = True
                case "School":
                    fragment['school'] = text
                case "Location":
                    nodes = text.split("/")
                    fragment['location'] = {}
                    if len(nodes) == 1:
                        fragment['location']['state'] = None
                        fragment['location']['country'] = nodes[0]
                    elif len(nodes) == 2:
                        fragment['location']['state'] = nodes[0]
                        fragment['location']['country'] = nodes[1]
                case "Code":
                    fragment['code'] = text
                case "Record":
                    query = parse_qs(
                        urlparse(f"https://www.tabroom.com{cell.find('a')['href']}").query)
                    fragment['tab_competitor_ids'] = list(
                        map(lambda p: int(p[0]), query.values()))

        if not isWaitlisted:
            fragments.append(fragment)

    soup = get_soup(
        f'https://www.tabroom.com/index/tourn/results/ranked_list.mhtml?event_id={tab_event_id}&tourn_id={tab_tourn_id}').find('table', {'id': 'ranked_list'})
    rows = soup.find_all('tr')
    headers = list(map(lambda e: clean_element(e), rows[0].find_all('th')))

    for row in rows[1:]:
        for i, cell in enumerate(row.find_all('td')):
            if headers[i] != "Code":
                continue
            tab_entry_id = int(parse_qs(urlparse(
                f"https://www.tabroom.com{cell.find('a')['href']}").query)['entry_id'][0])
            code = clean_element(cell)
            for fragment in fragments:
                if fragment['code'] == code:
                    fragment['tab_entry_id'] = tab_entry_id

    return fragments
