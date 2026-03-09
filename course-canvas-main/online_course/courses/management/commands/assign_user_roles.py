from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from courses.models import UserRole


class Command(BaseCommand):
    help = 'Gán vai trò cho tất cả người dùng hiện có'

    def handle(self, *args, **options):
        users = User.objects.all()
        
        self.stdout.write(f'Tìm thấy {users.count()} người dùng')
        
        for user in users:
            # Kiểm tra xem đã có UserRole chưa
            if hasattr(user, 'user_role'):
                self.stdout.write(f'User {user.username} đã có vai trò: {user.user_role.get_role_display()}')
                continue
            
            # Xác định vai trò dựa trên đặc điểm
            if user.is_superuser or user.is_staff:
                role = 'admin'
            elif hasattr(user, 'staff_profile'):
                role = 'staff'
            else:
                role = 'customer'
            
            # Tạo UserRole
            UserRole.objects.create(
                user=user,
                role=role
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ Gán vai trò {role} cho user {user.username}')
            )
        
        self.stdout.write(
            self.style.SUCCESS('\n✓ Hoàn thành gán vai trò cho tất cả người dùng!')
        )
