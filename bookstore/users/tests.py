from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.db.utils import IntegrityError

from books.models import Category, Product
from users.models import Address, WishlistItem, UserProfile


class UserModelAndProfileTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")

    def test_user_profile_auto_created_on_signup(self):
        # UserProfile should be automatically created via post_save signal
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertEqual(self.user.profile.user, self.user)


class AddressModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="address_user", password="password123")
        self.addr1 = Address.objects.create(
            user=self.user,
            full_name="Người Dùng 1",
            phone="0911111111",
            city="Hà Nội",
            district="Ba Đình",
            ward="Điện Biên",
            address_line="1 Hùng Vương",
            is_default=True
        )

    def test_is_default_address_switch(self):
        # When creating addr2 as default, addr1 should lose its default status
        self.assertTrue(self.addr1.is_default)

        addr2 = Address.objects.create(
            user=self.user,
            full_name="Người Dùng 2",
            phone="0922222222",
            city="Hà Nội",
            district="Hoàn Kiếm",
            ward="Hàng Trống",
            address_line="2 Tràng Tiền",
            is_default=True
        )

        self.addr1.refresh_from_db()
        self.assertFalse(self.addr1.is_default)
        self.assertTrue(addr2.is_default)


class WishlistModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="wish_user", password="password123")
        self.cat = Category.objects.create(name="Khoa học", slug="khoa-hoc-wish")
        self.product = Product.objects.create(
            category=self.cat,
            name="Sách Yêu Thích 1",
            price=Decimal("99000.00"),
            stock=10
        )

    def test_wishlist_item_creation(self):
        item = WishlistItem.objects.create(user=self.user, product=self.product)
        self.assertEqual(str(item), f"{self.user.username} - {self.product.name}")

    def test_wishlist_item_unique_constraint(self):
        WishlistItem.objects.create(user=self.user, product=self.product)
        with self.assertRaises(IntegrityError):
            WishlistItem.objects.create(user=self.user, product=self.product)
