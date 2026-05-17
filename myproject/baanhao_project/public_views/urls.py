from django.urls import path
from . import views

app_name = 'public_views'

urlpatterns = [
    # ถ้าเข้ามาที่ /public/announcements/ จะวิ่งไปที่ฟังก์ชัน public_announcements
    path('announcements/', views.public_announcements, name='announcements'),
    
    # ถ้าเข้ามาที่ /public/calendar/ จะวิ่งไปที่ฟังก์ชัน public_calendar
    path('calendar/', views.public_calendar, name='calendar'),
]