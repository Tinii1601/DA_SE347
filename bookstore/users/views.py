# users/views.py
from django.views.generic import FormView, TemplateView, CreateView, UpdateView
from django.contrib.auth.views import LoginView as AuthLoginView, LogoutView as AuthLogoutView, PasswordResetView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import (
    RegistrationForm,
    LoginForm,
    AddressForm,
    ProfileUpdateForm,
    PasswordChangeCustomForm,
    CustomPasswordResetForm,
)
from django.contrib.auth import login
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from .models import UserProfile, Address, WishlistItem
from django.contrib.auth import update_session_auth_hash
from books.models import Product
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.http import HttpResponseRedirect

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


class CustomPasswordResetView(PasswordResetView):
    template_name = 'users/password_reset_form.html'
    email_template_name = 'users/password_reset_email.txt'
    html_email_template_name = 'users/emails/password_reset.html'
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('users:password_reset_done')

    def form_valid(self, form):
        opts = {
            'use_https': self.request.is_secure(),
            'token_generator': self.token_generator,
            'from_email': self.from_email,
            'email_template_name': self.email_template_name,
            'subject_template_name': self.subject_template_name,
            'request': self.request,
            'html_email_template_name': self.html_email_template_name,
            'extra_email_context': self.extra_email_context,
            'domain_override': self.request.get_host(),
        }
        form.save(**opts)
        return HttpResponseRedirect(self.get_success_url())

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
        context["wishlist_items"] = (
            WishlistItem.objects.filter(user=self.request.user)
            .select_related("product")
        )
        return context


@require_POST
def toggle_wishlist(request, product_id):
    if not request.user.is_authenticated:
        return redirect(f"/users/login/?next={request.get_full_path()}")

    product = get_object_or_404(Product, id=product_id)
    obj, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        obj.delete()
        added = False
    else:
        added = True

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'added': added})

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or '/'
    return redirect(next_url)
        
