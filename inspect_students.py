import requests
API_BASE = 'https://attendance-ask7.onrender.com/api'
res = requests.get(f'{API_BASE}/students/?course=8')
students = res.json()
print(f"Total students for course 8 via filter: {len(students)}")
if students:
    print("First student raw data:")
    print(students[0])
