from django.db import models
from django.conf import settings
from django.utils import timezone

class Department(models.Model):
    name = models.CharField(max_length=100)
    building = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    course_id = models.CharField(max_length=20, unique=True)
    course_name = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                 limit_choices_to={'role': 'teacher'}, related_name='courses_taught')
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True,
                                       limit_choices_to={'role': 'student'}, related_name='enrolled_courses')
    description = models.TextField(blank=True)
    credit_hours = models.DecimalField(max_digits=3, decimal_places=1, default=3.0)

    def __str__(self):
        return f"{self.course_id} - {self.course_name}"

class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                     limit_choices_to={'role': 'teacher'}, related_name='uploaded_assignments')
    upload_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    file = models.FileField(upload_to='assignments/', blank=True, null=True)
    max_marks = models.IntegerField(default=100)

    def __str__(self):
        return f"{self.title} - {self.course.course_id}"

    def is_overdue(self):
        return timezone.now() > self.due_date

class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 limit_choices_to={'role': 'student'}, related_name='submissions')
    submitted_file = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    marks_obtained = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)

    class Meta:
        unique_together = ('assignment', 'student')

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"

class PreviousQuestion(models.Model):
    question_name = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='previous_questions')
    year = models.IntegerField()
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_questions')
    file = models.FileField(upload_to='previous_questions/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.question_name} ({self.year})"

class Routine(models.Model):
    DAYS = [
        ('monday','Monday'), ('tuesday','Tuesday'), ('wednesday','Wednesday'),
        ('thursday','Thursday'), ('friday','Friday'), ('saturday','Saturday'),
    ]
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='routines')
    day = models.CharField(max_length=15, choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    semester = models.IntegerField()
    room_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.course} - {self.day} {self.start_time}"
