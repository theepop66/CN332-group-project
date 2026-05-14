from django.shortcuts import render
from django.core.paginator import Paginator
from .models import VisitLog

def visitor_list(request):
    # Fetch all visit logs, order by newest first
    logs = VisitLog.objects.all().order_by('-created_at')
    
    # Optional search filtering
    search_query = request.GET.get('q')
    if search_query:
        logs = logs.filter(visitor_name__icontains=search_query) | \
               logs.filter(license_plate__icontains=search_query) | \
               logs.filter(house_number__icontains=search_query)

    # Status filtering
    status_filter = request.GET.get('status')
    if status_filter:
        logs = logs.filter(status=status_filter)
        
    paginator = Paginator(logs, 10) # 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistics for dashboard-like view
    stats = {
        'total': VisitLog.objects.count(),
        'pending': VisitLog.objects.filter(status='pending').count(),
        'approved': VisitLog.objects.filter(status='approved').count(),
        'rejected': VisitLog.objects.filter(status='rejected').count(),
    }

    context = {
        'page_obj': page_obj,
        'stats': stats,
        'current_status': status_filter or 'all'
    }

    return render(request, 'visitors/visitor_list.html', context)
