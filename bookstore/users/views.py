# users/views.py
from django.views.generic import FormView, TemplateView, CreateView
from django.contrib.auth.views import LoginView as AuthLoginView, LogoutView as AuthLogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import RegistrationForm, LoginForm, AddressForm
from django.contrib.auth import login
from django.shortcuts import redirect, render
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

# Password Reset Views
from django.views import View
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
import random

class ForgotPasswordView(View):
    def get(self, request):
        return render(request, 'users/forgot_password.html')

    def post(self, request):
        email = request.POST.get('email')
        try:
            # Check if user exists with this email
            # Note: UserProfile has email, but User model also has email. 
            # We should check UserProfile primarily as per model definition, 
            # but standard auth uses User.email. Let's check both or UserProfile.
            # Based on models.py, UserProfile has the email field.
            try:
                profile = UserProfile.objects.get(email=email)
                user = profile.user
            except UserProfile.DoesNotExist:
                # Fallback to User model email if profile email not found
                user = User.objects.get(email=email)
            
            # Generate OTP
            otp = str(random.randint(100000, 999999))
            
            # Store in session
            request.session['reset_email'] = email
            request.session['reset_otp'] = otp
            
            # Send Email
            try:
                send_mail(
                    'Mã xác thực OTP - Bookstore',
                    f'Mã OTP của bạn là: {otp}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                return redirect('users:verify_otp')
            except Exception as e:
                print(f"Error sending email: {e}")
                return render(request, 'users/forgot_password.html', {
                    'error': f'Lỗi gửi email: {str(e)}. Vui lòng kiểm tra cấu hình hoặc thử lại sau.'
                })
            
        except (UserProfile.DoesNotExist, User.DoesNotExist):
            return render(request, 'users/forgot_password.html', {
                'error': 'Email không tồn tại trong hệ thống.'
            })

class VerifyOTPView(View):
    def get(self, request):
        if 'reset_email' not in request.session:
            return redirect('users:forgot_password')
        return render(request, 'users/verify_otp.html')

    def post(self, request):
        otp_input = request.POST.get('otp')
        session_otp = request.session.get('reset_otp')
        
        if otp_input == session_otp:
            request.session['reset_verified'] = True
            return redirect('users:reset_password')
        else:
            return render(request, 'users/verify_otp.html', {
                'error': 'Mã OTP không chính xác.'
            })

class ResetPasswordView(View):
    def get(self, request):
        if not request.session.get('reset_verified'):
            return redirect('users:forgot_password')
        return render(request, 'users/reset_password.html')

    def post(self, request):
        if not request.session.get('reset_verified'):
            return redirect('users:forgot_password')
            
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            return render(request, 'users/reset_password.html', {
                'error': 'Mật khẩu xác nhận không khớp.'
            })
            
        email = request.session.get('reset_email')
        try:
            try:
                profile = UserProfile.objects.get(email=email)
                user = profile.user
            except UserProfile.DoesNotExist:
                user = User.objects.get(email=email)
                
            user.set_password(new_password)
            user.save()
            
            # Clear session
            del request.session['reset_email']
            del request.session['reset_otp']
            del request.session['reset_verified']
            
            return redirect('users:reset_success')
            
        except Exception as e:
            return render(request, 'users/reset_password.html', {
                'error': 'Có lỗi xảy ra. Vui lòng thử lại.'
            })

class ResetSuccessView(TemplateView):
    template_name = 'users/reset_success.html'
