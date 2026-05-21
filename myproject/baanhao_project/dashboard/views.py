from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from issues.models import Issue, IssueStatus
from invoices.models import Invoice
from notifications.models import Notification
from events.models import Event
from django.utils import timezone
from django.db.models import Sum
from users.models import User, UserRole
from visitors.models import VisitLog

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
    
    # ดึงข้อมูล Issue และ Visitor มาแสดงในส่วนกิจกรรม
    recent_issues = Issue.objects.order_by('-created_date')[:5]
    recent_visitors = VisitLog.objects.order_by('-created_at')[:5]

    activities = []
    for issue in recent_issues:
        activities.append({
            'title': f"แจ้งปัญหา: {issue.title}",
            'event_date': issue.created_date,
            'location': issue.location,
            'type': 'issue'
        })
    for visitor in recent_visitors:
        activities.append({
            'title': f"ผู้ติดต่อ: {visitor.visitor_name}",
            'event_date': visitor.created_at,
            'location': f"บ้านเลขที่ {visitor.house_number}" if visitor.house_number else "ทางเข้าโครงการ",
            'type': 'visitor'
        })
    
    # เรียงลำดับตามวันที่ล่าสุด
    activities.sort(key=lambda x: x['event_date'], reverse=True)
    upcoming_events = activities[:5]

    # ดึงข้อมูลเจ้าหน้าที่ (Staff)
    staff_members = User.objects.exclude(role=UserRole.RESIDENT).order_by('role')[:6]

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
        'staff_members': staff_members,
    }

    return render(request, 'dashboard/dashboard.html', context)