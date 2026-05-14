from django.contrib.auth.decorators import login_required
from datetime import timedelta

from django.db.models import Q, Sum
from django.shortcuts import render
from django.utils import timezone

from invoices.models import Invoice, Transaction
from issues.models import Issue, IssueStatus
from issues.query import overdue_issue_queryset
from notifications.models import Notification

from .models import Event


def _pct_change(current, previous):
    if previous == 0:
        return None if current == 0 else 100.0
    return round(100 * (current - previous) / previous, 1)


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

    now = timezone.now()
    today = now.date()
    week_start = today - timedelta(days=7)
    prev_week_start = today - timedelta(days=14)

    issues_created_this = issues.filter(created_date__date__gte=week_start).count()
    issues_created_prev = issues.filter(
        created_date__date__gte=prev_week_start,
        created_date__date__lt=week_start,
    ).count()
    trend_issues_created = _pct_change(issues_created_this, issues_created_prev)

    inprog_created_this = issues.filter(
        status=IssueStatus.IN_PROGRESS,
        created_date__date__gte=week_start,
    ).count()
    inprog_created_prev = issues.filter(
        status=IssueStatus.IN_PROGRESS,
        created_date__date__gte=prev_week_start,
        created_date__date__lt=week_start,
    ).count()
    trend_inprogress_created = _pct_change(inprog_created_this, inprog_created_prev)

    waiting_new_this = issues.filter(status=IssueStatus.OPEN, created_date__date__gte=week_start).count()
    waiting_new_prev = issues.filter(
        status=IssueStatus.OPEN,
        created_date__date__gte=prev_week_start,
        created_date__date__lt=week_start,
    ).count()
    trend_waiting_new = _pct_change(waiting_new_this, waiting_new_prev)

    paid_this = (
        Transaction.objects.filter(
            payment_status=Transaction.PaymentStatus.VERIFIED,
            paid_date__gte=week_start,
        ).aggregate(s=Sum('paid_amount'))['s']
        or 0
    )
    paid_prev = (
        Transaction.objects.filter(
            payment_status=Transaction.PaymentStatus.VERIFIED,
            paid_date__gte=prev_week_start,
            paid_date__lt=week_start,
        ).aggregate(s=Sum('paid_amount'))['s']
        or 0
    )
    trend_paid_amount = _pct_change(float(paid_this), float(paid_prev))

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
        'trend_issues_created': trend_issues_created,
        'trend_inprogress_created': trend_inprogress_created,
        'trend_waiting_new': trend_waiting_new,
        'trend_paid_amount': trend_paid_amount,
    }
    return render(request, 'dashboard/dashboard.html', context)
