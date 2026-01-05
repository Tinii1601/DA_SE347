# users/forms.py
import re
from datetime import date
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import (UserCreationForm, AuthenticationForm,SetPasswordForm, PasswordResetForm, PasswordChangeForm)
from django.contrib.auth.models import User
from .models import UserProfile, Address
from django.contrib.auth.password_validation import validate_password

# ĐĂNG KÝ 
class RegistrationForm(UserCreationForm):
    username = forms.CharField(
        label="Tên đăng nhập", max_length=150, widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'Tên đăng nhập'})
    )
    first_name = forms.CharField( 
        label="Họ", max_length=50,widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Họ'}))
    last_name = forms.CharField(
        label="Tên", max_length=100,widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tên'}))
    date_of_birth = forms.DateField(
        label="Ngày sinh",widget=forms.DateInput(attrs={'type': 'date','class': 'form-control'}))
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    phone = forms.CharField(
        max_length=15, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Số điện thoại'}))
    agree_terms = forms.BooleanField(
        required=True,label="Tôi đồng ý với Điều khoản & Chính sách")
    class Meta:
        model = User
        fields = ('username', 'phone', 'email', 'password1', 'password2')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Tên đăng nhập'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Mật khẩu'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nhập lại mật khẩu'})
    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not username: raise ValidationError("Tên đăng nhập không được để trống.")
        if " " in username: raise ValidationError("Tên đăng nhập không được chứa khoảng trắng.")
        if User.objects.filter(username__iexact=username).exists():raise ValidationError("Tên đăng nhập đã tồn tại.")
        return username
    def clean_first_name(self):
        name = self.cleaned_data.get('first_name', '').strip()
        if not name: raise ValidationError("Họ không được để trống.")
        if not re.match(r'^[A-Za-zÀ-ỹ\s]+$', name): raise ValidationError("Họ chỉ được chứa chữ cái và khoảng trắng.")
        return name
    def clean_last_name(self):
        name = self.cleaned_data.get('last_name', '').strip()
        if not name: raise ValidationError("Tên không được để trống.")
        if not re.match(r'^[A-Za-zÀ-ỹ\s]+$', name): raise ValidationError("Tên chỉ được chứa chữ cái và khoảng trắng.")
        return name
    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if not re.match(r'^0\d{9}$', phone): raise ValidationError("Số điện thoại phải gồm 10 chữ số và bắt đầu bằng 0.")
        if UserProfile.objects.filter(phone=phone).exists(): raise ValidationError("Số điện thoại này đã được sử dụng.")
        return phone
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists(): raise ValidationError("Email này đã được sử dụng.")
        return email
    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if not dob: raise ValidationError("Vui lòng chọn ngày sinh.")
        today = date.today()
        age = today.year - dob.year - (
            (today.month, today.day) < (dob.month, dob.day)
        )
        if age < 14: raise ValidationError("Người dùng phải đủ 14 tuổi trở lên.")
        return dob
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Tạo hoặc cập nhật UserProfile
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.phone = self.cleaned_data['phone']
            profile.date_of_birth = self.cleaned_data['date_of_birth']
            profile.email = user.email
            profile.save()
        return user

# ĐĂNG NHẬP
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Số điện thoại (*)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mô tả cụ thể tại đây'})
    )
    password = forms.CharField(
        label="Mật khẩu (*)",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mô tả cụ thể tại đây'})
    )
    class Meta:
        fields = ['username', 'password']

# ĐỊA CHỈ GIAO HÀNG
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['full_name', 'phone', 'address_line', 'ward', 'district', 'city']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line': forms.TextInput(attrs={'class': 'form-control'}),
            'ward': forms.TextInput(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
        }
    def clean_full_name(self):
        name = self.cleaned_data.get('full_name', '').strip()
        if not name: raise ValidationError("Họ và tên không được để trống.")
        if not re.match(r'^[A-Za-zÀ-ỹ\s]+$', name): raise ValidationError("Họ và tên chỉ được chứa chữ cái và khoảng trắng.")
        return name
    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if not re.match(r'^0\d{9}$', phone): raise ValidationError("Số điện thoại phải gồm 10 chữ số và bắt đầu bằng 0.")
        return phone
    def clean_address_line(self):
        addr = self.cleaned_data.get('address_line', '').strip()
        if not addr: raise ValidationError("Địa chỉ không được để trống.")
        return addr
    def clean_city(self):
        city = self.cleaned_data.get('city')
        if not city: raise ValidationError("Vui lòng chọn tỉnh / thành phố.")
        return city
    def clean_district(self):
        district = self.cleaned_data.get('district')
        if not district: raise ValidationError("Vui lòng chọn quận / huyện.")
        return district
    def clean_ward(self):
        ward = self.cleaned_data.get('ward')
        if not ward: raise ValidationError("Vui lòng chọn phường / xã.")
        return ward
    def is_valid(self):
        valid = super().is_valid()
        for field in self.errors:
            if field in self.fields:
                self.fields[field].widget.attrs['class'] += ' is-invalid'
        return valid
# QUÊN MẬT KHẨU      
class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nhập email của bạn'
        })
