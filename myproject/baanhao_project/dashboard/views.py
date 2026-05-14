from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from issues.models import Issue, IssueStatus
from invoices.models import Invoice
from notifications.models import Notification
from events.models import Event
from django.utils import timezone
from django.db.models import Sum

@login_required
def dashboard(request):
    total_tasks = Issue.objects.count()
    progress_inprogress = Issue.objects.filter(status=IssueStatus.IN_PROGRESS).count()
    waiting_tasks = Issue.objects.filter(status=IssueStatus.PENDING).count()
    
    # Calculate fee achieved percentage
    total_invoice_amount = Invoice.objects.aggregate(total=Sum('amount'))['total'] or 0
    paid_invoice_amount = Invoice.objects.filter(status='paid').aggregate(total=Sum('amount'))['total'] or 0
    fee_achieved = 0
    if total_invoice_amount > 0:
        fee_achieved = round((paid_invoice_amount / total_invoice_amount) * 100)

    recent_notifications = Notification.objects.order_by('-created_at')[:3]
    upcoming_events = Event.objects.filter(event_date__gte=timezone.now()).order_by('event_date')[:2]

    # Calculate status counts for the chart
    overdue_tasks = Issue.objects.filter(status=IssueStatus.OVERDUE).count()

    context = {
        'total_tasks': total_tasks,
        'progress_inprogress': progress_inprogress,
        'waiting_tasks': waiting_tasks,
        'fee_achieved': fee_achieved,
        'recent_notifications': recent_notifications,
        'upcoming_events': upcoming_events,
        'overdue_tasks': overdue_tasks,
    }

    return render(request, 'dashboard/dashboard.html', context)