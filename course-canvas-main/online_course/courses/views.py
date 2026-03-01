from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from .models import Course, Enrollment, Review


def home(request):
    return render(request, 'index.html')


def courses(request):
    course_list = Course.objects.filter(status='approved').order_by('-created_at')
    return render(request, 'courses/courses.html', {
        'courses': course_list
    })


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

        Review.objects.update_or_create(
            user=request.user,
            course=course,
            defaults={
                'rating': rating,
                'comment': comment
            }
        )

        messages.success(request, "Đánh giá của bạn đã được gửi!")

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