# users/views.py
from django.views.generic import FormView, TemplateView, CreateView
from django.contrib.auth.views import LoginView as AuthLoginView, LogoutView as AuthLogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import RegistrationForm, LoginForm, AddressForm
from django.contrib.auth import login
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages
from .models import UserProfile, Address

class RegisterView(FormView):
    template_name = 'users/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('users:login')  

    def form_valid(self, form):
        # Lưu user + profile
        form.save()
        
        # Hiển thị thông báo thành công
        messages.success(
            self.request,
            'Đăng ký thành công! Vui lòng đăng nhập để tiếp tục.'
        )
        
        # Không login tự động → chuyển đến trang login
        return super().form_valid(form)
    
    def form_invalid(self, form):
        # Hiển thị lỗi nếu form không hợp lệ
        messages.error(self.request, 'Vui lòng sửa các lỗi bên dưới.')
        return super().form_invalid(form)

class LoginView(AuthLoginView):
    template_name = 'users/login.html'
    form_class = LoginForm

class LogoutView(AuthLogoutView):
    next_page = reverse_lazy('core:home')

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['addresses'] = Address.objects.filter(user=self.request.user)
        return context

class AddressCreateView(LoginRequiredMixin, CreateView):
    model = Address
    template_name = 'users/address_form.html'
    form_class = AddressForm
    success_url = '/users/profile/'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)