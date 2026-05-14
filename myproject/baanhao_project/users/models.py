from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# Enum สำหรับ Role และ Gender ตาม Diagram
class UserRole(models.TextChoices):
    ADMIN = 'ADMIN', _('Admin')
    RESIDENT = 'RESIDENT', _('Resident')
    TECHNICIAN = 'TECHNICIAN', _('Technician')
    JURISTIC = 'JURISTIC', _('Juristic Officer')
    SECURITY = 'SECURITY', _('Security')

class Gender(models.TextChoices):
    MALE = 'MALE', _('Male')
    FEMALE = 'FEMALE', _('Female')
    OTHER = 'OTHER', _('Other')

# Main User Model (Based on Abstract User in Diagram)
class User(AbstractUser):
    # Field ที่ Django มีให้อยู่แล้ว: username, email, first_name, last_name, is_active (status), date_joined (registeredDate)
    
    line_id = models.CharField(max_length=50, unique=True, null=True, blank=True, help_text="Line User ID")
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.RESIDENT)
    gender = models.CharField(max_length=10, choices=Gender.choices, null=True, blank=True)
    
    # ใช้ email เป็นตัว login หลักแทน username (Optional: ถ้าอยากทำแบบ Modern)
    # USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

# Role-Specific Models (Subclasses in Diagram)

class Resident(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='resident_profile')
    # House เชื่อมกับแอปอื่น (สมมติว่าชื่อแอป 'properties') ใส่เป็น string ไปก่อนได้
    house = models.ForeignKey(
        'properties.House', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='residents' # เพื่อให้ House เรียกดูสมาชิกในบ้านได้ (house.residents.all())
    )
    
    is_owner = models.BooleanField(default=False)
    
    # Note: registeredVehicles ใน Diagram เป็น List<String> 
    # ใน Django ควรแยกเป็นอีก Table ชื่อ Vehicle แล้ว FK มาที่ Resident หรือ House
    
    def __str__(self):
        return f"Resident: {self.user.username}"

class Technician(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='technician_profile')
    current_status = models.CharField(max_length=20, default="AVAILABLE") # Diagram: currentStatus
    current_maintenance = models.ForeignKey('issues.Maintenance', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    
    def __str__(self):
        return f"Tech: {self.user.username}"

class JuristicOfficer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='juristic_profile')
    officer_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)

    def __str__(self):
        return f"Officer: {self.user.username}"

class Security(models.Model):
    is_on_duty = models.BooleanField(default=False, help_text="Status: On Duty or Off Duty")
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='security_profile')
    station_id = models.CharField(max_length=50)
    shift_time = models.CharField(max_length=50) # e.g. "08:00-16:00"

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    permission_level = models.CharField(max_length=20) # Diagram: Enum

# Registration Request
class RequestStatus(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    APPROVED = 'APPROVED', _('Approved')
    REJECTED = 'REJECTED', _('Rejected')

class RegistrationRequest(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='registration_request')
    status = models.CharField(max_length=20, choices=RequestStatus.choices, default=RequestStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_requests')

    def __str__(self):
        return f"Registration: {self.user.username} ({self.get_status_display()})"