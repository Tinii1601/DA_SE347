# reviews/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('<int:book_id>/add/', views.ReviewCreateView.as_view(), name='review_add'),
]