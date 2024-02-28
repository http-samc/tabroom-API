import requests

API_BASE = "http://localhost:8080/core/v1"

data = requests.post(f"{API_BASE}/paradigm-emails/advanced/findMany", json={
    "include": {
        "paradigms": {
            "select": {
                "judge": {
                    "select": {
                        "name": True,
                        "id": True
                    }
                }
            },
            "take": 1
        }
    }
}).json()

print(len(data))

std = []

for hit in data:
    names = hit['paradigms'][0]['judge']['name'].split(" ")
    if not len(names) >= 2:
        continue

    std.append({
        'first': names[0],
        'last': " ".join(names[1:]),
        'url': f"https://debate.land/judges/{hit['paradigms'][0]['judge']['id']}",
        'email': hit['email']
    })

print(len(std))

txt = ""

for row in std:
    txt += f"{row['first']},{row['last']},{row['email']},{row['url']}\n"

with open("t.csv", "w") as f:
    f.write(txt)

print(std[0])
