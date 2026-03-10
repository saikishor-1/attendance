from django.db import models

class Course(models.Model):
    course_code = models.CharField(max_length=20, unique=True)
    course_name = models.CharField(max_length=200)
    faculty_name = models.CharField(max_length=100)
    credits = models.IntegerField(default=3)

    def __str__(self):
        return f"{self.course_code} - {self.course_name}"

class Student(models.Model):
    roll_id = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='students')
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    section = models.CharField(max_length=50) # section/batch
    enrollment_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Active') # Active/Inactive
    guardian_name = models.CharField(max_length=100, null=True, blank=True)
    guardian_phone = models.CharField(max_length=20, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('roll_id', 'course')

    def __str__(self):
        return f"{self.roll_id} - {self.name}"

class AttendanceRecord(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Leave', 'Leave'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    time_in = models.TimeField(null=True, blank=True)
    time_out = models.TimeField(null=True, blank=True)
    recorded_by = models.CharField(max_length=100) # faculty name
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course', 'date')

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"
