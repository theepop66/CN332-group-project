from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    path("", views.notification_view, name="list"),
    path("mark-all-read/", views.mark_all_notifications_read, name="mark_all_read"),
    path("broadcast/", views.broadcast_system, name="broadcast_system"),
]