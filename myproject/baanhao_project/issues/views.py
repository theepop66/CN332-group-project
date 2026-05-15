from django.shortcuts import render
from .models import Issue

from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Issue, IssueStatus, Complaint, Maintenance
from .forms import ComplaintForm, MaintenanceForm

import calendar
from datetime import date,datetime, timedelta
from .models import Maintenance

def all_tasks(request):
    # --- 1. Base Query ---
    # ใช้ select_related เพื่อดึงข้อมูลที่เกี่ยวข้องมาใน Query เดียว (ลด N+1 problem)
    # เราดึง 'complaint' และ 'maintenance' มาด้วยเลยเพื่อเช็คประเภทได้เร็วขึ้น
    task_list = Issue.objects.all().select_related(
        'reporter', 
        'reporter__user',
        'assigned_officer', 
        'assigned_officer__user',
        'complaint', 
        'maintenance',
        'maintenance__technician',
        'maintenance__technician__user'
    ).order_by('-created_date')

    # --- 2. Search Logic ---
    search_query = request.GET.get('q')
    if search_query:
        task_list = task_list.filter(
            Q(title__icontains=search_query) | 
            Q(location__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # --- 3. Filter Logic (Status Tabs) ---
    status_filter = request.GET.get('status')
    if status_filter == 'waiting':
        # กรองทั้ง PENDING (ใหญ่) และ pending (เล็ก)
        task_list = task_list.filter(Q(status__iexact='PENDING'))
    elif status_filter == 'in_process':
        task_list = task_list.filter(Q(status__iexact='IN_PROGRESS'))
    elif status_filter == 'overdue':
        task_list = task_list.filter(Q(status__iexact='OVERDUE'))
    elif status_filter == 'complete': 
        # รวมสถานะที่ถือว่าเสร็จสิ้นทั้งหมด
        task_list = task_list.filter(Q(status__iexact='SUCCESS') | Q(status__iexact='RESOLVED') | Q(status__iexact='CLOSED'))

    # --- 4. Count Data ---
    counts = {
        'all': Issue.objects.count(),
        'waiting': Issue.objects.filter(status__iexact='PENDING').count(),
        'in_process': Issue.objects.filter(status__iexact='IN_PROGRESS').count(),
        'overdue': Issue.objects.filter(status__iexact='OVERDUE').count(),
        'complete': Issue.objects.filter(Q(status__iexact='SUCCESS') | Q(status__iexact='RESOLVED') | Q(status__iexact='CLOSED')).count(),
    }

    # --- 5. Pagination ---
    paginator = Paginator(task_list, 30) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # --- 6. Data Transformation ---
    final_tasks = []
    for task in page_obj:
        # กำหนดชื่อผู้รับผิดชอบเบื้องต้นจาก assigned_officer (ถ้ามี)
        assign_to = '-'
        if task.assigned_officer:
            assign_to = task.assigned_officer.user.get_full_name() or task.assigned_officer.user.username

        # ตรวจสอบประเภทและรายละเอียดเพิ่มเติม
        task_type = 'Issue'
        badge_class = 'badge-secondary'

        # ใช้ hasattr ตรวจสอบ reverse relationship (complaint/maintenance)
        if hasattr(task, 'complaint') and task.complaint:
            task_type = 'Complaint'
            badge_class = 'badge-complaint'
            if assign_to == '-': # ถ้ายังไม่มี officer รับผิดชอบ ให้โชว์เป็น Security ตามดีไซน์
                assign_to = 'Security'
        
        elif hasattr(task, 'maintenance') and task.maintenance:
            task_type = 'Maintenance'
            badge_class = 'badge-maintenance'
            # ถ้าเป็น Maintenance และมีช่าง ให้โชว์ชื่อช่าง
            if task.maintenance.technician:
                assign_to = task.maintenance.technician.user.get_full_name() or task.maintenance.technician.user.username
            elif assign_to == '-':
                assign_to = 'Unassigned'

        final_tasks.append({
            'id': task.id,
            'title': task.title,
            'location': task.location,
            'created_date': task.created_date,
            'status': task.status,
            'status_display': task.get_status_display(),
            'type': task_type,
            'assign_to': assign_to,
            'type_badge_class': badge_class
        })

    context = {
        'tasks': final_tasks,
        'page_obj': page_obj,
        'counts': counts,
        'current_status': status_filter if status_filter else 'all',
    }

    return render(request, 'issues/all_tasks.html', context)


def complaint_tasks(request):
    # 1. Query: ดึงเฉพาะ Complaint เท่านั้น!
    tasks = Complaint.objects.select_related('issue_ptr', 'reporter').order_by('-created_date')

    # 2. Search Logic
    search_query = request.GET.get('q')
    if search_query:
        tasks = tasks.filter(
            Q(title__icontains=search_query) | 
            Q(location__icontains=search_query)
        )

    # 3. Count Data (นับแยกประเภท)
    base_qs = Complaint.objects.all()
    counts = {
        'all': base_qs.count(),
        'waiting': base_qs.filter(status=IssueStatus.PENDING).count(),
        'in_process': base_qs.filter(status=IssueStatus.IN_PROGRESS).count(),
        'overdue': base_qs.filter(status=IssueStatus.OVERDUE).count(),
        'complete': base_qs.filter(status=IssueStatus.SUCCESS).count(),
    }

    # 4. Pagination
    paginator = Paginator(tasks, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 5. Data Transformation
    final_tasks = []
    for task in page_obj:
        item = {
            'id': task.id,
            'title': task.title,
            'location': task.location,
            'created_date': task.created_date,
            'status': task.status,
            'assign_to': 'Security',
        }
        final_tasks.append(item)

    context = {
        'tasks': final_tasks,
        'page_obj': page_obj,
        'counts': counts,
        'current_status': request.GET.get('status') or 'all',
    }

    return render(request, 'issues/all_tasks_complaints.html', context)

def maintenance_tasks(request):
    # --- 1. Base Query ---
    # เรียกจากตาราง Maintenance โดยตรง
    # select_related 'technician' เพื่อดึงชื่อช่างมาด้วยในคำสั่งเดียว (ลด Query)
    tasks = Maintenance.objects.select_related('issue_ptr', 'reporter', 'technician').order_by('-created_date')

    # --- 2. Search Logic ---
    search_query = request.GET.get('q')
    if search_query:
        tasks = tasks.filter(
            Q(title__icontains=search_query) | 
            Q(location__icontains=search_query)
        )

    # --- 3. Filter Logic (Status) ---
    status_filter = request.GET.get('status')
    if status_filter == 'waiting':
        tasks = tasks.filter(status=IssueStatus.PENDING)
    elif status_filter == 'in_process':
        tasks = tasks.filter(status=IssueStatus.IN_PROGRESS)
    elif status_filter == 'overdue':
        tasks = tasks.filter(status=IssueStatus.OVERDUE)
    elif status_filter == 'complete': 
        tasks = tasks.filter(status=IssueStatus.SUCCESS)

    # --- 4. Count Data (เฉพาะ Maintenance) ---
    base_qs = Maintenance.objects.all()
    counts = {
        'all': base_qs.count(),
        'waiting': base_qs.filter(status=IssueStatus.PENDING).count(),
        'in_process': base_qs.filter(status=IssueStatus.IN_PROGRESS).count(),
        'overdue': base_qs.filter(status=IssueStatus.OVERDUE).count(),
        'complete': base_qs.filter(status=IssueStatus.SUCCESS).count(),
    }

    # --- 5. Pagination ---
    paginator = Paginator(tasks, 8) # 8 รายการต่อหน้า
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # --- 6. Prepare Data ---
    final_tasks = []
    for task in page_obj:
        # หาชื่อช่าง
        tech_name = 'Unassigned'
        if task.technician:
            # เข้าถึง User ผ่าน Technician model
            tech_name = task.technician.user.get_full_name() or task.technician.user.username

        item = {
            'id': task.id,
            'title': task.title,
            'location': task.location,
            'created_date': task.created_date,
            'status': task.status,
            'assign_to': tech_name, # ส่งชื่อช่างไปแสดง
            'image': task.before_image.url if task.before_image else None
        }
        final_tasks.append(item)

    context = {
        'tasks': final_tasks,
        'page_obj': page_obj,
        'counts': counts,
        'current_status': status_filter if status_filter else 'all',
    }

    # Render ไฟล์ HTML ใหม่สำหรับ Maintenance
    return render(request, 'issues/all_tasks_maintenance.html', context)

def create_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.status = 'PENDING' # กำหนดค่าเริ่มต้น
            task.save()
            return redirect('complaint_tasks')
    else:
        form = ComplaintForm()
    
    return render(request, 'issues/create_complaint.html', {'form': form})

def create_maintenance(request):
    if request.method == 'POST':
        form = MaintenanceForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.status = 'PENDING'
            task.save()
            return redirect('maintenance_tasks')
    else:
        form = MaintenanceForm()

    return render(request, 'issues/create_maintenance.html', {'form': form})

def maintenance_detail(request, pk):
    task = get_object_or_404(Maintenance, pk=pk)
    
    # Logic สำหรับปุ่มกดเปลี่ยนสถานะ (Action Buttons)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'complete':
            task.status = IssueStatus.SUCCESS
            task.save()
        elif action == 'cancel':
            # เนื่องจากใน Enum เดิมไม่มี CANCELLED อาจจะใช้การลบ หรือเพิ่ม Status ใหม่ใน models.py
            # ในที่นี้สมมติว่าให้เป็น SUCCESS ไปก่อน หรือคุณไปเพิ่ม Status 'CANCELLED' เองนะครับ
            pass 
        return redirect('maintenance_detail', pk=pk)

    return render(request, 'issues/maintenance_detail.html', {'task': task})

def complaint_detail(request, pk):
    task = get_object_or_404(Complaint, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'complete':
            task.status = IssueStatus.SUCCESS
            task.save()
        # Complaint อาจไม่มีปุ่ม Cancel หรือมี Logic ต่างกัน
        return redirect('complaint_detail', pk=pk)

    return render(request, 'issues/complaint_detail.html', {'task': task})

def maintenance_calendar(request):

    today = date.today()

    # ==========================
    # 1. รับ view ก่อนเลย (กัน error)
    # ==========================
    view_mode = request.GET.get("view", "month")

    # ==========================
    # 2. รับ date อย่างปลอดภัย
    # ==========================
    date_param = request.GET.get("date")

    if date_param:
        try:
            selected_date = datetime.strptime(date_param, "%Y-%m-%d").date()
        except ValueError:
            selected_date = today
    else:
        selected_date = today

    year = selected_date.year
    month = selected_date.month
    day = selected_date.day

    # ==========================
    # 3. prev / next (ใช้ selected_date)
    # ==========================
    if view_mode == "month":
        prev_date = selected_date.replace(day=1) - timedelta(days=1)
        next_date = (selected_date.replace(day=28) + timedelta(days=4)).replace(day=1)

    elif view_mode == "week":
        prev_date = selected_date - timedelta(days=7)
        next_date = selected_date + timedelta(days=7)

    elif view_mode == "day":
        prev_date = selected_date - timedelta(days=1)
        next_date = selected_date + timedelta(days=1)

    else:
        prev_date = selected_date
        next_date = selected_date

    # ==========================
    # 4. Calendar logic
    # ==========================
    cal = calendar.Calendar(firstweekday=0)

    if view_mode == "month":
        month_days = cal.monthdayscalendar(year, month)

    elif view_mode == "week":
        start_week = selected_date - timedelta(days=selected_date.weekday())
        month_days = [[(start_week + timedelta(days=i)).day for i in range(7)]]

    elif view_mode == "day":
        month_days = [[day]]

    else:
        month_days = cal.monthdayscalendar(year, month)

    # ==========================
    # 5. Data - ดึงจาก Issue และใช้ updated_at ตามที่ขอ
    # ==========================
    issues = Issue.objects.filter(
        updated_at__year=year,
        updated_at__month=month
    )

    events_by_day = {}

    for issue in issues:
        if issue.updated_at:
            d = issue.updated_at.day
            
            # กำหนดสีตามประเภท
            color = "blue"
            if hasattr(issue, 'complaint') and issue.complaint:
                color = "purple"
            elif hasattr(issue, 'maintenance') and issue.maintenance:
                color = "green"

            events_by_day.setdefault(d, []).append({
                "title": issue.title,
                "color": color
            })

    context = {
        "calendar": month_days,
        "month_name": calendar.month_name[month],
        "month_number": month,
        "year": year,
        "current_day": today.day,
        "events_by_day": events_by_day,
        "view_mode": view_mode,
        "selected_date": selected_date,
        "prev_date": prev_date.strftime("%Y-%m-%d"),
        "next_date": next_date.strftime("%Y-%m-%d"),
    }

    return render(request, "issues/calendar_maintenance.html", context)

def complaint_calendar(request):
    return render(request, "issues/complaint_calendar.html")