from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.utils import IntegrityError

from books.models import Category, Product
from reviews.models import Review


class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="reader1", password="password123")
        self.cat = Category.objects.create(name="Tâm lý học", slug="tam-ly-hoc")
        self.product = Product.objects.create(
            category=self.cat,
            name="Tư Duy Nhanh Và Chậm",
            price=Decimal("150000.00"),
            stock=10
        )

    def test_review_string_representation(self):
        review = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comment="Sách rất hay và bổ ích!"
        )
        self.assertEqual(str(review), f"reader1 - Tư Duy Nhanh Và Chậm (5 sao)")

    def test_unique_review_per_user_and_product(self):
        Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comment="Đánh giá lần đầu"
        )
        # Creating second review for same product and user should raise IntegrityError
        with self.assertRaises(IntegrityError):
            Review.objects.create(
                product=self.product,
                user=self.user,
                rating=4,
                comment="Cố tình tạo thêm đánh giá thứ 2"
            )


class ReviewViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="reviewer_john", password="password123")
        self.other_user = User.objects.create_user(username="reviewer_mary", password="password123")

        self.cat = Category.objects.create(name="Khoa học", slug="khoa-hoc")
        self.product = Product.objects.create(
            category=self.cat,
            name="Vũ Trụ Trong Vỏ Hạt Dẻ",
            price=Decimal("120000.00"),
            stock=10
        )

    def test_authenticated_user_can_add_review(self):
        self.client.login(username="reviewer_john", password="password123")
        url = reverse('reviews:review_add', args=[self.product.id])
        response = self.client.post(url, {
            'rating': 5,
            'comment': 'Cuốn sách tuyệt vời nhất tôi từng đọc!'
        }, HTTP_HOST='127.0.0.1')

        # Should redirect back to product detail page
        self.assertEqual(response.status_code, 302)
        review = Review.objects.filter(product=self.product, user=self.user).first()
        self.assertIsNotNone(review)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Cuốn sách tuyệt vời nhất tôi từng đọc!')

    def test_unauthenticated_user_redirected_to_login(self):
        url = reverse('reviews:review_add', args=[self.product.id])
        response = self.client.post(url, {
            'rating': 5,
            'comment': 'Đánh giá ẩn danh'
        }, HTTP_HOST='127.0.0.1')
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_user_can_edit_own_review(self):
        review = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=3,
            comment="Nội dung tàm tạm"
        )
        self.client.login(username="reviewer_john", password="password123")
        url = reverse('reviews:review_edit', args=[review.pk])
        response = self.client.post(url, {
            'rating': 5,
            'comment': 'Đọc kỹ lại thấy rất hay!'
        }, HTTP_HOST='127.0.0.1')

        self.assertEqual(response.status_code, 302)
        review.refresh_from_db()
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Đọc kỹ lại thấy rất hay!')

    def test_user_cannot_edit_other_user_review(self):
        review = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comment="Bình luận của John"
        )
        # Login as mary and attempt to edit john's review
        self.client.login(username="reviewer_mary", password="password123")
        url = reverse('reviews:review_edit', args=[review.pk])
        response = self.client.get(url, HTTP_HOST='127.0.0.1')

        # Should return 404 because queryset is filtered by request.user
        self.assertEqual(response.status_code, 404)


class ProductDetailRatingStatsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.u1 = User.objects.create_user(username="u1", password="123")
        self.u2 = User.objects.create_user(username="u2", password="123")
        self.u3 = User.objects.create_user(username="u3", password="123")

        self.cat = Category.objects.create(name="Triết học", slug="triet-hoc")
        self.product = Product.objects.create(
            category=self.cat,
            name="Khắc Kỷ Từ Căn Bản",
            price=Decimal("100000.00"),
            stock=10
        )

        # 3 reviews: 5 stars, 4 stars, 5 stars -> Sum = 14, Avg = 14 / 3 = 4.67 -> round to 4.7
        Review.objects.create(product=self.product, user=self.u1, rating=5, comment="Rất hay", is_approved=True)
        Review.objects.create(product=self.product, user=self.u2, rating=4, comment="Khá tốt", is_approved=True)
        Review.objects.create(product=self.product, user=self.u3, rating=5, comment="Tuyệt vời", is_approved=True)

    def test_product_detail_calculates_correct_stats(self):
        url = reverse('books:book_detail', args=[self.product.slug])
        response = self.client.get(url, HTTP_HOST='127.0.0.1')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_reviews'], 3)
        self.assertEqual(response.context['avg_rating'], 4.7)

        # 5 star count should be 2, 4 star count should be 1
        rows = {r['star']: r for r in response.context['rating_rows']}
        self.assertEqual(rows[5]['count'], 2)
        self.assertEqual(rows[4]['count'], 1)
        self.assertEqual(rows[3]['count'], 0)
        self.assertEqual(rows[5]['percent'], 66)
        self.assertEqual(rows[4]['percent'], 33)
