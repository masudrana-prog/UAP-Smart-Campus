from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, StudentProfile, TeacherProfile, AlumniProfile

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone', 'role', 'profile_picture')}),
    )

admin.site.register(StudentProfile)
admin.site.register(TeacherProfile)
admin.site.register(AlumniProfile)

from .models import Faculty, Message

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'designation', 'rank', 'email', 'is_active', 'order']
    list_filter = ['department', 'rank', 'is_active']
    search_fields = ['name', 'department', 'email']
    list_editable = ['order', 'is_active']

admin.site.register(Message)
