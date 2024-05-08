import os
from bullmq import Queue
from typing import List
import asyncio

async def main(states: List[str]):
    queue = Queue("scraping", {
        "connection": os.environ['REDIS_URL']
    })

    total = 0
    for state in states:
        deleted = await queue.clean(10, 1000, 'completed')
        print(f"Deleted {len(deleted)} jobs with state '{state}'")
        total += len(deleted)

    print(f"Deleted {total} total jobs.")

    await queue.close()

if __name__ == "__main__":
    asyncio.run(main(["failed", "completed", "delayed", "active"]))