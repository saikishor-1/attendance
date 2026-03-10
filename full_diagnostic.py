import requests

API_BASE = "https://attendance-ask7.onrender.com/api"

def main():
    print("--- FULL DIAGNOSTIC ---")
    courses = requests.get(f"{API_BASE}/courses/").json()
    print(f"Total Courses: {len(courses)}")
    for c in courses:
        students = requests.get(f"{API_BASE}/students/?course={c['id']}").json()
        print(f"ID {c['id']} | {c['course_code']} | {c['course_name']} | Students: {len(students)}")
    
    print("------------------------")
    total_students = requests.get(f"{API_BASE}/students/").json()
    print(f"Total Students in DB: {len(total_students)}")

if __name__ == "__main__":
    main()
