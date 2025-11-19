# BOOKSTORE – WEBSITE BÁN SÁCH (ĐỒ ÁN MÔN HỌC DJANGO)

Website bán sách online 

## Thành viên nhóm
- Phạm Minh Tiến – 2252171 
- Nguyễn Thị Kim Ngọc – 22520959
- Nguyễn Thành long – 22520819

## Cách chạy dự án – CHỈ 4 BƯỚC

### Bước 1: Cài đặt python (Nếu chưa có)
Link tải python: https://www.python.org/downloads/release/python-31210/

Nhớ tick chọn “Add Python to PATH” khi cài!

### Bước 2: Clone dự án
```bash
git clone https://github.com/Tinii1601/DA_SE347.git
```

### Bước 3: Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### Bước 4: Lưu và chạy web
```bash
cd bookstore
python manage.py migrate
python manage.py runserver
```

Mở trình duyệt:

Trang chủ: http://127.0.0.1:8000

Admin: http://127.0.0.1:8000/admin

Tài khoản: tien

Mật khẩu: 123
