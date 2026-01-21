from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from orders.models import Order
from orders.cart import Cart
from .models import Payment
from .utils import get_payos_client, create_or_get_payment_link
from payos.types import ItemData, CreatePaymentLinkRequest
import json
from django.views.decorators.http import require_POST
from django.contrib import messages
from urllib.parse import quote_plus

def payment_vietqr(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    payment_content = f"DH {order.order_number}"
    content_encoded = quote_plus(payment_content)
    account_name_encoded = quote_plus(settings.VIETQR_ACCOUNT_NAME)
    generated_qr_url = (
        f"https://img.vietqr.io/image/{settings.VIETQR_BANK_BIN}-{settings.VIETQR_ACCOUNT_NUMBER}-compact.png"
        f"?amount={int(order.total_amount)}&addInfo={content_encoded}&accountName={account_name_encoded}"
    )
    qr_url = settings.VIETQR_QR_URL or generated_qr_url

    return render(request, 'payment/payment_vietqr.html', {
        'order': order,
        'bank_name': settings.VIETQR_BANK_NAME,
        'bank_account_name': settings.VIETQR_ACCOUNT_NAME,
        'bank_account_number': settings.VIETQR_ACCOUNT_NUMBER,
        'payment_content': payment_content,
        'payment_amount': order.total_amount,
        'qr_url': qr_url,
        'generated_qr_url': generated_qr_url,
    })


@require_POST
def payment_vietqr_confirm(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    payment = getattr(order, 'payment', None)
    if payment:
        payment.status = 'pending'
        payment.transaction_id = payment.transaction_id or 'USER_REPORTED'
        payment.save()

    cart = Cart(request)
    cart.clear()

    messages.success(request, 'Đã ghi nhận thanh toán. Đơn hàng sẽ được xác minh thủ công.')
    return redirect('orders:order_detail', pk=order.id)

def payment_cancel(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'payment/payment_cancel.html', {'order': order})

def create_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Construct PaymentData
    # Lấy domain động hiện tại (localhost hoặc pythonanywhere)
    domain = request.build_absolute_uri('/')[:-1] 
    
    # Use total_amount from order which already includes shipping and discount
    total_amount = int(order.total_amount)

    # Create a single summary item to ensure amount matches
    items = [ItemData(
        name=f"Thanh toan don hang {order.order_number}",
        quantity=1,
        price=total_amount
    )]

    payment_data = CreatePaymentLinkRequest(
        orderCode=int(order.id), # Using ID as orderCode
        amount=total_amount,
        description=f"Thanh toan don hang {order.order_number}",
        items=items,
        cancelUrl=f"{domain}/payment/cancel/{order.id}/",
        returnUrl=f"{domain}/payment/return/{order.id}/"
    )
    
    payos = get_payos_client()
    try:
        payment_link_data = payos.payment_requests.create(payment_data)
        return redirect(payment_link_data.checkoutUrl)
    except Exception as e:
        print(f"Error creating payment link: {e}")
        # For demo purposes, if error (e.g. duplicate orderCode), try to get existing link
        try:
             payment_link_data = payos.payment_requests.get(int(order.id))
             # If status is PENDING, redirect to checkout
             if payment_link_data.status == "PENDING":
                 return redirect(payment_link_data.checkoutUrl)
        except:
            pass
            
        return render(request, 'orders/checkout.html', {'error': f'Lỗi tạo link thanh toán PayOS: {str(e)}'})

def payment_return(request, order_id):
    # Handle return from PayOS
    order = get_object_or_404(Order, id=order_id)
    
    # In a real app, we should verify the signature of the return data
    # For now, we assume success if they reach this URL with code=00
    code = request.GET.get('code')
    if code == '00':
        order.status = 'confirmed'
        order.save()
        
        if hasattr(order, 'payment'):
            order.payment.status = 'completed'
            order.payment.save()
            
        # Clear cart on successful payment
        cart = Cart(request)
        cart.clear()
            
        return redirect('orders:order_success', order_id=order.id)
    else:
        return redirect('orders:checkout')

def check_payment_status(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        
        # 1. Nếu đơn hàng đã được xác nhận trong DB rồi thì trả về PAID ngay
        if order.status == 'confirmed':
            return JsonResponse({'status': 'PAID'})
            
        # 2. Nếu chưa, server sẽ chủ động hỏi PayOS (Dành cho localhost không có webhook)
        try:
            payos = get_payos_client()
            payment_link_info = payos.payment_requests.get(int(order_id))
            
            if payment_link_info.status == "PAID":
                # Cập nhật trạng thái đơn hàng ngay lập tức
                order.status = 'confirmed'
                order.save()
                
                if hasattr(order, 'payment'):
                    order.payment.status = 'completed'
                    order.payment.save()
                    
                return JsonResponse({'status': 'PAID'})
        except Exception as e:
            print(f"Lỗi khi kiểm tra trạng thái PayOS: {e}")
            
        return JsonResponse({'status': 'PENDING'})
    except Order.DoesNotExist:
        return JsonResponse({'status': 'ERROR'}, status=404)

@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        try:
            payos = get_payos_client()
            body = json.loads(request.body)
            
            # Verify webhook data
            webhook_data = payos.webhooks.verify(body)
            
            # Process data
            order_id = webhook_data.orderCode
            order = Order.objects.get(id=order_id)
            
            if webhook_data.code == "00": # Success
                order.status = 'confirmed'
                order.save()
                if hasattr(order, 'payment'):
                    order.payment.status = 'completed'
                    order.payment.save()
            
            return JsonResponse({'success': True})
        except Exception as e:
            print(f"Webhook error: {e}")
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False}, status=405)
