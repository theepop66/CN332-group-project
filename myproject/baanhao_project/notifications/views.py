from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Notification

def notification_view(request):
    notifications = Notification.objects.all().order_by('-created_at')
    
    paginator = Paginator(notifications, 8)  # 8 ต่อหน้า
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "notifications/notifications.html", {
        "page_obj": page_obj
    })

def broadcast_system(request):
    time_slots = []
    for h in range(7, 21):
        time_slots.append(f"{h:02d}:00")
        time_slots.append(f"{h:02d}:30")

    return render(request, "notifications/broadcast_system.html", {
        "time_slots": time_slots
    })