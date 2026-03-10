import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_project.settings')
django.setup()

def main():
    with connection.cursor() as cursor:
        # Query for all unique indexes on the student table
        cursor.execute(\"\"\"
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'attendance_app_student'
        \"\"\")
        indexes = cursor.fetchall()
        print(\"Indexes on attendance_app_student:\")
        for name, definition in indexes:
            print(f\" - {name}: {definition}\")

if __name__ == \"__main__\":
    main()
