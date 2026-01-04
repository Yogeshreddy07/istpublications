# apps/emails/urls.py

from django.urls import path
from . import views

app_name = 'emails'

urlpatterns = [
    # Admin dashboard
    path('admin/dashboard/', views.email_dashboard, name='dashboard'),
    path('admin/statistics/', views.email_statistics_api, name='statistics'),
]
