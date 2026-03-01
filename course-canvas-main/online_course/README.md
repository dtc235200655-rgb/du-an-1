# 📚 Online Courses – Django Project

Đây là project **Website đăng ký khóa học trực tuyến** được xây dựng bằng **Django**.  
Hệ thống gồm **User (học viên)** và **Admin (quản trị viên)** với quy trình duyệt khóa học và duyệt đăng ký học.

---

## 🚀 1. YÊU CẦU HỆ THỐNG

- Python **3.10+** (khuyến nghị 3.11)
- pip
- Virtualenv (không bắt buộc nhưng khuyến nghị)

---

## ⚙️ 2. CÀI ĐẶT & CHẠY PROJECT

### 🔹 Bước 1: Giải nén project
```bash
unzip course-canvas-main.zip
cd online_course_project
```

### 🔹 Bước 2: Cài thư viện cần thiết
```bash
pip install -r requirements.txt
```

### 🔹 Bước 3: Chạy migrate database
```bash
python manage.py migrate
```

### 🔹 Bước 4: Chạy server
```bash
python manage.py runserver
```

➡️ Truy cập website tại:  
👉 http://127.0.0.1:8000/

---

## 🔐 3. TÀI KHOẢN ADMIN (CÓ SẴN)

| Loại | Email / Username | Password |
|----|-----------------|----------|
| Admin | Admin@gmail.com | 123456 |

👉 Truy cập trang quản trị:  
http://127.0.0.1:8000/admin/

---

## 👤 4. CHỨC NĂNG CHO USER (HỌC VIÊN)

- Đăng ký tài khoản
- Đăng nhập
- Xem danh sách khóa học đã duyệt
- Đăng ký học
- Xem Dashboard cá nhân
- Hủy đăng ký khi đang chờ duyệt

---

## 🛠️ 5. CHỨC NĂNG ADMIN

### ➕ Quản lý danh mục & khóa học
- Thêm / sửa / xóa khóa học
- Duyệt khóa học

### ✅ Duyệt đăng ký học viên
- Vào Admin → Enrollments
- Chuyển trạng thái Pending → Approved
- Nhấn Save

---

## 🔄 6. LUỒNG HOẠT ĐỘNG

User → Đăng ký học → Pending → Admin duyệt → Approved → User học

---

## 📁 7. CẤU TRÚC PROJECT

```
online_course/
├─ manage.py
├─ requirements.txt
├─ README.md
├─ courses/
├─ templates/
├─ static/
└─ media/
```

---

## 👨‍💻 8. TÁC GIẢ

Sinh viên: (Điền tên)  
Môn học: (Điền môn học)

---

🎉 Hoàn thành
