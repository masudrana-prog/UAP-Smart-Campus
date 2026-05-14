from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('alumni', 'Alumni'),
    ]
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"

    def is_student(self): return self.role == 'student'
    def is_teacher(self): return self.role == 'teacher'
    def is_alumni(self): return self.role == 'alumni'
    def is_admin_role(self): return self.role == 'admin'

    def get_profile(self):
        if self.role == 'student':
            return getattr(self, 'studentprofile', None)
        elif self.role == 'teacher':
            return getattr(self, 'teacherprofile', None)
        elif self.role == 'alumni':
            return getattr(self, 'alumniprofile', None)
        return None

class StudentProfile(models.Model):
    YEAR_CHOICES = [(i, f'Year {i}') for i in range(1, 5)]
    SEMESTER_CHOICES = [(i, f'Semester {i}') for i in range(1, 9)]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='studentprofile')
    student_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    year = models.IntegerField(choices=YEAR_CHOICES, default=1)
    semester = models.IntegerField(choices=SEMESTER_CHOICES, default=1)

    def __str__(self):
        return f"Student: {self.user.get_full_name()} - {self.student_id}"

class AlumniProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='alumniprofile')
    alumni_id = models.CharField(max_length=20, unique=True)
    graduation_year = models.IntegerField()
    profession = models.CharField(max_length=200, blank=True)
    company = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"Alumni: {self.user.get_full_name()} ({self.graduation_year})"

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacherprofile')
    teacher_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)

    def __str__(self):
        return f"Teacher: {self.user.get_full_name()} - {self.designation}"


class Faculty(models.Model):
    RANK_CHOICES = [
        ('professor', 'Professor'),
        ('associate_professor', 'Associate Professor'),
        ('assistant_professor', 'Assistant Professor'),
        ('lecturer', 'Lecturer'),
        ('senior_lecturer', 'Senior Lecturer'),
        ('adjunct', 'Adjunct Faculty'),
    ]
    name = models.CharField(max_length=200)
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    rank = models.CharField(max_length=30, choices=RANK_CHOICES, default='lecturer')
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    office_room = models.CharField(max_length=50, blank=True)
    photo = models.ImageField(upload_to='faculty_photos/', blank=True, null=True)
    bio = models.TextField(blank=True)
    research_interest = models.CharField(max_length=300, blank=True)
    joined_year = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text='Display order (lower = shown first)')
    linked_user = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='faculty_profile',
        help_text='Link to a teacher user account (optional)'
    )

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Faculty Members'

    def __str__(self):
        return f"{self.name} — {self.designation}"


class Message(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='received_messages'
    )
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['sent_at']

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}"
