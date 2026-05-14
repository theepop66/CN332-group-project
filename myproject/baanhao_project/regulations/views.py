from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Regulation


@login_required
def regulation_list(request):
    regulations = Regulation.objects.all().order_by('category', 'topic')
    return render(request, 'regulations/regulation_list.html', {'regulations': regulations})
