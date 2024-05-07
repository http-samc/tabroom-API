import numpy as np

def apply_iqr(x: list) -> list:
    """Filters a list by removing outliers
    Args:
        x (list): The list to filter using the standard IQR of 1.5.

    Returns:
        list: The outlier-filtered list.
    """

    a = np.array(x)
    upper_quartile = np.percentile(a, 75)
    lower_quartile = np.percentile(a, 25)
    IQR = (upper_quartile - lower_quartile) * 1.5
    quartileSet = (lower_quartile - IQR, upper_quartile + IQR)
    resultList = []
    for y in a.tolist():
        if y >= quartileSet[0] and y <= quartileSet[1]:
            resultList.append(y)
    return resultList