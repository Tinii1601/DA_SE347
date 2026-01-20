from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.contrib import messages

from .forms import ReviewForm
from .models import Review
from books.models import Product

class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/review_form.html'

    def dispatch(self, request, *args, **kwargs):
        product = get_object_or_404(Product, id=self.kwargs['product_id'])
        existing_review = Review.objects.filter(user=request.user, product=product).first()
        if existing_review:
            messages.info(request, "Bạn đã đánh giá sản phẩm này. Bạn có thể chỉnh sửa đánh giá của mình tại đây.")
            return HttpResponseRedirect(reverse('reviews:review_edit', kwargs={'pk': existing_review.pk}))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('books:book_detail', kwargs={'slug': self.object.product.slug})

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.product = get_object_or_404(Product, id=self.kwargs['product_id'])
        return super().form_valid(form)


class ReviewUpdateView(LoginRequiredMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/review_edit.html'

    def get_queryset(self):
        # Ensure user can only edit their own reviews
        return Review.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy('books:book_detail', kwargs={'slug': self.object.product.slug})
