# reviews/views.py
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ReviewForm
from .models import Review
from books.models import Book

class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    template_name = 'reviews/review_form.html'
    form_class = ReviewForm
    success_url = '/books/{book_slug}/'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.book = Book.objects.get(id=self.kwargs['book_id'])
        return super().form_valid(form)