from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import User, StudentProfile, TeacherProfile, AlumniProfile
from .forms import UserRegistrationForm, UserLoginForm, UserUpdateForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = UserLoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid email or password.')
    return render(request, 'users/login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = UserRegistrationForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        role = form.cleaned_data['role']
        if role == 'student':
            StudentProfile.objects.create(
                user=user,
                student_id=form.cleaned_data.get('student_id', f'STU{user.pk:04d}'),
                department=form.cleaned_data.get('department', ''),
                year=form.cleaned_data.get('year', 1),
                semester=form.cleaned_data.get('semester', 1),
            )
        elif role == 'teacher':
            TeacherProfile.objects.create(
                user=user,
                teacher_id=form.cleaned_data.get('teacher_id', f'TCH{user.pk:04d}'),
                department=form.cleaned_data.get('department', ''),
                designation=form.cleaned_data.get('designation', 'Lecturer'),
            )
        elif role == 'alumni':
            AlumniProfile.objects.create(
                user=user,
                alumni_id=form.cleaned_data.get('alumni_id', f'ALM{user.pk:04d}'),
                graduation_year=form.cleaned_data.get('graduation_year', 2020),
                profession=form.cleaned_data.get('profession', ''),
            )
        messages.success(request, 'Account created! Please log in.')
        return redirect('login')
    return render(request, 'users/register.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile_view(request):
    user = request.user
    profile = user.get_profile()
    return render(request, 'users/profile.html', {'user': user, 'profile': profile})

@login_required
def update_profile(request):
    user = request.user
    form = UserUpdateForm(request.POST or None, request.FILES or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')
    return render(request, 'users/update_profile.html', {'form': form})

@login_required
def alumni_list(request):
    alumni = AlumniProfile.objects.select_related('user').all()
    return render(request, 'users/alumni_list.html', {'alumni': alumni})


# ── Faculty ──────────────────────────────────────────────────────────
from .models import Faculty, Message

@login_required
def faculty_list(request):
    department_filter = request.GET.get('dept', '')
    faculty = Faculty.objects.filter(is_active=True)
    if department_filter:
        faculty = faculty.filter(department=department_filter)
    departments = Faculty.objects.filter(is_active=True).values_list(
        'department', flat=True
    ).distinct().order_by('department')
    return render(request, 'users/faculty_list.html', {
        'faculty': faculty,
        'departments': departments,
        'department_filter': department_filter,
    })

@login_required
def faculty_detail(request, pk):
    member = get_object_or_404(Faculty, pk=pk, is_active=True)
    return render(request, 'users/faculty_detail.html', {'member': member})

@login_required
def add_faculty(request):
    if not request.user.is_admin_role():
        messages.error(request, 'Only admins can manage faculty.')
        return redirect('faculty_list')
    if request.method == 'POST':
        from .models import Faculty
        Faculty.objects.create(
            name=request.POST.get('name'),
            department=request.POST.get('department'),
            designation=request.POST.get('designation'),
            rank=request.POST.get('rank', 'lecturer'),
            email=request.POST.get('email', ''),
            phone=request.POST.get('phone', ''),
            office_room=request.POST.get('office_room', ''),
            bio=request.POST.get('bio', ''),
            research_interest=request.POST.get('research_interest', ''),
            joined_year=request.POST.get('joined_year') or None,
            order=request.POST.get('order', 0),
            photo=request.FILES.get('photo'),
        )
        messages.success(request, 'Faculty member added!')
        return redirect('faculty_list')
    return render(request, 'users/add_faculty.html')

@login_required
def edit_faculty(request, pk):
    if not request.user.is_admin_role():
        messages.error(request, 'Only admins can manage faculty.')
        return redirect('faculty_list')
    member = get_object_or_404(Faculty, pk=pk)
    if request.method == 'POST':
        member.name = request.POST.get('name')
        member.department = request.POST.get('department')
        member.designation = request.POST.get('designation')
        member.rank = request.POST.get('rank', 'lecturer')
        member.email = request.POST.get('email', '')
        member.phone = request.POST.get('phone', '')
        member.office_room = request.POST.get('office_room', '')
        member.bio = request.POST.get('bio', '')
        member.research_interest = request.POST.get('research_interest', '')
        member.joined_year = request.POST.get('joined_year') or None
        member.order = request.POST.get('order', 0)
        member.is_active = 'is_active' in request.POST
        if request.FILES.get('photo'):
            member.photo = request.FILES.get('photo')
        member.save()
        messages.success(request, 'Faculty member updated!')
        return redirect('faculty_detail', pk=pk)
    return render(request, 'users/edit_faculty.html', {'member': member})

@login_required
def delete_faculty(request, pk):
    if not request.user.is_admin_role():
        messages.error(request, 'Only admins can delete faculty.')
        return redirect('faculty_list')
    member = get_object_or_404(Faculty, pk=pk)
    if request.method == 'POST':
        member.delete()
        messages.success(request, 'Faculty member removed.')
        return redirect('faculty_list')
    return render(request, 'users/confirm_delete_faculty.html', {'member': member})


# ── Messaging ─────────────────────────────────────────────────────────
@login_required
def inbox(request):
    user = request.user
    # Get all unique conversations
    from django.db.models import Q, Max, OuterRef, Subquery
    # Mark messages to current user as read
    Message.objects.filter(receiver=user, is_read=False).update(is_read=True)

    # Get latest message per conversation partner
    partners_sent = Message.objects.filter(sender=user).values_list('receiver', flat=True)
    partners_recv = Message.objects.filter(receiver=user).values_list('sender', flat=True)
    partner_ids = set(list(partners_sent) + list(partners_recv))

    conversations = []
    from users.models import User as UserModel
    for pid in partner_ids:
        partner = UserModel.objects.filter(pk=pid).first()
        if not partner:
            continue
        last_msg = Message.objects.filter(
            Q(sender=user, receiver=partner) | Q(sender=partner, receiver=user)
        ).order_by('-sent_at').first()
        unread_count = Message.objects.filter(sender=partner, receiver=user, is_read=False).count()
        conversations.append({
            'partner': partner,
            'last_msg': last_msg,
            'unread': unread_count,
        })
    conversations.sort(key=lambda x: x['last_msg'].sent_at if x['last_msg'] else 0, reverse=True)
    return render(request, 'users/inbox.html', {'conversations': conversations})

@login_required
def conversation(request, user_id):
    from users.models import User as UserModel
    from django.db.models import Q
    other_user = get_object_or_404(UserModel, pk=user_id)
    current_user = request.user

    # Allow: student↔alumni or alumni↔student only (+ admin can view all)
    allowed = (
        (current_user.is_student() and other_user.is_alumni()) or
        (current_user.is_alumni() and other_user.is_student()) or
        current_user.is_admin_role() or current_user.is_teacher()
    )
    if not allowed:
        messages.error(request, 'You can only message alumni.')
        return redirect('inbox')

    # Mark as read
    Message.objects.filter(sender=other_user, receiver=current_user, is_read=False).update(is_read=True)

    msgs = Message.objects.filter(
        Q(sender=current_user, receiver=other_user) |
        Q(sender=other_user, receiver=current_user)
    ).order_by('sent_at')

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(sender=current_user, receiver=other_user, content=content)
            return redirect('conversation', user_id=user_id)

    return render(request, 'users/conversation.html', {
        'other_user': other_user, 'messages_list': msgs
    })

@login_required
def start_conversation(request, user_id):
    """Redirect to conversation — creates it implicitly on first message."""
    return redirect('conversation', user_id=user_id)
