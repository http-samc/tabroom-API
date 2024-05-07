from ..utils.soup import get_soup
from ..utils.clean import clean_element


def get_division_name(tab_tourn_id: int, tab_event_id: int) -> str:
    """Gets the name of a divsion.

    Args:
        tab_tourn_id (int): The unique ID assigned to the tournament, visible in the `tourn_id` query parameter.
        tab_event_id (int): The unique ID assigned to the event, visible in the `event_id` query parameter.

    Returns:
        str: The name of the division, as assigned by Tabroom.
    """

    soup = get_soup(
        f"https://www.tabroom.com/index/tourn/fields.mhtml?tourn_id={tab_tourn_id}&event_id={tab_event_id}")
    h4s = soup.find_all('h4')

    # Fall back to prelim records page if event field page wasn't published
    if len(h4s) < 2:
        soup = get_soup(
            f"https://www.tabroom.com/index/tourn/results/ranked_list.mhtml?event_id={tab_event_id}&tourn_id={tab_tourn_id}")
        h4s = soup.find_all('h4')

    return clean_element(h4s[1]).replace(" Results", "")
