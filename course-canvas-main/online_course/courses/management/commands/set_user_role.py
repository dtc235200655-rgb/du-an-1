from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from courses.models import UserRole


class Command(BaseCommand):
    help = 'Thiết lập vai trò cho người dùng'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Tên người dùng')
        parser.add_argument('role', type=str, choices=['admin', 'staff', 'customer'], help='Vai trò')

    def handle(self, *args, **options):
        username = options['username']
        role = options['role']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Không tìm thấy người dùng với tên: {username}')
            )
            return
        
        # Tạo hoặc cập nhật UserRole
        user_role, created = UserRole.objects.get_or_create(
            user=user,
            defaults={'role': role}
        )
        
        if not created:
            user_role.role = role
            user_role.save()
            self.stdout.write(
                self.style.SUCCESS(f'✓ Đã cập nhật vai trò của {username} thành {user_role.get_role_display()}')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Đã gán vai trò {user_role.get_role_display()} cho {username}')
            )
