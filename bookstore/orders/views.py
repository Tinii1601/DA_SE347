# orders/views.py
from django.views.generic import TemplateView, FormView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm
from .models import Order
from django.shortcuts import redirect

class CartView(LoginRequiredMixin, TemplateView):
    template_name = 'orders/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Giả định có session cart (thêm logic thực tế nếu cần)
        context['cart_items'] = []  # Thay bằng giỏ hàng thực
        return context

class CheckoutView(LoginRequiredMixin, FormView):
    template_name = 'orders/checkout.html'
    form_class = CheckoutForm
    success_url = '/orders/history/'

    def form_valid(self, form):
        # Tạo order (thêm logic thực tế: lưu order, payment)
        order = Order.objects.create(
            user=self.request.user,
            total_amount=0,  # Tính từ cart
            note=form.cleaned_data['note']
        )
        # Tạo payment
        payment = order.payment
        payment.method = form.cleaned_data['payment_method']
        payment.save()
        return super().form_valid(form)

class OrderHistoryView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_history.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)