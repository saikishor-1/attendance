from rest_framework import serializers
from .models import Course, Student, AttendanceRecord

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    # CRITICAL: Explicitly declare register_number with no validators.
    # DRF auto-generates a UniqueValidator for this field when it detects
    # a single-column DB UNIQUE index. This overrides that auto-generation
    # so that the same student can enroll in multiple courses.
    register_number = serializers.CharField(max_length=20, validators=[])

    class Meta:
        model = Student
        fields = '__all__'
        # Only enforce uniqueness as a (register_number, course) pair.
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
