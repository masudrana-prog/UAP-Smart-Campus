from django import forms
from .models import Assignment, AssignmentSubmission, PreviousQuestion

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'course', 'due_date', 'file', 'max_marks']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        if teacher:
            from .models import Course
            self.fields['course'].queryset = Course.objects.filter(teacher=teacher)

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['submitted_file']

class PreviousQuestionForm(forms.ModelForm):
    class Meta:
        model = PreviousQuestion
        fields = ['question_name', 'course', 'year', 'file']
