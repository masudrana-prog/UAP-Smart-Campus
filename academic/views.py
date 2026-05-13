from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Course, Assignment, AssignmentSubmission, PreviousQuestion, Routine, Department
from .forms import AssignmentForm, SubmissionForm, PreviousQuestionForm

def alumni_restricted(view_func):
    """Blocks alumni but allows admin, student, teacher."""
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_alumni():
            messages.error(request, "Alumni do not have access to this section.")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper

@login_required
@alumni_restricted
def course_list(request):
    user = request.user
    if user.is_student():
        courses = user.enrolled_courses.all()
    elif user.is_teacher():
        courses = Course.objects.filter(teacher=user)
    else:  # admin
        courses = Course.objects.all()
    return render(request, 'academic/course_list.html', {'courses': courses})

@login_required
@alumni_restricted
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    assignments = course.assignments.order_by('due_date')
    questions = course.previous_questions.order_by('-year')
    submitted_ids = []
    if request.user.is_student():
        submitted_ids = AssignmentSubmission.objects.filter(
            student=request.user, assignment__course=course
        ).values_list('assignment_id', flat=True)
    return render(request, 'academic/course_detail.html', {
        'course': course, 'assignments': assignments,
        'questions': questions, 'submitted_ids': list(submitted_ids)
    })

@login_required
@alumni_restricted
def assignment_list(request):
    user = request.user
    if user.is_student():
        enrolled = user.enrolled_courses.all()
        assignments = Assignment.objects.filter(course__in=enrolled).order_by('due_date')
        submitted_ids = AssignmentSubmission.objects.filter(student=user).values_list('assignment_id', flat=True)
        return render(request, 'academic/assignment_list.html', {
            'assignments': assignments, 'submitted_ids': list(submitted_ids)
        })
    elif user.is_teacher():
        assignments = Assignment.objects.filter(uploaded_by=user).order_by('-upload_date')
        return render(request, 'academic/assignment_list.html', {'assignments': assignments})
    elif user.is_admin_role():
        # Admin sees ALL assignments
        assignments = Assignment.objects.all().order_by('-upload_date')
        return render(request, 'academic/assignment_list.html', {'assignments': assignments})
    return redirect('dashboard')

@login_required
@alumni_restricted
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    submission = None
    if request.user.is_student():
        submission = AssignmentSubmission.objects.filter(
            assignment=assignment, student=request.user
        ).first()
    all_submissions = None
    if request.user.is_teacher() and assignment.uploaded_by == request.user:
        all_submissions = assignment.submissions.select_related('student').all()
    elif request.user.is_admin_role():
        all_submissions = assignment.submissions.select_related('student').all()
    return render(request, 'academic/assignment_detail.html', {
        'assignment': assignment, 'submission': submission, 'all_submissions': all_submissions
    })

@login_required
def submit_assignment(request, pk):
    if not request.user.is_student():
        messages.error(request, 'Only students can submit assignments.')
        return redirect('assignment_list')
    assignment = get_object_or_404(Assignment, pk=pk)
    if AssignmentSubmission.objects.filter(assignment=assignment, student=request.user).exists():
        messages.warning(request, 'You have already submitted this assignment.')
        return redirect('assignment_detail', pk=pk)
    form = SubmissionForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        sub = form.save(commit=False)
        sub.assignment = assignment
        sub.student = request.user
        sub.save()
        messages.success(request, 'Assignment submitted successfully!')
        return redirect('assignment_list')
    return render(request, 'academic/submit_assignment.html', {'form': form, 'assignment': assignment})

@login_required
def upload_assignment(request):
    if not request.user.is_teacher():
        messages.error(request, 'Only teachers can upload assignments.')
        return redirect('dashboard')
    form = AssignmentForm(request.POST or None, request.FILES or None, teacher=request.user)
    if request.method == 'POST' and form.is_valid():
        assignment = form.save(commit=False)
        assignment.uploaded_by = request.user
        assignment.save()
        messages.success(request, 'Assignment uploaded!')
        return redirect('assignment_list')
    return render(request, 'academic/upload_assignment.html', {'form': form})

@login_required
@alumni_restricted
def previous_questions(request):
    # Admin & teacher see all; student sees their dept courses
    user = request.user
    questions = PreviousQuestion.objects.select_related('course').order_by('-year')
    courses = Course.objects.all()
    course_filter = request.GET.get('course')
    if course_filter:
        questions = questions.filter(course_id=course_filter)
    return render(request, 'academic/previous_questions.html', {
        'questions': questions, 'courses': courses, 'course_filter': course_filter
    })

@login_required
def routine_view(request):
    user = request.user
    if user.is_student():
        profile = getattr(user, 'studentprofile', None)
        if profile:
            routines = Routine.objects.filter(
                department__name=profile.department, semester=profile.semester
            ).order_by('day', 'start_time')
        else:
            routines = []
    elif user.is_teacher():
        routines = Routine.objects.filter(course__teacher=user).order_by('day', 'start_time')
    else:
        routines = Routine.objects.all().order_by('day', 'start_time')
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    routine_by_day = {day: [] for day in days}
    for r in routines:
        routine_by_day[r.day].append(r)
    has_routine = any(slots for slots in routine_by_day.values())
    return render(request, 'academic/routine.html', {
        'routine_by_day': routine_by_day, 'days': days, 'has_routine': has_routine
    })
