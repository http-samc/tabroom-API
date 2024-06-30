import os

# API_BASE = "http://localhost:8080/core" if os.environ['RUNTIME'] == "local" else f"{os.environ['REMOTE_API_URL']}/core"
API_BASE = os.environ['REMOTE_API_URL'] + '/core'
# API_BASE = "http://localhost:8080/core"