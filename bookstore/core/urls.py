# core/urls.py
from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('stores/', views.StoreListView.as_view(), name='stores'),
    path('pages/<slug:slug>/', views.ContentPageDetailView.as_view(), name='page_detail'),
    path('chinh-sach-quyen-rieng-tu/', TemplateView.as_view(template_name='privacy_policy.html'), name='privacy_policy'),
    path('xoa-du-lieu/', TemplateView.as_view(template_name='data_deletion.html'), name='data_deletion'),
    path('facebook/data-deletion/', views.facebook_data_deletion_callback, name='facebook_data_deletion'),
    path('tin-tuc-su-kien/', views.NewsListView.as_view(), name='news_list'),
    path('tin-tuc-su-kien/<slug:slug>/', views.NewsDetailView.as_view(), name='news_detail'),
    path('lien-he/', views.ContactView.as_view(), name='contact'),
    path('test-404/', TemplateView.as_view(template_name='404.html'), name='test_404'),
]
