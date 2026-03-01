from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Category, Course, Enrollment, Review
from .forms import CourseAdminForm, EnrollmentAdminForm, ReviewAdminForm


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin cho Danh mục khóa học"""
    list_display = ['name', 'is_active', 'course_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    ordering = ['name']
    
    fieldsets = (
        ('Thông tin danh mục', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Thông tin hệ thống', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']
    
    def course_count(self, obj):
        """Đếm số khóa học trong danh mục"""
        count = obj.courses.count()
        return format_html(
            '<span style="background-color: #0d6efd; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            count
        )
    course_count.short_description = "Số khóa học"
    
    def has_delete_permission(self, request, obj=None):
        """Không cho xóa danh mục đã có khóa học"""
        if obj and obj.courses.exists():
            return False
        return super().has_delete_permission(request, obj)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin cho Khóa học - Có đầy đủ chức năng duyệt"""
    form = CourseAdminForm
    
    list_display = [
        'title', 
        'category', 
        'price_display',
        'status_badge', 
        'created_by', 
        'enrollment_count',
        'quick_actions',
        'created_at'
    ]
    
    list_filter = ['status', 'category', 'created_at', 'created_by']
    search_fields = ['title', 'description', 'created_by__username']
    readonly_fields = ['created_by', 'created_at', 'updated_at', 'image_preview']
    list_per_page = 20
    ordering = ['-created_at']
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('title', 'description', 'category', 'price')
        }),
        ('Hình ảnh', {
            'fields': ('image', 'image_preview')
        }),
        ('Trạng thái & Phê duyệt', {
            'fields': ('status',),
            'description': 'Thay đổi trạng thái để phê duyệt hoặc từ chối khóa học'
        }),
        ('Thông tin hệ thống', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_courses', 'reject_courses', 'set_pending', 'set_draft']
    
    def price_display(self, obj):
        try:
            price = float(obj.price)
            formatted_price = f"{price:,.0f} VNĐ"
        except (TypeError, ValueError):
            formatted_price = obj.price

        return format_html(
        '<span style="color: #198754; font-weight: bold;">{}</span>',
        formatted_price
    )
    
    def status_badge(self, obj):
        """Badge màu sắc cho trạng thái"""
        colors = {
            'draft': '#6c757d',
            'pending': '#fd7e14',
            'approved': '#198754',
            'rejected': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 12px; border-radius: 4px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = "Trạng thái"
    status_badge.admin_order_field = 'status'
    
    def quick_actions(self, obj):
        """Nút duyệt nhanh"""
        if obj.status == 'pending':
            approve_url = reverse('admin:courses_course_changelist')
            return format_html(
                '<a class="button" href="{}?action=approve&id={}" '
                'style="background-color: #28a745; color: white; padding: 5px 10px; '
                'border-radius: 3px; text-decoration: none; display: inline-block;" '
                'onclick="return confirm(\'Duyệt khóa học này?\');">✅ Duyệt</a> '
                '<a class="button" href="{}?action=reject&id={}" '
                'style="background-color: #dc3545; color: white; padding: 5px 10px; '
                'border-radius: 3px; text-decoration: none; display: inline-block; margin-left: 5px;" '
                'onclick="return confirm(\'Từ chối khóa học này?\');">❌ Từ chối</a>',
                approve_url, obj.pk, approve_url, obj.pk
            )
        return mark_safe('-')
    quick_actions.short_description = "Duyệt nhanh"
    
    def image_preview(self, obj):
        """Xem trước ảnh khóa học"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 200px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        return format_html('<span style="color: #999;">Chưa có ảnh</span>')
    image_preview.short_description = 'Xem trước hình ảnh'
    
    def enrollment_count(self, obj):
        """Số lượng đăng ký"""
        total = obj.enrollments.count()
        approved = obj.enrollments.filter(status='approved').count()
        pending = obj.enrollments.filter(status='pending').count()
        
        return format_html(
            '<div style="line-height: 1.5;">'
            '<span style="color: #0d6efd; font-weight: bold;">Tổng: {}</span><br>'
            '<small><span style="color: #198754;">✓ {}</span> | <span style="color: #ffc107;">⏳ {}</span></small>'
            '</div>',
            total,
            approved,
            pending
        )
    enrollment_count.short_description = "Đăng ký"
    
    def changelist_view(self, request, extra_context=None):
        """Xử lý duyệt nhanh từ URL"""
        if 'action' in request.GET and 'id' in request.GET:
            action = request.GET.get('action')
            course_id = request.GET.get('id')
            
            try:
                course = Course.objects.get(pk=course_id)
                if action == 'approve':
                    course.status = 'approved'
                    course.save()
                    self.message_user(request, f'✅ Đã duyệt khóa học "{course.title}"', level='success')
                elif action == 'reject':
                    course.status = 'rejected'
                    course.save()
                    self.message_user(request, f'❌ Đã từ chối khóa học "{course.title}"', level='warning')
            except Course.DoesNotExist:
                self.message_user(request, '⚠️ Khóa học không tồn tại', level='error')
        
        return super().changelist_view(request, extra_context)
    
    # ========== ACTIONS - Duyệt hàng loạt ==========
    
    def approve_courses(self, request, queryset):
        """Duyệt các khóa học đã chọn"""
        updated = queryset.update(status='approved')
        self.message_user(
            request, 
            f'✅ Đã duyệt {updated} khóa học.',
            level='success'
        )
    approve_courses.short_description = '✅ Duyệt các khóa học đã chọn'
    
    def reject_courses(self, request, queryset):
        """Từ chối các khóa học đã chọn"""
        updated = queryset.update(status='rejected')
        self.message_user(
            request,
            f'❌ Đã từ chối {updated} khóa học.',
            level='warning'
        )
    reject_courses.short_description = '❌ Từ chối các khóa học đã chọn'
    
    def set_pending(self, request, queryset):
        """Chuyển sang chờ duyệt"""
        updated = queryset.update(status='pending')
        self.message_user(
            request,
            f'⏳ Đã chuyển {updated} khóa học sang chờ duyệt.',
            level='info'
        )
    set_pending.short_description = '⏳ Chuyển sang chờ duyệt'
    
    def set_draft(self, request, queryset):
        """Chuyển về nháp"""
        updated = queryset.update(status='draft')
        self.message_user(
            request,
            f'📝 Đã chuyển {updated} khóa học về nháp.',
            level='info'
        )
    set_draft.short_description = '📝 Chuyển về nháp'
    
    def save_model(self, request, obj, form, change):
        """Tự động gán người tạo khi thêm mới"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """Admin cho Đăng ký học - Quản lý và duyệt đăng ký"""
    form = EnrollmentAdminForm
    
    list_display = [
        'id',
        'user_info',
        'course_info',
        'status_badge',
        'quick_approve',
        'created_at',
        'approved_at',
    ]
    
    list_filter = ['status', 'created_at', 'course__category']
    search_fields = [
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name',
        'course__title'
    ]
    readonly_fields = ['created_at', 'updated_at', 'approved_at']
    list_per_page = 25
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Thông tin đăng ký', {
            'fields': ('user', 'course')
        }),
        ('Trạng thái & Ghi chú', {
            'fields': ('status', 'admin_note'),
            'description': 'Duyệt hoặc từ chối đăng ký học viên'
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at', 'approved_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_enrollments', 'reject_enrollments', 'cancel_enrollments']
    
    def user_info(self, obj):
        """Thông tin học viên"""
        full_name = obj.user.get_full_name() or obj.user.username
        return format_html(
            '<div style="line-height: 1.5;">'
            '<strong style="color: #0d6efd;">{}</strong><br>'
            '<small style="color: #6c757d;">✉ {}</small>'
            '</div>',
            full_name,
            obj.user.email
        )
    user_info.short_description = "Học viên"
    user_info.admin_order_field = 'user__username'
    
    def course_info(self, obj):
        """Thông tin khóa học - FIXED"""
        price_text = "{:,.0f} VNĐ".format(float(obj.course.price))
        return format_html(
            '<div style="line-height: 1.5;">'
            '<strong>{}</strong><br>'
            '<small style="color: #198754; font-weight: bold;">{}</small>'
            '</div>',
            obj.course.title,
            price_text
        )
    course_info.short_description = "Khóa học"
    course_info.admin_order_field = 'course__title'
    
    def status_badge(self, obj):
        """Badge trạng thái đăng ký"""
        status_config = {
            'pending': {'color': '#ffc107', 'icon': '⏳'},
            'approved': {'color': '#28a745', 'icon': '✅'},
            'rejected': {'color': '#dc3545', 'icon': '❌'},
            'cancelled': {'color': '#6c757d', 'icon': '🚫'},
        }
        
        config = status_config.get(obj.status, {'color': '#6c757d', 'icon': '•'})
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 6px 14px; border-radius: 20px; font-weight: bold; display: inline-block;">'
            '{} {}'
            '</span>',
            config['color'],
            config['icon'],
            obj.get_status_display()
        )
    status_badge.short_description = "Trạng thái"
    status_badge.admin_order_field = 'status'
    
    def quick_approve(self, obj):
        """Nút duyệt nhanh"""
        if obj.status == 'pending':
            approve_url = reverse('admin:courses_enrollment_changelist')
            return format_html(
                '<a class="button" href="{}?action=approve&id={}" '
                'style="background-color: #28a745; color: white; padding: 5px 10px; '
                'border-radius: 3px; text-decoration: none; font-size: 12px;" '
                'onclick="return confirm(\'Duyệt đăng ký này?\');">✅ Duyệt</a> '
                '<a class="button" href="{}?action=reject&id={}" '
                'style="background-color: #dc3545; color: white; padding: 5px 10px; '
                'border-radius: 3px; text-decoration: none; font-size: 12px; margin-left: 3px;" '
                'onclick="return confirm(\'Từ chối đăng ký này?\');">❌ Từ chối</a>',
                approve_url, obj.pk, approve_url, obj.pk
            )
        elif obj.status == 'approved':
            return mark_safe('<span style="color: #28a745; font-weight: bold;">✓ Đã duyệt</span>')
        elif obj.status == 'rejected':
            return mark_safe('<span style="color: #dc3545; font-weight: bold;">✗ Đã từ chối</span>')
        return mark_safe('-')
    quick_approve.short_description = "Duyệt nhanh"
    
    def changelist_view(self, request, extra_context=None):
        """Xử lý duyệt nhanh từ URL"""
        if 'action' in request.GET and 'id' in request.GET:
            action = request.GET.get('action')
            enrollment_id = request.GET.get('id')
            
            try:
                enrollment = Enrollment.objects.get(pk=enrollment_id)
                if action == 'approve' and enrollment.status == 'pending':
                    enrollment.status = 'approved'
                    enrollment.approved_at = timezone.now()
                    enrollment.save()
                    self.message_user(
                        request, 
                        f'✅ Đã duyệt đăng ký của {enrollment.user.username} - Khóa: {enrollment.course.title}',
                        level='success'
                    )
                elif action == 'reject' and enrollment.status == 'pending':
                    enrollment.status = 'rejected'
                    enrollment.save()
                    self.message_user(
                        request,
                        f'❌ Đã từ chối đăng ký của {enrollment.user.username}',
                        level='warning'
                    )
            except Enrollment.DoesNotExist:
                self.message_user(request, '⚠️ Đăng ký không tồn tại', level='error')
        
        return super().changelist_view(request, extra_context)
    
    # ========== ACTIONS - Duyệt đăng ký hàng loạt ==========
    
    def approve_enrollments(self, request, queryset):
        """Duyệt các đăng ký đã chọn"""
        pending_enrollments = queryset.filter(status='pending')
        updated = pending_enrollments.update(
            status='approved',
            approved_at=timezone.now()
        )
        
        if updated > 0:
            self.message_user(
                request,
                f'✅ Đã duyệt {updated} đăng ký học.',
                level='success'
            )
        else:
            self.message_user(
                request,
                '⚠️ Không có đăng ký nào ở trạng thái "Chờ duyệt".',
                level='warning'
            )
    approve_enrollments.short_description = "✅ Duyệt các đăng ký đã chọn"
    
    def reject_enrollments(self, request, queryset):
        """Từ chối các đăng ký đã chọn"""
        pending_enrollments = queryset.filter(status='pending')
        updated = pending_enrollments.update(status='rejected')
        
        if updated > 0:
            self.message_user(
                request,
                f'❌ Đã từ chối {updated} đăng ký học.',
                level='warning'
            )
        else:
            self.message_user(
                request,
                '⚠️ Không có đăng ký nào ở trạng thái "Chờ duyệt".',
                level='warning'
            )
    reject_enrollments.short_description = "❌ Từ chối các đăng ký đã chọn"
    
    def cancel_enrollments(self, request, queryset):
        """Hủy các đăng ký đã chọn"""
        updated = queryset.update(status='cancelled')
        
        self.message_user(
            request,
            f'🚫 Đã hủy {updated} đăng ký học.',
            level='info'
        )
    cancel_enrollments.short_description = "🚫 Hủy các đăng ký đã chọn"
    
    def save_model(self, request, obj, form, change):
        """Tự động cập nhật thời gian duyệt"""
        if obj.status == 'approved' and not obj.approved_at:
            obj.approved_at = timezone.now()
        
        super().save_model(request, obj, form, change)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    form = ReviewAdminForm
    list_display = ('user', 'course', 'rating', 'has_image', 'is_visible', 'created_at')
    list_filter = ('course', 'rating', 'is_visible')
    search_fields = ('user__username', 'course__title')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'image_preview')
    
    fieldsets = (
        ('Thông tin đánh giá', {
            'fields': ('user', 'course', 'rating', 'comment')
        }),
        ('Ảnh đính kèm', {
            'fields': ('image', 'image_preview'),
            'description': 'Ảnh minh họa cho đánh giá (tùy chọn)'
        }),
        ('Quản lý', {
            'fields': ('admin_reply', 'is_visible')
        }),
        ('Thông tin hệ thống', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def has_image(self, obj):
        """Hiển thị icon nếu có ảnh"""
        if obj.image:
            return '✅'
        return '❌'
    has_image.short_description = 'Có ảnh'
    
    def image_preview(self, obj):
        """Xem trước ảnh đính kèm"""
        if obj.image:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-width: 200px; max-height: 200px; border-radius: 8px; border: 1px solid #ddd;" />'
                '</a>',
                obj.image.url,
                obj.image.url
            )
        return format_html('<span style="color: #999;">Không có ảnh</span>')
    image_preview.short_description = 'Xem trước ảnh'

# ========== TÙY CHỈNH DJANGO ADMIN SITE ==========

admin.site.site_header = "📚 Quản trị Online Courses"
admin.site.site_title = "Admin Online Courses"
admin.site.index_title = "Chào mừng đến trang quản trị"