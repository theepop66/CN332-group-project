import calendar
from datetime import date, datetime, timedelta

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ComplaintForm, MaintenanceForm
from .models import Complaint, Issue, IssueStatus, Maintenance
from .query import completed_q, overdue_issue_queryset


def _issue_counts(base_qs):
    overdue_qs = overdue_issue_queryset()
    return {
        'all': base_qs.count(),
        'waiting': base_qs.filter(status=IssueStatus.OPEN).count(),
        'in_process': base_qs.filter(status=IssueStatus.IN_PROGRESS).count(),
        'overdue': base_qs.filter(pk__in=overdue_qs.values_list('pk', flat=True)).count(),
        'complete': base_qs.filter(completed_q()).count(),
    }


def _apply_status_filter(task_list, status_filter):
    if status_filter == 'waiting':
        return task_list.filter(status=IssueStatus.OPEN)
    if status_filter == 'in_process':
        return task_list.filter(status=IssueStatus.IN_PROGRESS)
    if status_filter == 'overdue':
        od = overdue_issue_queryset()
        return task_list.filter(pk__in=od.values_list('pk', flat=True))
    if status_filter == 'complete':
        return task_list.filter(completed_q())
    return task_list


def _overdue_pk_set():
    return set(overdue_issue_queryset().values_list('pk', flat=True))


def _is_issue_overdue(issue_pk):
    return issue_pk in _overdue_pk_set()


def all_tasks(request):
    task_list = Issue.objects.all().select_related('reporter', 'assigned_officer__user').order_by('-created_date')

    search_query = request.GET.get('q')
    if search_query:
        task_list = task_list.filter(
            Q(title__icontains=search_query)
            | Q(location__icontains=search_query)
            | Q(description__icontains=search_query)
        )

    status_filter = request.GET.get('status')
    task_list = _apply_status_filter(task_list, status_filter)

    counts = _issue_counts(Issue.objects.all())

    paginator = Paginator(task_list, 30)
    page_obj = paginator.get_page(request.GET.get('page'))

    overdue_pks = _overdue_pk_set()
    final_tasks = []
    for task in page_obj:
        item = {
            'id': task.id,
            'title': task.title,
            'location': task.location,
            'created_date': task.created_date,
            'status': task.status,
            'status_display': task.get_status_display(),
            'is_overdue': task.pk in overdue_pks,
            'type': 'Issue',
            'assign_to': '-',
            'type_badge_class': 'badge-secondary',
        }

        if isinstance(task, Complaint):
            item['type'] = 'Complaint'
            item['type_badge_class'] = 'badge-complaint'
            if task.assigned_officer:
                item['assign_to'] = task.assigned_officer.user.get_full_name() or task.assigned_officer.user.username
            else:
                item['assign_to'] = '—'
        elif isinstance(task, Maintenance):
            item['type'] = 'Maintenance'
            item['type_badge_class'] = 'badge-maintenance'
            tech = task.technician
            item['assign_to'] = (
                (tech.user.get_full_name() or tech.user.username) if tech else 'Unassigned'
            )

        final_tasks.append(item)

    return render(
        request,
        'issues/all_tasks.html',
        {
            'tasks': final_tasks,
            'page_obj': page_obj,
            'counts': counts,
            'current_status': status_filter if status_filter else 'all',
        },
    )


def complaint_tasks(request):
    tasks = Complaint.objects.select_related('issue_ptr', 'reporter', 'assigned_officer__user').order_by('-created_date')

    search_query = request.GET.get('q')
    if search_query:
        tasks = tasks.filter(Q(title__icontains=search_query) | Q(location__icontains=search_query))

    status_filter = request.GET.get('status')
    tasks = _apply_status_filter(tasks, status_filter)

    counts = _issue_counts(Complaint.objects.all())

    paginator = Paginator(tasks, 30)
    page_obj = paginator.get_page(request.GET.get('page'))

    overdue_pks = _overdue_pk_set()
    final_tasks = []
    for task in page_obj:
        assign_to = '—'
        if task.assigned_officer:
            assign_to = task.assigned_officer.user.get_full_name() or task.assigned_officer.user.username
        final_tasks.append(
            {
                'id': task.id,
                'title': task.title,
                'location': task.location,
                'created_date': task.created_date,
                'status': task.status,
                'status_display': task.get_status_display(),
                'is_overdue': task.pk in overdue_pks,
                'assign_to': assign_to,
            }
        )

    return render(
        request,
        'issues/all_tasks_complaints.html',
        {
            'tasks': final_tasks,
            'page_obj': page_obj,
            'counts': counts,
            'current_status': status_filter if status_filter else 'all',
        },
    )


