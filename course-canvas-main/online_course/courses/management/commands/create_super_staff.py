from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from courses.models import StaffProfile


class Command(BaseCommand):
    help = 'Tạo nhân viên cấp cao để test hệ thống'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='staff_admin',
            help='Tên đăng nhập cho nhân viên cấp cao'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='staff@example.com',
            help='Email cho nhân viên cấp cao'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='staff123',
            help='Mật khẩu cho nhân viên cấp cao'
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        
        # Kiểm tra xem user đã tồn tại chưa
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User {username} đã tồn tại')
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
                self.style.SUCCESS(f'Tạo user {username} thành công')
            )
        
        # Kiểm tra xem đã có StaffProfile chưa
        if hasattr(user, 'staff_profile'):
            staff_profile = user.staff_profile
            self.stdout.write(
                self.style.WARNING(f'Nhân viên {username} đã tồn tại')
            )
        else:
            # Tạo StaffProfile
            staff_profile = StaffProfile.objects.create(
                user=user,
                role='super_staff',
                phone='0123456789',
                department='Quản trị hệ thống'
            )
            self.stdout.write(
                self.style.SUCCESS(f'Tạo StaffProfile cho {username} thành công')
            )
        
        # Gán vào nhóm Nhân viên cấp cao
        try:
            group = Group.objects.get(name='Nhân viên cấp cao')
            user.groups.add(group)
            self.stdout.write(
                self.style.SUCCESS(f'Gán {username} vào nhóm Nhân viên cấp cao')
            )
        except Group.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Nhóm Nhân viên cấp cao chưa được tạo. Hãy chạy: python manage.py setup_staff_groups')
            )
            return
        
        # Kích hoạt tài khoản
        staff_profile.is_active = True
        staff_profile.save()
        
        self.stdout.write(
            self.style.SUCCESS('\n✓ Hoàn thành!')
        )
        self.stdout.write(
            f'  Username: {username}'
        )
        self.stdout.write(
            f'  Password: {password}'
        )
        self.stdout.write(
            f'  Truy cập: http://localhost:8000/staff/dashboard/'
        )
