import json
import requests
from pymongo import MongoClient

client = MongoClient(env.MONOG_URI)

db = client[env.NSD_DB]
collection = db[env.NSD_COLLECTION]

nsd_emails = []
for document in collection.find({}, {'email': 1, '_id': 0}):
    if 'email' in document:
        nsd_emails.append(document['email'])


dl_emails = list(map(lambda e: e['email'], requests.get(
    "http://localhost:8080/core/v1/notification-subscribers").json()))

unconverted_nsd = []
unconverted_dl = []

for e in nsd_emails:
    if e not in dl_emails:
        unconverted_dl.append(e)

for e in dl_emails:
    if e not in nsd_emails:
        unconverted_nsd.append(e)


with open('data.json', 'w') as f:
    json.dumps({
        'nsd': unconverted_nsd,
        'dl': unconverted_dl
    })
