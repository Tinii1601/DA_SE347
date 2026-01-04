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
from .models import Order, OrderItem
from payment.models import Payment

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
        default_address = addresses.filter(is_default=True).first() or addresses.first()
        
        return render(request, 'orders/checkout.html', {
            'cart': cart,
            'form': form,
            'addresses': addresses,
            'default_address': default_address
        })

    def post(self, request):
        cart = Cart(request)
        if len(cart) == 0:
            return redirect('orders:cart_detail')
            
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Handle Address: Check if new address data is provided
            full_name = request.POST.get('full_name')
            phone = request.POST.get('phone')
            city = request.POST.get('city')
            district = request.POST.get('district')
            ward = request.POST.get('ward')
            address_line = request.POST.get('address_line')

            if full_name and phone and city and district and ward and address_line:
                # Create or update address
                # For simplicity in this flow, we'll create a new one or get an existing identical one
                address, created = Address.objects.get_or_create(
                    user=request.user,
                    full_name=full_name,
                    phone=phone,
                    city=city,
                    district=district,
                    ward=ward,
                    address_line=address_line,
                    defaults={'is_default': True} # Set as default if created
                )
            else:
                # Fallback to existing logic (address_id)
                address_id = request.POST.get('address_id')
                if not address_id:
                    # Try to get the default address
                    address = Address.objects.filter(user=request.user, is_default=True).first()
                    if not address:
                        # If no default, get the first one
                        address = Address.objects.filter(user=request.user).first()
                    
                    if not address:
                         addresses = Address.objects.filter(user=request.user)
                         return render(request, 'orders/checkout.html', {
                            'cart': cart,
                            'form': form,
                            'addresses': addresses,
                            'error': 'Vui lòng nhập thông tin giao hàng'
                        })
                else:
                    address = get_object_or_404(Address, id=address_id, user=request.user)
            
            # Create Order
            order = form.save(commit=False)
            order.user = request.user
            order.shipping_address = address
            order.total_amount = cart.get_total_price()
            
            # Apply Coupon
            coupon_id = request.session.get('coupon_id')
            if coupon_id:
                try:
                    from .models import Coupon
                    coupon = Coupon.objects.get(id=coupon_id)
                    if coupon.is_valid():
                        discount = coupon.calculate_discount(order.total_amount, order.shipping_fee)
                        order.coupon = coupon
                        order.discount_amount = discount
                        order.total_amount = float(order.total_amount) + float(order.shipping_fee) - float(discount)
                        
                        # Update usage
                        coupon.used_count += 1
                        coupon.save()
                        
                        # Clear session
                        del request.session['coupon_id']
                    else:
                        # Coupon invalid, just calculate total with shipping
                        order.total_amount = float(order.total_amount) + float(order.shipping_fee)
                except Coupon.DoesNotExist:
                     order.total_amount = float(order.total_amount) + float(order.shipping_fee)
            else:
                order.total_amount = float(order.total_amount) + float(order.shipping_fee)

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
            
            # Redirect based on payment method
            print(f"DEBUG: Payment method selected: {payment_method}")
            
            if payment_method == 'momo':
                return redirect('payment:payment_momo', order_id=order.id)
            elif payment_method == 'vietqr':
                return redirect('payment:payment_vietqr', order_id=order.id)
            elif payment_method == 'cod':
                # Clear Cart only for COD
                cart.clear()
                return redirect('orders:order_success', order_id=order.id)
            else:
                # For other methods (e.g. vnpay), do not clear cart immediately
                # TODO: Implement handlers for other methods
                return redirect('orders:order_success', order_id=order.id)
                
        addresses = Address.objects.filter(user=request.user)
        return render(request, 'orders/checkout.html', {
            'cart': cart,
            'form': form,
            'addresses': addresses
        })

def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})


class OrderHistoryView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_history.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

@require_POST
def apply_coupon(request):
    import json
    from django.utils import timezone
    from .models import Coupon
    
    try:
        data = json.loads(request.body)
        code = data.get('code')
        cart = Cart(request)
        total_price = cart.get_total_price()
        shipping_fee = 30000 # Default shipping fee
        
        try:
            coupon = Coupon.objects.get(code=code)
            if coupon.is_valid():
                discount = coupon.calculate_discount(total_price, shipping_fee)
                if discount > 0:
                    # Store in session
                    request.session['coupon_id'] = coupon.id
                    
                    final_total = float(total_price) + shipping_fee - float(discount)
                    return JsonResponse({
                        'success': True,
                        'discount': float(discount),
                        'total': final_total,
                        'message': f'Áp dụng mã {code} thành công!'
                    })
                else:
                    return JsonResponse({'success': False, 'message': 'Đơn hàng chưa đủ điều kiện áp dụng mã này.'})
            else:
                return JsonResponse({'success': False, 'message': 'Mã giảm giá không hợp lệ hoặc đã hết hạn.'})
        except Coupon.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Mã giảm giá không tồn tại.'})
            
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})