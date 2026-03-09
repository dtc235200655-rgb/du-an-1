# Hướng dẫn Hệ thống Đăng nhập Đa vai trò

## Tổng quan
Hệ thống cho phép người dùng chọn vai trò khi đăng nhập:
- **Admin** (Quản trị viên): Truy cập trang quản trị Django
- **Staff** (Nhân viên): Truy cập bảng điều khiển nhân viên
- **Customer** (Khách hàng): Truy cập bảng điều khiển người dùng

## Cách sử dụng

### 1. Đăng nhập với vai trò
1. Truy cập trang `/login/`
2. Chọn vai trò của bạn bằng cách click vào card tương ứng:
   -🔴Admin** - Quản trị viên
   -🔵Staff** - Nhân viên  
   -🟢 **Customer** - Khách hàng
3. Nhập tên đăng nhập và mật khẩu
4. Click nút "Đăng nhập"
5. Hệ thống sẽ tự động chuyển hướng bạn đến đúng bảng điều khiển

### 2. Quản lý vai trò

#### Gán vai trò cho người dùng mới
Khi đăng ký tài khoản mới, hệ thống tự động gán vai trò "Customer" (Khách hàng).

#### Thay đổi vai trò người dùng hiện có
Sử dụng command line:

```bash
# Gán vai trò cho người dùng
python manage.py set_user_role <username> <role>

# Ví dụ:
python manage.py set_user_role manh123 admin
python manage.py set_user_role staff_user staff
python manage.py set_user_role customer1 customer
```

#### Gán vai trò cho tất cả người dùng hiện có
```bash
python manage.py assign_user_roles
```

### 3. Kiểm tra vai trò người dùng

#### Trong template:
```html
{% if user.user_role %}
    <span class="badge {{ user.user_role.get_role_badge_class }}">
        {{ user.user_role.get_role_display }}
    </span>
{% endif %}
```

#### Trong view:
```python
# Kiểm tra vai trò
if user.user_role.role == 'admin':
    # Logic cho admin
elif user.user_role.role == 'staff':
    # Logic cho staff
else:
    # Logic cho customer
```

## Tùy chỉnh Redirect

Mỗi vai trò có URL redirect riêng:
- **Admin**: `/admin/` (Trang quản trị Django)
- **Staff**: `/staff/dashboard/` (Bảng điều khiển nhân viên)
- **Customer**: `/dashboard/` (Bảng điều khiển người dùng)

Bạn có thể tùy chỉnh trong model `UserRole`:
```python
def get_role_redirect_url(self):
    redirect_urls = {
        'admin': '/admin/',
        'staff': '/staff/dashboard/',
        'customer': '/dashboard/',
    }
    return redirect_urls.get(self.role, '/dashboard/')
```

## Class CSS cho badge vai trò

Mỗi vai trò có class badge riêng:
- **Admin**: `bg-danger` (màu đỏ)
- **Staff**: `bg-primary` (màu xanh dương)
- **Customer**: `bg-success` (màu xanh lá)

## Bảo mật

Hệ thống kiểm tra vai trò người dùng khi đăng nhập:
- Nếu vai trò được chọn không khớp với vai trò thực tế → Hiển thị lỗi
- Nếu người dùng không có UserRole → Tự động gán vai trò "Customer"

## Ví dụ thực tế

### Người dùng Admin:
1. Chọn vai trò "Admin"
2. Đăng nhập thành công
3. Tự động chuyển đến `/admin/`
4. Thanh điều hướng hiển thị "Admin Panel"

### Người dùng Staff:
1. Chọn vai trò "Staff"  
2. Đăng nhập thành công
3. Tự động chuyển đến `/staff/dashboard/`
4. Thanh điều hướng hiển thị "Staff Dashboard" và badge màu xanh

### Người dùng Customer:
1. Chọn vai trò "Customer"
2. Đăng nhập thành công
3. Tự động chuyển đến `/dashboard/`
4. Thanh điều hướng hiển thị "Dashboard" và badge màu xanh lá

## Troubleshooting

### Lỗi: "Tài khoản này không có vai trò..."
Nguyên nhân: Vai trò được chọn không khớp với vai trò thực tế của tài khoản.

Giải pháp: Chọn đúng vai trò hoặc cập nhật vai trò của tài khoản bằng command.

### Không thấy badge vai trò
Nguyên nhân: Người dùng chưa có UserRole.

Giải pháp: Chạy command `assign_user_roles` hoặc `set_user_role`.
