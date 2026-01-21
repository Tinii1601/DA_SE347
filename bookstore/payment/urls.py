from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('create/<int:order_id>/', views.create_payment, name='create_payment'),
    path('vietqr/<int:order_id>/', views.payment_vietqr, name='payment_vietqr'),
    path('vietqr/confirm/<int:order_id>/', views.payment_vietqr_confirm, name='payment_vietqr_confirm'),
    path('return/<int:order_id>/', views.payment_return, name='payment_return'),
    path('cancel/<int:order_id>/', views.payment_cancel, name='payment_cancel'),
    path('check-status/<int:order_id>/', views.check_payment_status, name='check_status'),
    path('webhook/', views.webhook, name='webhook'),
]
