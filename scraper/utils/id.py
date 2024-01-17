import hashlib
from unidecode import unidecode
from typing import List


def get_id(nodes: List[str]) -> str:
    """Gets a unique object ID.

    Args:
        nodes (List[str]): The components to be used in getting the ID.

    Returns:
        str: The 24 character object ID.
    """
    nodes = list(map(unidecode, nodes))
    nodes = sorted(nodes)
    return hashlib.sha224(
        "".join(nodes).lower().encode('utf-8')
    ).hexdigest()[0:24]
