from typing import TypedDict, List
from pipelines.transformer import transform_data
from pipelines.uploader import upload_data, clear
from scraper.utils.unscraped_entries import get_unscraped_entries
from scraper.lib.entry import scrape_entry
from scraper.lib.entries import scrape_entries
from scraper.lib.tournament import scrape_tournament
from pipelines.post_upload.index import update_indicies
from pipelines.post_upload.otr import update_otrs
from pipelines.post_upload.stats import update_stats
from pipelines.post_upload.update_search import update_team_index, update_judge_index, update_competitor_index
from shared.lprint import lprint
import traceback
import datetime
from bullmq import Worker, Job

from scraper.lib.division import get_division_name
import requests
import requests_cache

import os
import time
import sys
import asyncio
import csv
requests_cache.install_cache("tabroom_cache")

class ScrapingJobData(TypedDict):
    class Group(TypedDict):
        id: int | None
        nickname: str

    class Season(TypedDict):
        id: int | None
        year: int

    class Division(TypedDict):
        class Circuit(TypedDict):
            id: int | None
            geographyName: str

        tabEventId: int
        event: str
        classification: str
        circuits: List[Circuit]
        firstElimRound: str | None
        tocFullBidLevel: str | None
        tournBoost: float

    group: Group
    season: Season
    tabTournId: int
    divisions: List[Division]

async def processTournament(data: ScrapingJobData):
    start = time.perf_counter()

    for i, division in enumerate(data['divisions']):
        lprint(
            f"[{round(time.perf_counter() - start, 1)}]: Scraping {i+1}/{len(data['divisions'])}: {data['season']['year']} {data['group']['nickname']} {division['classification']} {division['event']}")

        tournament = scrape_tournament(data['tabTournId'])
        division_name = get_division_name(data['tabTournId'], division['tabEventId'])
        entries = []

        for entryFragment in scrape_entries(data['tabTournId'], division['tabEventId']):
            entry = scrape_entry(data['tabTournId'], entryFragment)
            entries.append(entry)

        unscraped_entries = get_unscraped_entries(entries)

        while unscraped_entries:
            lprint(f"[{round(time.perf_counter() - start, 1)}]: Aggregating unscraped entries")
            for tab_entry_id in unscraped_entries:
                entries.append(scrape_entry(data['tabTournId'], {
                    'code': None,
                    'location': None,
                    'school': None,
                    'tab_competitor_ids': [],
                    'tab_entry_id': tab_entry_id
                }))

            unscraped_entries = get_unscraped_entries(entries)

        data = transform_data(data['tabTournId'], division['tabEventId'], data['group']['nickname'], division['event'], tournament, entries, list(map(lambda c: c['geographyName'], division['circuits'])),
                              data['season']['year'], division['tournBoost'], division['classification'], division_name, division['firstElimRound'], division['tocFullBidLevel'], division['event'] == "PublicForum")

        upload_data(data)
        lprint(f"[{round(time.perf_counter() - start, 1)}]: Updating OTRs")
        update_otrs(division['tabEventId'])
        lprint(f"[{round(time.perf_counter() - start, 1)}]: Updating Indicies")
        update_indicies(division['tabEventId'])
        lprint(f"[{round(time.perf_counter() - start, 1)}]: Updating Stats")
        update_stats(division['tabEventId'])
        lprint(f"[{round(time.perf_counter() - start, 1)}]: Re-indexing Search Database — Competitors")
        update_competitor_index()
        lprint(f"[{round(time.perf_counter() - start, 1)}]: Re-indexing Search Database — Teams")
        update_team_index()
        lprint(f"[{round(time.perf_counter() - start, 1)}]: Re-indexing Search Database — Judges")
        update_judge_index()
        lprint(f"[{round(time.perf_counter() - start, 1)}]: Done")

async def processJob(job: Job, token: str):
    lprint(f'Starting job: {job.name} {datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")}')

    try:
        await processTournament(job.data)
    except Exception as e:
        lprint("ERROR")
        lprint(traceback.format_exc())
        raise Exception()

async def processCSV(path: str):
    DATA = []

    with open(path, "r") as f:
        table = csv.reader(f)

        for row in table:
            DATA.append(row)

    for tourn in DATA:
        try:
            await processTournament({
                'group': {
                    'id': None,
                    'nickname': tourn[0]
                },
                'season': {
                    'id': None,
                    'year': int(tourn[5])
                },
                'tabTournId': int(tourn[1]),
                'divisions': [{
                    'event': tourn[3],
                    'circuits': list(map(lambda c: {
                        'id': None,
                        'geographyName': c
                    }, tourn[6].split(";"))),
                    'tabEventId': int(tourn[2]),
                    'classification': tourn[4],
                    'firstElimRound': None if tourn[7] == "None" else tourn[7],
                    'tocFullBidLevel': None if tourn[8] == "None" else tourn[8],
                    'tournBoost': float(tourn[9]),
                }]
            })
        except Exception as e:
            lprint("ERROR")
            lprint(traceback.format_exc())
            continue

async def startWorker():
    lprint("Starting worker...")
    worker = Worker("scraping", processJob, { "connection": os.environ['REDIS_URL'] })

    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    if len(sys.argv) > 1 and '--file' in sys.argv and sys.argv.index('--file') > 0 and sys.argv.index('--file') < len(sys.argv) - 1:
        asyncio.run(processCSV(sys.argv[sys.argv.index('--file') + 1]))
    else:
        asyncio.run(startWorker())
