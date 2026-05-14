from django.db import models
from django.conf import settings # เพื่ออ้างอิง User model
from django.utils import timezone

# 1. สร้าง Enum สำหรับ Status และ Priority ตาม Diagram
class IssueStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'           # รอรับเรื่อง
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress' # กำลังดำเนินการ
    OVERDUE = 'OVERDUE', 'Overdue'
    SUCCESS = 'SUCCESS', 'SUCCESS'               # ปิดงาน

class Priority(models.TextChoices):
    LOW = 'LOW', 'Low'
    MEDIUM = 'MEDIUM', 'Medium'
    HIGH = 'HIGH', 'High'
    CRITICAL = 'CRITICAL', 'Critical'

# 2. Main Issue Model (Parent Table)
# แม้ Diagram เขียนว่า Abstract แต่เราจะให้เป็น Concrete Table 
# เพื่อให้เรา query Issue.objects.all() แล้วเจอทั้ง Complaint และ Maintenance ได้ง่ายๆ
class Issue(models.Model):
    # Diagram: issueID (ใช้ id อัตโนมัติ หรือจะสร้าง custom field ก็ได้)
    # Diagram: reporter: Resident
    reporter = models.ForeignKey(
        'users.Resident', 
        on_delete=models.CASCADE, 
        related_name='reported_issues'
    )
    
    title = models.CharField(max_length=200) # Diagram: title
    description = models.TextField()         # Diagram: description
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM) # Diagram: priority
    status = models.CharField(max_length=20, choices=IssueStatus.choices, default=IssueStatus.PENDING) # Diagram: status
    
    created_date = models.DateTimeField(auto_now_add=True) # Diagram: createdDate
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    location = models.CharField(max_length=100, help_text="Ex. Living Room, Kitchen") # Diagram: location
    
    # Diagram: analysisJSON: JSONField (สำหรับเก็บผลจาก AI)
    # ต้องใช้ database ที่รองรับ JSON เช่น PostgreSQL หรือ SQLite (Django 3.1+)
    analysis_json = models.JSONField(null=True, blank=True) 

    assigned_officer = models.ForeignKey('users.JuristicOfficer', null=True, blank=True, on_delete=models.SET_NULL)
    reporter_line_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"[{self.status}] {self.title} (by {self.reporter})"

# 3. Complaint Model (การร้องเรียน)
class Complaint(Issue):
    class Category(models.TextChoices):
        NOISE = 'NOISE', 'Noise Disturbance'
        SMELL = 'SMELL', 'Unpleasant Smell'
        PARKING = 'PARKING', 'Illegal Parking'
        OTHER = 'OTHER', 'Other'

    # Inherits fields from Issue automatically
    category = models.CharField(max_length=50, choices=Category.choices) # Diagram: category
    evidence_image = models.ImageField(upload_to='complaints/', null=True, blank=True) # Diagram: evidenceImage

    def __str__(self):
        return f"Complaint: {self.title}"

# 4. Maintenance Model (การแจ้งซ่อม)
class Maintenance(Issue):
    # Diagram: maintenanceID (ใช้ id อัตโนมัติ)
    equipment_type = models.CharField(max_length=100, help_text="Ex. Air Conditioner, Pipe") # Diagram: equipmentType
    
    # Diagram: technician: Technician
    technician = models.ForeignKey(
        'users.Technician', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_tasks'
    )
    
    appointment_date = models.DateTimeField(null=True, blank=True) # Diagram: appointmentDate
    
    # Diagram: beforeWorkImage / afterWorkImage
    before_image = models.ImageField(upload_to='maintenance/before/', null=True, blank=True)
    after_image = models.ImageField(upload_to='maintenance/after/', null=True, blank=True)

    def __str__(self):
        return f"Maintenance: {self.title}"