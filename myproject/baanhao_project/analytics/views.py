import json
from datetime import timedelta

from django.db.models import Case, Count, When
from django.shortcuts import render
from django.utils import timezone

from issues.models import Complaint, Issue, IssueStatus, Maintenance
from issues.query import overdue_issue_queryset


def analytics_view(request):
    issues = Issue.objects.all()
    total = issues.count()
    completed = issues.filter(
        status__in=[IssueStatus.RESOLVED, IssueStatus.CLOSED],
    ).count()
    processing = issues.filter(status=IssueStatus.IN_PROGRESS).count()
    overdue = overdue_issue_queryset().count()
    pending = issues.filter(status=IssueStatus.OPEN).count()

    today = timezone.localdate()
    trend_labels = []
    trend_counts = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        trend_labels.append(day.strftime('%a'))
        trend_counts.append(Issue.objects.filter(created_date__date=day).count())

    perf_rows = []
    for row in Maintenance.objects.values('equipment_type').annotate(
        total=Count('id'),
        done=Count(
            Case(
                When(
                    status__in=[IssueStatus.RESOLVED, IssueStatus.CLOSED],
                    then=1,
                )
            )
        ),
    ):
        et = row['equipment_type'] or '—'
        if row['total']:
            pct = int(round(100 * row['done'] / row['total']))
            perf_rows.append({'label': et, 'pct': pct})

    perf_rows.sort(key=lambda x: -x['pct'])
    performance_rows = perf_rows[:3]

    cat_rows = []
    for row in Complaint.objects.values('category').annotate(
        total=Count('id'),
        done=Count(
            Case(
                When(
                    status__in=[IssueStatus.RESOLVED, IssueStatus.CLOSED],
                    then=1,
                )
            )
        ),
    ):
        label = row['category'] or '—'
        if row['total']:
            pct = int(round(100 * row['done'] / row['total']))
            cat_rows.append({'label': label, 'pct': pct})

    attn_maint = sorted(perf_rows, key=lambda x: x['pct'])[:3]
    attn_cat = sorted(cat_rows, key=lambda x: x['pct'])[:3]
    attention_rows = attn_maint if attn_maint else attn_cat

    context = {
        'total_tasks': total,
        'completed': completed,
        'processing': processing,
        'overdue': overdue,
        'pending': pending,
        'chart_done': completed,
        'chart_pending': pending,
        'chart_processing': processing,
        'chart_overdue': overdue,
        'trend_labels_json': json.dumps(trend_labels),
        'trend_data_json': json.dumps(trend_counts),
        'performance_rows': performance_rows,
        'attention_rows': attention_rows,
    }
    return render(request, 'analytics/analytics.html', context)
