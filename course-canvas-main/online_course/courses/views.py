from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.core.paginator import Paginator
from .models import Course, Enrollment, Review, Category
from .forms import CourseCreateForm, CourseUpdateForm
from .utils import validate_image_file


def home(request):
    return render(request, 'index.html')


from django.db.models import Q   # thêm dòng này ở đầu file nếu chưa có

def courses(request):
    # ===== LẤY CÁC THAM SỐ TÌM KIẾM =====
    query = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', '')
    category_id = request.GET.get('category', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    
    # ===== BASE QUERYSET =====
    course_list = Course.objects.filter(status='approved').select_related('category', 'created_by')
    
    # ===== TÌM KIẾM =====
    if query:
        course_list = course_list.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(created_by__username__icontains=query)
        )
    
    # ===== LỌC THEO DANH MỤC =====
    if category_id:
        try:
            category_id = int(category_id)
            course_list = course_list.filter(category_id=category_id)
        except (ValueError, TypeError):
            pass
    
    # ===== LỌC THEO GIÁ =====
    if price_min:
        try:
            course_list = course_list.filter(price__gte=float(price_min))
        except (ValueError, TypeError):
            pass
    
    if price_max:
        try:
            course_list = course_list.filter(price__lte=float(price_max))
        except (ValueError, TypeError):
            pass
    
    # ===== SẮP XẾP =====
    sort_options = {
        'newest': '-created_at',
        'oldest': 'created_at',
        'price_low': 'price',
        'price_high': '-price',
        'title_a': 'title',
        'title_z': '-title',
        'popular': '-enrollments__count'  # Sẽ annotate sau
    }
    
    if sort in sort_options:
        if sort == 'popular':
            course_list = course_list.annotate(
                enrollment_count=Count('enrollments', filter=Q(enrollments__status='approved'))
            ).order_by('-enrollment_count')
        else:
            course_list = course_list.order_by(sort_options[sort])
    else:
        course_list = course_list.order_by('-created_at')
    
    # ===== PHÂN TRANG =====
    paginator = Paginator(course_list, 9)  # 9 khóa học mỗi trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # ===== LẤY DANH MỤC CHO BỘ LỌC =====
    categories = Category.objects.filter(is_active=True, courses__status='approved').distinct()
    
    context = {
        'courses': page_obj,
        'categories': categories,
        'query': query,
        'sort': sort,
        'category_id': int(category_id) if category_id else None,
        'price_min': price_min,
        'price_max': price_max,
        'sort_options': sort_options,
        'paginator': paginator,
        'page_obj': page_obj,
    }
    
    return render(request, 'courses/courses.html', context)


def course_detail(request, pk):
    course = get_object_or_404(
        Course,
        pk=pk,
        status='approved'
    )

    is_enrolled = False
    enrollment_status = None

    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(
            user=request.user,
            course=course
        ).first()

        if enrollment:
            is_enrolled = True
            enrollment_status = enrollment.status

    # Lấy danh sách review (chỉ hiển thị review được admin cho phép)
    reviews = Review.objects.filter(
        course=course,
        is_visible=True
    ).select_related('user').order_by('-created_at')

    # Tính điểm trung bình
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    context = {
        'course': course,
        'is_enrolled': is_enrolled,
        'enrollment_status': enrollment_status,
        'reviews': reviews,
        'average_rating': round(average_rating, 1) if average_rating else None,
    }

    return render(request, 'courses/course_detail.html', context)


# ================= REVIEW =================

@login_required
def add_review(request, pk):
    course = get_object_or_404(
        Course,
        pk=pk,
        status='approved'
    )
    
    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")
        image = request.FILES.get("image")
        
        # Validate ảnh nếu có
        if image:
            from .utils import validate_review_image
            errors = validate_review_image(image)
            if errors:
                for error in errors:
                    messages.error(request, error)
                return redirect('courses:course_detail', pk=pk)
        
        # Tạo hoặc cập nhật đánh giá
        review, created = Review.objects.update_or_create(
            user=request.user,
            course=course,
            defaults={
                'rating': rating,
                'comment': comment,
                'image': image if image else None
            }
        )
        
        if created:
            messages.success(request, "Đánh giá của bạn đã được gửi!")
        else:
            messages.success(request, "Đánh giá của bạn đã được cập nhật!")

    return redirect('courses:course_detail', pk=pk)


