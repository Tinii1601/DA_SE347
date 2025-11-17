# books/forms.py
from django import forms


class BookSearchForm(forms.Form):
    q = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tìm kiếm sách, tác giả, ISBN...',
            'aria-label': 'Tìm kiếm'
        })
    )
    category = forms.ModelChoiceField(
        queryset=None,
        empty_label="Tất cả thể loại",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Category
        self.fields['category'].queryset = Category.objects.all()