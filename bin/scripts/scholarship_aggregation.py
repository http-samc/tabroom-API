from requests_cache import DO_NOT_CACHE, CachedSession
import json
from pypdf import PdfMerger
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from shared.const import API_BASE

requests = CachedSession(expire_after=DO_NOT_CACHE)

BLACKLIST = [
    "user_2b4alIRBuNAPScbMPN8r5BnJiwv",
    "user_2bXg38yZPlGe1W687TtAzAee3DE",
    "user_2e93zuZHd85tlMZbugWFmbvA0Uk",
    "user_2eIpeaRn8xjWiBbwg0SLkC5Spz4",
    "user_2eKdncKI7dISOQaITRNkZapqLhh"
]

def download_file(url: str) -> str:
    filename = f"./data/temp/{url.split('/')[-1]}.pdf"
    res = requests.get(url)
    with open(filename, "wb") as f:
        f.write(res.content)

    return filename

users = requests.get(f"{API_BASE}/users").json()

applications = []

for user in users:
    if user['scholarshipApplication'] is None or user['clerkUuid'] in BLACKLIST:
        continue

    application = json.loads(user['scholarshipApplication']['toJSON'])
    application['uuid'] = user['clerkUuid']

    applications.append(application)

with open("./data/applications.csv", "w") as f:
    f.write(','.join(applications[0].keys()))
    f.write('\n')
    for application in applications:
        f.write(','.join(str(x) for x in application.values()))
        f.write('\n')

for i, application in enumerate(applications):
    print(f"Processing application {i + 1}/{len(applications)}")
    transcriptPath = download_file(application['transcriptFile'])
    essayPath = download_file(application["essayFile"])
    supplementPath = download_file(application["supplementFile"]) if application["supplementFile"] else None
    achievementsPath = download_file(application["achievementsFile"]) if application["achievementsFile"] else None
    coverText = f"""Applicant ID: {application['uuid']}\nApplication Type: {application['scholarshipType'].upper()}\n\n<a href="https://forms.gle/cTZY6wtM4qbgdUkH9" underline=true textcolor="blue">Application Rating Google Form</a>\n\nEach component (essays, etc.) has its own rating field from 1-10 (1 is the lowest rating,| and 10 is the highest rating) in the Google Form. The overall rating is a composite of different factors automatically weighted into a composite score you can view in the rating spreadsheet. Please do not worry about giving lower or higher ratings than other readers; we pull the top two applicants from YOUR pool, and ratings are not a part of the committee review.\n\nSTART APPLICANT FILE \nEssay 1: This essay will only be read by your assigned readers and will not be shared publicly without your consent. Please respond to the following prompt:\n\nPrompt: Choose any societal issue you are passionate about and present a well-researched argument in an essay not exceeding 500 words. Your essay should demonstrate your ability to think critically, analyze information, and effectively communicate your ideas. We are looking for students who can think outside the box and provide unique perspectives on any issue you deem necessary."""

    coverPath = "./data/temp/cover_page.pdf"
    cover_page = SimpleDocTemplate(coverPath, pagesize=LETTER)
    cover_page.build([Paragraph(coverText.replace("\n", "<br />"), getSampleStyleSheet()['Normal'])])

    merger = PdfMerger()

    merger.append(coverPath)
    merger.append(essayPath)

    if supplementPath:
        merger.append("./data/application/page_2.pdf")
        merger.append(supplementPath)

    merger.append("./data/application/page_3.pdf")
    merger.append(achievementsPath)

    merger.append("./data/application/page_4.pdf")
    merger.append(transcriptPath)

    merger.write(f"./data/applications/{application['scholarshipType']}/{application['scholarshipType'].upper()} Scholarship—ID:{application['uuid']}.pdf")
    merger.close()