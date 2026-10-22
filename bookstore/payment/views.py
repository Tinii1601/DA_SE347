import json
import logging
from urllib.parse import quote_plus
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from orders.models import Order
from orders.cart import Cart
from .models import Payment
from .utils import get_payos_client
from payos.types import ItemData, CreatePaymentLinkRequest

logger = logging.getLogger(__name__)


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
    with transaction.atomic():
        payment = getattr(order, 'payment', None)
        if payment:
            payment.status = 'pending'
            payment.transaction_id = payment.transaction_id or 'USER_REPORTED'
            payment.save(update_fields=['status', 'transaction_id'])

    cart = Cart(request)
    cart.remove_selected()

    messages.success(request, 'Đã ghi nhận yêu cầu chuyển khoản. Đơn hàng sẽ được nhân viên xác nhận ngay khi nhận được thanh toán.')
    return redirect('orders:order_detail', pk=order.id)


def payment_cancel(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'payment/payment_cancel.html', {'order': order})


def create_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # 1. Kiểm tra cấu hình bộ 3 API Key của PayOS
    if not (settings.PAYOS_CLIENT_ID and settings.PAYOS_API_KEY and settings.PAYOS_CHECKSUM_KEY):
        logger.warning("PayOS API keys missing in environment. Fallback to VietQR for order %s", order.order_number)
        messages.warning(
            request,
            "Cổng thanh toán PayOS chưa được cấu hình API Key trên máy chủ. Đang chuyển hướng bạn sang hình thức quét mã VietQR."
        )
        return redirect('payment:payment_vietqr', order_id=order.id)

    # 2. Xây dựng domain an toàn (Render reverse proxy https)
    domain = request.build_absolute_uri('/')[:-1]
    if not domain.startswith('http://127.0.0.1') and not domain.startswith('http://localhost') and domain.startswith('http://'):
        domain = 'https://' + domain[7:]

    total_amount = int(order.total_amount)

    # 3. Tạo orderCode duy nhất (không vượt quá giới hạn MAX_SAFE_INTEGER của PayOS 9007199254740991)
    timestamp_suffix = int(timezone.now().timestamp()) % 1000000
    order_code = int(f"{order.id}{timestamp_suffix:06d}")

    # Lưu order_code vào Payment.transaction_id để Webhook / Return tra cứu ngược lại Order
    payment, _ = Payment.objects.get_or_create(
        order=order,
        defaults={'method': 'payos', 'amount': order.total_amount, 'status': 'pending'}
    )
    payment.method = 'payos'
    payment.transaction_id = str(order_code)
    payment.save(update_fields=['method', 'transaction_id'])

    # 4. Tạo ItemData và Description theo chuẩn PayOS (Mô tả tối đa 25 ký tự không dấu)
    items = [ItemData(
        name=f"Don hang {order.order_number}"[:50],
        quantity=1,
        price=total_amount
    )]
    description = f"DH {order.id} {order.order_number[-6:]}"[:25]

    payment_data = CreatePaymentLinkRequest(
        order_code=order_code,
        amount=total_amount,
        description=description,
        items=items,
        cancel_url=f"{domain}/payment/cancel/{order.id}/",
        return_url=f"{domain}/payment/return/{order.id}/"
    )

    # 5. Gọi PayOS API tạo link thanh toán
    try:
        payos = get_payos_client()
        payment_link_data = payos.payment_requests.create(payment_data)
        checkout_url = getattr(payment_link_data, 'checkout_url', None) or getattr(payment_link_data, 'checkoutUrl', None)
        if checkout_url:
            return redirect(checkout_url)
        raise ValueError("PayOS không trả về URL thanh toán.")
    except Exception as e:
        logger.error("Lỗi khi tạo payment link PayOS cho đơn hàng %s: %s", order.id, e, exc_info=True)
        messages.error(
            request,
            f"Không thể mở cổng PayOS ({str(e)}). Bạn có thể thanh toán thuận tiện qua mã VietQR bên dưới."
        )
        return redirect('payment:payment_vietqr', order_id=order.id)


