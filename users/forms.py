from django import forms
from .models import User, StudentProfile, TeacherProfile, AlumniProfile

DEPARTMENT_CHOICES = [
    ('CSE', 'Computer Science & Engineering'),
    ('EEE', 'Electrical & Electronic Engineering'),
    ('BBA', 'Business Administration'),
    ('English', 'English'),
    ('Law', 'Law'),
    ('Civil', 'Civil Engineering'),
    ('Pharmacy', 'Pharmacy'),
]

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password'}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirm Password'}))
    # Student fields
    student_id = forms.CharField(required=False, max_length=20)
    year = forms.IntegerField(required=False, min_value=1, max_value=4)
    semester = forms.IntegerField(required=False, min_value=1, max_value=8)
    # Teacher fields
    teacher_id = forms.CharField(required=False, max_length=20)
    designation = forms.CharField(required=False, max_length=100)
    # Alumni fields
    alumni_id = forms.CharField(required=False, max_length=20)
    graduation_year = forms.IntegerField(required=False, min_value=1990, max_value=2030)
    profession = forms.CharField(required=False, max_length=200)
    # Common
    department = forms.ChoiceField(choices=[('', 'Select Department')] + DEPARTMENT_CHOICES, required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'role', 'profile_picture']

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('password2'):
            raise forms.ValidationError("Passwords don't match.")
        return cleaned

class UserLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'profile_picture']
