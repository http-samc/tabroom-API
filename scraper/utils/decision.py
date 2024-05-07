from . import constants

def get_decision(side: str, vote_type: str) -> str:
    """Gets the side a judge voted for.

    Args:
        side (str): Pro || Con || Aff || Neg || Bye
        vote_type (str): W || L || Win || Loss

    Returns:
        str: Pro || Con || Aff || Neg || Bye
    """

    if not side in constants.PRO_SIDES + constants.CON_SIDES + [constants.BYE]:
        raise Exception(
            f'Unrecognized competitor side choice: {side}'
        )

    elif side == constants.BYE:
        return None

    if vote_type == 'W' or vote_type == "Win": return side

    if side in constants.PRO_SIDES:
        return constants.CON
    return constants.PRO
