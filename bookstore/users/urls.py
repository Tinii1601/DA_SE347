# users/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomPasswordResetForm, CustomSetPasswordForm
from .views import ProfileView, ProfilePageView, WishlistView

app_name = 'users'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', ProfilePageView.as_view(), name='profile'),
    path('profile/wishlist/', WishlistView.as_view(), name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='wishlist_toggle'),
    path('address/add/', views.AddressCreateView.as_view(), name='address_add'),
    # Password reset
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='forget_password'),
    path('password-reset/done/',auth_views.PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'),
        name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(
        template_name='users/password_reset_confirm.html',form_class=CustomSetPasswordForm,success_url='/users/password-reset-complete/'),
        name='password_reset_confirm'),
    path('password-reset-complete/',auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'),
        name='password_reset_complete'),
    path('password/change/', auth_views.PasswordChangeView.as_view(
        template_name='users/profile/profile_password.html',success_url='/users/profile/'),
        name='password_change')

]
