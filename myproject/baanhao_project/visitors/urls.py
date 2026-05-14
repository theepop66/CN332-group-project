from django.urls import path

from . import views

app_name = 'visitors'

urlpatterns = [
    path('', views.visitor_pass_list, name='list'),
]