def maintenance_tasks(request):
    tasks = Maintenance.objects.select_related('issue_ptr', 'reporter', 'technician__user').order_by('-created_date')

    search_query = request.GET.get('q')
    if search_query:
        tasks = tasks.filter(Q(title__icontains=search_query) | Q(location__icontains=search_query))

    status_filter = request.GET.get('status')
    tasks = _apply_status_filter(tasks, status_filter)

    counts = _issue_counts(Maintenance.objects.all())

    paginator = Paginator(tasks, 8)
    page_obj = paginator.get_page(request.GET.get('page'))

    overdue_pks = _overdue_pk_set()
    final_tasks = []
    for task in page_obj:
        tech_name = 'Unassigned'
        if task.technician:
            tech_name = task.technician.user.get_full_name() or task.technician.user.username

        final_tasks.append(
            {
                'id': task.id,
                'title': task.title,
                'location': task.location,
                'created_date': task.created_date,
                'status': task.status,
                'status_display': task.get_status_display(),
                'is_overdue': task.pk in overdue_pks,
                'assign_to': tech_name,
                'image': task.before_image.url if task.before_image else None,
            }
        )

    return render(
        request,
        'issues/all_tasks_maintenance.html',
        {
            'tasks': final_tasks,
            'page_obj': page_obj,
            'counts': counts,
            'current_status': status_filter if status_filter else 'all',
        },
    )


def create_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.status = IssueStatus.OPEN
            task.save()
            return redirect('issues:complaint_tasks')
    else:
        form = ComplaintForm()

    return render(request, 'issues/create_complaint.html', {'form': form})


def create_maintenance(request):
    if request.method == 'POST':
        form = MaintenanceForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.status = IssueStatus.OPEN
            task.save()
            return redirect('issues:maintenance_tasks')
    else:
        form = MaintenanceForm()

    return render(request, 'issues/create_maintenance.html', {'form': form})


def maintenance_detail(request, pk):
    task = get_object_or_404(
        Maintenance.objects.select_related('reporter__user', 'reporter__house', 'technician__user'),
        pk=pk,
    )

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'complete':
            task.status = IssueStatus.RESOLVED
            task.save()
        elif action == 'cancel':
            task.status = IssueStatus.CLOSED
            task.save()
        return redirect('issues:maintenance_detail', pk=pk)

    return render(
        request,
        'issues/maintenance_detail.html',
        {'task': task, 'is_overdue': _is_issue_overdue(task.pk)},
    )


def complaint_detail(request, pk):
    task = get_object_or_404(
        Complaint.objects.select_related('reporter__user', 'assigned_officer__user'),
        pk=pk,
    )

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'complete':
            task.status = IssueStatus.RESOLVED
            task.save()
        return redirect('issues:complaint_detail', pk=pk)

    return render(
        request,
        'issues/complaint_detail.html',
        {'task': task, 'is_overdue': _is_issue_overdue(task.pk)},
    )


def _calendar_context(request, *, use_appointment):
    today = date.today()
    view_mode = request.GET.get('view', 'month')
    date_param = request.GET.get('date')

    if date_param:
        try:
            selected_date = datetime.strptime(date_param, '%Y-%m-%d').date()
        except ValueError:
            selected_date = today
    else:
        selected_date = today

    year = selected_date.year
    month = selected_date.month
    day = selected_date.day

    if view_mode == 'month':
        prev_date = selected_date.replace(day=1) - timedelta(days=1)
        next_date = (selected_date.replace(day=28) + timedelta(days=4)).replace(day=1)
    elif view_mode == 'week':
        prev_date = selected_date - timedelta(days=7)
        next_date = selected_date + timedelta(days=7)
    elif view_mode == 'day':
        prev_date = selected_date - timedelta(days=1)
        next_date = selected_date + timedelta(days=1)
    else:
        prev_date = selected_date
        next_date = selected_date

    cal = calendar.Calendar(firstweekday=0)

    if view_mode == 'month':
        month_days = cal.monthdayscalendar(year, month)
    elif view_mode == 'week':
        start_week = selected_date - timedelta(days=selected_date.weekday())
        month_days = [[(start_week + timedelta(days=i)).day for i in range(7)]]
    elif view_mode == 'day':
        month_days = [[day]]
    else:
        month_days = cal.monthdayscalendar(year, month)

    events_by_day = {}

    if use_appointment:
        qs = Maintenance.objects.filter(appointment_date__year=year, appointment_date__month=month)
        for m in qs:
            if not m.appointment_date:
                continue
            d = m.appointment_date.day
            events_by_day.setdefault(d, []).append({'title': m.title, 'color': 'blue'})
    else:
        qs = Complaint.objects.filter(created_date__year=year, created_date__month=month)
        for c in qs:
            d = c.created_date.day
            events_by_day.setdefault(d, []).append({'title': c.title, 'color': 'orange'})

    return {
        'calendar': month_days,
        'month_name': calendar.month_name[month],
        'month_number': month,
        'year': year,
        'current_day': today.day,
        'events_by_day': events_by_day,
        'view_mode': view_mode,
        'selected_date': selected_date,
        'prev_date': prev_date.strftime('%Y-%m-%d'),
        'next_date': next_date.strftime('%Y-%m-%d'),
    }


def maintenance_calendar(request):
    ctx = _calendar_context(request, use_appointment=True)
    return render(request, 'issues/calendar_maintenance.html', ctx)


def complaint_calendar(request):
    ctx = _calendar_context(request, use_appointment=False)
    return render(request, 'issues/complaint_calendar.html', ctx)
