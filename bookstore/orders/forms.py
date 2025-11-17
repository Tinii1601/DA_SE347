# orders/forms.py
from django import forms
from .models import Order, Payment


class CheckoutForm(forms.ModelForm):
    payment_method = forms.ChoiceField(
        choices=Payment.METHOD_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    coupon_code = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mã giảm giá (nếu có)'})
    )

    class Meta:
        model = Order
        fields = ['note']
        widgets = {
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ghi chú (tùy chọn)'})
        }