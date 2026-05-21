from django.shortcuts import render
import calendar # ต้องเพิ่ม Import โมดูล calendar ที่ด้านบนสุดของไฟล์ด้วยนะครับ
from datetime import date # เพิ่ม Import date

# ดึง Model จากแอปอื่นๆ มาใช้งาน
from notifications.models import Notification
from issues.models import Issue, Maintenance, Complaint

def public_announcements(request):
    # 1. ดึงข้อมูลประกาศทั้งหมด เรียงจากใหม่ไปเก่า (id มากไปน้อย)
    # หมายเหตุ: ถ้าใน Notification ของเธอมีฟิลด์จำพวก status='PUBLISHED' ค่อยมาใส่ .filter() เพิ่มทีหลังได้ครับ
    announcements = Notification.objects.all().order_by('-id')
    
    # 2. ห่อข้อมูลใส่ context เตรียมส่งให้หน้าเว็บ
    context = {
        'announcements': announcements
    }
    
    # 3. ส่งไปแสดงผลที่ไฟล์ template (เดี๋ยวเราจะสร้างไฟล์นี้ใน Phase 3)
    return render(request, 'public_views/announcements.html', context)

def public_calendar(request):
    today = date.today()
    
    try:
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))
    except ValueError:
        year = today.year
        month = today.month

    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year
        
    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year

    current_date_obj = date(year, month, 1)

    # ดึงข้อมูลมาแค่ครั้งเดียว (ลดการโหลด Database)
    events_in_month = Maintenance.objects.filter(
        appointment_date__isnull=False,
        appointment_date__year=year,
        appointment_date__month=month
    ).order_by('appointment_date')
    
    # จัดกลุ่มงานตามวันที่ ใน Python แทน (แก้บั๊กข้อมูลไม่แสดง)
    events_by_day = {}
    for event in events_in_month:
        day = event.appointment_date.day
        if day not in events_by_day:
            events_by_day[day] = []
        events_by_day[day].append(event)

    cal = calendar.Calendar(firstweekday=6)
    weeks = cal.monthdayscalendar(year, month)
    
    calendar_grid = []
    for week in weeks:
        week_data = []
        for day in week:
            if day > 0:
                day_events = events_by_day.get(day, []) # ดึงงานที่ตรงกับวันนี้
                # เช็กว่าใช่วันนี้ (Today) หรือไม่ จะได้ทำสีไฮไลต์
                is_today = (day == today.day and month == today.month and year == today.year)
            else:
                day_events = []
                is_today = False
            
            week_data.append({
                'day': day,
                'events': day_events,
                'is_current_month': day > 0,
                'is_today': is_today
            })
        calendar_grid.append(week_data)
        
    context = {
        'calendar_grid': calendar_grid,
        'current_month_name': current_date_obj.strftime("%B %Y"),
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'today_month': today.month,
        'today_year': today.year,
    }
    
    return render(request, 'public_views/calendar.html', context)