import requests

API_BASE = "https://attendance-ask7.onrender.com/api"

def main():
    print("Fetching and deleting all students...")
    r = requests.get(f"{API_BASE}/students/")
    if r.status_code == 200:
        students = r.json()
        for s in students:
            requests.delete(f"{API_BASE}/students/{s['id']}/")
    
    print("Fetching and deleting all courses...")
    r = requests.get(f"{API_BASE}/courses/")
    if r.status_code == 200:
        courses = r.json()
        for c in courses:
            requests.delete(f"{API_BASE}/courses/{c['id']}/")
    
    print("Database wiped clean!")

if __name__ == "__main__":
    main()
