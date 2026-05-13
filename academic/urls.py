from django.urls import path
from . import views

urlpatterns = [
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:pk>/', views.course_detail, name='course_detail'),
    path('assignments/', views.assignment_list, name='assignment_list'),
    path('assignments/<int:pk>/', views.assignment_detail, name='assignment_detail'),
    path('assignments/<int:pk>/submit/', views.submit_assignment, name='submit_assignment'),
    path('assignments/upload/', views.upload_assignment, name='upload_assignment'),
    path('previous-questions/', views.previous_questions, name='previous_questions'),
    path('routine/', views.routine_view, name='routine'),
]
