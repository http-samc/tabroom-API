import math

def get_deflator(x: int) -> float:
    """Gets a targeted deflator for an OTR score.

    Args:
        x (int): The number of tournaments attended.

    Returns:
        float: The deflator (decimal from 0 to 1).
    """

    N = 1
    Y0 = 0.15
    K = 1.3

    return round(N/((N/Y0 - 1)*math.pow(math.e, -K*x) + 1), 2)