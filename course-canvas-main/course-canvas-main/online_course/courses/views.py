from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Course, Enrollment


def home(request):
    """Trang chủ"""
    return render(request, 'index.html')


def courses(request):
    """Danh sách tất cả khóa học (chỉ hiện khóa đã duyệt)"""
    course_list = Course.objects.filter(status='approved').order_by('-created_at')
    return render(request, 'courses/courses.html', {
        'courses': course_list
    })


def course_detail(request, pk):
    """Chi tiết khóa học"""
    course = get_object_or_404(
        Course,
        pk=pk,
        status='approved'
    )
    
    # Kiểm tra xem user đã đăng ký chưa (nếu đã login)
    is_enrolled = False
    enrollment_status = None
    
    if request.user.is_authenticated:
        try:
            enrollment = Enrollment.objects.get(
                user=request.user,
                course=course
            )
            is_enrolled = True
            enrollment_status = enrollment.status
        except Enrollment.DoesNotExist:
            pass
    
    return render(request, 'courses/course_detail.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'enrollment_status': enrollment_status,
    })


@login_required
def enroll_course(request, pk):
    """Đăng ký học khóa học"""
    # Chỉ cho phép POST request
    if request.method != 'POST':
        return redirect('course_detail', pk=pk)
    
    # Lấy khóa học (chỉ lấy khóa đã duyệt)
    course = get_object_or_404(
        Course,
        pk=pk,
        status='approved'
    )
    
    # Tạo hoặc lấy enrollment (tránh đăng ký trùng)
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={'status': 'pending'}
    )
    
    # Nếu đã đăng ký trước đó
    if not created:
        # Nếu đã bị từ chối/hủy → cho phép đăng ký lại
        if enrollment.status in ['rejected', 'cancelled']:
            enrollment.status = 'pending'
            enrollment.save()
            messages.success(
                request, 
                f'Bạn đã đăng ký lại khóa học "{course.title}". Vui lòng chờ admin duyệt.'
            )
        # Nếu đang chờ duyệt hoặc đã duyệt
        else:
            status_messages = {
                'pending': 'Bạn đã đăng ký khóa học này trước đó. Vui lòng chờ admin duyệt.',
                'approved': 'Bạn đã được duyệt cho khóa học này rồi!'
            }
            messages.info(request, status_messages.get(enrollment.status))
            return redirect('course_detail', pk=pk)
    else:
        # Đăng ký mới thành công
        messages.success(
            request,
            f'Đăng ký khóa học "{course.title}" thành công! Vui lòng chờ admin duyệt.'
        )
    
    return render(request, 'courses/enroll_success.html', {
        'course': course,
        'enrollment': enrollment
    })


@login_required
def my_courses(request):
    """Danh sách khóa học của tôi"""
    enrollments = Enrollment.objects.filter(
        user=request.user
    ).select_related('course').order_by('-created_at')
    
    return render(request, 'courses/my_courses.html', {
        'enrollments': enrollments
    })


@login_required
def cancel_enrollment(request, pk):
    """Hủy đăng ký khóa học (chỉ được hủy khi status=pending)"""
    if request.method != 'POST':
        return redirect('my_courses')
    
    enrollment = get_object_or_404(
        Enrollment,
        pk=pk,
        user=request.user
    )
    
    # Chỉ cho phép hủy khi đang chờ duyệt
    if enrollment.status == 'pending':
        enrollment.status = 'cancelled'
        enrollment.save()
        messages.success(request, f'Đã hủy đăng ký khóa học "{enrollment.course.title}"')
    else:
        messages.error(request, 'Không thể hủy đăng ký này')
    
    return redirect('my_courses')


def login_view(request):
    """Trang đăng nhập"""
    return render(request, 'login.html')


def register_view(request):
    """Trang đăng ký"""
    return render(request, 'register.html')


@login_required
def dashboard(request):
    """Dashboard - Trang cá nhân của user"""
    enrollments = Enrollment.objects.filter(
        user=request.user
    ).select_related('course').order_by('-created_at')
    
    # Đếm số lượng theo trạng thái
    approved_count = enrollments.filter(status='approved').count()
    pending_count = enrollments.filter(status='pending').count()
    rejected_count = enrollments.filter(status='rejected').count()
    cancelled_count = enrollments.filter(status='cancelled').count()
    
    return render(request, 'courses/dashboard.html', {
        'enrollments': enrollments,
        'approved_count': approved_count,
        'pending_count': pending_count,
        'rejected_count': rejected_count,
        'cancelled_count': cancelled_count,
    })