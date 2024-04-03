from bs4 import BeautifulSoup
import requests


def get_soup(url: str) -> BeautifulSoup:
    """Get a BeautifulSoup object for a given URL.

    Args:
        url (str): The URL to make a GET request to.

    Raises:
        TabroomException: Thrown if a the request was not made successfully (no 2xx status code).

    Returns:
        BeautifulSoup: The soup created from the response text.
    """

    res = requests.get(url)

    if not res.status_code >= 200 and not res.status_code < 300:
        raise Exception(f'Error fetching {url} [{res.status_code}]')
    else:
        return BeautifulSoup(res.text, 'html.parser')
