from bs4 import PageElement
from unidecode import unidecode

def clean_text(text: str) -> str:
    """Sanatizes text.

    Args:
        text (str): Any string.

    Returns:
        str: A string with excess whitespaces removed.
    """
    return unidecode(' '.join(text.strip().split()))

def clean_element(element: PageElement) -> str:
    """Gets the text of a BeautifulSoup4 element and cleans it
    with clean_text.

    Args:
        element (PageElement): A BeautifulSoup4 element.

    Returns:
        str: The cleaned text of the element.
    """

    return clean_text(element.get_text())