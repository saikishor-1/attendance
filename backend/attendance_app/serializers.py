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
        # Remove any auto-generated per-field unique validator on register_number.
        # Uniqueness should only be enforced as (register_number, course) pair.
        # DRF may auto-generate a UniqueValidator for register_number from a
        # stale model state; we override validators to prevent that.
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Student.objects.all(),
                fields=['register_number', 'course'],
                message='This student is already enrolled in this course.'
            )
        ]

class AttendanceRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.name')
    register_number = serializers.ReadOnlyField(source='student.register_number')
    
    class Meta:
        model = AttendanceRecord
        fields = '__all__'
