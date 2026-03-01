from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    """Model Danh mục khóa học"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Tên danh mục")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    
    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Course(models.Model):
    """Model Khóa học"""
    STATUS_CHOICES = [
        ('draft', 'Nháp'),
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
    ]
    
    # Thông tin cơ bản
    title = models.CharField(max_length=200, verbose_name="Tiêu đề")
    description = models.TextField(verbose_name="Mô tả")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Giá")
    image = models.ImageField(upload_to='courses/', verbose_name="Hình ảnh")
    
    # Danh mục
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='courses',
        verbose_name="Danh mục"
    )
    
    # Trạng thái và quy trình duyệt
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='draft',
        verbose_name="Trạng thái"
    )
    
    # Người tạo và thời gian
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='courses',
        verbose_name="Người tạo"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    
    class Meta:
        verbose_name = "Khóa học"
        verbose_name_plural = "Khóa học"
        ordering = ['-created_at']
        permissions = [
            ("can_approve_course", "Có thể duyệt khóa học"),
            ("can_reject_course", "Có thể từ chối khóa học"),
        ]
    
    def __str__(self):
        return self.title
    
    def get_status_display_badge(self):
        """Trả về màu sắc cho badge trạng thái"""
        status_colors = {
            'draft': 'gray',
            'pending': 'orange',
            'approved': 'green',
            'rejected': 'red',
        }
        return status_colors.get(self.status, 'gray')


class Enrollment(models.Model):
    """Model Đăng ký học - Quản lý học viên đăng ký khóa học"""
    STATUS_CHOICES = [
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
        ('cancelled', 'Đã hủy'),
    ]
    
    # Thông tin đăng ký
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name="Học viên"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name="Khóa học"
    )
    
    # Trạng thái đăng ký
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Trạng thái"
    )
    
    # Thời gian
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đăng ký")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="Ngày duyệt")
    
    # Ghi chú từ admin (nếu từ chối)
    admin_note = models.TextField(blank=True, verbose_name="Ghi chú từ admin")
    
    class Meta:
        verbose_name = "Đăng ký học"
        verbose_name_plural = "Đăng ký học"
        ordering = ['-created_at']
        unique_together = ['user', 'course']  # Tránh đăng ký trùng
        permissions = [
            ("can_approve_enrollment", "Có thể duyệt đăng ký"),
            ("can_reject_enrollment", "Có thể từ chối đăng ký"),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title} ({self.get_status_display()})"
    
    def get_status_display_badge(self):
        """Trả về màu sắc cho badge trạng thái"""
        status_colors = {
            'pending': 'warning',
            'approved': 'success',
            'rejected': 'danger',
            'cancelled': 'secondary',
        }
        return status_colors.get(self.status, 'secondary')