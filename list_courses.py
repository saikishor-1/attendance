import requests
API_BASE = 'https://attendance-ask7.onrender.com/api'
courses = requests.get(f'{API_BASE}/courses/').json()
for c in courses:
    print(f"{c['id']}: {c['course_name']}")
