from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from issues.models import Issue, IssueStatus, Maintenance
from notifications.models import Notification

@login_required
def dashboard(request):
    total_tasks = Issue.objects.count()
    waiting_tasks = Issue.objects.filter(status=IssueStatus.PENDING).count()
    progress_inprogress = Issue.objects.filter(status=IssueStatus.IN_PROGRESS).count()
    overdue_tasks = Issue.objects.filter(status=IssueStatus.OVERDUE).count()
    
    recent_notifications = Notification.objects.order_by('-created_at')[:3]
    upcoming_events = Maintenance.objects.filter(appointment_date__isnull=False).order_by('appointment_date')[:5]

    context = {
        'total_tasks': total_tasks,
        'waiting_tasks': waiting_tasks,
        'progress_inprogress': progress_inprogress,
        'overdue_tasks': overdue_tasks,
        'recent_notifications': recent_notifications,
        'upcoming_events': upcoming_events,
    }

    return render(request, 'dashboard/dashboard.html', context)