from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from academic.models import Assignment, AssignmentSubmission, Course, Routine
from library.models import BookIssue
from social.models import Post
from campus.models import Event, Order

@login_required
def dashboard(request):
    user = request.user
    context = {'user': user}

    if user.is_student():
        profile = getattr(user, 'studentprofile', None)
        enrolled_courses = user.enrolled_courses.all()
        # Pending assignments with deadlines
        assignments = Assignment.objects.filter(
            course__in=enrolled_courses,
            due_date__gte=timezone.now()
        ).order_by('due_date')[:5]
        submitted_ids = AssignmentSubmission.objects.filter(
            student=user
        ).values_list('assignment_id', flat=True)
        # Active book borrows
        book_issues = BookIssue.objects.filter(borrower=user, status='issued').select_related('book')
        # Today's routine
        today = timezone.now().strftime('%A').lower()
        today_routine = Routine.objects.filter(
            course__in=enrolled_courses, day=today
        ).select_related('course').order_by('start_time')

        context.update({
            'profile': profile,
            'enrolled_courses': enrolled_courses,
            'assignments': assignments,
            'submitted_ids': list(submitted_ids),
            'book_issues': book_issues,
            'today_routine': today_routine,
        })

    elif user.is_teacher():
        profile = getattr(user, 'teacherprofile', None)
        my_courses = Course.objects.filter(teacher=user)
        my_assignments = Assignment.objects.filter(uploaded_by=user).order_by('-upload_date')[:5]
        pending_submissions = AssignmentSubmission.objects.filter(
            assignment__uploaded_by=user, marks_obtained__isnull=True
        ).count()
        context.update({
            'profile': profile,
            'my_courses': my_courses,
            'my_assignments': my_assignments,
            'pending_submissions': pending_submissions,
        })

    elif user.is_alumni():
        profile = getattr(user, 'alumniprofile', None)
        upcoming_events = Event.objects.filter(status='upcoming').order_by('date')[:5]
        context.update({
            'profile': profile,
            'upcoming_events': upcoming_events,
        })

    elif user.is_admin_role():
        from users.models import User as UserModel
        total_students = UserModel.objects.filter(role='student').count()
        total_teachers = UserModel.objects.filter(role='teacher').count()
        total_alumni = UserModel.objects.filter(role='alumni').count()
        recent_posts = Post.objects.order_by('-date')[:5]
        pending_orders = Order.objects.filter(status='pending').count()
        context.update({
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_alumni': total_alumni,
            'recent_posts': recent_posts,
            'pending_orders': pending_orders,
        })

    # Common: recent posts and upcoming events
    context['recent_posts'] = Post.objects.filter(is_approved=True).order_by('-date')[:4]
    context['upcoming_events'] = Event.objects.filter(status='upcoming').order_by('date')[:3]
    return render(request, 'users/dashboard.html', context)
