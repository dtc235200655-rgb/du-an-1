from django.urls import path
from . import views


app_name = 'courses'

urlpatterns = [
    
    # Trang chủ / danh sách khóa học
    path('', views.courses, name='list'),

    # Chi tiết khóa học
    path('<int:pk>/', views.course_detail, name='course_detail'),

    # Đánh giá 
    path('<int:pk>/review/', views.add_review, name='add_review'),

    # Đăng ký học
    path('<int:pk>/enroll/', views.enroll_course, name='enroll_course'),
    
    # Dashboard sau đăng nhập
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Khóa học của tôi
    path('my-courses/', views.my_courses, name='my_courses'),

    # Hủy đăng ký
    path('enrollment/<int:pk>/cancel/', views.cancel_enrollment, name='cancel_enrollment'),
    
    # Quản lý khóa học
    path('create/', views.create_course, name='create_course'),
    path('<int:pk>/edit/', views.edit_course, name='edit_course'),
    path('<int:pk>/delete/', views.delete_course, name='delete_course'),
    
    # Quản lý nhân viên
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/management/', views.staff_management, name='staff_management'),
    path('staff/create/', views.create_staff, name='create_staff'),
    
]