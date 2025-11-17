import os
import django
import csv
from pathlib import Path
from decimal import Decimal
import cloudinary.uploader
# from django.contrib.auth.models import User
# from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookstore.settings')
django.setup()

from books.models import Category, Book
# from users.models import UserProfile, Address
# from orders.models import Order, OrderItem, Payment, Coupon

DATA_DIR = Path('data')
COVERS_DIR = Path('static/img/books')

def import_categories():
    print("Import danh mục...")
    with open(DATA_DIR / 'categories.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            Category.objects.get_or_create(
                name=row['name'],
                defaults={'description': row['description']}
            )
    print("Hoàn tất danh mục.\n")

# def import_users():
#     print("Import người dùng...")
#     with open(DATA_DIR / 'users.csv', encoding='utf-8') as f:
#         reader = csv.DictReader(f)
#         for row in reader:
#             user, created = User.objects.update_or_create(
#                 username=row['username'],
#                 defaults={
#                     'email': row['email'],
#                     'first_name': row['first_name'],
#                     'last_name': row['last_name'],
#                     'is_staff': row['is_staff'] == 'True'
#                 }
#             )
#             if created:
#                 user.set_password(row['password'])
#                 user.save()
#             # Tạo profile
#             profile, _ = UserProfile.objects.get_or_create(user=user)
#             profile.phone = row['phone']
#             profile.save()
#             print(f"{'Tạo' if created else 'Cập nhật'}: {user.get_full_name() or user.username}")
#     print("Hoàn tất người dùng.\n")

def import_books():
    print("Import sách + ảnh...")
    with open(DATA_DIR / 'books_data.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            category = Category.objects.get(name=row['category'])
            image_path = COVERS_DIR / row['image_file']
            public_id = f"{row['title'].lower().replace(' ', '-')}"
            
            if image_path.exists():
                cloudinary.uploader.upload(
                    str(image_path),
                    folder='books/covers',
                    public_id=public_id,
                    overwrite=True,
                    transformation=[{'width': 800, 'height': 1200, 'crop': 'fill'}]
                )
            
            book, _ = Book.objects.update_or_create(
                title=row['title'],
                author=row['author'],
                defaults={
                    'slug': public_id,
                    'publisher': row['publisher'],
                    'isbn': row['isbn'],
                    'description': row['description'],
                    'price': Decimal(row['price']),
                    'discount_price': Decimal(row['discount_price']) if row['discount_price'] else None,
                    'stock': int(row['stock']),
                    'cover_image': f"books/covers/{public_id}",
                    'category': category,
                    'published_year': int(row['published_year']) if row['published_year'] else None,
                    'pages': int(row['pages']) if row['pages'] else None,
                    'is_active': True
                }
            )
            print(f"Đã thêm: {book.title}")
    print("Hoàn tất sách.\n")

# def import_orders():
#     print("Import đơn hàng...")
#     with open(DATA_DIR / 'orders.csv', encoding='utf-8') as f:
#         reader = csv.DictReader(f)
#         for i, row in enumerate(reader, 1):
#             user = User.objects.get(username=row['username'])
#             books = [b.strip() for b in row['book_titles'].split(',')]
#             quantities = [int(q) for q in row['quantities'].split(',')]
            
#             order = Order.objects.create(
#                 user=user,
#                 order_number=f"ORD{2025}{i:05d}",
#                 total_amount=Decimal(row['total_amount']),
#                 status=row['status'],
#                 note=row['note']
#             )
            
#             for book_title, qty in zip(books, quantities):
#                 book = Book.objects.get(title=book_title)
#                 OrderItem.objects.create(
#                     order=order,
#                     book=book,
#                     price=book.get_final_price(),
#                     quantity=qty
#                 )
            
#             Payment.objects.create(
#                 order=order,
#                 method=row['payment_method'],
#                 amount=order.total_amount,
#                 status='completed' if order.status in ['delivered', 'completed'] else 'pending'
#             )
#             print(f"Đơn hàng: {order.order_number} – {user.username}")
#     print("Hoàn tất đơn hàng.\n")

if __name__ == '__main__':
    import_categories()
    # import_users()
    import_books()
    # import_orders()
    print("HOÀN TẤT TOÀN BỘ DỮ LIỆU THỰC TẾ!")