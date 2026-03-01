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
    
    
    
]
