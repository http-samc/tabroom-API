# Scraping Monorepo

Install
`python3 -m venv env`
`. env/bin/activate`
`pip install -r requirements.txt`

docker run --env INFISICAL_TOKEN=$INFISICAL_TOKEN scraper-0.5.0
docker build -t scraper-0.5.0 .
export INFISICAL_TOKEN=$(infisical login --method=universal-auth --client-id=64c7a609-81f4-4f7b-85ce-ce3ef5e8f14f --client-secret=e8675d44e6cd7768fbb57adbda8c8c90dd2ed43695564ec0f785ea0bc5e93b3e --plain --silent)
