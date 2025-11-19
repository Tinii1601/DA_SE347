# reviews/urls.py
from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('<int:book_id>/add/', views.ReviewCreateView.as_view(), name='review_add'),
    path('<int:pk>/edit/', views.ReviewUpdateView.as_view(), name='review_edit'),
]