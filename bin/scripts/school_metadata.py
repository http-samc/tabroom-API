from geopy.geocoders import Nominatim
import json
from typing import Tuple, List, TypedDict
from scraper.utils.soup import get_soup
from scraper.utils.clean import clean_element
from shared.const import API_BASE
import requests
from requests_cache import DO_NOT_CACHE, CachedSession
requests = CachedSession(expire_after=DO_NOT_CACHE)

geolocator = Nominatim(user_agent="Debate Land")

def search_school(name: str) -> List[Tuple[str, str]]:
    soup = get_soup(
        f"https://www.maxpreps.com/schools/{'-'.join(name.split(' '))}")

    results: List[Tuple[str, str]] = []
    for link in soup.find_all('a', class_="school-link"):
        results.append((clean_element(link), link['href']))

    return results


class SchoolData(TypedDict):
    logo: str
    mascot: str
    school_type: str
    colors: List[str]
    location: Tuple[float, float]


def scrape_school(url: str) -> SchoolData:
    data: SchoolData = {}
    soup = get_soup(url)

    metadata_elems = soup.find_all('dd')
    data['school_type'] = clean_element(metadata_elems[0])
    data['mascot'] = clean_element(metadata_elems[2])
    data['colors'] = []
    for wrapper in metadata_elems[3].find_all('span', class_="color"):
        data['colors'].append(
            wrapper.find()['style'].replace('background-color:', ''))
    data['logo'] = soup.find_all('img')[4]['src']
    metadata = json.loads(clean_element(soup.find('script', id="ld+json")))
    location = geolocator.geocode(metadata['address']['streetAddress'])
    data['location'] = (float(location.raw['lat']), float(location.raw['lon']))
    return data


def check_schools(division_id: int):
    division = requests.get(
        f"{API_BASE}/tournaments/divisions/{division_id}?expand=schools").json()

    for school in division['schools']:
        if school['lat'] != None:
            continue  # We already have metadata for the school

        results = search_school(school['name'])
        print(f"Finding metadata for {school['name']}. Select match: ")

        for i, result in enumerate(results):
            print(f"\t[{i + 1}] {result[0]} {result[1]}")

        result = int(input("Select match: "))
        metadata = scrape_school(result[1])

        requests.patch(f"{API_BASE}/schools/{school['id']}", json={
            "logo": metadata['logo'],
            "lat": metadata['location'][0],
            "long": metadata['location'][1],
            "type": "Private" if "private" in metadata['school_type'].lower() else "Public",
            "mascot": metadata['mascot']
        })


if __name__ == "__main__":
    from pprint import pprint
    pprint(search_school("st john's"))
    pprint(scrape_school("https://www.maxpreps.com/il/palatine/fremd-vikings/"))

# from scraper.lib.division import get_division_name

# print(get_division_name(21281, 183907))
