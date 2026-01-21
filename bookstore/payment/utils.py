from django.conf import settings
from payos import PayOS
from payos.types import ItemData, CreatePaymentLinkRequest
from orders.models import Order
import time
import sys
import os

def get_payos_client():
    # DEBUG: Print keys to stderr (logs) to check if they are loaded
    client_id = settings.PAYOS_CLIENT_ID
    api_key = settings.PAYOS_API_KEY
    checksum_key = settings.PAYOS_CHECKSUM_KEY
    
    # Mask keys for security in logs, show first 5 chars
    masked_cid = client_id[:5] + "..." if client_id else "NONE"
    masked_api = api_key[:5] + "..." if api_key else "NONE"
    
    print(f"DEBUG PAYOS: ClientID={masked_cid}, APIKey={masked_api}", file=sys.stderr)
    
    if not client_id or not api_key:
        print("DEBUG PAYOS: ERROR - Keys are missing!", file=sys.stderr)

    return PayOS(
        client_id=client_id,
        api_key=api_key,
        checksum_key=checksum_key
    )

def create_or_get_payment_link(order, domain=None):
    payos = get_payos_client()
    if not domain:
        domain = "http://127.0.0.1:8000"        
    
    try:
        # Try to get existing payment link
        # return payos.payment_requests.get(int(order.id))
        raise Exception("Force create new link to avoid collision")
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

        # Generate unique orderCode to avoid collision with old orders
        # Using timestamp to ensure uniqueness: ID + last 6 digits of timestamp
        orderCode = int(str(order.id) + str(int(time.time())))

        payment_data = CreatePaymentLinkRequest(
            orderCode=orderCode,
            amount=total_amount,
            description=f"DH {order.order_number}",
            items=items,
            cancelUrl=f"{domain}/payment/cancel/{order.id}/",
            returnUrl=f"{domain}/payment/return/{order.id}/"
        )
        
        return payos.payment_requests.create(payment_data)
