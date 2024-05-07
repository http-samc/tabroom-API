from typing import TypedDict, List
from ..utils.soup import get_soup
from ..utils.clean import clean_element

class RoundTopic(TypedDict):
    round_name: str
    topic: str

def get_topics(tab_tourn_id: int, tab_event_id: int) -> List[RoundTopic]:
    """Gets topics for events that change them on the round-level.

    Args:
        tab_tourn_id (int): The unique ID assigned to the tournament, visible in the `tourn_id` query parameter.
        tab_event_id (int): The unique ID assigned to the tournament, visible in the `event_id` query parameter.

    Returns:
        List[RoundTopic]: The parsed topic information for each round.
    """