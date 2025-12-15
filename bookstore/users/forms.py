# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile, Address


# ĐĂNG KÝ 
class RegistrationForm(UserCreationForm):
    full_name = forms.CharField(
        label="Họ và tên (*)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mô tả cụ thể tại đây'})
    )
    date_of_birth = forms.DateField(
        label="Ngày sinh (*)",
        widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Mô tả cụ thể tại đây', 'type': 'date'})
    )
    phone = forms.CharField(
        label="Số điện thoại (*)",
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mô tả cụ thể tại đây'})
    )
    email = forms.EmailField(
        label="Email (*)",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Mô tả cụ thể tại đây'})
    )

    class Meta:
        model = User
        fields = ['full_name', 'date_of_birth', 'phone', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove username field from the form as we will set it to phone number
        if 'username' in self.fields:
            del self.fields['username']
            
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Mô tả cụ thể tại đây'})
        self.fields['password1'].label = "Mật khẩu (*)"
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Mô tả cụ thể tại đây'})
        self.fields['password2'].label = "Xác nhận mật khẩu (*)"

    def save(self, commit=True):
        user = super().save(commit=False)
        # Set username to phone number
        user.username = self.cleaned_data['phone']
        user.email = self.cleaned_data['email']
        
        # Split full name
        full_name = self.cleaned_data['full_name']
        if ' ' in full_name:
            user.first_name, user.last_name = full_name.rsplit(' ', 1)
        else:
            user.first_name = full_name
        
        if commit:
            user.save()
            # Tạo hoặc cập nhật UserProfile
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.phone = self.cleaned_data['phone']
            profile.email = self.cleaned_data['email']
            profile.date_of_birth = self.cleaned_data['date_of_birth']
            profile.save()
        return user

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if User.objects.filter(username=phone).exists():
            raise forms.ValidationError("Số điện thoại này đã được đăng ký.")
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Địa chỉ email này đã được sử dụng. Vui lòng chọn email khác.")
        return email


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
    full_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Họ và tên'})
    )
    phone = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Số điện thoại'})
    )
    address_line = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Số nhà, đường'})
    )
    ward = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phường/Xã'})
    )
    district = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Quận/Huyện'})
    )
    city = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tỉnh/Thành phố'})
    )

    class Meta:
        model = Address
        fields = ['full_name', 'phone', 'address_line', 'ward', 'district', 'city', 'is_default']
        widgets = {
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }