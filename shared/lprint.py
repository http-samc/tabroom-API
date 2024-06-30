from posthog import Posthog
import os
from datetime import datetime
import time

posthog = Posthog(project_api_key=os.environ['POSTHOG_KEY'], host=os.environ['POSTHOG_HOST'])

def lprint(job_id: int | None, event: str, start: float | None = None, message: str | None = None):
    elapsed = round(time.perf_counter() - start, 1) if start else None
    log_string = f"[{elapsed if elapsed else datetime.now().isoformat()}]\t{event}{f' — {message}' if message else ''}"

    print(log_string)

    # Only send actual job logs to Posthog
    if job_id is not None:
        posthog.capture(f"scraping_job-{job_id}", event=event, timestamp=datetime.now(), properties={
            'elapsed': elapsed,
            'message': message
        })

    with open("logs.txt", "a") as f:
        f.write(log_string + "\n")
