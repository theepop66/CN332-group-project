from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect, render

from .models import Notification, NotificationType


@login_required
def notification_view(request):
    qs = Notification.objects.filter(Q(user=request.user) | Q(user__isnull=True)).order_by('-created_at')
    paginator = Paginator(qs, 8)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'notifications/notifications.html', {'page_obj': page_obj})


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
