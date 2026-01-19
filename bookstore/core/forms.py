from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(label="Tên của bạn", max_length=120)
    email = forms.EmailField(label="Email liên hệ")
    phone = forms.CharField(label="Số điện thoại", max_length=30, required=False)
    subject = forms.CharField(label="Tiêu đề", max_length=200)
    message = forms.CharField(label="Lời nhắn", widget=forms.Textarea)
