# books/urls.py
from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='book_list'),
    path('category/<slug:category_slug>/', views.ProductListView.as_view(), name='category_detail'),
    path('search/', views.ProductSearchView.as_view(), name='book_search'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='book_detail'),
]