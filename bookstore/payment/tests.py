from decimal import Decimal
from unittest.mock import patch, MagicMock
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
            method="payos",
            status="pending",
            amount=self.order.total_amount
        )

    def test_payment_creation_and_defaults(self):
        self.assertEqual(self.payment.status, 'pending')
        self.assertEqual(self.payment.amount, Decimal("250000.00"))
        self.assertEqual(str(self.payment), f"Thanh toán {self.order.order_number}")
        # Verify only COD and PayOS are in choices (VietQR removed)
        methods = [choice[0] for choice in Payment.METHOD_CHOICES]
        self.assertEqual(methods, ['cod', 'payos'])

    def test_payment_status_save_without_updated_at(self):
        self.payment.status = 'completed'
        self.payment.save(update_fields=['status'])
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'completed')

    def test_check_payment_status_endpoint(self):
        url = reverse('payment:check_status', args=[self.order.id])
        with self.settings(PAYOS_CLIENT_ID='', PAYOS_API_KEY='', PAYOS_CHECKSUM_KEY=''):
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

    def test_payos_create_fallback_when_keys_missing(self):
        url = reverse('payment:create_payment', args=[self.order.id])
        with self.settings(PAYOS_CLIENT_ID='', PAYOS_API_KEY='', PAYOS_CHECKSUM_KEY=''):
            response = self.client.get(url, HTTP_HOST='127.0.0.1')
            self.assertRedirects(response, reverse('orders:order_detail', kwargs={'pk': self.order.id}))

    def test_payos_create_redirects_to_checkout_url(self):
        url = reverse('payment:create_payment', args=[self.order.id])
        with self.settings(PAYOS_CLIENT_ID='test_client', PAYOS_API_KEY='test_key', PAYOS_CHECKSUM_KEY='test_checksum'):
            with patch('payment.views.get_payos_client') as mock_payos:
                mock_client = MagicMock()
                mock_link_data = MagicMock()
                mock_link_data.checkout_url = 'https://pay.payos.vn/web/123456'
                mock_client.payment_requests.create.return_value = mock_link_data
                mock_payos.return_value = mock_client

                response = self.client.get(url, HTTP_HOST='127.0.0.1')
                self.assertEqual(response.status_code, 302)
                self.assertEqual(response.url, 'https://pay.payos.vn/web/123456')

    def test_payos_payment_return_success(self):
        url = reverse('payment:payment_return', args=[self.order.id]) + '?code=00'
        response = self.client.get(url, HTTP_HOST='127.0.0.1')
        self.assertRedirects(response, reverse('orders:order_success', args=[self.order.id]))

        self.order.refresh_from_db()
        self.payment.refresh_from_db()
        self.assertEqual(self.order.status, 'confirmed')
        self.assertEqual(self.payment.status, 'completed')
        self.assertIsNotNone(self.payment.paid_at)

    def test_payos_payment_return_cancelled(self):
        url = reverse('payment:payment_return', args=[self.order.id]) + '?code=01&cancel=true'
        response = self.client.get(url, HTTP_HOST='127.0.0.1')
        self.assertRedirects(response, reverse('payment:payment_cancel', args=[self.order.id]))

    def test_payment_cancel_page_renders(self):
        url = reverse('payment:payment_cancel', args=[self.order.id])
        response = self.client.get(url, HTTP_HOST='127.0.0.1')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order.order_number)
        self.assertContains(response, 'Thanh toán chưa hoàn tất')
