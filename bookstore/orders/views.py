from decimal import Decimal
import logging
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q, F
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from books.models import Product
from users.models import Address, WishlistItem
from .cart import Cart
from .forms import CartAddProductForm, CheckoutForm
from .models import Order, OrderItem, Coupon
from payment.models import Payment
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse

logger = logging.getLogger(__name__)

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    # Quay lại trang hiện tại (trang chi tiết sách hoặc trang danh sách), fallback về chi tiết sách
    fallback_url = reverse('books:book_detail', args=[product.slug])
    referer_url = request.META.get('HTTP_REFERER') or fallback_url

    if form.is_valid():
        cd = form.cleaned_data
        requested_quantity = cd['quantity']
        override = cd['override']
        
        # Kiểm tra tồn kho trước khi thêm vào giỏ
        current_cart_item = cart.cart.get(str(product.id))
        current_qty = current_cart_item.get('quantity', 0) if current_cart_item else 0
        total_requested = requested_quantity if override else (current_qty + requested_quantity)

        # 1. Sản phẩm hết hàng hoàn toàn
        if product.stock <= 0:
            msg = f"Sản phẩm '{product.name}' hiện đã hết hàng."
            if is_ajax:
                return JsonResponse({'success': False, 'error': msg, 'cart_length': len(cart)})
            messages.error(request, msg)
            return redirect('orders:cart_detail' if override else referer_url)

        # 2. Yêu cầu vượt quá số lượng tồn kho
        if total_requested > product.stock:
            if override:
                # Nếu đang cập nhật từ giỏ hàng: tự động gán về số lượng tồn kho tối đa
                cart.add(product=product, quantity=product.stock, override_quantity=True)
                msg = f"Sản phẩm '{product.name}' chỉ còn {product.stock} cuốn. Đã tự động điều chỉnh về số lượng tối đa!"
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'adjusted': True,
                        'quantity': product.stock,
                        'cart_length': len(cart),
                        'message': msg
                    })
                messages.warning(request, msg)
                return redirect('orders:cart_detail')
            else:
                # Nếu bấm thêm từ trang chi tiết sản phẩm / danh sách
                remaining = max(0, product.stock - current_qty)
                if remaining > 0:
                    cart.add(product=product, quantity=remaining, override_quantity=False)
                    msg = f"Sản phẩm '{product.name}' chỉ còn {product.stock} cuốn (bạn đã có {current_qty} cuốn). Đã tự động thêm {remaining} cuốn tối đa có thể vào giỏ hàng!"
                    if is_ajax:
                        return JsonResponse({
                            'success': True,
                            'adjusted': True,
                            'cart_length': len(cart),
                            'message': msg
                        })
                    messages.warning(request, msg)
                    return redirect(referer_url)
                else:
                    msg = f"Bạn đã có đủ số lượng tối đa ({product.stock} cuốn) của sản phẩm '{product.name}' trong giỏ hàng."
                    if is_ajax:
                        return JsonResponse({'success': False, 'error': msg, 'cart_length': len(cart)})
                    messages.warning(request, msg)
                    return redirect(referer_url)

        # 3. Thêm/cập nhật giỏ hàng hợp lệ
        cart.add(product=product,
                 quantity=requested_quantity,
                 override_quantity=override)
        
        msg = f"Đã cập nhật số lượng '{product.name}' thành công!" if override else f"Đã thêm '{product.name}' vào giỏ hàng thành công!"
        if is_ajax:
            return JsonResponse({
                'success': True,
                'cart_length': len(cart),
                'message': msg
            })

        messages.success(request, msg)
        # Nếu đang chỉnh từ giỏ hàng thì ở lại giỏ hàng; nếu thêm từ trang sản phẩm thì ở lại trang sản phẩm!
        if override:
            return redirect('orders:cart_detail')
        return redirect(referer_url)

    # Form không hợp lệ
    err_msg = "Số lượng nhập vào không hợp lệ."
    if is_ajax:
        return JsonResponse({'success': False, 'error': err_msg}, status=400)
    messages.error(request, err_msg)
    return redirect('orders:cart_detail' if request.POST.get('override') == 'True' else referer_url)

