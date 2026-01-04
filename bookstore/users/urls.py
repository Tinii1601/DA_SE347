# users/urls.py
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('address/add/', views.AddressCreateView.as_view(), name='address_add'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('verify-otp/', views.VerifyOTPView.as_view(), name='verify_otp'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset_password'),
    path('reset-success/', views.ResetSuccessView.as_view(), name='reset_success'),
]