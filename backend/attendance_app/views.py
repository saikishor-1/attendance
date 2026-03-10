from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from django.db import connection
from django.conf import settings
import os
import datetime

@api_view(['GET'])
@permission_classes([AllowAny])
def api_diag(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT tablename, indexname, indexdef FROM pg_indexes WHERE schemaname = 'public'")
            indexes = [{"table": row[0], "name": row[1], "def": row[2]} for row in cursor.fetchall()]
            
            cursor.execute("SELECT name FROM django_migrations WHERE app = 'attendance_app'")
            migrations = [row[0] for row in cursor.fetchall()]
            
        # Check build file
        build_info = "N/A"
        try:
            paths_to_check = [
                os.path.join(settings.BASE_DIR, 'build_check.txt'),
                os.path.join(settings.BASE_DIR, '..', 'build_check.txt'),
                '/opt/render/project/src/backend/build_check.txt'
            ]
            for p in paths_to_check:
                if os.path.exists(p):
                    with open(p, 'r') as f:
                        build_info = f.read().strip()
                        break
            else:
                build_info = "File not found"
        except Exception as e:
            build_info = f"Error: {str(e)}"

        return JsonResponse({
            "status": "success",
            "v": "2026-03-10-2235",
            "build_info": build_info,
            "indexes": indexes,
            "migrations": migrations
        })
    except Exception as e:
        return JsonResponse({"status": "error", "msg": str(e)})

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def drop_unique_index(request):
    """List and drop single-column unique indexes on register_number."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = 'attendance_app_student'
            """)
            indexes = [{"name": row[0], "def": row[1]} for row in cursor.fetchall()]

            cursor.execute("""
                SELECT conname, contype
                FROM pg_constraint
                WHERE conrelid = 'attendance_app_student'::regclass
            """)
            constraints = [{"name": row[0], "type": row[1]} for row in cursor.fetchall()]

            if request.method == 'POST':
                dropped = []
                for idx in indexes:
                    name = idx['name']
                    defn = idx['def']
                    if 'UNIQUE' in defn and 'register_number' in defn and 'course' not in defn:
                        try:
                            cursor.execute(f'DROP INDEX IF EXISTS "{name}" CASCADE')
                            dropped.append(f"Dropped: {name}")
                        except Exception as e:
                            dropped.append(f"FAILED {name}: {str(e)}")

                return JsonResponse({
                    "dropped": dropped,
                    "indexes": indexes,
                    "constraints": constraints
                })

            return JsonResponse({"indexes": indexes, "constraints": constraints})
    except Exception as e:
        return JsonResponse({"status": "error", "msg": str(e)})

