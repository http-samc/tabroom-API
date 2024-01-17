from . import constants


def get_side(side: str) -> str:
    """Gets a standardized side from a raw one.

    Args:
        side (str): The raw side.

    Raises:
        Exception: Thrown if a side cannot be determined.

    Returns:
        str: The parsed side.
    """

    if not len(side):
        return constants.BYE

    side = side[0].upper() + side[1:].lower()

    # Transform Parli
    if side in constants.PRO_SIDES:
        return constants.PRO
    elif side in constants.CON_SIDES:
        return constants.CON
    elif side == constants.BYE:
        return constants.BYE
    else:
        raise Exception(f'Could not standardize side {side}.')
