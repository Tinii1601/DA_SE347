"""
URL configuration for bookstore project.
"""
# bookstore/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.shortcuts import redirect
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('', include('core.urls')),  # Home
    path('books/', include('books.urls')),
    path('users/', include('users.urls')),
    path('orders/', include('orders.urls')),
    path('cart/', lambda request: redirect('orders:cart_detail'), name='cart_shortcut'),
    path('reviews/', include('reviews.urls')),
    path('payment/', include('payment.urls')),
    path('chatbot/', include('chatbot.urls')),
    path('accounts/', include('allauth.urls')),

    # Serve media files (images, covers, banners, avatars) in both dev and production
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
