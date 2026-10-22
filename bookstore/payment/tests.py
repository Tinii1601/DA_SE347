from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from books.models import Category, Product
from users.models import Address
from orders.models import Order
from payment.models import Payment


class PaymentModelAndViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="pay_user", password="password123")
        self.client.login(username="pay_user", password="password123")

        self.address = Address.objects.create(
            user=self.user,
            full_name="Lê Văn C",
            phone="0901234567",
            city="Đà Nẵng",
            district="Hải Châu",
            ward="Hải Châu 1",
            address_line="10 Bạch Đằng"
        )
        self.order = Order.objects.create(
            user=self.user,
            shipping_address=self.address,
            total_amount=Decimal("250000.00"),
            status="pending"
        )
        self.payment = Payment.objects.create(
            order=self.order,
            method="cod",
            status="pending",
            amount=self.order.total_amount
        )

    def test_payment_creation_and_defaults(self):
        self.assertEqual(self.payment.status, 'pending')
        self.assertEqual(self.payment.amount, Decimal("250000.00"))
        self.assertEqual(str(self.payment), f"Thanh toán {self.order.order_number}")

    def test_payment_status_save_without_updated_at(self):
        # Verify that payment status can be updated with update_fields=['status'] without ValueError
        self.payment.status = 'completed'
        self.payment.save(update_fields=['status'])
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'completed')

    def test_check_payment_status_endpoint(self):
        url = reverse('payment:check_status', args=[self.order.id])
        response = self.client.get(url, HTTP_HOST='127.0.0.1')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'PENDING')

        # Update order to confirmed and recheck
        self.order.status = 'confirmed'
        self.order.save(update_fields=['status'])

        response2 = self.client.get(url, HTTP_HOST='127.0.0.1')
        self.assertEqual(response2.status_code, 200)
        data2 = response2.json()
        self.assertEqual(data2.get('status'), 'PAID')
