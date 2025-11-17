# core/views.py
from django.views.generic import TemplateView
from books.models import Book

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['new_books'] = Book.objects.filter(is_active=True).order_by('-created_at')[:10]
        context['best_sellers'] = Book.objects.filter(is_active=True).order_by('-price')[:5]
        return context