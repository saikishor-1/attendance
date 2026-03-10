import requests
import json

API_BASE = "https://attendance-ask7.onrender.com/api"

# Student from course 7: 99240040649 | MULLAGURI MANI KUMAR
reg_no = "99240040649"
name = "MULLAGURI MANI KUMAR"

# Target courses 8-12
target_courses = [8, 9, 10, 11, 12]

print(f"Testing multi-course enrollment for student {reg_no}...")

for c_id in target_courses:
    student_data = {
        "register_number": reg_no,
        "name": name,
        "course": c_id,
        "section": "A"
    }
    print(f"Attempting to enroll in course {c_id}...")
    res = requests.post(f"{API_BASE}/students/", json=student_data)
    if res.status_code == 201:
        print(f"SUCCESS: Enrolled student {reg_no} into course {c_id}!")
    else:
        print(f"FAILED: Status {res.status_code}")
        print(f"Response: {res.text}")
