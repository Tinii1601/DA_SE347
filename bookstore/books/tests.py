from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from books.models import Category, Product


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Công nghệ thông tin", slug="cong-nghe-thong-tin")
        self.product = Product.objects.create(
            category=self.category,
            name="Lập trình Python từ cơ bản đến nâng cao",
            price=Decimal("200000.00"),
            discount_percentage=20,
            stock=15,
            description="Sách hướng dẫn học Python"
        )

    def test_get_final_price_with_discount(self):
        # 200,000 with 20% discount should be 160,000
        expected_price = Decimal("160000.00")
        self.assertEqual(self.product.get_final_price(), expected_price)

    def test_get_final_price_no_discount(self):
        self.product.discount_percentage = 0
        self.product.save()
        self.assertEqual(self.product.get_final_price(), Decimal("200000.00"))

    def test_is_on_sale(self):
        self.assertTrue(self.product.is_on_sale)
        self.product.discount_percentage = 0
        self.product.save()
        self.assertFalse(self.product.is_on_sale)

    def test_in_stock(self):
        self.assertTrue(self.product.in_stock())
        self.product.stock = 0
        self.product.save()
        self.assertFalse(self.product.in_stock())

    def test_slug_auto_generation(self):
        prod = Product.objects.create(
            category=self.category,
            name="Sách Lập Trình Django Web",
            price=Decimal("150000.00"),
            stock=5
        )
        self.assertTrue(bool(prod.slug))
        self.assertIn("sach-lap-trinh-django-web", prod.slug)


class CategoryModelTest(TestCase):
    def setUp(self):
        self.parent = Category.objects.create(name="Sách Giáo Khoa", slug="sach-giao-khoa")
        self.child = Category.objects.create(name="Toán Học", slug="toan-hoc", parent=self.parent)

    def test_category_descendants(self):
        descendant_ids = self.parent.get_descendants_and_self_ids()
        self.assertIn(self.parent.id, descendant_ids)
        self.assertIn(self.child.id, descendant_ids)

    def test_category_ancestors(self):
        ancestors = self.child.get_ancestors()
        self.assertEqual(len(ancestors), 1)
        self.assertEqual(ancestors[0], self.parent)


class ProductListViewFilterTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.cat = Category.objects.create(name="Văn học", slug="van-hoc")

        self.book_a = Product.objects.create(
            category=self.cat, name="Sách A Giá Rẻ", price=Decimal("80000.00"),
            discount_percentage=0, stock=10
        )
        self.book_b = Product.objects.create(
            category=self.cat, name="Sách B Tầm Trung", price=Decimal("150000.00"),
            discount_percentage=15, stock=5
        )
        self.book_c = Product.objects.create(
            category=self.cat, name="Sách C Hết Hàng", price=Decimal("300000.00"),
            discount_percentage=0, stock=0
        )
        self.book_d = Product.objects.create(
            category=self.cat, name="Sách D Cao Cấp", price=Decimal("600000.00"),
            discount_percentage=25, stock=3
        )

    def test_product_list_loads_successfully(self):
        response = self.client.get(reverse('books:book_list'), HTTP_HOST='127.0.0.1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['books']), 4)

    def test_filter_price_range_0_100(self):
        response = self.client.get(reverse('books:book_list') + '?price_range=0-100', HTTP_HOST='127.0.0.1')
        self.assertEqual(response.status_code, 200)
        book_ids = [b.id for b in response.context['books']]
        self.assertIn(self.book_a.id, book_ids)
        self.assertNotIn(self.book_b.id, book_ids)
        self.assertNotIn(self.book_c.id, book_ids)
        self.assertNotIn(self.book_d.id, book_ids)

    def test_filter_price_range_100_200(self):
        response = self.client.get(reverse('books:book_list') + '?price_range=100-200', HTTP_HOST='127.0.0.1')
        self.assertEqual(response.status_code, 200)
        book_ids = [b.id for b in response.context['books']]
        self.assertIn(self.book_b.id, book_ids)
        self.assertNotIn(self.book_a.id, book_ids)

    def test_filter_in_stock(self):
        response = self.client.get(reverse('books:book_list') + '?in_stock=1', HTTP_HOST='127.0.0.1')
        self.assertEqual(response.status_code, 200)
        book_ids = [b.id for b in response.context['books']]
        self.assertIn(self.book_a.id, book_ids)
        self.assertIn(self.book_b.id, book_ids)
        self.assertIn(self.book_d.id, book_ids)
        self.assertNotIn(self.book_c.id, book_ids)  # Out of stock excluded

    def test_filter_on_sale(self):
        response = self.client.get(reverse('books:book_list') + '?on_sale=1', HTTP_HOST='127.0.0.1')
        self.assertEqual(response.status_code, 200)
        book_ids = [b.id for b in response.context['books']]
        self.assertIn(self.book_b.id, book_ids)
        self.assertIn(self.book_d.id, book_ids)
        self.assertNotIn(self.book_a.id, book_ids)
        self.assertNotIn(self.book_c.id, book_ids)

    def test_custom_price_min_max(self):
        response = self.client.get(reverse('books:book_list') + '?price_min=100000&price_max=400000', HTTP_HOST='127.0.0.1')
        self.assertEqual(response.status_code, 200)
        book_ids = [b.id for b in response.context['books']]
        self.assertIn(self.book_b.id, book_ids)
        self.assertIn(self.book_c.id, book_ids)
        self.assertNotIn(self.book_a.id, book_ids)
        self.assertNotIn(self.book_d.id, book_ids)

    def test_sorting_by_price(self):
        # Sort ascending
        response_asc = self.client.get(reverse('books:book_list') + '?sort=price', HTTP_HOST='127.0.0.1')
        prices_asc = [b.price for b in response_asc.context['books']]
        self.assertEqual(prices_asc, sorted(prices_asc))

        # Sort descending
        response_desc = self.client.get(reverse('books:book_list') + '?sort=-price', HTTP_HOST='127.0.0.1')
        prices_desc = [b.price for b in response_desc.context['books']]
        self.assertEqual(prices_desc, sorted(prices_desc, reverse=True))
