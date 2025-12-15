# core/urls.py
from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('test-404/', TemplateView.as_view(template_name='404.html'), name='test_404'),
]