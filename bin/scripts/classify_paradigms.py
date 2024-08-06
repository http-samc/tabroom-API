from requests_cache import DO_NOT_CACHE, CachedSession

requests = CachedSession(expire_after=DO_NOT_CACHE)
from scraper.lib.paradigm import classify_paradigm

def getParadigmBatch(only_unclassified: bool, batchNumber: int, size: int = 500,):
    paradigms = requests.post("https://api.debate.land/core/paradigms/advanced/findMany", json={
        "where": {
            "flowRating": {
                "lt": 1
            },
            "progressiveRating": {
                "lt": 1
            }
        },
        "select": {
            "id": True,
            "text": True
        },
        "take": size,
        "skip": size * batchNumber
    }).json()

    return paradigms

def classify_paradigms(only_unclassified: bool = True):
    batchNumber = 0

    while True:
        batch = getParadigmBatch(only_unclassified, batchNumber)
        print(f"Classifying batch #{batchNumber + 1} of size {len(batch)}.")

        for paradigm in batch:
            try:
                flowRating, progressiveRating = classify_paradigm(paradigm['text'])
                res = requests.patch(f"https://api.debate.land/core/paradigms/{paradigm['id']}", json={
                    "flowRating": flowRating,
                    "progressiveRating": progressiveRating
                })
                print(flowRating, progressiveRating)
                if res.status_code != 200:
                    raise Exception("Failed patch call.")
            except Exception as e:
                print("Error classifying", e)

        if len(batch) < 500:
            break
        batchNumber += 1
