from django.urls import path
from . import views

app_name = "visitors"

urlpatterns = [
    path("", views.visitor_list, name="visitor_list"),
]
