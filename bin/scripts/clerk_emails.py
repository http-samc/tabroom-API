from requests_cache import DO_NOT_CACHE, CachedSession
import os

requests = CachedSession(expire_after=DO_NOT_CACHE)

users = []
offset = 0 

while True:
    batch = requests.get(f"https://api.clerk.com/v1/users?limit=500&offset={500 * offset}&order_by=-created_at", headers={
        'Authorization': f'Bearer {os.environ["CLERK_KEY"]}'
    }).json()

    for user in batch:
        users.append(user)

    if len(batch) < 500:
        break
    else:
        offset += 1

csv = "First Name,Email"

for user in users:
    csv += f"\n{user['unsafe_metadata']['first']},{user['email_addresses'][0]['email_address']}"

with open("data/users.csv", "w") as f:
    f.write(csv)

print(f"Wrote data for {len(users)} users to /data/users.csv!")