def payment_return(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    code = request.GET.get('code')
    status = request.GET.get('status')

    # PayOS trả về code='00' hoặc status='PAID' khi thanh toán thành công
    if code == '00' or status == 'PAID':
        with transaction.atomic():
            order.status = 'confirmed'
            order.save(update_fields=['status', 'updated_at'])

            payment, _ = Payment.objects.get_or_create(
                order=order,
                defaults={'method': 'payos', 'amount': order.total_amount, 'status': 'completed'}
            )
            payment.status = 'completed'
            payment.paid_at = timezone.now()
            payment.save(update_fields=['status', 'paid_at'])

        cart = Cart(request)
        cart.remove_selected()

        logger.info("Order %s confirmed via PayOS return URL", order.order_number)
        messages.success(request, f"Thanh toán đơn hàng #{order.order_number} thành công!")
        return redirect('orders:order_success', order_id=order.id)
    else:
        logger.info("PayOS payment not completed for order %s (code=%s, status=%s)", order.order_number, code, status)
        return redirect('payment:payment_cancel', order_id=order.id)


def check_payment_status(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        if order.status == 'confirmed':
            return JsonResponse({'status': 'PAID'})

        payment = getattr(order, 'payment', None)
        if payment and payment.status == 'completed':
            return JsonResponse({'status': 'PAID'})

        try:
            if settings.PAYOS_CLIENT_ID and settings.PAYOS_API_KEY and settings.PAYOS_CHECKSUM_KEY:
                payos = get_payos_client()
                order_code = int(payment.transaction_id) if (payment and payment.transaction_id and payment.transaction_id.isdigit()) else int(order_id)
                payment_link_info = payos.payment_requests.get(order_code)
                status = getattr(payment_link_info, 'status', None)

                if status == "PAID":
                    with transaction.atomic():
                        order.status = 'confirmed'
                        order.save(update_fields=['status', 'updated_at'])
                        if payment:
                            payment.status = 'completed'
                            payment.paid_at = timezone.now()
                            payment.save(update_fields=['status', 'paid_at'])
                    return JsonResponse({'status': 'PAID'})
        except Exception as e:
            logger.warning("Error checking PayOS status for order %s: %s", order_id, e)

        return JsonResponse({'status': 'PENDING'})
    except Order.DoesNotExist:
        return JsonResponse({'status': 'ERROR'}, status=404)


@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        try:
            if not (settings.PAYOS_CLIENT_ID and settings.PAYOS_API_KEY and settings.PAYOS_CHECKSUM_KEY):
                return JsonResponse({'success': False, 'error': 'PayOS keys not configured'}, status=400)

            payos = get_payos_client()
            body = json.loads(request.body)

            # Xác thực chữ ký webhook từ PayOS
            webhook_data = payos.webhooks.verify(body)

            order_code = getattr(webhook_data, 'order_code', None) or getattr(webhook_data, 'orderCode', None)
            code = getattr(webhook_data, 'code', None)

            # Tìm Payment theo transaction_id (=order_code) hoặc fallback tìm theo order_id
            payment = None
            if order_code:
                payment = Payment.objects.filter(transaction_id=str(order_code)).select_related('order').first()
                if not payment and str(order_code).isdigit():
                    payment = Payment.objects.filter(order_id=int(order_code)).select_related('order').first()

            if payment and code == "00":
                with transaction.atomic():
                    order = payment.order
                    order.status = 'confirmed'
                    order.save(update_fields=['status', 'updated_at'])
                    payment.status = 'completed'
                    payment.paid_at = timezone.now()
                    payment.save(update_fields=['status', 'paid_at'])
                logger.info("PayOS Webhook: Order %s marked as confirmed/completed", payment.order.order_number)

            # Luôn trả về 200 OK cho PayOS (kể cả webhook kiểm tra kết nối ban đầu)
            return JsonResponse({'success': True})
        except Exception as e:
            logger.error("PayOS Webhook error: %s", e, exc_info=True)
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False}, status=405)
