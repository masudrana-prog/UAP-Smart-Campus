from django.contrib import admin
from .models import Department, Course, Assignment, AssignmentSubmission, PreviousQuestion, Routine

admin.site.register(Department)
admin.site.register(Course)
admin.site.register(Assignment)
admin.site.register(AssignmentSubmission)
admin.site.register(PreviousQuestion)
admin.site.register(Routine)
