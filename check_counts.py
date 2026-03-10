import requests

API_BASE = "https://attendance-ask7.onrender.com/api"

def main():
    print("Checking course student counts...")
    courses = requests.get(f"{API_BASE}/courses/").json()
    for c in courses:
        students = requests.get(f"{API_BASE}/students/?course={c['id']}").json()
        print(f"Course ID {c['id']} ({c['course_name']}): {len(students)} students")

if __name__ == "__main__":
    main()
