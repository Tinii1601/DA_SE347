from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from books.models import Category, Product
from users.models import Address
from orders.models import Order, OrderItem, Coupon
from payment.models import Payment


class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="customer1", password="password123")
        self.address = Address.objects.create(
            user=self.user,
            full_name="Nguyễn Văn A",
            phone="0912345678",
            city="Hà Nội",
            district="Cầu Giấy",
            ward="Dịch Vọng",
            address_line="123 Đường Cầu Giấy"
        )

    def test_order_number_auto_generation(self):
        order = Order.objects.create(
            user=self.user,
            shipping_address=self.address,
            total_amount=Decimal("150000.00")
        )
        # Format: ORD + 12 digits date + 4 hex chars = 19 characters (<= max_length 20)
        self.assertTrue(order.order_number.startswith("ORD"))
        self.assertLessEqual(len(order.order_number), 20)
        self.assertEqual(len(order.order_number), 19)


class CartAddViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.cat = Category.objects.create(name="Khoa học", slug="khoa-hoc")
        self.product = Product.objects.create(
            category=self.cat,
            name="Vũ Trụ Trong Vỏ Hạt Dẻ",
            price=Decimal("120000.00"),
            stock=5
        )
        self.out_of_stock_product = Product.objects.create(
            category=self.cat,
            name="Lược Sử Thời Gian",
            price=Decimal("110000.00"),
            stock=0
        )

    def test_cart_add_normal_ajax(self):
        url = reverse('orders:cart_add', args=[self.product.id])
        response = self.client.post(
            url,
            {'quantity': 2, 'override': 'False'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            HTTP_HOST='127.0.0.1'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertEqual(data.get('cart_length'), 2)
        self.assertFalse(data.get('adjusted'))

    def test_cart_add_exceeding_stock_auto_clamps(self):
        # User attempts to add 10 items, but stock is only 5
        url = reverse('orders:cart_add', args=[self.product.id])
        response = self.client.post(
            url,
            {'quantity': 10, 'override': 'False'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            HTTP_HOST='127.0.0.1'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        # Should be flagged as adjusted and clamped to stock 5
        self.assertTrue(data.get('adjusted'))
        self.assertIn("5", data.get('message'))

    def test_cart_add_out_of_stock_rejected(self):
        url = reverse('orders:cart_add', args=[self.out_of_stock_product.id])
        response = self.client.post(
            url,
            {'quantity': 1, 'override': 'False'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            HTTP_HOST='127.0.0.1'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data.get('success'))
        self.assertIn("hết hàng", data.get('error').lower())


class OrderCancellationAndStockRestorationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test_buyer", password="password123")
        self.client.login(username="test_buyer", password="password123")

        self.other_user = User.objects.create_user(username="other_buyer", password="password123")

        self.address = Address.objects.create(
            user=self.user,
            full_name="Trần Thị B",
            phone="0987654321",
            city="TP. Hồ Chí Minh",
            district="Quận 1",
            ward="Bến Nghé",
            address_line="45 Lê Duẩn"
        )
        self.cat = Category.objects.create(name="Kinh tế", slug="kinh-te")
        self.product = Product.objects.create(
            category=self.cat,
            name="Nhà Đầu Tư Thông Minh",
            price=Decimal("180000.00"),
            stock=10
        )

        # Create a coupon
        now = timezone.now()
        self.coupon = Coupon.objects.create(
            code="SALE20",
            discount_type="percent",
            value=Decimal("20.00"),
            valid_from=now - timedelta(days=1),
            valid_to=now + timedelta(days=5),
            max_uses=10,
            used_count=1
        )

        # Create an Order with items
        self.order = Order.objects.create(
            user=self.user,
            shipping_address=self.address,
            coupon=self.coupon,
            shipping_fee=Decimal("30000.00"),
            discount_amount=Decimal("36000.00"),
            total_amount=Decimal("174000.00"),
            status="pending"
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            price=Decimal("180000.00"),
            quantity=3
        )
        # Payment record for this order
        self.payment = Payment.objects.create(
            order=self.order,
            method="cod",
            status="pending",
            amount=self.order.total_amount
        )

    def test_cancel_order_restores_stock_and_coupon(self):
        initial_stock = self.product.stock  # 10
        initial_used_count = self.coupon.used_count  # 1

        url = reverse('orders:cancel_order', args=[self.order.id])
        response = self.client.get(url, HTTP_HOST='127.0.0.1')
        self.assertEqual(response.status_code, 302)  # Redirects to history

        # Refresh order, product, coupon from DB
        self.order.refresh_from_db()
        self.product.refresh_from_db()
        self.coupon.refresh_from_db()
        self.payment.refresh_from_db()

        # 1. Order status is canceled
        self.assertEqual(self.order.status, 'canceled')

        # 2. Product stock is restored (+3 quantity)
        self.assertEqual(self.product.stock, initial_stock + 3)

        # 3. Coupon used_count is decremented
        self.assertEqual(self.coupon.used_count, initial_used_count - 1)

        # 4. Payment status updated without crash
        self.assertEqual(self.payment.status, 'canceled')

    def test_other_user_cannot_cancel_order(self):
        # Login as other_user
        self.client.login(username="other_buyer", password="password123")
        url = reverse('orders:cancel_order', args=[self.order.id])
        response = self.client.get(url, HTTP_HOST='127.0.0.1')

        # Should be 404 because user=request.user filter
        self.assertEqual(response.status_code, 404)

        # Verify order was NOT canceled
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'pending')
