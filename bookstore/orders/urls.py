# orders/urls.py
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('success/<int:order_id>/', views.order_success, name='order_success'),
    path('history/', views.OrderHistoryView.as_view(), name='order_history'),
    path('detail/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
]
