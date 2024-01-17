from pipelines.transformer import transform_data
from pipelines.uploader import upload_data, clear
from scraper.utils.unscraped_entries import get_unscraped_entries
from scraper.lib.entry import scrape_entry
from scraper.lib.entries import scrape_entries
from scraper.lib.tournament import scrape_tournament
from pipelines.post_upload.index import update_indicies
from pipelines.post_upload.otr import update_otrs
from pipelines.post_upload.stats import update_stats

from scraper.lib.division import get_division_name
import requests
import requests_cache

# TODO: Allow multiple events to be scraped at once
import json
import time
import csv
requests_cache.install_cache("tabroom_cache")

# clear()

DATA = []

start = time.perf_counter()

with open("data.csv", "r") as f:
    table = csv.reader(f)

    for row in table:
        DATA.append(row)

for tourn in DATA:
    print(
        f"Scraping {tourn[0]} {tourn[3]} {tourn[4]} at {round(time.perf_counter() - start, 1)}")
    NICKNAME = tourn[0]
    TOURN = int(tourn[1])
    EVENT = int(tourn[2])
    FORMAT = tourn[3]
    CLASSIFICATION = tourn[4]
    SEASON = int(tourn[5])
    CIRCUITS = tourn[6].split(";")
    FIRST_ELIM_ROUND = None if tourn[7] == "None" else tourn[7]
    TOC_FULL_BID_LEVEL = None if tourn[8] == "None" else tourn[8]
    BOOST = float(tourn[9])
    HAS_PARTIAL_BIDS = True if FORMAT == "PublicForum" else False

    tournament = scrape_tournament(TOURN)
    division_name = get_division_name(TOURN, EVENT)
    entries = []

    for entryFragment in scrape_entries(TOURN, EVENT):
        entry = scrape_entry(TOURN, entryFragment)
        entries.append(entry)

    unscraped_entries = get_unscraped_entries(entries)

    while unscraped_entries:
        print("Aggregating unscraped entries...")
        for tab_entry_id in unscraped_entries:
            entries.append(scrape_entry(TOURN, {
                'code': None,
                'location': None,
                'school': None,
                'tab_competitor_ids': [],
                'tab_entry_id': tab_entry_id
            }))

        unscraped_entries = get_unscraped_entries(entries)

    data = transform_data(TOURN, EVENT, NICKNAME, FORMAT, tournament, entries, CIRCUITS,
                          SEASON, BOOST, CLASSIFICATION, division_name, FIRST_ELIM_ROUND, TOC_FULL_BID_LEVEL, HAS_PARTIAL_BIDS)

    # with open('t.json', 'w') as f:
    #     json.dump(data, f)
    upload_data(data)
    print(f"Updating OTRs at {round(time.perf_counter() - start, 1)}")
    update_otrs(EVENT)
    print(f"Updating Indicies at {round(time.perf_counter() - start, 1)}")
    update_indicies(EVENT)
    print(f"Updating Stats at {round(time.perf_counter() - start, 1)}")
    update_stats(EVENT)
    print(f"Done at {round(time.perf_counter() - start, 1)}")
