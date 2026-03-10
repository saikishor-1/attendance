import requests

API_BASE = "https://attendance-ask7.onrender.com/api"

def main():
    print("Fetching all students...")
    r = requests.get(f"{API_BASE}/students/")
    if r.status_code == 200:
        students = r.json()
        print(f"Deleting {len(students)} students...")
        for s in students:
            requests.delete(f"{API_BASE}/students/{s['id']}/")
        print("Success!")
    else:
        print("Failed to fetch students.")

if __name__ == "__main__":
    main()
