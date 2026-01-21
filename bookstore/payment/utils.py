from django.conf import settings
from payos import PayOS
from payos.types import ItemData, CreatePaymentLinkRequest
from orders.models import Order
import time
import sys
import os

def get_payos_client():
    client_id = settings.PAYOS_CLIENT_ID
    api_key = settings.PAYOS_API_KEY
    checksum_key = settings.PAYOS_CHECKSUM_KEY
    
    if not client_id or not api_key or not checksum_key:
        print("DEBUG PAYOS: ERROR - One or more keys are missing!", file=sys.stderr)

    return PayOS(
        client_id=client_id,
        api_key=api_key,
        checksum_key=checksum_key
    )

def create_or_get_payment_link(order, domain=None):
    payos = get_payos_client()
    if not domain:
        domain = "http://127.0.0.1:8000"        
    
    # 1. Try to get existing payment link first to ensure consistency (orderCode = order.id)
    try:
        existing_link = payos.payment_requests.get(int(order.id))
        if existing_link and existing_link.status != "CANCELLED":
            print(f"DEBUG PAYOS: Found existing link for Order {order.id}", file=sys.stderr)
            return existing_link
    except:
        pass # Link not found or error, proceed to create

    # 2. Create new payment link
    total_amount = int(order.total_amount)
    
    items = [ItemData(
        name=f"Thanh toan don hang {order.order_number}",
        quantity=1,
        price=total_amount
    )]

    # Use order.id as orderCode to allow simple status checking
    orderCode = int(order.id)

    payment_data = CreatePaymentLinkRequest(
        orderCode=orderCode,
        amount=total_amount,
        description=f"DH {order.order_number}",
        items=items,
        cancelUrl=f"{domain}/payment/cancel/{order.id}/",
        returnUrl=f"{domain}/payment/return/{order.id}/"
    )
    
    return payos.payment_requests.create(payment_data)
