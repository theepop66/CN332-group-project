"""
URL configuration for baanhao_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [

    # Root: redirect to login page
    path('', RedirectView.as_view(url='/users/login/', permanent=False)),

    # Django administration
    path('admin/', admin.site.urls),
    
    # Allauth
    path('accounts/', include('allauth.urls')),

    # Dashboard
    path('', include('dashboard.urls')),
    
    # Issue
    path('all_tasks/', include('issues.urls')),
    
    # Users
    path('users/', include('users.urls')),

    # analytics
    path("analytics/", include("analytics.urls")),

    #notifications
    path('notifications/', include('notifications.urls')),

    path('regulations/', include('regulations.urls')),
    path('visitors/', include('visitors.urls')),
    path('invoices/', include('invoices.urls')),
]
