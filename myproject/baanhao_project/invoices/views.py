from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Invoice


@login_required
def invoice_list(request):
    invoices = Invoice.objects.select_related('resident__user').order_by('-due_date')
    return render(request, 'invoices/invoice_list.html', {'invoices': invoices})
