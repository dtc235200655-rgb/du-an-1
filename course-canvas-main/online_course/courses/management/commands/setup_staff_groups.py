from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from courses.models import Course, Enrollment, Review, StaffProfile


class Command(BaseCommand):
    help = 'Tạo các nhóm nhân viên và phân quyền'

    def handle(self, *args, **options):
        # Tạo các nhóm
        groups_data = [
            {
                'name': 'Quản lý khóa học',
                'permissions': [
                    'can_manage_courses',
                    'can_approve_course',
                    'can_reject_course',
                    'view_course',
                    'add_course',
                    'change_course',
                    'delete_course',
                ]
            },
            {
                'name': 'Quản lý đăng ký',
                'permissions': [
                    'can_manage_enrollments',
                    'can_approve_enrollment',
                    'can_reject_enrollment',
                    'view_enrollment',
                    'add_enrollment',
                    'change_enrollment',
                    'delete_enrollment',
                ]
            },
            {
                'name': 'Quản lý đánh giá',
                'permissions': [
                    'can_manage_reviews',
                    'view_review',
                    'change_review',
                    'delete_review',
                ]
            },
            {
                'name': 'Quản lý nội dung',
                'permissions': [
                    'can_manage_content',
                    'view_category',
                    'add_category',
                    'change_category',
                    'delete_category',
                ]
            },
            {
                'name': 'Nhân viên cấp cao',
                'permissions': [
                    'can_manage_courses',
                    'can_manage_enrollments',
                    'can_manage_reviews',
                    'can_manage_content',
                    'can_view_reports',
                    'can_approve_course',
                    'can_reject_course',
                    'can_approve_enrollment',
                    'can_reject_enrollment',
                    'view_course',
                    'add_course',
                    'change_course',
                    'delete_course',
                    'view_enrollment',
                    'add_enrollment',
                    'change_enrollment',
                    'delete_enrollment',
                    'view_review',
                    'change_review',
                    'delete_review',
                    'view_category',
                    'add_category',
                    'change_category',
                    'delete_category',
                    'view_user',
                    'change_user',
                ]
            }
        ]

        # Tạo các nhóm và gán quyền
        for group_data in groups_data:
            group, created = Group.objects.get_or_create(name=group_data['name'])
            
            if created:
                self.stdout.write(f'Tạo nhóm: {group_data["name"]}')
            else:
                self.stdout.write(f'Nhóm đã tồn tại: {group_data["name"]}')
                # Xóa các quyền cũ
                group.permissions.clear()
            
            # Gán quyền
            for perm_codename in group_data['permissions']:
                try:
                    # Xử lý các quyền đặc biệt
                    if perm_codename.startswith('can_'):
                        # Tìm permission trong StaffProfile
                        content_type = ContentType.objects.get_for_model(StaffProfile)
                        permission = Permission.objects.get(
                            content_type=content_type,
                            codename=perm_codename
                        )
                    else:
                        # Tìm permission trong các model khác
                        app_labels = ['courses', 'auth', 'admin']
                        permission = None
                        
                        for app_label in app_labels:
                            try:
                                content_type = ContentType.objects.get(
                                    app_label=app_label,
                                    model__in=['course', 'enrollment', 'review', 'category', 'user']
                                )
                                permission = Permission.objects.get(
                                    content_type=content_type,
                                    codename=perm_codename
                                )
                                break
                            except:
                                continue
                    
                    if permission:
                        group.permissions.add(permission)
                        self.stdout.write(f'  ✓ Gán quyền: {perm_codename}')
                    else:
                        self.stdout.write(f' ✗ Không tìm thấy quyền: {perm_codename}')
                        
                except Exception as e:
                    self.stdout.write(f' ✗ỗi gán quyền {perm_codename}: {str(e)}')
            
            group.save()
        
        self.stdout.write(
            self.style.SUCCESS('\n✓ Hoàn thành thiết lập các nhóm nhân viên!')
        )