@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('orders:cart_detail')

@require_POST
def cart_update_selection(request):
    cart = Cart(request)
    selected_items = request.POST.getlist('selected_items')
    select_all = request.POST.get('select_all')

    if select_all == '1':
        cart.set_all_selected(True)
    elif select_all == '0':
        cart.set_all_selected(False)
    else:
        cart.set_selected(selected_items)

    next_action = request.POST.get('next')
    if next_action == 'checkout':
        return redirect('orders:checkout')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'selected_total': float(cart.get_selected_total_price()),
            'cart_total': float(cart.get_total_price()),
            'selected_count': len(selected_items) if select_all in [None, ''] else (
                len(cart.cart) if select_all == '1' else 0
            )
        })

    return redirect('orders:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    
    # Wrapper class to persist form data across iterations
    class CartWrapper:
        def __init__(self, cart):
            self.cart = cart
            self.items = []
            for item in cart:
                item['update_quantity_form'] = CartAddProductForm(initial={
                                    'quantity': item['quantity'],
                                    'override': True})
                self.items.append(item)
        
        def __iter__(self):
            return iter(self.items)
            
        def __len__(self):
            return len(self.items)
            
        def get_total_price(self):
            return self.cart.get_total_price()

    cart_wrapper = CartWrapper(cart)
    
    # Logic for "Continue Shopping" URL
    referer = request.META.get('HTTP_REFERER')
    # Only update if referer exists and is NOT from within the cart/order system
    if referer and '/orders/' not in referer and '/cart/' not in referer:
        request.session['continue_shopping_url'] = referer
    
    continue_shopping_url = request.session.get('continue_shopping_url', '/')

    # Get random products for recommendations
    import random
    all_products = list(Product.objects.filter(is_active=True, category__is_active=True))
    recommended_products = random.sample(all_products, min(len(all_products), 4))

    return render(request, 'orders/cart_detail.html', {
        'cart': cart_wrapper, 
        'selected_total': cart.get_selected_total_price(),
        'continue_shopping_url': continue_shopping_url,
        'recommended_books': recommended_products 
    })

class CheckoutView(LoginRequiredMixin, View):
    def get(self, request):
        cart = Cart(request)
        selected_items = cart.get_selected_items()
        if len(cart) == 0 or len(selected_items) == 0:
            messages.warning(request, "Vui lòng chọn ít nhất 1 sản phẩm để thanh toán.")
            return redirect('orders:cart_detail')
        
        form = CheckoutForm()
        addresses = Address.objects.filter(user=request.user)
        default_address = addresses.filter(is_default=True).first() or addresses.first()
        
        now = timezone.now()
        selected_total = cart.get_selected_total_price()
        coupons = Coupon.objects.filter(is_active=True).order_by('-value', 'code')
        available_coupons = []
        for coupon in coupons:
            if not (coupon.valid_from <= now <= coupon.valid_to):
                available_coupons.append({
                    'coupon': coupon,
                    'eligible': False,
                    'reason': 'Hết hạn hoặc chưa đến ngày áp dụng',
                })
                continue
            if coupon.used_count >= coupon.max_uses:
                available_coupons.append({
                    'coupon': coupon,
                    'eligible': False,
                    'reason': 'Đã hết lượt sử dụng',
                })
                continue
            if selected_total < coupon.min_order_value:
                available_coupons.append({
                    'coupon': coupon,
                    'eligible': False,
                    'reason': f'Đơn tối thiểu {coupon.min_order_value:,.0f}₫',
                })
                continue
            available_coupons.append({
                'coupon': coupon,
                'eligible': True,
                'reason': 'Có thể áp dụng',
            })

        return render(request, 'orders/checkout.html', {
            'cart': cart,
            'selected_items': selected_items,
            'selected_total': selected_total,
            'available_coupons': available_coupons,
            'form': form,
            'addresses': addresses,
            'default_address': default_address
        })

    def post(self, request):
        cart = Cart(request)
        selected_items = cart.get_selected_items()
        if len(cart) == 0 or len(selected_items) == 0:
            messages.warning(request, "Vui lòng chọn ít nhất 1 sản phẩm để thanh toán.")
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
            
            try:
                with transaction.atomic():
                    # 1. Kiểm tra và khóa dòng tồn kho (Row-level lock chống Race Condition)
                    for item in selected_items:
                        prod = Product.objects.select_for_update().get(id=item['product'].id)
                        if prod.stock < item['quantity']:
                            raise ValidationError(
                                f"Sản phẩm '{prod.name}' hiện chỉ còn {prod.stock} cuốn trong kho (bạn đặt {item['quantity']} cuốn)."
                            )

                    # 2. Tạo Order
                    order = form.save(commit=False)
                    order.user = request.user
                    order.shipping_address = address
                    selected_total = cart.get_selected_total_price()
                    order.total_amount = selected_total
                    
                    # 3. Áp dụng Coupon (với select_for_update để tránh dùng vượt max_uses)
                    coupon_id = request.session.get('coupon_id')
                    if coupon_id:
                        try:
                            coupon = Coupon.objects.select_for_update().get(id=coupon_id)
                            if coupon.is_valid():
                                discount = coupon.calculate_discount(order.total_amount, order.shipping_fee)
                                order.coupon = coupon
                                order.discount_amount = discount
                                order.total_amount = (
                                    Decimal(str(order.total_amount)) + 
                                    Decimal(str(order.shipping_fee)) - 
                                    Decimal(str(discount))
                                )
                                # Cập nhật lượt dùng
                                coupon.used_count = F('used_count') + 1
                                coupon.save(update_fields=['used_count'])
                            else:
                                order.total_amount = Decimal(str(order.total_amount)) + Decimal(str(order.shipping_fee))
                        except Coupon.DoesNotExist:
                            order.total_amount = Decimal(str(order.total_amount)) + Decimal(str(order.shipping_fee))
                    else:
                        order.total_amount = Decimal(str(order.total_amount)) + Decimal(str(order.shipping_fee))

                    order.save()
                    
                    # 4. Tạo OrderItems và trừ tồn kho an toàn
                    for item in selected_items:
                        OrderItem.objects.create(
                            order=order,
                            product=item['product'],
                            price=item['price'],
                            quantity=item['quantity']
                        )
                        # Trừ tồn kho nguyên tử
                        Product.objects.filter(id=item['product'].id).update(stock=F('stock') - item['quantity'])
                    
                    # 5. Tạo Payment
                    payment_method = form.cleaned_data['payment_method']
                    Payment.objects.create(
                        order=order,
                        method=payment_method,
                        amount=order.total_amount
                    )

                # Sau khi transaction commit thành công:
                if coupon_id and 'coupon_id' in request.session:
                    del request.session['coupon_id']

                # Xóa các món đã đặt khỏi giỏ hàng
                cart.remove_selected()

                logger.info(
                    "Đơn hàng %s được tạo thành công bởi user %s (Tổng tiền: %s, Phương thức: %s)",
                    order.order_number, request.user.username, order.total_amount, payment_method
                )
                
                if payment_method == 'payos':
                    return redirect('payment:create_payment', order_id=order.id)
                elif payment_method == 'vietqr':
                    return redirect('payment:payment_vietqr', order_id=order.id)
                else:
                    return redirect('orders:order_success', order_id=order.id)

            except ValidationError as ve:
                messages.error(request, str(ve.message if hasattr(ve, 'message') else ve))
                return redirect('orders:cart_detail')
            except Exception as e:
                logger.exception("Lỗi khi xử lý đơn hàng cho user %s: %s", request.user.username, e)
                messages.error(request, f"Có lỗi xảy ra trong quá trình xử lý đơn hàng: {str(e)}")
                return redirect('orders:checkout')
                
        addresses = Address.objects.filter(user=request.user)
        now = timezone.now()
        selected_total = cart.get_selected_total_price()
        coupons = Coupon.objects.filter(is_active=True).order_by('-value', 'code')
        available_coupons = []
        for coupon in coupons:
            if not (coupon.valid_from <= now <= coupon.valid_to):
                available_coupons.append({
                    'coupon': coupon,
                    'eligible': False,
                    'reason': 'Hết hạn hoặc chưa đến ngày áp dụng',
                })
                continue
            if coupon.used_count >= coupon.max_uses:
                available_coupons.append({
                    'coupon': coupon,
                    'eligible': False,
                    'reason': 'Đã hết lượt sử dụng',
                })
                continue
            if selected_total < coupon.min_order_value:
                available_coupons.append({
                    'coupon': coupon,
                    'eligible': False,
                    'reason': f'Đơn tối thiểu {coupon.min_order_value:,.0f}₫',
                })
                continue
            available_coupons.append({
                'coupon': coupon,
                'eligible': True,
                'reason': 'Có thể áp dụng',
            })

        return render(request, 'orders/checkout.html', {
            'cart': cart,
            'selected_items': selected_items,
            'selected_total': selected_total,
            'available_coupons': available_coupons,
            'form': form,
            'addresses': addresses
        })

def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})