# ĐẶT LẠI MẬT KHẨU
class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.error_messages['password_mismatch'] = (
            'Mật khẩu xác nhận không khớp. Vui lòng nhập lại.'
        )

        self.fields['new_password1'].error_messages = {
            'password_too_short': 'Mật khẩu phải có ít nhất 8 ký tự.',
            'password_too_common': 'Mật khẩu này quá phổ biến, vui lòng chọn mật khẩu khác.',
            'password_entirely_numeric': 'Mật khẩu không được chỉ chứa chữ số.',
        }
        self.fields['new_password1'].widget.input_type = 'password'
        self.fields['new_password2'].widget.input_type = 'password'

        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nhập mật khẩu mới'
        })

        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Xác nhận mật khẩu mới'
        })

# CẬP NHẬT THÔNG TIN CÁ NHÂN   
class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        label="Họ",widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label="Tên",widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    phone = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    avatar = forms.ImageField(required=False,widget=forms.FileInput(attrs={
            'id': 'id_avatar','accept': 'image/*','style': 'display:none;'})
    )
    class Meta:
        model = UserProfile
        fields = ['date_of_birth', 'phone', 'avatar']
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['first_name'].initial = self.user.first_name
        self.fields['last_name'].initial = self.user.last_name
    def clean_first_name(self):
        name = self.cleaned_data.get('first_name', '').strip()
        if not name:raise ValidationError("Họ không được để trống.")
        if not re.match(r'^[A-Za-zÀ-ỹ\s]+$', name):raise ValidationError("Họ chỉ được chứa chữ cái và khoảng trắng.")
        return name
    def clean_last_name(self):
        name = self.cleaned_data.get('last_name', '').strip()
        if not name: raise ValidationError("Tên không được để trống.")
        if not re.match(r'^[A-Za-zÀ-ỹ\s]+$', name): raise ValidationError("Tên chỉ được chứa chữ cái và khoảng trắng.")
        return name
    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if not re.match(r'^0\d{9}$', phone): raise ValidationError("Số điện thoại phải gồm 10 chữ số và bắt đầu bằng 0.")
        if UserProfile.objects.exclude(user=self.user).filter(phone=phone).exists(): raise ValidationError("Số điện thoại này đã được sử dụng.")
        return phone
    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if not dob: raise ValidationError("Vui lòng chọn ngày sinh.")
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < 14: raise ValidationError("Người dùng phải đủ 14 tuổi trở lên.")
        return dob
    def is_valid(self):
        valid = super().is_valid()
        for field in self.errors:
            if field in self.fields:
                self.fields[field].widget.attrs['class'] += ' is-invalid'
        return valid
    def save(self, commit=True):
        profile = super().save(commit=False)
        self.user.first_name = self.cleaned_data['first_name']
        self.user.last_name = self.cleaned_data['last_name']
        if commit:
            self.user.save()
            profile.user = self.user
            profile.save()
        return profile
# ĐỔI MẬT KHẨU TRONG PROFILE
class PasswordChangeCustomForm(forms.Form):
    old_password = forms.CharField(label="Mật khẩu hiện tại",widget=forms.PasswordInput(attrs={
        "class": "form-control",
        "placeholder": "Nhập mật khẩu hiện tại"})
    )
    new_password1 = forms.CharField(
        label="Mật khẩu mới",widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Nhập mật khẩu mới"
        })
    )
    new_password2 = forms.CharField(
        label="Xác nhận mật khẩu mới",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Nhập lại mật khẩu mới"
        })
    )
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    def clean_old_password(self):
        old_password = self.cleaned_data.get("old_password")
        if not self.user.check_password(old_password): raise ValidationError("Mật khẩu hiện tại không đúng.")
        return old_password
    def clean_new_password1(self):
        password = self.cleaned_data.get("new_password1")
        validate_password(password, self.user)
        return password
    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("new_password1")
        p2 = cleaned_data.get("new_password2")
        if p1 and p2 and p1 != p2:
            self.add_error("new_password2", "Mật khẩu xác nhận không khớp.")
        return cleaned_data
    def save(self):
        self.user.set_password(self.cleaned_data["new_password1"])
        self.user.save()
        return self.user