from django.urls import path
from . import views

urlpatterns = [
    path('canteen/', views.canteen_menu, name='canteen_menu'),
    path('canteen/<int:canteen_id>/order/', views.place_order, name='place_order'),
    path('canteen/my-orders/', views.my_orders, name='my_orders'),
    path('events/', views.event_list, name='event_list'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('lost-found/', views.lost_found, name='lost_found'),
    path('lost-found/report/', views.report_lost, name='report_lost'),
    path('lost-found/<int:pk>/claim/', views.claim_item, name='claim_item'),
    path('lost-found/<int:pk>/delete/', views.delete_item, name='delete_item'),
]
