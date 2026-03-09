from rest_framework import serializers
from .models import Course, Student, AttendanceRecord

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class AttendanceRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.name')
    register_number = serializers.ReadOnlyField(source='student.register_number')
    
    class Meta:
        model = AttendanceRecord
        fields = '__all__'
