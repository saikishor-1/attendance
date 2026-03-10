import requests
import time
import json

URL = 'https://attendance-ask7.onrender.com/api_diag/'

while True:
    try:
        r = requests.get(URL, timeout=10)
        data = r.json()
        if 'applied_migrations' in data:
            print("DIAGNOSTIC IS LIVE!")
            print(json.dumps(data, indent=2))
            break
        else:
            print(f"Waiting for update... Keys present: {list(data.keys())}")
    except Exception as e:
        print(f"Request failed: {e}")
    time.sleep(10)
