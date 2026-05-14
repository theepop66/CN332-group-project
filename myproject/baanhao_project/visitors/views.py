from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import VisitorPass


@login_required
def visitor_pass_list(request):
    passes = VisitorPass.objects.select_related('house', 'created_by__user').order_by('-schedule_date')
    return render(request, 'visitors/visitor_list.html', {'visitor_passes': passes})
