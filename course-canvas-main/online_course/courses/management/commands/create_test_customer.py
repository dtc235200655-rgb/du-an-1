from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from courses.models import UserRole


class Command(BaseCommand):
    help = 'Tạo tài khoản khách hàng mẫu để test'

    def handle(self, *args, **options):
        # Tạo tài khoản customer test
        username = 'customer_test'
        email = 'customer@example.com'
        password = 'customer123'
        
        # Kiểm tra xem đã tồn tại chưa
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'Tài khoản {username} đã tồn tại!')
            )
            user = User.objects.get(username=username)
        else:
            # Tạo user mới
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f'✓ Đã tạo tài khoản: {username}')
            )
        
        # Gán role customer
        user_role, created = UserRole.objects.get_or_create(
            user=user,
            defaults={'role': 'customer'}
        )
        
        if not created:
            user_role.role = 'customer'
            user_role.save()
        
        self.stdout.write(
            self.style.SUCCESS(f'✓ Đã gán role customer cho {username}')
        )
        
        # Hiển thị thông tin đăng nhập
        print('\n' + '='*60)
        print('📋 THÔNG TIN ĐĂNG NHẬP TÀI KHOẢN KHÁCH HÀNG')
        print('='*60)
        print(f'Username: {username}')
        print(f'Password: {password}')
        print(f'Role: Khách hàng (Customer)')
        print(f'Dashboard: /courses/dashboard/')
        print('='*60)
        print('\n💡 Để đăng nhập:')
        print('1. Truy cập: http://localhost:8000/login/')
        print('2. Chọn role: Khách hàng')
        print('3. Nhập username/password ở trên')
        print('4. Click "Đăng nhập"')
        print('='*60 + '\n')
