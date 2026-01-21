from django.conf import settings
from payos import PayOS
from payos.types import ItemData, CreatePaymentLinkRequest
from orders.models import Order

def get_payos_client():
    return PayOS(
        client_id=settings.PAYOS_CLIENT_ID,
        api_key=settings.PAYOS_API_KEY,
        checksum_key=settings.PAYOS_CHECKSUM_KEY
    )

def create_or_get_payment_link(order, domain=None):
    payos = get_payos_client()
    if not domain:
        domain = "http://127.0.0.1:8000"
    
    try:
        # Try to get existing payment link
        return payos.payment_requests.get(int(order.id))
    except:
        # Create new payment link
        # To avoid issues with sum of items not matching total amount due to discounts,
        # we will send a single summary item.
        total_amount = int(order.total_amount)
        
        items = [ItemData(
            name=f"Thanh toan don hang {order.order_number}",
            quantity=1,
            price=total_amount
        )]

        payment_data = CreatePaymentLinkRequest(
            orderCode=int(order.id),
            amount=total_amount,
            description=f"DH {order.order_number}",
            items=items,
            cancelUrl=f"{domain}/payment/cancel/{order.id}/",
            returnUrl=f"{domain}/payment/return/{order.id}/"
        )
        
        return payos.payment_requests.create(payment_data)