# ================= ENROLL =================

@login_required
def enroll_course(request, pk):
    if request.method != 'POST':
        return redirect('courses:course_detail', pk=pk)

    course = get_object_or_404(
        Course,
        pk=pk,
        status='approved'
    )

    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={'status': 'pending'}
    )

    if not created:
        if enrollment.status in ['rejected', 'cancelled']:
            enrollment.status = 'pending'
            enrollment.save()
            messages.success(
                request,
                f'Bạn đã đăng ký lại khóa học "{course.title}". Vui lòng chờ admin duyệt.'
            )
        else:
            status_messages = {
                'pending': 'Bạn đã đăng ký khóa học này trước đó. Vui lòng chờ admin duyệt.',
                'approved': 'Bạn đã được duyệt cho khóa học này rồi!'
            }
            messages.info(request, status_messages.get(enrollment.status))
            return redirect('courses:course_detail', pk=pk)
    else:
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
    enrollments = Enrollment.objects.filter(
        user=request.user
    ).select_related('course').order_by('-created_at')

    return render(request, 'courses/my_courses.html', {
        'enrollments': enrollments
    })


@login_required
def cancel_enrollment(request, pk):
    if request.method != 'POST':
        return redirect('courses:my_courses')

    enrollment = get_object_or_404(
        Enrollment,
        pk=pk,
        user=request.user
    )

    if enrollment.status == 'pending':
        enrollment.status = 'cancelled'
        enrollment.save()
        messages.success(request, f'Đã hủy đăng ký khóa học "{enrollment.course.title}"')
    else:
        messages.error(request, 'Không thể hủy đăng ký này')

    return redirect('courses:my_courses')


# ================= AUTH =================

def login_view(request):
    return render(request, 'login.html')


def register_view(request):
    return render(request, 'register.html')


@login_required
def dashboard(request):
    enrollments = Enrollment.objects.filter(
        user=request.user
    ).select_related('course').order_by('-created_at')

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


# =========== COURSE MANAGEMENT VIEWS ===========

@login_required
def create_course(request):
    """Tạo khóa học mới với validation file upload"""
    if request.method == 'POST':
        form = CourseCreateForm(request.POST, request.FILES, user=request.user)
        
        if form.is_valid():
            # Kiểm tra thêm file upload
            image = request.FILES.get('image')
            if image:
                errors = validate_image_file(image)
                if errors:
                    for error in errors:
                        messages.error(request, error)
                    return render(request, 'courses/create_course.html', {'form': form})
            
            course = form.save()
            messages.success(request, f'Khóa học "{course.title}" đã được tạo thành công! Chờ admin duyệt.')
            return redirect('courses:dashboard')
        else:
            # Hiển thị lỗi form
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CourseCreateForm()
    
    return render(request, 'courses/create_course.html', {'form': form})


@login_required
def edit_course(request, pk):
    """Sửa khóa học với validation file upload"""
    course = get_object_or_404(Course, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        form = CourseUpdateForm(request.POST, request.FILES, instance=course, user=request.user)
        
        if form.is_valid():
            # Kiểm tra file upload nếu có
            image = request.FILES.get('image')
            if image:
                errors = validate_image_file(image)
                if errors:
                    for error in errors:
                        messages.error(request, error)
                    return render(request, 'courses/edit_course.html', {'form': form, 'course': course})
            
            course = form.save()
            messages.success(request, f'Khóa học "{course.title}" đã được cập nhật!')
            return redirect('courses:dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CourseUpdateForm(instance=course)
    
    return render(request, 'courses/edit_course.html', {'form': form, 'course': course})


@login_required
def delete_course(request, pk):
    """Xóa khóa học (chỉ người tạo)"""
    course = get_object_or_404(Course, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        title = course.title
        course.delete()
        messages.success(request, f'Khóa học "{title}" đã được xóa thành công!')
        return redirect('courses:dashboard')
    
    return render(request, 'courses/delete_course.html', {'course': course})