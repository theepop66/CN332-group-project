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
    # เรียกจากตารางแม่ (Issue)
    # order_by('-created_date') ให้ตรงกับ field ใน model
    task_list = Issue.objects.all().select_related('reporter').order_by('-created_date')

    # --- 2. Search Logic (Title, Description, Location) ---
    search_query = request.GET.get('q')
    if search_query:
        task_list = task_list.filter(
            Q(title__icontains=search_query) | 
            Q(location__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # --- 3. Filter Logic (Status Tabs) ---
    # Map ค่าจาก URL ให้ตรงกับ Enum ใน models.py (IssueStatus)
    status_filter = request.GET.get('status')
    
    if status_filter == 'waiting':
        task_list = task_list.filter(status=IssueStatus.PENDING)
    elif status_filter == 'in_process':
        task_list = task_list.filter(status=IssueStatus.IN_PROGRESS)
    elif status_filter == 'overdue':
        task_list = task_list.filter(status=IssueStatus.OVERDUE)
    elif status_filter == 'complete': 
        task_list = task_list.filter(status=IssueStatus.SUCCESS)

    # --- 4. Count Data (สำหรับ Badge บน Tabs) ---
    counts = {
        'all': Issue.objects.count(),
        'waiting': Issue.objects.filter(status=IssueStatus.PENDING).count(),
        'in_process': Issue.objects.filter(status=IssueStatus.IN_PROGRESS).count(),
        'overdue': Issue.objects.filter(status=IssueStatus.OVERDUE).count(),
        'complete': Issue.objects.filter(status=IssueStatus.SUCCESS).count(),
    }

    # --- 5. Pagination ---
    # UI เขียนว่า Showing 1 to 8 -> ใช้ 8 รายการต่อหน้า
    paginator = Paginator(task_list, 30) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # --- 6. Data Transformation Logic ---
    # แปลงข้อมูลเพื่อส่งไปแสดงผลให้ตรงกับ Design
    final_tasks = []
    
    for task in page_obj:
        # ข้อมูลพื้นฐานจาก Issue (Parent)
        item = {
            'id': task.id,
            'title': task.title,
            'location': task.location,
            'created_date': task.created_date,
            'status': task.status, # ค่าจะเป็น 'PENDING', 'IN_PROGRESS' ฯลฯ
            'status_display': task.get_status_display(), # ค่าที่อ่านรู้เรื่อง เช่น 'Pending', 'In Progress'
            'type': 'Issue',      # Default
            'assign_to': '-',
            'type_badge_class': 'badge-secondary' # Default CSS Class
        }

        # ตรวจสอบว่าเป็น Complaint หรือ Maintenance
        # โดยใช้ hasattr เช็คว่า task instance นี้มี attributes ของลูกไหม
        
        if hasattr(task, 'complaint'):
            item['type'] = 'Complaint'
            item['type_badge_class'] = 'badge-complaint' # ไว้ไปเขียน CSS
            # ใน Model Complaint ของคุณไม่มี field assignee
            # แต่ใน UI มีคำว่า Security -> เราจึง Hardcode ไว้ก่อน
            item['assign_to'] = 'Security' 
            
        elif hasattr(task, 'maintenance'):
            item['type'] = 'Maintenance'
            item['type_badge_class'] = 'badge-maintenance' # ไว้ไปเขียน CSS
            
            # ดึงข้อมูล Technician
            # เข้าถึงผ่าน task.maintenance.technician
            tech = task.maintenance.technician
            if tech:
                # ใช้ str(tech) ถ้า Technician model มี def __str__ 
                # หรือ tech.user.get_full_name() ถ้าเชื่อมกับ User
                item['assign_to'] = str(tech) 
            else:
                item['assign_to'] = 'Unassigned'

        final_tasks.append(item)

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
    # 5. Data
    # ==========================
    maintenances = Maintenance.objects.filter(
        appointment_date__year=year,
        appointment_date__month=month
    )

    events_by_day = {}

    for m in maintenances:
        if m.appointment_date:
            d = m.appointment_date.day
            events_by_day.setdefault(d, []).append({
                "title": m.title,
                "color": "blue"
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