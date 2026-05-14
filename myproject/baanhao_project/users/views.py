from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import User, UserRole, RegistrationRequest, RequestStatus
from .forms import RegistrationForm


def social_login_check_view(request, provider):
    """
    Intermediary view for social login from the LOGIN page.
    Sets a session flag so the adapter knows this is login-only (not signup).
    """
    request.session['social_action'] = 'login'
    return redirect(f'/accounts/{provider}/login/?process=login')


def login_view(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            # Check if user exists but is inactive (pending approval)
            try:
                pending_user = User.objects.get(username=username)
                if not pending_user.is_active:
                    messages.error(request, 'Your account is pending admin approval')
                else:
                    messages.error(request, 'Invalid username or password')
            except User.DoesNotExist:
                messages.error(request, 'Invalid username or password')
    
    return render(request, 'users/login.html')


def logout_view(request):
    """Handle user logout"""
    storage = messages.get_messages(request)
    for _ in storage:
        pass
    
    logout(request)
    messages.success(request, 'You have been logged out')
    return redirect('users:login')


def register_view(request):
    """Handle user registration"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Create user with is_active=False (pending approval)
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                phone_number=form.cleaned_data['phone_number'],
                password=form.cleaned_data['password'],
                is_active=False,
                role=UserRole.RESIDENT,
            )
            # Create registration request
            RegistrationRequest.objects.create(user=user)
            return render(request, 'users/register_success.html')
    else:
        form = RegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})


def social_extra_info_view(request):
    """Collect extra info (phone, email) from social login users before submitting for approval."""
    social_user_id = request.session.get('social_signup_user_id')
    if not social_user_id:
        return redirect('users:login')

    try:
        user = User.objects.get(id=social_user_id)
    except User.DoesNotExist:
        return redirect('users:login')

    provider = request.session.get('social_signup_provider', '')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()

        errors = {}

        # Validate username
        if not username:
            errors['username_error'] = 'Please enter a username'
        elif User.objects.filter(username=username).exclude(id=user.id).exists():
            errors['username_error'] = 'This username is already taken'

        # Validate email
        if not email:
            errors['email_error'] = 'Please enter your email'
        elif User.objects.filter(email=email).exclude(id=user.id).exists():
            errors['email_error'] = 'This email is already in use'

        # Validate phone number
        if not phone_number:
            errors['phone_error'] = 'Please enter your phone number'
        elif User.objects.filter(phone_number=phone_number).exclude(id=user.id).exists():
            errors['phone_error'] = 'This phone number is already in use'

        if errors:
            return render(request, 'users/social_extra_info.html', {
                'username': username,
                'email': email,
                'phone_number': phone_number,
                'provider': provider,
                **errors,
            })

        # Save extra info
        user.username = username
        user.email = email
        user.phone_number = phone_number
        user.save()

        # Create registration request for admin approval
        RegistrationRequest.objects.get_or_create(user=user)

        # Clean up session
        del request.session['social_signup_user_id']
        if 'social_signup_provider' in request.session:
            del request.session['social_signup_provider']

        return render(request, 'users/register_success.html')

    # GET: show form with pre-filled data
    # Don't show placeholder emails from providers that didn't provide one
    display_email = user.email if user.email and '@placeholder.local' not in user.email else ''
    return render(request, 'users/social_extra_info.html', {
        'username': user.username,
        'email': display_email,
        'phone_number': user.phone_number or '',
        'provider': provider,
        'email_readonly': bool(display_email),
    })


@login_required
def pending_registrations_view(request):
    """Admin view: list pending registration requests"""
    if request.user.role != UserRole.ADMIN and not request.user.is_superuser:
        messages.error(request, 'คุณไม่มีสิทธิ์เข้าถึงหน้านี้')
        return redirect('dashboard')
    
    pending = RegistrationRequest.objects.filter(status=RequestStatus.PENDING).order_by('-created_at')
    return render(request, 'users/pending_registrations.html', {'pending_requests': pending})


@login_required
def approve_registration_view(request, request_id):
    """Admin: approve a registration request"""
    if request.method != 'POST':
        return redirect('users:pending_registrations')
    
    if request.user.role != UserRole.ADMIN and not request.user.is_superuser:
        messages.error(request, 'คุณไม่มีสิทธิ์')
        return redirect('dashboard')
    
    reg_request = get_object_or_404(RegistrationRequest, id=request_id, status=RequestStatus.PENDING)
    reg_request.status = RequestStatus.APPROVED
    reg_request.reviewed_at = timezone.now()
    reg_request.reviewed_by = request.user
    reg_request.save()
    
    # Activate the user
    user = reg_request.user
    user.is_active = True
    user.save()
    
    messages.success(request, f'อนุมัติผู้ใช้ {user.username} เรียบร้อยแล้ว')
    return redirect('users:pending_registrations')


@login_required
def reject_registration_view(request, request_id):
    """Admin: reject a registration request"""
    if request.method != 'POST':
        return redirect('users:pending_registrations')
    
    if request.user.role != UserRole.ADMIN and not request.user.is_superuser:
        messages.error(request, 'คุณไม่มีสิทธิ์')
        return redirect('dashboard')
    
    reg_request = get_object_or_404(RegistrationRequest, id=request_id, status=RequestStatus.PENDING)
    reg_request.status = RequestStatus.REJECTED
    reg_request.reviewed_at = timezone.now()
    reg_request.reviewed_by = request.user
    reg_request.save()
    
    messages.success(request, f'ปฏิเสธผู้ใช้ {reg_request.user.username} เรียบร้อยแล้ว')
    return redirect('users:pending_registrations')


def staff_list(request):
    staff_users = User.objects.exclude(role=UserRole.RESIDENT).order_by('role', 'first_name')

    role_filter = request.GET.get('role')
    
    if role_filter == 'juristic':
        staff_users = staff_users.filter(role=UserRole.JURISTIC)
    elif role_filter == 'technician':
        staff_users = staff_users.filter(role=UserRole.TECHNICIAN)
    elif role_filter == 'security':
        staff_users = staff_users.filter(role=UserRole.SECURITY)
    elif role_filter == 'admin':
        staff_users = staff_users.filter(role=UserRole.ADMIN)

    all_staff_count = User.objects.exclude(role=UserRole.RESIDENT).count()

    paginator = Paginator(staff_users, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'staffs': page_obj,
        'all_count': all_staff_count,
        'current_role': role_filter if role_filter else 'all'
    }

    return render(request, 'users/staff_list.html', context)


def staff_detail(request, staff_id):
    staff = get_object_or_404(User, id=staff_id)
    
    all_staff = User.objects.exclude(role=UserRole.RESIDENT).order_by('role', 'first_name')
    staff_list_qs = list(all_staff)
    
    try:
        current_index = staff_list_qs.index(staff)
        previous_staff = staff_list_qs[current_index - 1] if current_index > 0 else None
        next_staff = staff_list_qs[current_index + 1] if current_index < len(staff_list_qs) - 1 else None
    except ValueError:
        previous_staff = None
        next_staff = None

    recent_tasks = []
    if staff.role == UserRole.TECHNICIAN and hasattr(staff, 'technician_profile'):
        from issues.models import Maintenance
        recent_tasks = Maintenance.objects.filter(technician=staff.technician_profile).order_by('-created_at')[:5]

    context = {
        'staff': staff,
        'previous_staff': previous_staff,
        'next_staff': next_staff,
        'recent_tasks': recent_tasks,
    }
    return render(request, 'users/staff_detail.html', context)