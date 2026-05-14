from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('alumni/', views.alumni_list, name='alumni_list'),
    # Faculty
    path('faculty/', views.faculty_list, name='faculty_list'),
    path('faculty/add/', views.add_faculty, name='add_faculty'),
    path('faculty/<int:pk>/', views.faculty_detail, name='faculty_detail'),
    path('faculty/<int:pk>/edit/', views.edit_faculty, name='edit_faculty'),
    path('faculty/<int:pk>/delete/', views.delete_faculty, name='delete_faculty'),
    # Messaging
    path('inbox/', views.inbox, name='inbox'),
    path('messages/<int:user_id>/', views.conversation, name='conversation'),
    path('messages/<int:user_id>/start/', views.start_conversation, name='start_conversation'),
]
