# apps/core/urls.py
from django.urls import path
from . import views

app_name = 'apps.core'  # Namespace برای استفاده در قالب‌ها

urlpatterns = [
    path('', views.home, name='home'),
path("preview404/", views.error_404_preview, name="preview_404"),
    path("preview500/", views.error_500_preview, name="preview_500"),

]


