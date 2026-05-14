from django.urls import path

from . import views

app_name = 'regulations'

urlpatterns = [
    path('', views.regulation_list, name='list'),
]
