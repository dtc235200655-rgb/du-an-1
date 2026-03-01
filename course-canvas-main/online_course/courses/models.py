from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg


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

    title = models.CharField(max_length=200, verbose_name="Tiêu đề")
    description = models.TextField(verbose_name="Mô tả")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Giá")
    image = models.ImageField(upload_to='courses/', verbose_name="Hình ảnh")

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses',
        verbose_name="Danh mục"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="Trạng thái"
    )

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
        status_colors = {
            'draft': 'gray',
            'pending': 'orange',
            'approved': 'green',
            'rejected': 'red',
        }
        return status_colors.get(self.status, 'gray')

    def average_rating(self):
        """Tính điểm trung bình"""
        return self.reviews.aggregate(avg=Avg('rating'))['avg']

    def total_reviews(self):
        """Tổng số review"""
        return self.reviews.count()


class Enrollment(models.Model):
    """Model Đăng ký học"""

    STATUS_CHOICES = [
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
        ('cancelled', 'Đã hủy'),
    ]

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

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Trạng thái"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đăng ký")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="Ngày duyệt")

    admin_note = models.TextField(blank=True, verbose_name="Ghi chú từ admin")

    class Meta:
        verbose_name = "Đăng ký học"
        verbose_name_plural = "Đăng ký học"
        ordering = ['-created_at']
        unique_together = ['user', 'course']
        permissions = [
            ("can_approve_enrollment", "Có thể duyệt đăng ký"),
            ("can_reject_enrollment", "Có thể từ chối đăng ký"),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.course.title} ({self.get_status_display()})"

    def get_status_display_badge(self):
        status_colors = {
            'pending': 'warning',
            'approved': 'success',
            'rejected': 'danger',
            'cancelled': 'secondary',
        }
        return status_colors.get(self.status, 'secondary')


# =============================
# ⭐ MODEL ĐÁNH GIÁ KHÓA HỌC
# =============================

class Review(models.Model):
    """Model Đánh giá khóa học"""

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="Khóa học"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Học viên"
    )

    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Số sao (1-5)"
    )

    comment = models.TextField(verbose_name="Nhận xét")

    # ✅ ADMIN CÓ THỂ PHẢN HỒI
    admin_reply = models.TextField(
        blank=True,
        null=True,
        verbose_name="Phản hồi từ Admin"
    )

    # ✅ ADMIN CÓ THỂ ẨN REVIEW TIÊU CỰC
    is_visible = models.BooleanField(
        default=True,
        verbose_name="Hiển thị công khai"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Đánh giá"
        verbose_name_plural = "Đánh giá"
        ordering = ['-created_at']
        unique_together = ['course', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.course.title} ({self.rating}⭐)"