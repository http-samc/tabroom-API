from clean import clean_element

def get_school(opponent: str) -> str:
    """Determines the school of an opponent.

    Args:
        opponent (str): The opponent to parse the school from.

    Returns:
        str: The school name.
    """
    return " ".join(clean_element(opponent).replace('vs ', '').split(' ')[0:-1]).split(':')[0]
