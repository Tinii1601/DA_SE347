# books/urls.py
from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.BookListView.as_view(), name='book_list'),
    path('<slug:slug>/', views.BookDetailView.as_view(), name='book_detail'),
    path('search/', views.BookSearchView.as_view(), name='book_search'),
]