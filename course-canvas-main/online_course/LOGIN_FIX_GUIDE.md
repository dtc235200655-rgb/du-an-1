# 🔧 Hướng dẫn khắc phục lỗi đăng nhập

## ✅ Vấn đề đã sửa

### Lỗi chính:
**Import `UserRole` không đúng vị trí trong `views.py`**

**Trước đây:**
```python
def login_view(request):
    if request.method == 'POST':
        # ... code ...
        else:
            from courses.models import UserRole  # ❌ Import muộn
            UserRole.objects.create(user=user, role='customer')
    
    from courses.models import UserRole  # ❌ Import ở cuối
    return render(request, 'login.html', {...})
```

**Bây giờ:**
```python
def login_view(request):
    from courses.models import UserRole  # ✅ Import ngay đầu
    
    if request.method == 'POST':
        # ... code ...
        else:
            UserRole.objects.create(user=user, role='customer')
    
    return render(request, 'login.html', {...})
```

## 📋 Các bước kiểm tra login

### 1. Kiểm tra database có UserRole
```bash
python manage.py shell
```

```python
from courses.models import UserRole
from django.contrib.auth.models import User

# Kiểm tra tất cả users
users = User.objects.all()
print(f"Tổng số users: {users.count()}")

# Kiểm tra từng user
for user in users:
    if hasattr(user, 'user_role'):
        print(f"✓ {user.username}: {user.user_role.get_role_display()}")
    else:
        print(f"✗ {user.username}: Chưa có role")

# Kiểm tra role choices
print(f"Role choices: {UserRole.ROLE_CHOICES}")
```

### 2. Gán roles cho users chưa có
```bash
python manage.py assign_user_roles
```

Hoặc gán thủ công:
```bash
python manage.py set_user_role <username> <role>
# Ví dụ:
python manage.py set_user_role Admin admin
python manage.py set_user_role staff_admin staff
python manage.py set_user_role Manh customer
```

### 3. Test login với từng role

#### Test với Admin:
- **Username**: Admin
- **Password**: (mật khẩu bạn đã đặt)
- **Chọn role**: Quản trị viên
- **Kết quả mong đợi**: Redirect đến `/admin/`

#### Test với Staff:
- **Username**: staff_admin
- **Password**: staff123
- **Chọn role**: Nhân viên
- **Kết quả mong đợi**: Redirect đến `/staff/dashboard/`

#### Test với Customer:
- **Username**: Manh
- **Password**: (mật khẩu bạn đã đặt)
- **Chọn role**: Khách hàng
- **Kết quả mong đợi**: Redirect đến `/dashboard/`

## ⚠️ Các lỗi thường gặp

### 1. "Tài khoản này không có vai trò..."
**Nguyên nhân**: Chọn role không khớp với role thực tế của user

**Giải pháp**:
- Chọn đúng role khi đăng nhập
- Hoặc cập nhật role của user: `python manage.py set_user_role username new_role`

### 2. "Tên đăng nhập hoặc mật khẩu không đúng"
**Nguyên nhân**: Username/password sai

**Giải pháp**:
- Kiểm tra lại username/password
- Reset password nếu cần:
```python
from django.contrib.auth.models import User
user = User.objects.get(username='your_username')
user.set_password('new_password')
user.save()
```

### 3. Lỗi import `UserRole`
**Nguyên nhân**: Import statement ở vị trí sai

**Giải pháp**: Đã sửa - import ở đầu function

### 4. Database chưa có UserRole records
**Nguyên nhân**: Users cũ chưa được gán role

**Giải pháp**:
```bash
python manage.py assign_user_roles
```

## 🔍 Debug checklist

- [ ] Chạy migrations đầy đủ
- [ ] Database có bảng `courses_userrole`
- [ ] Tất cả users đều có `user_role`
- [ ] Role values hợp lệ ('admin', 'staff', 'customer')
- [ ] Import statements đúng vị trí
- [ ] Template nhận đủ context variables
- [ ] CSRF token trong form
- [ ] Form action đúng URL

## 🧪 Test script

Tạo file `test_login.py`:
```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'online_course.settings')
django.setup()

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from courses.models import UserRole

# Test authentication
print("=== Testing Authentication ===")
test_users = [
    ('Admin', 'admin_password'),  # Thay bằng password thật
    ('staff_admin', 'staff123'),
    ('Manh', 'customer_password'),  # Thay bằng password thật
]

for username, password in test_users:
    try:
        user = authenticate(username=username, password=password)
        if user:
            role = user.user_role.role if hasattr(user, 'user_role') else 'No role'
            print(f"✓ {username}: Authenticated ({role})")
        else:
            print(f"✗ {username}: Failed")
    except Exception as e:
        print(f"✗ {username}: Error - {e}")

# Check all users
print("\n=== All Users Status ===")
for user in User.objects.all():
    has_role = hasattr(user, 'user_role')
    role = user.user_role.role if has_role else 'NO ROLE'
    print(f"{user.username}: {role}")
```

Chạy test:
```bash
python test_login.py
```

## 📝 Common fixes

### Fix 1: Tạo lại migration
```bash
python manage.py makemigrations
python manage.py migrate
```

### Fix 2: Xóa database và tạo lại (chỉ dùng cho development)
```bash
del db.sqlite3
python manage.py migrate
python manage.py createsuperuser
python manage.py assign_user_roles
```

### Fix 3: Clear cache và sessions
```bash
python manage.py clearsessions
```

## 💡 Tips

1. **Luôn chạy** `python manage.py assign_user_roles` sau khi tạo users mới
2. **Kiểm tra** role trước khi login
3. **Sử dụng** Django admin để xem users và roles
4. **Test** với nhiều scenarios khác nhau
5. **Log** errors để debug dễ dàng hơn

## 🆘 Still having issues?

Nếu vẫn còn lỗi, hãy:
1. Check Django logs: `python manage.py runserver --verbosity 2`
2. Xem browser console (F12)
3. Kiểm tra network tab trong DevTools
4. Verify database state với Django shell

---

*Document created: March 2026*
*Last updated: March 2026*
