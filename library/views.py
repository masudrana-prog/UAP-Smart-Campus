from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Book, BookIssue

def alumni_restricted(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_alumni():
            messages.error(request, "Alumni do not have access to the Library.")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper

@login_required
@alumni_restricted
def book_list(request):
    query = request.GET.get('q', '')
    books = Book.objects.all()
    if query:
        books = books.filter(title__icontains=query) | books.filter(author__icontains=query)
    return render(request, 'library/book_list.html', {'books': books, 'query': query})

@login_required
@alumni_restricted
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    user_issue = BookIssue.objects.filter(book=book, borrower=request.user, status='issued').first()
    return render(request, 'library/book_detail.html', {'book': book, 'user_issue': user_issue})

@login_required
@alumni_restricted
def borrow_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if not book.is_available():
        messages.error(request, 'No copies available right now.')
        return redirect('book_detail', pk=pk)
    if BookIssue.objects.filter(book=book, borrower=request.user, status='issued').exists():
        messages.warning(request, 'You already have this book issued.')
        return redirect('book_detail', pk=pk)
    BookIssue.objects.create(book=book, borrower=request.user)
    book.available_copies -= 1
    book.save()
    messages.success(request, f'"{book.title}" issued! Return by 14 days.')
    return redirect('my_books')

@login_required
@alumni_restricted
def return_book(request, pk):
    issue = get_object_or_404(BookIssue, pk=pk, borrower=request.user)
    from django.utils import timezone
    issue.status = 'returned'
    issue.returned_date = timezone.now().date()
    issue.save()
    issue.book.available_copies += 1
    issue.book.save()
    messages.success(request, f'"{issue.book.title}" returned successfully!')
    return redirect('my_books')

@login_required
@alumni_restricted
def my_books(request):
    active_issues = BookIssue.objects.filter(borrower=request.user, status='issued').select_related('book')
    history = BookIssue.objects.filter(borrower=request.user, status='returned').select_related('book').order_by('-returned_date')[:10]
    return render(request, 'library/my_books.html', {'active_issues': active_issues, 'history': history})