class OrderHistoryView(LoginRequiredMixin, ListView):
    template_name = 'orders/order_history.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .select_related("payment")
            .filter(
                Q(payment__method='cod') |
                Q(payment__status='completed') |
                Q(payment__transaction_id='USER_REPORTED')
            )
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active"] = "orders"
        context["wishlist_items"] = (
            WishlistItem.objects.filter(user=self.request.user)
            .select_related("product")
        )
        return context


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "orders/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .select_related("payment", "shipping_address")
            .prefetch_related("items__product")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        steps = [
            {"key": "pending", "label": "Đã nhận đơn"},
            {"key": "confirmed", "label": "Đang xử lý"},
            {"key": "shipping", "label": "Đang giao hàng"},
            {"key": "delivered", "label": "Đã giao hàng"},
        ]
        status = self.object.status
        canceled = status == "canceled"
        step_index = next((i for i, s in enumerate(steps) if s["key"] == status), 0)
        total_steps = max(len(steps) - 1, 1)
        progress_percent = 0 if canceled else int((step_index / total_steps) * 100)
        subtotal = self.object.total_amount - self.object.shipping_fee + self.object.discount_amount
        context.update(
            {
                "steps": steps,
                "step_index": step_index,
                "progress_percent": progress_percent,
                "is_canceled": canceled,
                "subtotal": subtotal,
                "active": "orders",
            }
        )
        return context

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == 'pending':
        with transaction.atomic():
            order.status = 'canceled'
            order.save(update_fields=['status', 'updated_at'])
            
            # 1. Hoàn lại số lượng tồn kho cho các sản phẩm trong đơn hàng
            for item in order.items.select_related('product'):
                Product.objects.filter(id=item.product_id).update(stock=F('stock') + item.quantity)
                
            # 2. Hoàn lại lượt sử dụng coupon nếu có
            if order.coupon_id:
                Coupon.objects.filter(id=order.coupon_id, used_count__gt=0).update(used_count=F('used_count') - 1)
                
            # 3. Cập nhật trạng thái payment nếu có (Payment model chỉ có status, không có updated_at)
            if hasattr(order, 'payment'):
                order.payment.status = 'canceled'
                order.payment.save(update_fields=['status'])
                
        logger.info("Đơn hàng %s đã được hủy bởi user %s. Đã hoàn lại tồn kho thành công.", order.order_number, request.user.username)
        messages.success(request, f"Đơn hàng #{order.order_number} đã được hủy thành công và hoàn trả số lượng vào kho.")
    else:
        messages.error(request, "Không thể hủy đơn hàng này do trạng thái hiện tại không cho phép.")
    return redirect('orders:order_detail', pk=order.id)

@require_POST
def apply_coupon(request):
    import json
    from django.utils import timezone
    from .models import Coupon
    
    try:
        data = json.loads(request.body)
        code = (data.get('code') or '').strip()
        cart = Cart(request)
        total_price = cart.get_selected_total_price()
        shipping_fee = 30000 # Default shipping fee

        if not code:
            return JsonResponse({'success': False, 'message': 'Vui lòng chọn hoặc nhập mã giảm giá.'})
        
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
