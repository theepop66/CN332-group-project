from django.shortcuts import render
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from issues.models import Issue, IssueStatus, Complaint, Maintenance
import json

def analytics_view(request):
    # 1. Status Counts (Case-insensitive)
    total_tasks = Issue.objects.count()
    completed_tasks = Issue.objects.filter(Q(status__iexact='SUCCESS') | Q(status__iexact='RESOLVED') | Q(status__iexact='CLOSED')).count()
    processing_tasks = Issue.objects.filter(status__iexact='IN_PROGRESS').count()
    overdue_tasks = Issue.objects.filter(status__iexact='OVERDUE').count()
    pending_tasks = Issue.objects.filter(Q(status__iexact='PENDING') | Q(status__iexact='WAITING')).count()

    # 2. Daily Trend (Last 7 days)
    today = timezone.now().date()
    seven_days_ago = today - timedelta(days=6)
    
    daily_counts = (
        Issue.objects.filter(created_date__date__gte=seven_days_ago)
        .annotate(day=TruncDate('created_date'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    # Prepare data for Chart.js
    trend_labels = []
    trend_data = []
    
    # Initialize 7 days with 0
    date_dict = {seven_days_ago + timedelta(days=i): 0 for i in range(7)}
    for entry in daily_counts:
        if entry['day'] in date_dict:
            date_dict[entry['day']] = entry['count']

    for d, count in date_dict.items():
        trend_labels.append(d.strftime('%a')) # Mon, Tue, etc.
        trend_data.append(count)

    # 3. Performance Stats (Completion rate by category/type)
    # This is a bit complex, we'll simplify by grouping by Complaint/Maintenance overall
    total_complaints = Complaint.objects.count()
    completed_complaints = Complaint.objects.filter(Q(status__iexact='SUCCESS') | Q(status__iexact='RESOLVED') | Q(status__iexact='CLOSED')).count()
    complaint_perf = round((completed_complaints / total_complaints * 100)) if total_complaints > 0 else 0

    total_maintenance = Maintenance.objects.count()
    completed_maintenance = Maintenance.objects.filter(Q(status__iexact='SUCCESS') | Q(status__iexact='RESOLVED') | Q(status__iexact='CLOSED')).count()
    maintenance_perf = round((completed_maintenance / total_maintenance * 100)) if total_maintenance > 0 else 0

    # Let's pass the context
    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'processing_tasks': processing_tasks,
        'overdue_tasks': overdue_tasks,
        'pending_tasks': pending_tasks,
        
        'trend_labels_json': json.dumps(trend_labels),
        'trend_data_json': json.dumps(trend_data),

        'complaint_perf': complaint_perf,
        'maintenance_perf': maintenance_perf,
    }

    return render(request, 'analytics/analytics.html', context)