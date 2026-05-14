"""Derived query helpers (DDL has no stored 'overdue' status — computed from dates)."""

from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

from .models import Complaint, Issue, IssueStatus, Maintenance


def overdue_issue_queryset():
    """
    Maintenance: appointment_date passed and still open/in_progress.
    Complaint: created_at older than 14 days and still open/in_progress.
    """
    now = timezone.now()
    stale = now - timedelta(days=14)

    m_ids = Maintenance.objects.filter(
        appointment_date__lt=now,
        status__in=[IssueStatus.OPEN, IssueStatus.IN_PROGRESS],
    ).values_list('pk', flat=True)

    c_ids = Complaint.objects.filter(
        created_date__lt=stale,
        status__in=[IssueStatus.OPEN, IssueStatus.IN_PROGRESS],
    ).values_list('pk', flat=True)

    return Issue.objects.filter(pk__in=list(m_ids) + list(c_ids)).distinct()


def completed_q():
    return Q(status=IssueStatus.RESOLVED) | Q(status=IssueStatus.CLOSED)
