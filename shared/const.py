import os

API_BASE = "http://localhost:8080/core" if os.environ['ENVIRONMENT'] == "development" else "https://api.debate.land/core"