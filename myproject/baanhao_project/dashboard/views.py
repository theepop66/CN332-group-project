from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.shortcuts import render
from django.utils import timezone

from invoices.models import Invoice
from issues.models import Issue, IssueStatus
from issues.query import overdue_issue_queryset
from notifications.models import Notification

from .models import Event


@login_required
def dashboard(request):
    issues = Issue.objects.all()
    total_tasks = issues.count()
    waiting_tasks = issues.filter(status=IssueStatus.OPEN).count()
    progress_inprogress = issues.filter(status=IssueStatus.IN_PROGRESS).count()
    overdue_count = overdue_issue_queryset().count()

    paid_total = (
        Invoice.objects.filter(status=Invoice.InvoiceStatus.PAID).aggregate(s=Sum('amount'))['s'] or 0
    )
    billable_total = Invoice.objects.aggregate(s=Sum('amount'))['s'] or 0
    fee_achieved = int(round(100 * paid_total / billable_total)) if billable_total else 0

    user = request.user
    recent_notifications = (
        Notification.objects.filter(Q(user=user) | Q(user__isnull=True))
        .select_related('issue')
        .order_by('-created_at')[:10]
    )

    notifications_updated = None
    latest_n = Notification.objects.order_by('-created_at').first()
    if latest_n:
        notifications_updated = latest_n.created_at

    now = timezone.now()
    upcoming_events = (
        Event.objects.filter(event_date__gte=now)
        .select_related('created_by', 'created_by__user')
        .order_by('event_date')[:5]
    )

    context = {
        'total_tasks': total_tasks,
        'progress_inprogress': progress_inprogress,
        'waiting_tasks': waiting_tasks,
        'fee_achieved': fee_achieved,
        'recent_notifications': recent_notifications,
        'notifications_updated': notifications_updated,
        'upcoming_events': upcoming_events,
        'chart_waiting': waiting_tasks,
        'chart_inprogress': progress_inprogress,
        'chart_overdue': overdue_count,
    }
    return render(request, 'dashboard/dashboard.html', context)
