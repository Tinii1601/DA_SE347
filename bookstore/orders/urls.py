# orders/urls.py
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:book_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:book_id>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('payment/momo/<int:order_id>/', views.payment_momo, name='payment_momo'),
    path('payment/vietqr/<int:order_id>/', views.payment_vietqr, name='payment_vietqr'),
    path('success/<int:order_id>/', views.order_success, name='order_success'),
    path('history/', views.OrderHistoryView.as_view(), name='order_history'),
]