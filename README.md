# BOOKSTORE – WEBSITE BÁN SÁCH (DJANGO)

Website bán sách online với đầy đủ luồng mua hàng, quản trị nội dung và thanh toán.

## Thành viên nhóm
- Phạm Minh Tiến – 2252171
- Nguyễn Thị Kim Ngọc – 22520959
- Nguyễn Thành Long – 22520819

## Tính năng chính
- Danh mục đa cấp, sản phẩm, đánh giá.
- Giỏ hàng chọn sản phẩm để thanh toán.
- Mã giảm giá, lịch sử đơn hàng.
- Banner động quản trị từ admin.
- Tin tức & nội dung tĩnh (ContentPage).
- Thanh toán COD và VietQR.
- Đăng nhập thường và social (Google, Facebook).

## Công nghệ
- Django 6.x, SQLite
- Bootstrap 5, CKEditor
- Django Allauth, Import-Export, Jazzmin

## Thiết lập nhanh
1. Cài Python 3.12
2. Cài dependencies: pip install -r requirements.txt
3. Chạy migrate và server:
	- python manage.py migrate
	- python manage.py runserver

## Truy cập
- Trang chủ: http://127.0.0.1:8000
- Admin: http://127.0.0.1:8000/admin

## Tài khoản mẫu (dev)
- Username: tien
- Password: 123

## Cấu hình môi trường (.env)
Khuyến nghị đưa các biến sau vào .env:
- SECRET_KEY, DEBUG, ALLOWED_HOSTS
- EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
- GEMINI_API_KEY
- PAYOS_CLIENT_ID, PAYOS_API_KEY, PAYOS_CHECKSUM_KEY
- GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
- FACEBOOK_CLIENT_ID, FACEBOOK_CLIENT_SECRET

## Cấu trúc thư mục (rút gọn)
```
bookstore/
	core/              # Trang chủ, tin tức, nội dung tĩnh, banner
	books/             # Danh mục, sản phẩm, tìm kiếm, chi tiết
	orders/            # Giỏ hàng, đơn hàng, mã giảm giá
	users/             # Đăng ký/đăng nhập, hồ sơ, quên mật khẩu
	payment/           # Thanh toán (VietQR, COD...)
	reviews/           # Đánh giá sản phẩm
	chatbot/           # Chatbot tư vấn
	static/            # CSS/JS/IMG
	templates/         # Template override (admin, base)
	media/             # Uploads
	manage.py
```

## Mô hình MVT (Django)
Mỗi app đều tuân theo MVT để tách lớp rõ ràng:
- Model: định nghĩa dữ liệu (VD: Product, Category, Order, Coupon, Banner...).
- View: xử lý nghiệp vụ và trả context cho template.
- Template: giao diện HTML/CSS/JS.

## Thành phần chính trong từng app
- core
	- Models: ContentPage, NewsPost, Banner, Store
	- Views/Templates: Trang chủ, tin tức, trang tĩnh, liên hệ
- books
	- Models: Category, Product, Attribute, ProductImage
	- Views/Templates: Danh sách, chi tiết, tìm kiếm
- orders
	- Models: Order, OrderItem, Coupon
	- Views/Templates: Giỏ hàng, checkout, lịch sử
- users
	- Models: UserProfile, Address
	- Views/Templates: Đăng ký/đăng nhập, hồ sơ, quên mật khẩu
- payment
	- Models: Payment
	- Views/Templates: VietQR/COD
- reviews
	- Models: Review
	- Views/Templates: Đánh giá sản phẩm
- chatbot
	- Views/Templates: Giao diện tư vấn

## Chi tiết theo file (tham chiếu nhanh)
- core/
	- models.py: ContentPage, NewsPost, Banner, Store
	- views.py: HomeView, NewsList/Detail, ContentPage, Contact
	- templates/: home.html, news_list.html, page_detail.html...
- books/
	- models.py: Category, Product, Attribute, ProductImage
	- views.py: ProductListView, ProductDetailView, ProductSearchView
	- templates/books/: book_list.html, book_detail.html, search.html
- orders/
	- models.py: Order, OrderItem, Coupon
	- cart.py: xử lý giỏ hàng & chọn sản phẩm
	- views.py: cart/checkout/order history
	- templates/orders/: cart_detail.html, checkout.html
- users/
	- models.py: UserProfile, Address
	- views.py: đăng ký/đăng nhập, hồ sơ, đổi mật khẩu
	- templates/users/: login/register/profile/password_reset...
- payment/
	- models.py: Payment
	- views.py: VietQR, COD, xử lý xác nhận
	- templates/payment/: payment_vietqr.html
- reviews/
	- models.py: Review
	- views.py: tạo/sửa đánh giá
	- templates/reviews/: review_form, review_list
- chatbot/
	- views.py: xử lý hội thoại
	- templates/chatbot/: window.html
