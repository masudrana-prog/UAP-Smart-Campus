from django.db import models
from django.conf import settings

class Campus(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=300)

    def __str__(self):
        return self.name

class Canteen(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    canteen = models.ForeignKey(Canteen, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - ৳{self.price}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('ready', 'Ready'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    canteen = models.ForeignKey(Canteen, on_delete=models.CASCADE, related_name='orders')
    items = models.ManyToManyField(MenuItem, through='OrderItem')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    ordered_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    special_instructions = models.TextField(blank=True)

    def __str__(self):
        return f"Order #{self.pk} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.menu_item.price * self.quantity

class Event(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    event_name = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    room = models.ForeignKey('Classroom', on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='organized_events')
    banner = models.ImageField(upload_to='event_banners/', blank=True, null=True)
    max_participants = models.IntegerField(default=100)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='registered_events')

    def __str__(self):
        return f"{self.event_name} - {self.date}"

class LostAndFound(models.Model):
    STATUS_CHOICES = [
        ('reported', 'Reported'),
        ('claimed', 'Claimed'),
    ]
    item_name = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='reported')
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reported_items')
    found_location = models.CharField(max_length=300, blank=True)
    date_reported = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='lost_found/', blank=True, null=True)
    claimed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='claimed_items')

    def __str__(self):
        return f"{self.item_name} ({self.status})"

class Classroom(models.Model):
    room_number = models.CharField(max_length=20)
    building = models.CharField(max_length=100)
    capacity = models.IntegerField(default=40)

    def __str__(self):
        return f"Room {self.room_number} - {self.building}"
