import requests
import json

API_BASE = "https://attendance-ask7.onrender.com/api"

courses_data = [
    {"course_code": "212CSE2101", "course_name": "Discrete Mathematics", "faculty_name": "MS. B. SHUNMUGA PRIYA", "credits": 4},
    {"course_code": "212CSE2303", "course_name": "Software Engineering", "faculty_name": "Mr. B. SHANMUGA RAJU", "credits": 3},
    {"course_code": "212CSE2304", "course_name": "Machine Learning", "faculty_name": "Mr. SIVAMURUGAN CHELLADURAI", "credits": 4},
    {"course_code": "212CSE2305", "course_name": "Database Management Systems", "faculty_name": "Mrs. KARDEEPA. P", "credits": 3},
    {"course_code": "213CSE2301", "course_name": "Predictive Analytics", "faculty_name": "Dr. J. BHARATH SINGH", "credits": 3},
    {"course_code": "215EXS2201", "course_name": "Design-Build", "faculty_name": "Mrs. KARDEEPA. P", "credits": 2},
]

students_raw = """1 | 99240040649 | MULLAGURI MANI KUMAR
2 | 99240040650 | KONDREDDY VAMSI VARDHAN REDDY
3 | 99240040651 | MODUPALLI SATHWIKA
4 | 99240040652 | VEMPALAKULA CHANDRA VAMSI
5 | 99240040653 | KOTAKONDA SHIVA PRASAD
6 | 99240040655 | MUDDAM AKHIL YADAV
7 | 99240040656 | KOMARAVELLY RAKESH
8 | 99240040657 | NAKKA UMA MAHESWARA RAO
9 | 99240040659 | YARLAGADDA SRI SAI TEJA
10 | 99240040660 | NALLIMILLI SASIDHARA REDDY
11 | 99240040661 | NALLAM VENKATA VINAY
12 | 99240040663 | NAPA GOWTHAM KUMAR
13 | 99240040665 | KONANKI CHARITHA
14 | 99240040666 | NARABOYINA MOUNIKA
15 | 99240040667 | NALLURI LAKSHMI CHARAN CHOWDARY
16 | 99240040668 | YELAMASETTI NITHIN
17 | 99240040669 | NARAYANA GARI VAISHNAVI
18 | 99240040670 | NAMMI NAVADEEP
19 | 99240040671 | VEGESNA MANOJ SAI VARMA
20 | 99240040672 | NARISETTI HEMA SEDHARDH
21 | 99240040673 | NANDAMURI MEGHANA
22 | 99240040674 | YERAKARAJU R N M SRINIVASA VARMA
23 | 99240040675 | NAMBULA AKSHAYA
24 | 99240040676 | NARA HARSHITHA SAI
25 | 99240040677 | YEDDULA PAVAN KUMAR REDDY
26 | 99240040678 | NAYANA SREE T G
27 | 99240040679 | NALLURI AKSHARAYAM CHOWDARY
28 | 99240040680 | KOLLE NAGENDRA BABU
29 | 99240040681 | PANUGANTI V S M RISHI KARTHIKEYA
30 | 99240040682 | PAMARTHI SAI SANDEEP
31 | 99240040683 | GUNAPATI VENKATA PRADEEP REDDY
32 | 99240040684 | S PAVITHRA
33 | 99240040685 | PAMPANA SAI KISHOR
34 | 99240040686 | PALEMPATI HEMANTH SRIRAM SAI
35 | 99240040687 | DADIREDDY GARI VARSHITHA
36 | 99240040688 | PALADUGU SAI PRASANNA
37 | 99240040689 | PASUNOORI SAI MURALIDHAR REDDY
38 | 99240040691 | PATIBANDLA MOKSHAGNA
39 | 99240040692 | GORLA MOHAN KRISHNA
40 | 99240040693 | PAMIDI MOHAMMAD KHALID
41 | 99240040695 | PATCHALA JOHN WESLEY
42 | 99240040696 | DASARI GANGA DILEEP REDDY
43 | 99240040697 | PATNAM SRI VENKATA SAMBASIVA RAO
44 | 99240040698 | PATIVADA YESWANTH VENKATA KUMAR
45 | 99240040700 | PALADUGU VENKATA PRAVEEN
46 | 99240040701 | PANDLA HARSHAVARDAN
47 | 99240040702 | PANGULURI NARENDRA SAI
48 | 99240040703 | SHAIK THANISH BASHEERUDDIN
49 | 99240040704 | PATTEM HARSHIKA SURYANJALI
50 | 99240040705 | PATIL NIHARIKA
51 | 99240040706 | GOPIREDDY SRI KANTH REDDY
52 | 99240040707 | PAMARTHI DINESH GOVIND
53 | 99240040708 | SHAIK MOHAMMAD AFRID
54 | 99240040709 | VEERAVALLI HEMANTH CHOWDARY
55 | 99240040710 | PUDU SATHEESH KUMAR
56 | 99240040711 | PUTSALA KUMAR KIRAN
57 | 99240040712 | PURAM AKHILA
58 | 99240040713 | PUNAGANTI BHAGYATEJ
59 | 99240040714 | RAHNT KUMAR
60 | 99240040715 | PUTTA DWARAKANATHA REDDY
61 | 99240040716 | PURAMSETTI VEERA VENKATA NAGA LAKSHMI DEVI
62 | 99240040717 | PUTLURU PRASHANTHI
63 | 99240040719 | YARLAGADDA BHAVESH
64 | 99240040720 | PRATHAPANI LAXMAN KUMAR
65 | 99240040721 | G SANTHOSH REDDY
66 | 99240040723 | PUVVADA GURU BRAHMAM
67 | 99240040724 | PUJARI PUNITH KUMAR
68 | 99240040725 | K BHUVANESWAR"""

def main():
    print("Uploading courses...")
    course_ids = []
    
    for c in courses_data:
        res = requests.post(f"{API_BASE}/courses/", json=c)
        if res.status_code == 201:
            print(f"Created course: {c['course_name']}")
            course_ids.append(res.json()['id'])
        else:
            print(f"Failed to create course {c['course_name']}: {res.text}")
            # Try to get it if it already exists
            existing = requests.get(f"{API_BASE}/courses/")
            for ex_c in existing.json():
                if ex_c.get('course_code') == c['course_code']:
                    course_ids.append(ex_c['id'])

    if not course_ids:
        print("Error: No courses found or created.")
        return

    lines = [l for l in students_raw.split('\n') if l.strip()]
    
    for c_id in course_ids:
        if c_id == 7:
            print(f"Skipping course ID 7 (already populated)...")
            continue
        print(f"\nUploading students for course ID {c_id}...")
        success_count = 0
        for line in lines:
            parts = line.split('|')
            if len(parts) == 3:
                reg_no = parts[1].strip()
                name = parts[2].strip()
                
                student_data = {
                "register_number": reg_no,
                    "name": name,
                    "course": c_id,
                    "section": "A"
                }
                res = requests.post(f"{API_BASE}/students/", json=student_data)
                if res.status_code == 201:
                    success_count += 1
                else:
                    print(f"Failed to create student {reg_no} for course {c_id}: {res.text}")
        print(f"Successfully uploaded {success_count} students to course ID {c_id}!")

if __name__ == "__main__":
    main()
