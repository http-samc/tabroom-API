from typing import List
from ..lib.entry import Entry

def get_unscraped_entries(entries: List[Entry]) -> List[int]:
    """Returns a list of all unscraped entries by parsing
    every single round and looking for tab_entry_ids without
    corresponding entries.

    Args:
        entries (List[Entry]): The list of (presumably) all entries.

    Returns:
        List[int]: A list of tab_entry_ids representing the entries
        that were at the tournament but not included in the supplied list
        of scraped entries.
    """

    known_entries: List[int] = [entry['tab_entry_id'] for entry in entries]
    unknown_entries: List[int] = []

    for entry in entries:
        for round in entry['rounds']:
            if not round['opponent']: continue
            opp_tab_id = round['opponent']['tab_entry_id']
            if opp_tab_id not in known_entries and opp_tab_id not in unknown_entries:
                unknown_entries.append(opp_tab_id)

    return unknown_entries