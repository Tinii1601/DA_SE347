# books/views.py
from django.views.generic import ListView, DetailView
from .models import Book
from .forms import BookSearchForm

class BookListView(ListView):
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    queryset = Book.objects.filter(is_active=True)

class BookDetailView(DetailView):
    model = Book
    template_name = 'books/book_detail.html'
    context_object_name = 'book'
    slug_field = 'slug'

class BookSearchView(ListView):
    model = Book
    template_name = 'books/search.html'
    context_object_name = 'books'

    def get_queryset(self):
        form = BookSearchForm(self.request.GET)
        if form.is_valid():
            q = form.cleaned_data.get('q')
            category = form.cleaned_data.get('category')
            queryset = Book.objects.filter(is_active=True)
            if q:
                queryset = queryset.filter(title__icontains=q) | queryset.filter(author__icontains=q)
            if category:
                queryset = queryset.filter(category=category)
            return queryset
        return Book.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = BookSearchForm(self.request.GET)
        return context