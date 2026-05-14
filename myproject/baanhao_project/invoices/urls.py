from django.urls import path

from . import views

app_name = 'invoices'

urlpatterns = [
    path('', views.invoice_list, name='list'),
]
