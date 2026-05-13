from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Campus, Canteen, MenuItem, Order, OrderItem, Event, LostAndFound, Classroom

admin.site.register(Campus)
admin.site.register(Canteen)
admin.site.register(MenuItem)
admin.site.register(Order)
admin.site.register(Event)
admin.site.register(LostAndFound)
admin.site.register(Classroom)
