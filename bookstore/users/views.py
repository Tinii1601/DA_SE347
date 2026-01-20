# users/views.py
from django.views.generic import FormView, TemplateView, CreateView, UpdateView
from django.contrib.auth.views import LoginView as AuthLoginView, LogoutView as AuthLogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import RegistrationForm, LoginForm, AddressForm, ProfileUpdateForm, PasswordChangeCustomForm
from django.contrib.auth import login
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages
from .models import UserProfile, Address
from django.contrib.auth import update_session_auth_hash

class RegisterView(FormView):
    template_name = 'users/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('users:login')  
    def form_valid(self, form):
        # Lưu user + profile
        form.save()
        # Hiển thị thông báo thành công
        messages.success(self.request,'Đăng ký thành công! Vui lòng đăng nhập để tiếp tục.')
        # Không login tự động → chuyển đến trang login
        return super().form_valid(form)
    def form_invalid(self, form):
        # Khi form không hợp lệ, trả về như mặc định —
        # các lỗi từng field sẽ hiển thị bên dưới input trong template.
        return super().form_invalid(form)
    
class LoginView(AuthLoginView):
    template_name = 'users/login.html'
    form_class = LoginForm
    
class LogoutView(AuthLogoutView):
    next_page = reverse_lazy('core:home')

class AddressCreateView(LoginRequiredMixin, CreateView):
    model = Address
    template_name = 'users/address_form.html'
    form_class = AddressForm
    success_url = '/users/profile/'
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    from django.views.generic import TemplateView

class ProfileView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = ProfileUpdateForm
    template_name = 'users/profile/profile_info.html'
    success_url = reverse_lazy('users:profile')
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user )
        return profile
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user   # truyền user cho form
        return kwargs
    def form_valid(self, form):
        messages.success(self.request, "Cập nhật thông tin thành công")
        return super().form_valid(form)

class ProfilePageView(LoginRequiredMixin, TemplateView):
    template_name = "users/profile/profile_page.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Profile
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        # Address (mặc định)
        address = Address.objects.filter(user=self.request.user, is_default=True).first()
        display_email = self.request.user.email
        if not display_email:
            social = self.request.user.socialaccount_set.first()
            if social:
                display_email = social.extra_data.get("email", "")
        context["profile_form"] = kwargs.get("profile_form",ProfileUpdateForm(instance=profile, user=self.request.user))
        context["address_form"] = kwargs.get("address_form",AddressForm(instance=address))
        context["default_address"] = address
        context["password_form"] = kwargs.get("password_form",PasswordChangeCustomForm(self.request.user))
        context["active"] = "info"
        context["display_email"] = display_email
        return context
    def post(self, request, *args, **kwargs):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        address = Address.objects.filter(user=request.user, is_default=True).first()
        if "save_profile" in request.POST:
            profile_form = ProfileUpdateForm(request.POST, request.FILES,instance=profile, user=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Cập nhật thông tin cá nhân thành công")
                return redirect("users:profile")
            return self.render_to_response(self.get_context_data(profile_form=profile_form))
        if "save_address" in request.POST:
            address_form = AddressForm(request.POST, instance=address)
            if address_form.is_valid():
                addr = address_form.save(commit=False)
                addr.user = request.user
                addr.is_default = True
                addr.save()
                messages.success(request, "Cập nhật địa chỉ thành công")
                return redirect("users:profile")
            return self.render_to_response(
                self.get_context_data(address_form=address_form)
            )
        elif "change_password" in request.POST:
            password_form = PasswordChangeCustomForm(
                request.user, request.POST
            )
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Đổi mật khẩu thành công")
            else:
                return self.render_to_response(
                    self.get_context_data(password_form=password_form)
                )
        return redirect("users:profile")


class WishlistView(LoginRequiredMixin, TemplateView):
    template_name = "users/profile/profile_wishlist.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active"] = "wishlist"
        return context
        
