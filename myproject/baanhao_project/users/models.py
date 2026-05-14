from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRole(models.TextChoices):
    """DDL users_user.role CHECK (admin, resident, technician, security, juristic_officer)."""

    ADMIN = 'admin', _('Admin')
    RESIDENT = 'resident', _('Resident')
    TECHNICIAN = 'technician', _('Technician')
    JURISTIC = 'juristic_officer', _('Juristic Officer')
    SECURITY = 'security', _('Security')


class Gender(models.TextChoices):
    """DDL gender CHECK (male, female, other)."""

    MALE = 'male', _('Male')
    FEMALE = 'female', _('Female')
    OTHER = 'other', _('Other')


class User(AbstractUser):
    line_id = models.CharField(max_length=50, unique=True, null=True, blank=True, help_text='Line User ID')
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.RESIDENT)
    gender = models.CharField(max_length=10, choices=Gender.choices, null=True, blank=True)

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'


class Resident(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='resident_profile')
    house = models.ForeignKey(
        'properties.House',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='residents',
    )
    is_owner = models.BooleanField(default=False)

    def __str__(self):
        return f'Resident: {self.user.username}'


class TechnicianStatus(models.TextChoices):
    AVAILABLE = 'available', _('Available')
    BUSY = 'busy', _('Busy')
    OFF_DUTY = 'off_duty', _('Off duty')


class Technician(models.Model):
    """users_technician — skill junction via skills_technician_skill; optional current_maintenance."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='technician_profile')
    skills = models.ManyToManyField(
        'skills.Skill',
        through='skills.TechnicianSkill',
        related_name='technicians',
        blank=True,
    )
    current_status = models.CharField(
        max_length=20,
        choices=TechnicianStatus.choices,
        default=TechnicianStatus.AVAILABLE,
    )
    current_maintenance = models.ForeignKey(
        'issues.Maintenance',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_technician_slots',
    )

    def __str__(self):
        return f'Tech: {self.user.username}'


class JuristicOfficer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='juristic_profile')
    officer_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)

    def __str__(self):
        return f'Officer: {self.user.username}'


class Security(models.Model):
    is_on_duty = models.BooleanField(default=False, help_text='Status: On Duty or Off Duty')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='security_profile')
    station_id = models.CharField(max_length=50)
    shift_time = models.CharField(max_length=50)


class AdminPermission(models.TextChoices):
    BASIC = 'basic', _('Basic')
    SUPER = 'super', _('Super')


class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    permission_level = models.CharField(
        max_length=20,
        choices=AdminPermission.choices,
        default=AdminPermission.BASIC,
    )


class RequestStatus(models.TextChoices):
    """DDL users_registrationrequest.status."""

    PENDING = 'pending', _('Pending')
    APPROVED = 'approved', _('Approved')
    REJECTED = 'rejected', _('Rejected')


class RegistrationRequest(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='registration_request')
    status = models.CharField(max_length=20, choices=RequestStatus.choices, default=RequestStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_requests',
    )

    def __str__(self):
        return f'Registration: {self.user.username} ({self.get_status_display()})'
