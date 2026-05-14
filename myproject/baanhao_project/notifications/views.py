from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .models import Notification, NotificationType


@login_required
def notification_view(request):
    qs = (
        Notification.objects.filter(Q(user=request.user) | Q(user__isnull=True))
        .select_related('issue')
        .order_by('-created_at')
    )

    type_filter = request.GET.get('type', '')
    if type_filter in NotificationType.values:
        qs = qs.filter(notification_type=type_filter)

    read_filter = request.GET.get('read', '')
    if read_filter == 'unread':
        qs = qs.filter(is_read=False)
    elif read_filter == 'read':
        qs = qs.filter(is_read=True)

    paginator = Paginator(qs, 8)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(
        request,
        'notifications/notifications.html',
        {
            'page_obj': page_obj,
            'type_filter': type_filter,
            'read_filter': read_filter,
            'notification_types': NotificationType.choices,
        },
    )


@login_required
@require_POST
def mark_all_notifications_read(request):
    n = Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    if n:
        messages.success(request, 'Marked your notifications as read.')
    else:
        messages.info(request, 'No unread personal notifications to update.')
    nxt = request.POST.get('next') or reverse('notifications:list')
    if not url_has_allowed_host_and_scheme(
        nxt,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        nxt = reverse('notifications:list')
    return redirect(nxt)


@login_required
def broadcast_system(request):
    time_slots = []
    for h in range(7, 21):
        time_slots.append(f'{h:02d}:00')
        time_slots.append(f'{h:02d}:30')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        message_body = request.POST.get('message', '').strip()
        scheduled_date = request.POST.get('scheduled_date', '').strip()
        scheduled_time = request.POST.get('scheduled_time', '').strip()

        if not title or not message_body:
            messages.error(request, 'กรุณากรอกหัวข้อและข้อความ')
        else:
            extra = ''
            if scheduled_date or scheduled_time:
                extra = f"\n(กำหนดส่ง: {scheduled_date or '-'} {scheduled_time or '-'})"
            full_message = message_body + extra
            User = get_user_model()
            Notification.objects.bulk_create(
                [
                    Notification(
                        user=u,
                        notification_type=NotificationType.ANNOUNCEMENT,
                        title=title,
                        message=full_message,
                        is_read=False,
                    )
                    for u in User.objects.filter(is_active=True)
                ]
            )
            messages.success(request, 'ส่งประกาศไปยังผู้ใช้ที่เปิดใช้งานแล้ว')
            return redirect('notifications:list')

    return render(request, 'notifications/broadcast_system.html', {'time_slots': time_slots})