from .models import Course, Student, AttendanceRecord
from .serializers import CourseSerializer, StudentSerializer, AttendanceRecordSerializer
from django.utils import timezone
import datetime

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    @action(detail=True, methods=['get'])
    def get_students(self, request, pk=None):
        course = self.get_object()
        students = Student.objects.filter(course=course)
        today = datetime.date.today()
        
        records = AttendanceRecord.objects.filter(course=course, date=today)
        record_map = {r.student_id: r for r in records}
        
        serializer = StudentSerializer(students, many=True)
        data = serializer.data
        
        for item in data:
            student_id = item['id']
            if student_id in record_map:
                record = record_map[student_id]
                item['attendance'] = {
                    'status': record.status,
                    'time_in': record.time_in if record.time_in else '09:00',
                    'time_out': record.time_out if record.time_out else '10:00'
                }
            else:
                item['attendance'] = {
                    'status': 'Present',
                    'time_in': '09:00',
                    'time_out': '10:00'
                }
                
        return Response(data)

    @action(detail=True, methods=['get'])
    def attendance_summary(self, request, pk=None):
        course = self.get_object()
        today = datetime.date.today()
        records = AttendanceRecord.objects.filter(course=course, date=today)
        
        total_students = Student.objects.filter(course=course).count()
        present_count = records.filter(status='Present').count()
        absent_count = records.filter(status='Absent').count()
        leave_count = records.filter(status='Leave').count()
        
        return Response({
            'total_students': total_students,
            'present_count': present_count,
            'absent_count': absent_count,
            'leave_count': leave_count,
            'attendance_percentage': (present_count / total_students * 100) if total_students > 0 else 0
        })

    @action(detail=True, methods=['get'])
    def attendance_report(self, request, pk=None):
        course = self.get_object()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        records = AttendanceRecord.objects.filter(course=course)
        if start_date:
            records = records.filter(date__gte=start_date)
        if end_date:
            records = records.filter(date__lte=end_date)
            
        serializer = AttendanceRecordSerializer(records, many=True)
        return Response(serializer.data)

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceRecordSerializer

    @action(detail=False, methods=['post'])
    def mark_attendance(self, request):
        student_id = request.data.get('student_id')
        course_id = request.data.get('course_id')
        date = request.data.get('date', datetime.date.today())
        status_val = request.data.get('status')
        time_in = request.data.get('time_in')
        time_out = request.data.get('time_out')
        recorded_by = request.data.get('recorded_by', 'Admin')

        attendance, created = AttendanceRecord.objects.update_or_create(
            student_id=student_id,
            course_id=course_id,
            date=date,
            defaults={
                'status': status_val,
                'time_in': time_in,
                'time_out': time_out,
                'recorded_by': recorded_by
            }
        )
        
        serializer = self.get_serializer(attendance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def reset_attendance(self, request):
        course_id = request.data.get('course_id')
        date = request.data.get('date', datetime.date.today())
        
        deleted, _ = AttendanceRecord.objects.filter(
            course_id=course_id, date=date
        ).delete()
        
        return Response({'message': f'Deleted {deleted} attendance records for course {course_id} on {date}.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def bulk_mark_attendance(self, request):
        records = request.data.get('records', [])
        course_id = request.data.get('course_id')
        date = request.data.get('date', datetime.date.today())
        recorded_by = request.data.get('recorded_by', 'Admin')

        records_to_update_or_create = []
        for r in records:
            attendance, _ = AttendanceRecord.objects.update_or_create(
                student_id=r.get('student_id'),
                course_id=course_id,
                date=date,
                defaults={
                    'status': r.get('status', 'Present'),
                    'time_in': r.get('time_in'),
                    'time_out': r.get('time_out'),
                    'recorded_by': recorded_by
                }
            )
            records_to_update_or_create.append(attendance)

        return Response({'message': f'Bulk updated {len(records_to_update_or_create)} records.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def generate_whatsapp_report(self, request):
        course_id = request.data.get('course_id')
        date = request.data.get('date', datetime.date.today())
        
        course = Course.objects.get(id=course_id)
        absent_records = AttendanceRecord.objects.filter(
            course=course, date=date, status='Absent'
        ).select_related('student')
        
        absent_list = [f"{r.student.register_number} - {r.student.name}" for r in absent_records]
        
        message = f"*Attendance Report*\n"
        message += f"Course: {course.course_code} | {course.course_name}\n"
        message += f"Faculty: {course.faculty_name}\n"
        message += f"Date: {date}\n\n"
        message += f"*Absent Students:*\n"
        message += "\n".join(absent_list) if absent_list else "None"
        message += f"\n\nTimestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return Response({'message': message})

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    @action(detail=False, methods=['get', 'post'])
    def drop_unique_index(self, request):
        """Temporary admin endpoint to list and drop unique constraints on register_number."""
        with connection.cursor() as cursor:
            # List all unique indexes/constraints on the student table
            cursor.execute("""
                SELECT indexname, indexdef 
                FROM pg_indexes 
                WHERE tablename = 'attendance_app_student' AND indexdef LIKE '%UNIQUE%'
            """)
            indexes = [{"name": row[0], "def": row[1]} for row in cursor.fetchall()]
            
            cursor.execute("""
                SELECT conname, contype
                FROM pg_constraint
                WHERE conrelid = 'attendance_app_student'::regclass
            """)
            constraints = [{"name": row[0], "type": row[1]} for row in cursor.fetchall()]

            if request.method == 'POST':
                dropped = []
                for idx in indexes:
                    name = idx['name']
                    # Only drop if it's a single-column index on register_number (not the composite unique_together one)
                    if 'register_number' in idx['def'] and 'course' not in idx['def']:
                        try:
                            cursor.execute(f'DROP INDEX IF EXISTS "{name}" CASCADE')
                            dropped.append(name)
                        except Exception as e:
                            dropped.append(f"FAILED {name}: {e}")
                
                return Response({
                    'dropped': dropped,
                    'remaining_indexes': indexes,
                    'constraints': constraints
                })
            
            return Response({'indexes': indexes, 'constraints': constraints})

    @action(detail=False, methods=['post'])
    def bulk_upload(self, request):
        # Implementation for bulk upload from Excel/CSV could go here
        # For now, we'll use a management command as requested
        return Response({'status': 'use management command for now'}, status=status.HTTP_200_OK)
