from django.db import models


class IssueStatus(models.TextChoices):
    """DDL issues_issue.status CHECK."""

    OPEN = 'open', 'Open'
    IN_PROGRESS = 'in_progress', 'In Progress'
    RESOLVED = 'resolved', 'Resolved'
    CLOSED = 'closed', 'Closed'


class Priority(models.TextChoices):
    """DDL issues_issue.priority CHECK."""

    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'
    URGENT = 'urgent', 'Urgent'


class Issue(models.Model):
    """issues_issue — DDL."""

    class Meta:
        db_table = 'issues_issue'

    reporter = models.ForeignKey(
        'users.Resident',
        on_delete=models.RESTRICT,
        related_name='reported_issues',
    )
    assigned_officer = models.ForeignKey(
        'users.JuristicOfficer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_issues',
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=20, choices=IssueStatus.choices, default=IssueStatus.OPEN)
    location = models.CharField(max_length=100, help_text='Ex. Living Room, Kitchen')
    analysis_json = models.JSONField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'[{self.status}] {self.title} (by {self.reporter})'


class Complaint(Issue):
    """issues_complaint — DDL categories."""

    class Category(models.TextChoices):
        NOISE = 'noise', 'Noise'
        CLEANLINESS = 'cleanliness', 'Cleanliness'
        SAFETY = 'safety', 'Safety'
        PARKING = 'parking', 'Parking'
        NEIGHBOR = 'neighbor', 'Neighbor'
        OTHER = 'other', 'Other'

    class Meta:
        db_table = 'issues_complaint'

    category = models.CharField(max_length=50, choices=Category.choices)
    evidence_image = models.ImageField(upload_to='complaints/', null=True, blank=True)

    def __str__(self):
        return f'Complaint: {self.title}'


class Maintenance(Issue):
    """issues_maintenance — DDL."""

    class Meta:
        db_table = 'issues_maintenance'

    equipment_type = models.CharField(max_length=100, help_text='Ex. Air Conditioner, Pipe')
    technician = models.ForeignKey(
        'users.Technician',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
    )
    appointment_date = models.DateTimeField(null=True, blank=True)
    before_image = models.ImageField(upload_to='maintenance/before/', null=True, blank=True)
    after_image = models.ImageField(upload_to='maintenance/after/', null=True, blank=True)

    def __str__(self):
        return f'Maintenance: {self.title}'
