from django.shortcuts import render
from issues.models import Issue, IssueStatus

def analytics_view(request):
    total_tasks = Issue.objects.count()
    completed_tasks = Issue.objects.filter(status=IssueStatus.SUCCESS).count()
    processing_tasks = Issue.objects.filter(status=IssueStatus.IN_PROGRESS).count()
    overdue_tasks = Issue.objects.filter(status=IssueStatus.OVERDUE).count()
    waiting_tasks = Issue.objects.filter(status=IssueStatus.PENDING).count()

    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'processing_tasks': processing_tasks,
        'overdue_tasks': overdue_tasks,
        'waiting_tasks': waiting_tasks,
    }
    return render(request, 'analytics/analytics.html', context)