from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class Book(models.Model):
    title = models.CharField(max_length=300)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=20, unique=True, blank=True)
    category = models.CharField(max_length=100, blank=True)
    total_copies = models.IntegerField(default=1)
    available_copies = models.IntegerField(default=1)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    description = models.TextField(blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.author}"

    def is_available(self):
        return self.available_copies > 0

class BookIssue(models.Model):
    STATUS_CHOICES = [
        ('issued', 'Issued'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ]
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='issues')
    borrower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='borrowed_books')
    issue_date = models.DateField(auto_now_add=True)
    return_deadline = models.DateField()
    returned_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='issued')

    def save(self, *args, **kwargs):
        if not self.pk:
            self.return_deadline = (timezone.now() + timedelta(days=14)).date()
        super().save(*args, **kwargs)

    def is_overdue(self):
        return self.status == 'issued' and timezone.now().date() > self.return_deadline

    def days_remaining(self):
        if self.status == 'issued':
            delta = self.return_deadline - timezone.now().date()
            return delta.days
        return 0

    def __str__(self):
        return f"{self.borrower.username} borrowed '{self.book.title}'"
