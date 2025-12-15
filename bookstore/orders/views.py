# orders/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, FormView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from books.models import Book
from users.models import Address
from .cart import Cart
from .forms import CartAddProductForm, CheckoutForm
from .models import Order, OrderItem, Payment

from django.http import JsonResponse

@require_POST
def cart_add(request, book_id):
    cart = Cart(request)
    book = get_object_or_404(Book, id=book_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(book=book,
                 quantity=cd['quantity'],
                 override_quantity=cd['override'])
    
    # Check for AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'cart_length': len(cart)})
        
    return redirect('orders:cart_detail')

@require_POST
def cart_remove(request, book_id):
    cart = Cart(request)
    book = get_object_or_404(Book, id=book_id)
    cart.remove(book)
    return redirect('orders:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={
                            'quantity': item['quantity'],
                            'override': True})
    
    # Logic for "Continue Shopping" URL
    referer = request.META.get('HTTP_REFERER')
    # Only update if referer exists and is NOT from within the cart/order system
    if referer and '/orders/' not in referer and '/cart/' not in referer:
        request.session['continue_shopping_url'] = referer
    
    continue_shopping_url = request.session.get('continue_shopping_url', '/')

    # Get random books for recommendations
    import random
    all_books = list(Book.objects.filter(is_active=True))
    recommended_books = random.sample(all_books, min(len(all_books), 4))

    return render(request, 'orders/cart_detail.html', {
        'cart': cart, 
        'continue_shopping_url': continue_shopping_url,
        'recommended_books': recommended_books
    })

class CheckoutView(LoginRequiredMixin, View):
    def get(self, request):
        cart = Cart(request)
        if len(cart) == 0:
            return redirect('orders:cart_detail')
        
        form = CheckoutForm()
        addresses = Address.objects.filter(user=request.user)
        
        return render(request, 'orders/checkout.html', {
            'cart': cart,
            'form': form,
            'addresses': addresses
        })

    def post(self, request):
        cart = Cart(request)
        if len(cart) == 0:
            return redirect('orders:cart_detail')
            
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Get address
            address_id = request.POST.get('address_id')
            if not address_id:
                # Handle case where no address is selected
                addresses = Address.objects.filter(user=request.user)
                return render(request, 'orders/checkout.html', {
                    'cart': cart,
                    'form': form,
                    'addresses': addresses,
                    'error': 'Vui lòng chọn địa chỉ giao hàng'
                })
            
            address = get_object_or_404(Address, id=address_id, user=request.user)
            
            # Create Order
            order = form.save(commit=False)
            order.user = request.user
            order.shipping_address = address
            order.total_amount = cart.get_total_price()
            order.save()
            
            # Create OrderItems
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    book=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            
            # Create Payment
            payment_method = form.cleaned_data['payment_method']
            Payment.objects.create(
                order=order,
                method=payment_method,
                amount=order.total_amount
            )
            
            # Clear Cart
            cart.clear()
            
            # Redirect based on payment method
            if payment_method == 'momo':
                return redirect('orders:payment_momo', order_id=order.id)
            elif payment_method == 'vietqr':
                return redirect('orders:payment_vietqr', order_id=order.id)
            else:
                return redirect('orders:order_success', order_id=order.id)
                
        addresses = Address.objects.filter(user=request.user)
        return render(request, 'orders/checkout.html', {
            'cart': cart,
            'form': form,
            'addresses': addresses
        })

def payment_momo(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/payment_momo.html', {'order': order})

def payment_vietqr(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/payment_vietqr.html', {'order': order})

def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})


class OrderHistoryView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_history.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)