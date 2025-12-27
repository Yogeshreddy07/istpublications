from django.urls import path
from . import views

urlpatterns = [
    path("contact", views.contact_form_submit, name="contact_submit"),
    path("health", views.health_check, name="health_check"),
]

