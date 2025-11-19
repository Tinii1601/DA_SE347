# reviews/views.py
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.contrib import messages

from .forms import ReviewForm
from .models import Review
from books.models import Book

class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/review_form.html' # Optional: can be removed if not used

    def dispatch(self, request, *args, **kwargs):
        book = get_object_or_404(Book, id=self.kwargs['book_id'])
        existing_review = Review.objects.filter(user=request.user, book=book).first()
        if existing_review:
            messages.info(request, "Bạn đã đánh giá cuốn sách này. Bạn có thể chỉnh sửa đánh giá của mình tại đây.")
            return HttpResponseRedirect(reverse('reviews:review_edit', kwargs={'pk': existing_review.pk}))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('books:book_detail', kwargs={'slug': self.object.book.slug})

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.book = get_object_or_404(Book, id=self.kwargs['book_id'])
        return super().form_valid(form)


class ReviewUpdateView(LoginRequiredMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/review_edit.html'

    def get_queryset(self):
        # Ensure user can only edit their own reviews
        return Review.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy('books:book_detail', kwargs={'slug': self.object.book.slug})